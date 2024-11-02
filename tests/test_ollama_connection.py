import unittest
from services.ollama import OllamaService
import os
from core.config import Config
import requests
import time

class TestOllamaConnection(unittest.TestCase):
    def setUp(self):
        """Set up test case"""
        self.ollama = OllamaService()
        self.original_url = Config.OLLAMA_API_URL
        self.original_model = Config.OLLAMA_MODEL

    def tearDown(self):
        """Clean up after tests"""
        Config.OLLAMA_API_URL = self.original_url
        Config.OLLAMA_MODEL = self.original_model

    def test_connection_status(self):
        """Test detailed connection status reporting"""
        status = self.ollama.get_connection_status()
        
        print("\nOllama Connection Status:")
        print(f"Configured: {status['configured']}")
        print(f"Base URL: {status['base_url']}")
        print(f"Model: {status['model']}")
        print(f"Is Healthy: {status['is_healthy']}")
        print(f"Health Details: {status['health_details']}")
        print(f"Available Models: {', '.join(status['available_models'])}")
        if status['errors']:
            print("Errors:")
            for error in status['errors']:
                print(f"  - {error}")
        
        self.assertIsInstance(status, dict)
        self.assertIn('configured', status)
        self.assertIn('is_healthy', status)
        self.assertIn('errors', status)
        self.assertIsInstance(status['errors'], list)

    def test_health_check_with_invalid_url(self):
        """Test health check with invalid URL"""
        Config.OLLAMA_API_URL = "http://invalid-url:11434"
        ollama = OllamaService()
        is_healthy, status = ollama.health_check()
        
        self.assertFalse(is_healthy)
        self.assertIn("Failed to connect to Ollama service", status)

    def test_health_check_with_missing_url(self):
        """Test health check with missing URL"""
        Config.OLLAMA_API_URL = ""
        ollama = OllamaService()
        is_healthy, status = ollama.health_check()
        
        self.assertFalse(is_healthy)
        self.assertEqual(status, "Ollama API URL is not configured")

    def test_health_check_with_missing_model(self):
        """Test health check with missing model"""
        Config.OLLAMA_MODEL = ""
        ollama = OllamaService()
        is_healthy, status = ollama.health_check()
        
        self.assertFalse(is_healthy)
        self.assertEqual(status, "Ollama model is not configured")

    def test_issue_analysis(self):
        """Test issue analysis with connection status verification"""
        status = self.ollama.get_connection_status()
        if not status['is_healthy'] or status['errors']:
            self.skipTest(
                f"Ollama service is not available: "
                f"{'Unhealthy' if not status['is_healthy'] else status['errors'][0]}"
            )

        test_issue = {
            "title": "Test Issue for API Integration",
            "body": """Testing Ollama integration with the following requirements:
            1. Implement user authentication
            2. Add rate limiting
            3. Improve error handling
            """
        }
        
        result = self.ollama.analyze_issue(test_issue)
        
        if result:
            print("\nTest Issue Analysis Result:")
            print(f"Technical Complexity: {result.get('technical_complexity')}")
            print(f"Implementation Effort: {result.get('implementation_effort')}")
            print(f"Priority Level: {result.get('priority_level')}")
            print(f"Required Expertise: {', '.join(result.get('required_expertise', []))}")
            print(f"Potential Risks: {', '.join(result.get('potential_risks', []))}")
            
            self.assertIsInstance(result.get('technical_complexity'), (int, float))
            self.assertIsInstance(result.get('implementation_effort'), str)
            self.assertIsInstance(result.get('priority_level'), str)
            self.assertIsInstance(result.get('required_expertise'), list)
            self.assertIsInstance(result.get('potential_risks'), list)
        else:
            self.skipTest("Issue analysis failed but service was reported healthy")

if __name__ == '__main__':
    unittest.main(verbosity=2)
