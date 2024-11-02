import unittest
import os
from app import create_app
from core.database import db
from models.user import User
from models.role import Role
from werkzeug.security import generate_password_hash
import json

class TestAPIResources(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        """Set up test environment once for all test cases"""
        os.environ['FLASK_TESTING'] = 'true'
        cls.app = create_app()
        cls.client = cls.app.test_client()
        cls.app_context = cls.app.app_context()
        cls.app_context.push()

    def setUp(self):
        """Set up test environment before each test"""
        # Clean up any existing data and rollback any pending transactions
        db.session.remove()
        db.drop_all()
        db.create_all()
        
        # Create default roles
        self.admin_role =         self.admin_role = Role()  # Create an instance of Role without arguments
        self.admin_role.name = 'admin'
        self.admin_role.description = 'Administrator role'

        self.user_role = Role()    # Create another instance of Role
        self.user_role.name = 'user'
        self.user_role.description = 'Regular user role'Role(name='admin', description='Administrator role')
        self.user_role = Role(name='user', description='Regular user role')
        db.session.add(self.admin_role)
        db.session.add(self.user_role)
        db.session.commit()
        
        # Create test users
        self.admin_user = User(
            username='admin_test',
            email='admin@test.com',
            password_hash=generate_password_hash('admin123')
        )
        self.admin_user.roles.append(self.admin_role)
        
        self.regular_user = User(
            username='user_test',
            email='user@test.com',
            password_hash=generate_password_hash('user123')
        )
        self.regular_user.roles.append(self.user_role)
        
        db.session.add(self.admin_user)
        db.session.add(self.regular_user)
        db.session.commit()

    def tearDown(self):
        """Clean up after each test"""
        db.session.remove()
        db.drop_all()
        db.engine.dispose()

    @classmethod
    def tearDownClass(cls):
        """Clean up after all tests"""
        db.session.remove()
        db.engine.dispose()
        cls.app_context.pop()
        os.environ.pop('FLASK_TESTING', None)

    def _get_tokens(self, username, password):
        """Helper method to get authentication tokens"""
        response = self.client.post('/api/v1/auth/login',
            json={'username': username, 'password': password})
        return json.loads(response.data.decode())

    def test_create_role_as_admin(self):
        """Test role creation as admin"""
        tokens = self._get_tokens('admin_test', 'admin123')
        headers = {'Authorization': f"Bearer {tokens['access_token']}"}
        new_role = {
            'name': 'test_moderator',
            'description': 'Test Moderator role'
        }
        response = self.client.post('/api/v1/api/roles',
            headers=headers,
            json=new_role)
        
        self.assertEqual(response.status_code, 201)
        data = json.loads(response.data.decode())
        self.assertIn('message', data)
        self.assertEqual(data['message'], 'Role created successfully')

    def test_create_role_as_user(self):
        """Test role creation as regular user (should fail)"""
        tokens = self._get_tokens('user_test', 'user123')
        headers = {'Authorization': f"Bearer {tokens['access_token']}"}
        new_role = {
            'name': 'test_role',
            'description': 'Test role'
        }
        response = self.client.post('/api/v1/api/roles',
            headers=headers,
            json=new_role)
        
        self.assertEqual(response.status_code, 403)
        data = json.loads(response.data.decode())
        self.assertIn('msg', data)
        self.assertEqual(data['msg'], 'Insufficient permissions')

    def test_get_roles_as_admin(self):
        """Test getting all roles as admin"""
        tokens = self._get_tokens('admin_test', 'admin123')
        headers = {'Authorization': f"Bearer {tokens['access_token']}"}
        response = self.client.get('/api/v1/api/roles', headers=headers)
        
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data.decode())
        self.assertIsInstance(data, list)
        self.assertGreaterEqual(len(data), 2)  # At least admin and user roles
        role_names = [role['name'] for role in data]
        self.assertIn('admin', role_names)
        self.assertIn('user', role_names)

    def test_get_users_list_as_admin(self):
        """Test getting user list as admin"""
        tokens = self._get_tokens('admin_test', 'admin123')
        headers = {'Authorization': f"Bearer {tokens['access_token']}"}
        response = self.client.get('/api/v1/api/users', headers=headers)
        
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data.decode())
        self.assertIsInstance(data, list)
        self.assertEqual(len(data), 2)  # admin and regular user
        usernames = [user['username'] for user in data]
        self.assertIn('admin_test', usernames)
        self.assertIn('user_test', usernames)

    def test_get_users_list_as_user(self):
        """Test getting user list as regular user (should fail)"""
        tokens = self._get_tokens('user_test', 'user123')
        headers = {'Authorization': f"Bearer {tokens['access_token']}"}
        response = self.client.get('/api/v1/api/users', headers=headers)
        
        self.assertEqual(response.status_code, 403)
        data = json.loads(response.data.decode())
        self.assertIn('msg', data)
        self.assertEqual(data['msg'], 'Insufficient permissions')

    def test_get_user_profile(self):
        """Test getting user's own profile"""
        tokens = self._get_tokens('user_test', 'user123')
        headers = {'Authorization': f"Bearer {tokens['access_token']}"}
        response = self.client.get('/api/v1/api/profile', headers=headers)
        
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data.decode())
        self.assertEqual(data['username'], 'user_test')
        self.assertEqual(data['email'], 'user@test.com')

    def test_get_specific_user_as_admin(self):
        """Test getting specific user details as admin"""
        tokens = self._get_tokens('admin_test', 'admin123')
        headers = {'Authorization': f"Bearer {tokens['access_token']}"}
        response = self.client.get(f'/api/v1/api/users/{self.regular_user.id}', headers=headers)
        
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data.decode())
        self.assertEqual(data['username'], 'user_test')
        self.assertEqual(data['email'], 'user@test.com')

if __name__ == '__main__':
    unittest.main()
