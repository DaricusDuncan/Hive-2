import unittest
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
import json
import time
import uuid
import os
from app import create_app
from core.database import db

class TestAuthFlow(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        """Set up the test environment once for all test cases."""
        os.environ['FLASK_TESTING'] = 'true'
        
        # Create app context
        cls.app = create_app()
        cls.app_context = cls.app.app_context()
        cls.app_context.push()
        
        # Configure Chrome options for Replit environment
        chrome_options = Options()
        chrome_options.add_argument('--headless')
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-dev-shm-usage')
        chrome_options.add_argument('--disable-gpu')
        chrome_options.add_argument('--remote-debugging-port=9222')
        chrome_options.binary_location = '/usr/bin/chromium'
        
        # Initialize Chrome WebDriver
        service = Service(executable_path='/usr/bin/chromedriver')
        cls.driver = webdriver.Chrome(service=service, options=chrome_options)
        cls.driver.implicitly_wait(10)
        cls.base_url = "http://localhost:5000"

    @classmethod
    def tearDownClass(cls):
        """Clean up after all tests."""
        if cls.driver:
            cls.driver.quit()
        cls.app_context.pop()
        os.environ.pop('FLASK_TESTING', None)

    def setUp(self):
        """Set up before each test case."""
        db.session.remove()
        db.drop_all()
        db.create_all()
        self.wait = WebDriverWait(self.driver, 10)
        
        # Generate unique test user credentials
        self.test_username = f"testuser_{uuid.uuid4().hex[:8]}"
        self.test_password = "Test@123456"
        self.test_email = f"{self.test_username}@example.com"

    def tearDown(self):
        """Clean up after each test."""
        db.session.remove()
        db.drop_all()
        db.engine.dispose()

    def wait_for_swagger_ui(self):
        """Wait for Swagger UI to load completely."""
        try:
            self.wait.until(
                EC.presence_of_element_located((By.CLASS_NAME, "swagger-ui"))
            )
            time.sleep(2)  # Allow additional time for JavaScript initialization
        except TimeoutException:
            self.fail("Swagger UI failed to load")

    def execute_endpoint(self, method, path, payload=None, token=None):
        """Execute a specific endpoint in Swagger UI."""
        try:
            # Set authorization token if provided
            if token:
                self.driver.execute_script(
                    'window.localStorage.setItem("swagger_accessToken", arguments[0])',
                    f"Bearer {token}"
                )
                self.driver.refresh()
                self.wait_for_swagger_ui()

            # Find and expand the endpoint
            endpoint_elem = self.wait.until(
                EC.presence_of_element_located(
                    (By.CSS_SELECTOR, f'.opblock-{method.lower()}[id*="{path}"]')
                )
            )
            if "is-open" not in endpoint_elem.get_attribute("class"):
                endpoint_elem.click()
                time.sleep(1)

            # If payload exists, fill it in
            if payload:
                try_out_button = self.wait.until(
                    EC.element_to_be_clickable(
                        (By.CSS_SELECTOR, f'.opblock-{method.lower()}[id*="{path}"] .try-out__btn')
                    )
                )
                try_out_button.click()
                time.sleep(1)

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
            time.sleep(2)

            # Get response
            response_code = self.wait.until(
                EC.presence_of_element_located(
                    (By.CSS_SELECTOR, f'.opblock-{method.lower()}[id*="{path}"] .response .response-col_status')
                )
            )
            
            response_body = self.wait.until(
                EC.presence_of_element_located(
                    (By.CSS_SELECTOR, f'.opblock-{method.lower()}[id*="{path}"] .response-col_description .microlight')
                )
            )
            
            return {
                'status_code': int(response_code.text),
                'body': json.loads(response_body.text) if response_body.text else None
            }
            
        except Exception as e:
            self.fail(f"Error executing endpoint: {str(e)}")

    def test_complete_auth_flow(self):
        """Test the complete authentication flow including refresh token mechanism."""
        try:
            # 1. Load Swagger UI
            self.driver.get(self.base_url)
            self.wait_for_swagger_ui()
            
            # 2. Register new user
            register_payload = {
                "username": self.test_username,
                "email": self.test_email,
                "password": self.test_password
            }
            register_response = self.execute_endpoint("post", "auth/register", register_payload)
            self.assertEqual(register_response['status_code'], 201)
            
            # 3. Login
            login_payload = {
                "username": self.test_username,
                "password": self.test_password
            }
            login_response = self.execute_endpoint("post", "auth/login", login_payload)
            self.assertEqual(login_response['status_code'], 200)
            self.assertIn('access_token', login_response['body'])
            self.assertIn('refresh_token', login_response['body'])
            
            access_token = login_response['body']['access_token']
            refresh_token = login_response['body']['refresh_token']
            
            # 4. Access protected endpoint
            profile_response = self.execute_endpoint(
                "get", "api/profile", token=access_token
            )
            self.assertEqual(profile_response['status_code'], 200)
            self.assertEqual(profile_response['body']['username'], self.test_username)
            
            # 5. Refresh token
            refresh_response = self.execute_endpoint(
                "post", "auth/refresh", token=refresh_token
            )
            self.assertEqual(refresh_response['status_code'], 200)
            self.assertIn('access_token', refresh_response['body'])
            
            # 6. Logout
            logout_response = self.execute_endpoint(
                "post", "auth/logout", token=access_token
            )
            self.assertEqual(logout_response['status_code'], 200)
            
            # Logout refresh token
            logout_refresh_response = self.execute_endpoint(
                "post", "auth/logout-refresh", token=refresh_token
            )
            self.assertEqual(logout_refresh_response['status_code'], 200)
            
        except Exception as e:
            self.fail(f"Test failed: {str(e)}")

if __name__ == '__main__':
    unittest.main()
