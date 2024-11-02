import os
import requests
from typing import Dict, Any, Optional
import json
from core.config import Config

class OllamaService:
    def __init__(self, model: str = None):
        """Initialize Ollama service with specified model"""
        self.base_url = Config.OLLAMA_API_URL
        self.model = model or Config.OLLAMA_MODEL
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
        {
            "technical_complexity": <1-10>,
            "impact_assessment": {
                "security": <1-10>,
                "performance": <1-10>,
                "ux": <1-10>
            },
            "implementation_effort": "<low|medium|high>",
            "priority_level": "<low|medium|high>",
            "required_expertise": ["<expertise1>", "<expertise2>"],
            "potential_risks": ["<risk1>", "<risk2>"]
        }
        """
    
    def _generate_prompt(self, issue_data: Dict[str, Any]) -> str:
        """Generate analysis prompt for the issue"""
        return self._template.format(
            title=issue_data.get('title', ''),
            body=issue_data.get('body', '')
        )
    
    def analyze_issue(self, issue_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Analyze a GitHub issue using Ollama
        
        Args:
            issue_data: Dictionary containing issue information
            
        Returns:
            Dictionary containing AI analysis results or None if analysis fails
        """
        try:
            prompt = self._generate_prompt(issue_data)
            
            response = requests.post(
                f"{self.base_url}/api/generate",
                json={
                    "model": self.model,
                    "prompt": prompt,
                    "stream": False
                },
                timeout=30  # Add timeout for API calls
            )
            
            if response.status_code != 200:
                print(f"Error from Ollama API: {response.status_code}")
                return None
                
            # Parse response
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
            except json.JSONDecodeError:
                print("Error parsing Ollama response")
                return None
                
        except Exception as e:
            print(f"Error during Ollama analysis: {str(e)}")
            return None

    def health_check(self) -> bool:
        """Check if Ollama service is available"""
        try:
            response = requests.get(
                f"{self.base_url}/api/health",
                timeout=5  # Short timeout for health check
            )
            return response.status_code == 200
        except:
            return False
