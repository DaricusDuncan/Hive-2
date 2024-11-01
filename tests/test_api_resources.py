import unittest
from app import create_app
from core.database import db
from models.user import User
from models.role import Role
from werkzeug.security import generate_password_hash
import json

class TestAPIResources(unittest.TestCase):
    def setUp(self):
        """Set up test environment before each test"""
        self.app = create_app()
        self.app.config['TESTING'] = True
        self.client = self.app.test_client()
        self.app_context = self.app.app_context()
        self.app_context.push()
        
        # Create test users with existing roles
        admin_role = Role.query.filter_by(name='admin').first()
        user_role = Role.query.filter_by(name='user').first()
        
        # Create test users
        self.admin_user = User(
            username='admin_test',
            email='admin@test.com',
            password_hash=generate_password_hash('admin123')
        )
        self.admin_user.roles.append(admin_role)
        
        self.regular_user = User(
            username='user_test',
            email='user@test.com',
            password_hash=generate_password_hash('user123')
        )
        self.regular_user.roles.append(user_role)
        
        db.session.add(self.admin_user)
        db.session.add(self.regular_user)
        db.session.commit()
        
        # Get authentication tokens
        self.admin_tokens = self._get_tokens('admin_test', 'admin123')
        self.user_tokens = self._get_tokens('user_test', 'user123')

    def tearDown(self):
        """Clean up after each test"""
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    def _get_tokens(self, username, password):
        """Helper method to get authentication tokens"""
        response = self.client.post('/api/v1/auth/login',
            json={'username': username, 'password': password})
        return json.loads(response.data.decode())

    def test_create_role_as_admin(self):
        """Test role creation as admin"""
        headers = {'Authorization': f"Bearer {self.admin_tokens['access_token']}"}
        new_role = {
            'name': 'test_moderator',  # Using unique role name
            'description': 'Test Moderator role'
        }
        response = self.client.post('/api/v1/api/roles',
            headers=headers,
            json=new_role)
        data = json.loads(response.data.decode())
        
        self.assertEqual(response.status_code, 201)
        self.assertIn('message', data)
        self.assertEqual(data['message'], 'Role created successfully')

    def test_create_role_as_user(self):
        """Test role creation as regular user (should fail)"""
        headers = {'Authorization': f"Bearer {self.user_tokens['access_token']}"}
        new_role = {
            'name': 'test_role',  # Using unique role name
            'description': 'Test role'
        }
        response = self.client.post('/api/v1/api/roles',
            headers=headers,
            json=new_role)
        data = json.loads(response.data.decode())
        
        self.assertEqual(response.status_code, 403)
        self.assertIn('msg', data)
        self.assertEqual(data['msg'], 'Insufficient permissions')

    def test_get_roles_as_admin(self):
        """Test getting all roles as admin"""
        headers = {'Authorization': f"Bearer {self.admin_tokens['access_token']}"}
        response = self.client.get('/api/v1/api/roles', headers=headers)
        data = json.loads(response.data.decode())
        
        self.assertEqual(response.status_code, 200)
        self.assertIsInstance(data, list)
        self.assertGreaterEqual(len(data), 2)  # At least admin and user roles
        role_names = [role['name'] for role in data]
        self.assertIn('admin', role_names)
        self.assertIn('user', role_names)

    def test_get_users_list_as_admin(self):
        """Test getting user list as admin"""
        headers = {'Authorization': f"Bearer {self.admin_tokens['access_token']}"}
        response = self.client.get('/api/v1/api/users', headers=headers)
        data = json.loads(response.data.decode())
        
        self.assertEqual(response.status_code, 200)
        self.assertIsInstance(data, list)
        self.assertEqual(len(data), 2)  # admin and regular user
        usernames = [user['username'] for user in data]
        self.assertIn('admin_test', usernames)
        self.assertIn('user_test', usernames)

    def test_get_users_list_as_user(self):
        """Test getting user list as regular user (should fail)"""
        headers = {'Authorization': f"Bearer {self.user_tokens['access_token']}"}
        response = self.client.get('/api/v1/api/users', headers=headers)
        data = json.loads(response.data.decode())
        
        self.assertEqual(response.status_code, 403)
        self.assertIn('msg', data)
        self.assertEqual(data['msg'], 'Insufficient permissions')

if __name__ == '__main__':
    unittest.main()
