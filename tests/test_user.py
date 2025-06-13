import unittest
from unittest.mock import patch, MagicMock
from flask import Flask
from controller.user_controller import user_bp  # ganti sesuai path aslimu

class UserControllerTestCase(unittest.TestCase):
    def setUp(self):
        self.app = Flask(__name__)
        self.app.register_blueprint(user_bp)
        self.client = self.app.test_client()
        self.app.config['TESTING'] = True

    @patch('controller.user_controller.get_db_connection')
    def test_create_user_success(self, mock_get_db_connection):
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_cursor.lastrowid = 1
        mock_conn.cursor.return_value = mock_cursor
        mock_get_db_connection.return_value = mock_conn

        response = self.client.post('/users', json={
            "first_name": "John",
            "last_name": "Doe",
            "email": "john@example.com"
        })

        self.assertEqual(response.status_code, 201)
        self.assertIn("id", response.get_json())

    @patch('controller.user_controller.get_db_connection')
    def test_create_user_missing_fields(self, mock_get_db_connection):
        response = self.client.post('/users', json={
            "first_name": "John"
        })
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.get_json()["message"], "First name, last name, and email are required")

    @patch('controller.user_controller.get_db_connection')
    def test_get_user_found(self, mock_get_db_connection):
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_cursor.fetchone.return_value = {
            'user_id': 1,
            'first_name': 'John',
            'last_name': 'Doe',
            'email': 'john@example.com',
            'address': None,
            'postal_code': None,
            'wallet': None
        }
        mock_conn.cursor.return_value = mock_cursor
        mock_get_db_connection.return_value = mock_conn

        response = self.client.get('/users/1')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.get_json()["email"], "john@example.com")

    @patch('controller.user_controller.get_db_connection')
    def test_get_user_not_found(self, mock_get_db_connection):
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_cursor.fetchone.return_value = None
        mock_conn.cursor.return_value = mock_cursor
        mock_get_db_connection.return_value = mock_conn

        response = self.client.get('/users/99')
        self.assertEqual(response.status_code, 404)
        self.assertEqual(response.get_json()["message"], "User not found")
        
    @patch('controller.user_controller.get_db_connection')
    def test_update_user_success(self, mock_get_db_connection):
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_cursor.rowcount = 1  # Simulasi user ditemukan & diupdate
        mock_conn.cursor.return_value = mock_cursor
        mock_get_db_connection.return_value = mock_conn

        response = self.client.put('/users/1', json={
            "first_name": "Jane",
            "email": "jane@example.com"
        })

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.get_json()["user_id"], 1)
        self.assertEqual(response.get_json()["first_name"], "Jane")
        self.assertEqual(response.get_json()["email"], "jane@example.com")

    @patch('controller.user_controller.get_db_connection')
    def test_update_user_not_found(self, mock_get_db_connection):
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_cursor.rowcount = 0  # Simulasi tidak ada user diupdate
        mock_conn.cursor.return_value = mock_cursor
        mock_get_db_connection.return_value = mock_conn

        response = self.client.put('/users/999', json={
            "first_name": "Jane"
        })

        self.assertEqual(response.status_code, 404)
        self.assertEqual(response.get_json()["message"], "User not found")

    @patch('controller.user_controller.get_db_connection')
    def test_update_user_no_fields(self, mock_get_db_connection):
        response = self.client.put('/users/1', json={})
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.get_json()["message"], "At least one of first_name, last_name, or email is required")

    @patch('controller.user_controller.get_db_connection')
    def test_delete_user_success(self, mock_get_db_connection):
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_cursor.fetchall.return_value = []  # No cart items
        mock_cursor.rowcount = 1  # Simulasi berhasil hapus
        mock_conn.cursor.return_value = mock_cursor
        mock_get_db_connection.return_value = mock_conn

        response = self.client.delete('/users/1')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.get_json()["message"], "User deleted")

    @patch('controller.user_controller.get_db_connection')
    def test_delete_user_with_cart_items(self, mock_get_db_connection):
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_cursor.fetchall.return_value = [{'cart_id': 1}]
        mock_conn.cursor.return_value = mock_cursor
        mock_get_db_connection.return_value = mock_conn

        response = self.client.delete('/users/1')
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.get_json()["message"], "Cannot delete user with active cart items.")

    @patch('controller.user_controller.get_db_connection')
    def test_delete_user_not_found(self, mock_get_db_connection):
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_cursor.fetchall.return_value = []  # No cart
        mock_cursor.rowcount = 0  # Gagal hapus
        mock_conn.cursor.return_value = mock_cursor
        mock_get_db_connection.return_value = mock_conn

        response = self.client.delete('/users/999')
        self.assertEqual(response.status_code, 404)
        self.assertEqual(response.get_json()["message"], "User not found")

if __name__ == '__main__':
    unittest.main()
