import unittest
import json
from app import create_app
from core.database import db
from models.user import User
from models.role import Role

class TestAuthAPI(unittest.TestCase):
    def setUp(self):
        """Set up test environment before each test case."""
        self.app = create_app()
        self.app.config['TESTING'] = True
        self.client = self.app.test_client()
        
        with self.app.app_context():
            db.drop_all()  # Clean start
            db.create_all()
            
            # Create roles
            user_role = Role(name='user', description='Regular user role')
            db.session.add(user_role)
            db.session.commit()
            
            self.test_user_data = {
                'username': 'testuser',
                'email': 'test@example.com',
                'password': 'Test@123'
            }

    def tearDown(self):
        """Clean up after each test case."""
        with self.app.app_context():
            db.session.remove()
            db.drop_all()

    def test_register_login_refresh_logout_flow(self):
        """Test the complete authentication flow."""
        # 1. Register new user
        register_response = self.client.post('/api/v1/auth/register',
            json=self.test_user_data)
        self.assertEqual(register_response.status_code, 201)
        
        # 2. Login with credentials
        login_response = self.client.post('/api/v1/auth/login',
            json={
                'username': self.test_user_data['username'],
                'password': self.test_user_data['password']
            })
        self.assertEqual(login_response.status_code, 200)
        tokens = json.loads(login_response.data)
        self.assertIn('access_token', tokens)
        self.assertIn('refresh_token', tokens)
        
        # 3. Access protected endpoint
        profile_response = self.client.get('/api/v1/api/profile',
            headers={'Authorization': f"Bearer {tokens['access_token']}"})
        self.assertEqual(profile_response.status_code, 200)
        profile_data = json.loads(profile_response.data)
        self.assertEqual(profile_data['username'], self.test_user_data['username'])
        
        # 4. Refresh token
        refresh_response = self.client.post('/api/v1/auth/refresh',
            headers={'Authorization': f"Bearer {tokens['refresh_token']}"})
        self.assertEqual(refresh_response.status_code, 200)
        new_tokens = json.loads(refresh_response.data)
        self.assertIn('access_token', new_tokens)
        
        # 5. Logout (revoke access token)
        logout_response = self.client.post('/api/v1/auth/logout',
            headers={'Authorization': f"Bearer {tokens['access_token']}"})
        self.assertEqual(logout_response.status_code, 200)
        
        # 6. Verify token is revoked
        profile_response = self.client.get('/api/v1/api/profile',
            headers={'Authorization': f"Bearer {tokens['access_token']}"})
        self.assertEqual(profile_response.status_code, 401)

    def test_invalid_login(self):
        """Test login with invalid credentials."""
        response = self.client.post('/api/v1/auth/login',
            json={
                'username': 'nonexistent',
                'password': 'wrong'
            })
        self.assertEqual(response.status_code, 401)

    def test_duplicate_registration(self):
        """Test registration with existing username."""
        # First registration
        self.client.post('/api/v1/auth/register',
            json=self.test_user_data)
        
        # Attempt duplicate registration
        response = self.client.post('/api/v1/auth/register',
            json=self.test_user_data)
        self.assertEqual(response.status_code, 400)

if __name__ == '__main__':
    unittest.main()
