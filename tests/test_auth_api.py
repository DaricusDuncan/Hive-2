import unittest
import os
from app import create_app
from core.database import db
from models.user import User
from models.role import Role
from models.token import TokenBlacklist
import json
from datetime import datetime, timedelta

class TestAuthAPI(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        os.environ['FLASK_TESTING'] = 'true'
        cls.app = create_app()
        cls.client = cls.app.test_client()
        cls.app_context = cls.app.app_context()
        cls.app_context.push()

    def setUp(self):
        # Clean up any existing data
        db.session.remove()
        db.drop_all()
        db.create_all()
        
        # Create default roles
        self.user_role = Role(name='user', description='Regular user role')
        db.session.add(self.user_role)
        db.session.commit()
        
        # Create test user
        self.test_user = User(username='test_user', email='test@example.com')
        self.test_user.set_password('test123')
        self.test_user.roles.append(self.user_role)
        db.session.add(self.test_user)
        db.session.commit()

    def tearDown(self):
        db.session.remove()
        db.drop_all()

    @classmethod
    def tearDownClass(cls):
        db.session.remove()
        db.engine.dispose()
        cls.app_context.pop()
        os.environ.pop('FLASK_TESTING', None)

    def test_refresh_token(self):
        """Test refresh token endpoint"""
        # First login to get tokens
        response = self.client.post('/api/v1/auth/login', json={
            'username': 'test_user',
            'password': 'test123'
        })
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data.decode())
        self.assertIn('refresh_token', data)
        refresh_token = data['refresh_token']
        
        # Use refresh token to get new access token
        response = self.client.post('/api/v1/auth/refresh',
            headers={'Authorization': f'Bearer {refresh_token}'})
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data.decode())
        self.assertIn('access_token', data)

    def test_login_success(self):
        """Test successful login"""
        response = self.client.post('/api/v1/auth/login', json={
            'username': 'test_user',
            'password': 'test123'
        })
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data.decode())
        self.assertIn('access_token', data)
        self.assertIn('refresh_token', data)

    def test_register_success(self):
        """Test successful user registration"""
        response = self.client.post('/api/v1/auth/register', json={
            'username': 'newuser',
            'email': 'new@example.com',
            'password': 'Pass123!'
        })
        self.assertEqual(response.status_code, 201)
        data = json.loads(response.data.decode())
        self.assertEqual(data['username'], 'newuser')
        self.assertEqual(data['email'], 'new@example.com')

    def test_logout(self):
        """Test logout endpoints"""
        # First login to get tokens
        response = self.client.post('/api/v1/auth/login', json={
            'username': 'test_user',
            'password': 'test123'
        })
        self.assertEqual(response.status_code, 200)
        tokens = json.loads(response.data.decode())
        
        # Test access token logout
        response = self.client.post('/api/v1/auth/logout',
            headers={'Authorization': f'Bearer {tokens["access_token"]}'})
        self.assertEqual(response.status_code, 200)
        
        # Verify token is blacklisted
        blacklisted = TokenBlacklist.query.first()
        self.assertIsNotNone(blacklisted)
        self.assertEqual(blacklisted.token_type, 'access')

if __name__ == '__main__':
    unittest.main()
