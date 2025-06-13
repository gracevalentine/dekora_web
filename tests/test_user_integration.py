import unittest
import json
from app import app  # ganti sesuai entrypoint Flask lu
from controller.db_config import get_db_connection

class UserIntegrationTest(unittest.TestCase):

    def setUp(self):
        self.app = app.test_client()
        self.conn = get_db_connection()
        self.cursor = self.conn.cursor()
        self.cleanup_test_user()

    def tearDown(self):
        self.cleanup_test_user()
        self.cursor.close()
        self.conn.close()

    def cleanup_test_user(self):
        self.cursor.execute("DELETE FROM users WHERE email = 'test_integ@example.com'")
        self.conn.commit()

    def test_create_get_update_delete_user_flow(self):
        # 1. Create user
        response = self.app.post('/users', json={
            "first_name": "Test",
            "last_name": "Integration",
            "email": "test_integ@example.com"
        })
        self.assertEqual(response.status_code, 201)
        user_data = response.get_json()
        user_id = user_data['id']

        # 2. Get user
        response = self.app.get(f'/users/{user_id}')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.get_json()['email'], "test_integ@example.com")

        # 3. Update user
        response = self.app.put(f'/users/{user_id}', json={
            "first_name": "Updated",
            "email": "test_integ@example.com"
        })
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.get_json()['first_name'], "Updated")

        # 4. Delete user
        response = self.app.delete(f'/users/{user_id}')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.get_json()['message'], "User deleted")

        # 5. Get after delete
        response = self.app.get(f'/users/{user_id}')
        self.assertEqual(response.status_code, 404)

