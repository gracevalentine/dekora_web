import unittest
from unittest.mock import patch, MagicMock
from flask import session
from app import app  # pastikan ini mengimpor Flask app kamu

class CartControllerTestCase(unittest.TestCase):
    def setUp(self):
        self.app = app.test_client()
        self.app.testing = True
        self.ctx = app.app_context()
        self.ctx.push()
        # Simulasi user login
        with self.app.session_transaction() as sess:
            sess['logged_in'] = True
            sess['user_id'] = 1
            sess['email'] = 'test@example.com'

    def tearDown(self):
        self.ctx.pop()

    @patch('controller.cart_controller.get_db_connection')
    def test_add_to_cart_new_item(self, mock_db):
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_db.return_value = mock_conn
        mock_conn.cursor.return_value = mock_cursor
        mock_cursor.fetchone.return_value = None  # produk belum ada di cart

        response = self.app.post('/add_to_cart', data={
            'product_id': 10,
            'quantity': 2
        })

        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Produk berhasil ditambahkan', response.data)

    @patch('controller.cart_controller.get_db_connection')
    def test_update_qty(self, mock_db):
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_db.return_value = mock_conn
        mock_conn.cursor.return_value = mock_cursor

        response = self.app.post('/update_qty', data={
            'cart_id': 123,
            'quantity': 5
        })

        self.assertEqual(response.status_code, 200)
        self.assertIn(b'success', response.data)

    @patch('controller.cart_controller.get_db_connection')
    def test_delete_cart(self, mock_db):
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_cursor.rowcount = 1
        mock_db.return_value = mock_conn
        mock_conn.cursor.return_value = mock_cursor

        response = self.app.post('/cart/delete', data={
            'cart_id': 123
        })

        self.assertEqual(response.status_code, 200)
        self.assertIn(b'berhasil dihapus', response.data)

    @patch('controller.cart_controller.get_db_connection')
    def test_clear_cart(self, mock_db):
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_db.return_value = mock_conn
        mock_conn.cursor.return_value = mock_cursor

        response = self.app.post('/clear_cart')

        self.assertEqual(response.status_code, 200)
        self.assertIn(b'berhasil dikosongkan', response.data)

    @patch('controller.cart_controller.requests.post')
    @patch('controller.cart_controller.get_db_connection')
    def test_checkout_success(self, mock_db, mock_requests):
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_db.return_value = mock_conn
        mock_conn.cursor.return_value = mock_cursor

        mock_cursor.fetchall.return_value = [
            {'cart_id': 1, 'quantity': 2, 'product_id': 5, 'name': 'Dog Toy', 'price': 50000, 'subtotal': 100000}
        ]
        mock_requests.return_value.status_code = 200
        mock_requests.return_value.json.return_value = {
            'invoice_url': 'https://checkout.xendit.co/xyz'
        }

        response = self.app.post('/checkout', data={
            'delivery_method': 'pickup'
        }, follow_redirects=False)

        self.assertEqual(response.status_code, 302)
        self.assertIn('https://checkout.xendit.co/xyz', response.headers['Location'])

