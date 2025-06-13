import unittest
from flask import session
from app import app  # Import Flask app dari file utama kamu
from unittest.mock import patch, MagicMock

class CartIntegrationTestCase(unittest.TestCase):
    def setUp(self):
        self.client = app.test_client()
        self.app_context = app.app_context()
        self.app_context.push()
        with self.client.session_transaction() as sess:
            sess['logged_in'] = True
            sess['user_id'] = 1
            sess['email'] = 'test@example.com'

    def tearDown(self):
        self.app_context.pop()

    @patch('controller.cart_controller.get_db_connection')
    def test_cart_page_logged_in(self, mock_db_conn):
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_cursor.fetchall.return_value = [
            {
                'cart_id': 1,
                'quantity': 2,
                'product_id': 5,
                'name': 'Dog Bone',
                'price': 50000,
                'image_url': 'url'
            }
        ]
        mock_conn.cursor.return_value = mock_cursor
        mock_db_conn.return_value = mock_conn

        response = self.client.get('/cart')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Dog Bone', response.data)

    @patch('controller.cart_controller.get_db_connection')
    def test_add_to_cart(self, mock_db_conn):
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_cursor.fetchone.return_value = None
        mock_conn.cursor.return_value = mock_cursor
        mock_db_conn.return_value = mock_conn

        response = self.client.post('/add_to_cart', data={
            'product_id': 10,
            'quantity': 3
        })

        self.assertEqual(response.status_code, 200)
        self.assertIn(b'berhasil ditambahkan', response.data)

    @patch('controller.cart_controller.get_db_connection')
    def test_update_qty_valid(self, mock_db_conn):
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_conn.cursor.return_value = mock_cursor
        mock_db_conn.return_value = mock_conn

        response = self.client.post('/update_qty', data={
            'cart_id': 99,
            'quantity': 2
        })

        self.assertEqual(response.status_code, 200)
        self.assertIn(b'success', response.data)

    @patch('controller.cart_controller.get_db_connection')
    def test_delete_cart_success(self, mock_db_conn):
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_cursor.rowcount = 1
        mock_conn.cursor.return_value = mock_cursor
        mock_db_conn.return_value = mock_conn

        response = self.client.post('/cart/delete', data={
            'cart_id': 10
        })

        self.assertEqual(response.status_code, 200)
        self.assertIn(b'dihapus', response.data)

    @patch('controller.cart_controller.get_db_connection')
    def test_clear_cart(self, mock_db_conn):
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_conn.cursor.return_value = mock_cursor
        mock_db_conn.return_value = mock_conn

        response = self.client.post('/clear_cart')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'dikosongkan', response.data)

    @patch('controller.cart_controller.requests.post')
    @patch('controller.cart_controller.get_db_connection')
    def test_checkout_redirect_to_invoice(self, mock_db_conn, mock_requests):
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_cursor.fetchall.return_value = [
            {'cart_id': 1, 'quantity': 2, 'product_id': 5, 'name': 'Bone', 'price': 50000, 'subtotal': 100000}
        ]
        mock_conn.cursor.return_value = mock_cursor
        mock_db_conn.return_value = mock_conn

        mock_requests.return_value.status_code = 200
        mock_requests.return_value.json.return_value = {
            'invoice_url': 'https://checkout.xendit.co/test123'
        }

        response = self.client.post('/checkout', data={
            'delivery_method': 'pickup'
        }, follow_redirects=False)

        self.assertEqual(response.status_code, 302)
        self.assertIn('https://checkout.xendit.co/test123', response.headers['Location'])

