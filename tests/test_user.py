import unittest
from app import app
import json

class TestUserController(unittest.TestCase):

    def setUp(self):
        self.client = app.test_client()
        self.client.testing = True

    def test_create_user(self):
        response = self.client.post('/users', json={
            'name': 'Test User',
            'email': 'test_user@example.com'
        })
        self.assertEqual(response.status_code, 201)
        self.assertIn(b'Test User', response.data)

    def test_get_user_valid(self):
        # Pastikan user dengan ID 1 ada
        self.client.post('/users', json={'name': 'Valid User', 'email': 'valid@example.com'})
        response = self.client.get('/users/1')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Valid User', response.data)

    def test_get_user_not_found(self):
        response = self.client.get('/users/99999')
        self.assertEqual(response.status_code, 404)
        self.assertIn(b'User not found', response.data)

    def test_update_user(self):
        self.client.post('/users', json={'name': 'Old Name', 'email': 'old@example.com'})
        response = self.client.put('/users/1', json={
            'name': 'Updated Name',
            'email': 'updated@example.com'
        })
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Updated Name', response.data)

    def test_delete_user(self):
        self.client.post('/users', json={'name': 'Delete Me', 'email': 'deleteme@example.com'})
        response = self.client.delete('/users/1')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'User deleted', response.data)

if __name__ == '__main__':
    unittest.main()
