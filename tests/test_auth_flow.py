import unittest
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from webdriver_manager.chrome import ChromeDriverManager
import json
import time
import uuid

class TestAuthFlow(unittest.TestCase):
    def setUp(self):
        """Set up the test environment before each test case."""
        chrome_options = Options()
        chrome_options.add_argument('--headless')  # Run in headless mode
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-dev-shm-usage')
        
        self.driver = webdriver.Chrome(
            service=Service(ChromeDriverManager().install()),
            options=chrome_options
        )
        self.wait = WebDriverWait(self.driver, 10)
        
        # Generate unique test user credentials
        self.test_username = f"testuser_{uuid.uuid4().hex[:8]}"
        self.test_password = "Test@123456"
        self.test_email = f"{self.test_username}@example.com"
        
        # Store tokens
        self.access_token = None
        self.refresh_token = None

    def tearDown(self):
        """Clean up after each test case."""
        if self.driver:
            self.driver.quit()

    def wait_for_swagger_ui(self):
        """Wait for Swagger UI to load completely."""
        self.wait.until(
            EC.presence_of_element_located((By.CLASS_NAME, "swagger-ui"))
        )

    def expand_endpoint(self, endpoint_name):
        """Expand a specific endpoint in Swagger UI."""
        endpoints = self.driver.find_elements(By.CLASS_NAME, "opblock-tag")
        for endpoint in endpoints:
            if endpoint_name.lower() in endpoint.text.lower():
                if "is-open" not in endpoint.get_attribute("class"):
                    endpoint.click()
                break

    def execute_endpoint(self, method, path, payload=None):
        """Execute a specific endpoint in Swagger UI."""
        # Find and expand the endpoint
        endpoint_elem = self.wait.until(
            EC.presence_of_element_located(
                (By.CSS_SELECTOR, f'.opblock-{method.lower()}[id*="{path}"]')
            )
        )
        if "is-open" not in endpoint_elem.get_attribute("class"):
            endpoint_elem.click()

        # If payload exists, fill it in
        if payload:
            # Click "Try it out"
            try_out_button = self.wait.until(
                EC.element_to_be_clickable(
                    (By.CSS_SELECTOR, f'.opblock-{method.lower()}[id*="{path}"] .try-out__btn')
                )
            )
            try_out_button.click()

            # Fill in the payload
            payload_input = self.wait.until(
                EC.presence_of_element_located(
                    (By.CSS_SELECTOR, f'.opblock-{method.lower()}[id*="{path}"] .body-param__text')
                )
            )
            payload_input.clear()
            payload_input.send_keys(json.dumps(payload))

        # Execute
        execute_button = self.wait.until(
            EC.element_to_be_clickable(
                (By.CSS_SELECTOR, f'.opblock-{method.lower()}[id*="{path}"] .execute')
            )
        )
        execute_button.click()

        # Wait for response
        response_code = self.wait.until(
            EC.presence_of_element_located(
                (By.CSS_SELECTOR, f'.opblock-{method.lower()}[id*="{path}"] .response .response-col_status')
            )
        )
        
        # Get response body
        response_body = self.wait.until(
            EC.presence_of_element_located(
                (By.CSS_SELECTOR, f'.opblock-{method.lower()}[id*="{path}"] .response-col_description .microlight')
            )
        )
        
        return {
            'status_code': int(response_code.text),
            'body': json.loads(response_body.text) if response_body.text else None
        }

    def test_complete_auth_flow(self):
        """Test the complete authentication flow including refresh token mechanism."""
        # 1. Load Swagger UI
        self.driver.get("http://localhost:8000")
        self.wait_for_swagger_ui()
        
        # 2. Register new user
        register_payload = {
            "username": self.test_username,
            "email": self.test_email,
            "password": self.test_password
        }
        register_response = self.execute_endpoint("post", "auth/register", register_payload)
        self.assertEqual(register_response['status_code'], 201)
        
        # 3. Login to get tokens
        login_payload = {
            "username": self.test_username,
            "password": self.test_password
        }
        login_response = self.execute_endpoint("post", "auth/login", login_payload)
        self.assertEqual(login_response['status_code'], 200)
        self.assertIn('access_token', login_response['body'])
        self.assertIn('refresh_token', login_response['body'])
        
        self.access_token = login_response['body']['access_token']
        self.refresh_token = login_response['body']['refresh_token']
        
        # 4. Access protected endpoint with access token
        # Add Authorization header
        self.driver.execute_script(
            'window.localStorage.setItem("swagger_accessToken", arguments[0])',
            f"Bearer {self.access_token}"
        )
        
        # Refresh the page to apply the token
        self.driver.refresh()
        self.wait_for_swagger_ui()
        
        # Get user profile
        profile_response = self.execute_endpoint("get", "api/profile")
        self.assertEqual(profile_response['status_code'], 200)
        self.assertEqual(profile_response['body']['username'], self.test_username)
        
        # 5. Use refresh token to get new access token
        # First clear the access token
        self.driver.execute_script('window.localStorage.removeItem("swagger_accessToken")')
        self.driver.refresh()
        self.wait_for_swagger_ui()
        
        # Add refresh token as Bearer token
        self.driver.execute_script(
            'window.localStorage.setItem("swagger_accessToken", arguments[0])',
            f"Bearer {self.refresh_token}"
        )
        self.driver.refresh()
        self.wait_for_swagger_ui()
        
        # Get new access token
        refresh_response = self.execute_endpoint("post", "auth/refresh")
        self.assertEqual(refresh_response['status_code'], 200)
        self.assertIn('access_token', refresh_response['body'])
        
        # 6. Logout (revoke both tokens)
        # First revoke access token
        self.driver.execute_script(
            'window.localStorage.setItem("swagger_accessToken", arguments[0])',
            f"Bearer {self.access_token}"
        )
        self.driver.refresh()
        self.wait_for_swagger_ui()
        
        logout_response = self.execute_endpoint("post", "auth/logout")
        self.assertEqual(logout_response['status_code'], 200)
        
        # Then revoke refresh token
        self.driver.execute_script(
            'window.localStorage.setItem("swagger_accessToken", arguments[0])',
            f"Bearer {self.refresh_token}"
        )
        self.driver.refresh()
        self.wait_for_swagger_ui()
        
        logout_refresh_response = self.execute_endpoint("post", "auth/logout-refresh")
        self.assertEqual(logout_refresh_response['status_code'], 200)

if __name__ == '__main__':
    unittest.main()
