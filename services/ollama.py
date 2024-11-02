import os
import requests
from typing import Dict, Any, Optional, Tuple
import json
from core.config import Config
import time
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry

class OllamaService:
    def __init__(self, model: str = None, max_retries: int = 3):
        """Initialize Ollama service with specified model"""
        self.base_url = Config.OLLAMA_API_URL
        self.model = model or Config.OLLAMA_MODEL
        self.max_retries = max_retries
        self.session = self._create_session()
        self._template = """
        Analyze the following GitHub issue and provide structured feedback:
        
        Title: {title}
        Description: {body}
        
        Please analyze the following aspects:
        1. Technical complexity (scale 1-10)
        2. Impact assessment
        3. Implementation effort
        4. Priority level
        5. Required expertise
        6. Potential risks
        
        Provide the analysis in JSON format with the following structure:
        {{
            "technical_complexity": <1-10>,
            "impact_assessment": {{
                "security": <1-10>,
                "performance": <1-10>,
                "ux": <1-10>
            }},
            "implementation_effort": "<low|medium|high>",
            "priority_level": "<low|medium|high>",
            "required_expertise": ["<expertise1>", "<expertise2>"],
            "potential_risks": ["<risk1>", "<risk2>"]
        }}
        """

    def _create_session(self) -> requests.Session:
        """Create a session with retry mechanism"""
        session = requests.Session()
        retry_strategy = Retry(
            total=self.max_retries,
            backoff_factor=0.5,
            status_forcelist=[429, 500, 502, 503, 504],
        )
        adapter = HTTPAdapter(max_retries=retry_strategy)
        session.mount("http://", adapter)
        session.mount("https://", adapter)
        return session

    def get_connection_status(self) -> Dict[str, Any]:
        """
        Get detailed connection status including configuration and health
        
        Returns:
            Dict containing connection status details
        """
        status = {
            'configured': bool(self.base_url and self.model),
            'base_url': self.base_url,
            'model': self.model,
            'is_healthy': False,
            'health_details': '',
            'available_models': [],
            'errors': []
        }
        
        if not status['configured']:
            if not self.base_url:
                status['errors'].append("Ollama API URL is not configured")
            if not self.model:
                status['errors'].append("Ollama model is not configured")
            return status
            
        try:
            # Test basic connectivity
            health_response = self.session.get(
                f"{self.base_url}/api/health",
                timeout=5
            )
            
            status['is_healthy'] = health_response.status_code == 200
            status['health_details'] = f"Health check status: {health_response.status_code}"
            
            # Get available models if health check passed
            if status['is_healthy']:
                try:
                    model_response = self.session.get(
                        f"{self.base_url}/api/tags",
                        timeout=5
                    )
                    
                    if model_response.status_code == 200:
                        models_data = model_response.json()
                        if isinstance(models_data, dict) and 'models' in models_data:
                            status['available_models'] = [
                                model['name'] for model in models_data.get('models', [])
                            ]
                            
                            if self.model not in status['available_models']:
                                status['errors'].append(
                                    f"Model '{self.model}' is not available. "
                                    f"Available models: {', '.join(status['available_models'])}"
                                )
                    else:
                        status['errors'].append("Failed to retrieve available models")
                        
                except Exception as e:
                    status['errors'].append(f"Error checking available models: {str(e)}")
                    
        except requests.exceptions.ConnectionError:
            status['errors'].append(f"Failed to connect to Ollama service at {self.base_url}")
        except requests.exceptions.Timeout:
            status['errors'].append("Connection to Ollama service timed out")
        except Exception as e:
            status['errors'].append(f"Unexpected error: {str(e)}")
            
        return status

    def health_check(self) -> Tuple[bool, str]:
        """
        Check if Ollama service is available and configured correctly
        
        Returns:
            Tuple[bool, str]: (is_healthy, status_message)
        """
        status = self.get_connection_status()
        
        if not status['configured']:
            return False, status['errors'][0]
            
        if not status['is_healthy']:
            return False, status['health_details']
            
        if status['errors']:
            return False, status['errors'][0]
            
        if self.model not in status['available_models']:
            return False, f"Model '{self.model}' is not available"
            
        return True, "Ollama service is healthy and configured correctly"

    def analyze_issue(self, issue_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Analyze a GitHub issue using Ollama
        
        Args:
            issue_data: Dictionary containing issue information
            
        Returns:
            Dictionary containing AI analysis results or None if analysis fails
        """
        try:
            # Check connection status
            status = self.get_connection_status()
            if not status['is_healthy'] or status['errors']:
                print("Ollama service is not available:")
                for error in status['errors']:
                    print(f"  - {error}")
                return None

            prompt = self._generate_prompt(issue_data)
            
            for attempt in range(self.max_retries):
                try:
                    response = self.session.post(
                        f"{self.base_url}/api/generate",
                        json={
                            "model": self.model,
                            "prompt": prompt,
                            "stream": False
                        },
                        timeout=30
                    )
                    
                    if response.status_code == 200:
                        try:
                            result = json.loads(response.json()['response'])
                            return {
                                'technical_complexity': result.get('technical_complexity', 5),
                                'impact_assessment': {
                                    'security': result.get('impact_assessment', {}).get('security', 1),
                                    'performance': result.get('impact_assessment', {}).get('performance', 1),
                                    'ux': result.get('impact_assessment', {}).get('ux', 1)
                                },
                                'implementation_effort': result.get('implementation_effort', 'medium'),
                                'priority_level': result.get('priority_level', 'medium'),
                                'required_expertise': result.get('required_expertise', []),
                                'potential_risks': result.get('potential_risks', [])
                            }
                        except (json.JSONDecodeError, KeyError) as e:
                            print(f"Error parsing Ollama response: {str(e)}")
                            continue
                            
                    elif response.status_code == 404:
                        print(f"Model '{self.model}' not found")
                        return None
                    elif response.status_code >= 500:
                        print(f"Server error (attempt {attempt + 1}/{self.max_retries})")
                        if attempt < self.max_retries - 1:
                            time.sleep(2 ** attempt)
                            continue
                    else:
                        print(f"Unexpected status code: {response.status_code}")
                        return None
                        
                except requests.exceptions.Timeout:
                    print(f"Request timeout (attempt {attempt + 1}/{self.max_retries})")
                    if attempt < self.max_retries - 1:
                        time.sleep(2 ** attempt)
                        continue
                    return None
                except requests.exceptions.RequestException as e:
                    print(f"Request failed: {str(e)}")
                    return None
                    
            return None
                
        except Exception as e:
            print(f"Error during Ollama analysis: {str(e)}")
            return None
            
    def _generate_prompt(self, issue_data: Dict[str, Any]) -> str:
        """Generate analysis prompt for the issue"""
        return self._template.format(
            title=issue_data.get('title', ''),
            body=issue_data.get('body', '')
        )
