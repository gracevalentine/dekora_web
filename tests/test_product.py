import unittest
from unittest.mock import patch, MagicMock
from app import app  # pastikan app Flask lu di-import di sini

class ProductControllerTest(unittest.TestCase):

    def setUp(self):
        self.client = app.test_client()

    @patch('controller.product_controller.get_db_connection')
    def test_catalog_without_keyword(self, mock_get_conn):
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_cursor.fetchall.return_value = [
            {'product_id': 1, 'name': 'Wooden Chair', 'category': 'Furniture', 'price': 120000},
            {'product_id': 2, 'name': 'Modern Table', 'category': 'Furniture', 'price': 200000}
        ]
        mock_conn.cursor.return_value = mock_cursor
        mock_get_conn.return_value = mock_conn

        response = self.client.get('/catalog')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Wooden Chair', response.data)

    @patch('controller.product_controller.get_db_connection')
    def test_catalog_with_keyword(self, mock_get_conn):
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_cursor.fetchall.return_value = [
            {'product_id': 3, 'name': 'Luxury Sofa', 'category': 'Furniture', 'price': 350000}
        ]
        mock_conn.cursor.return_value = mock_cursor
        mock_get_conn.return_value = mock_conn

        response = self.client.get('/catalog?q=sofa')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Luxury Sofa', response.data)

    @patch('controller.product_controller.get_db_connection')
    def test_product_detail_found(self, mock_get_conn):
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_cursor.fetchone.return_value = {
            'product_id': 5,
            'name': 'Test Chair',
            'category': 'Furniture',
            'price': 150000,
            'description': 'Comfortable chair'  # kalau dipakai juga di HTML
        }
        mock_conn.cursor.return_value = mock_cursor
        mock_get_conn.return_value = mock_conn

        response = self.client.get('/product/5')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Test Chair', response.data)


    @patch('controller.product_controller.get_db_connection')
    def test_product_detail_not_found(self, mock_get_conn):
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_cursor.fetchone.return_value = None
        mock_conn.cursor.return_value = mock_cursor
        mock_get_conn.return_value = mock_conn

        response = self.client.get('/product/9999')
        self.assertEqual(response.status_code, 404)
