import unittest
from app import app
from controller.db_config import get_db_connection

class TestProductController(unittest.TestCase):
    def setUp(self):
        self.client = app.test_client()
        self.context = app.app_context()
        self.context.push()

        # Tambahkan produk dummy
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO products (product_id, name, price, category, image_url, description)
            VALUES (%s, %s, %s, %s, %s, %s)
            ON DUPLICATE KEY UPDATE name = VALUES(name)
        """, (999, 'Produk Test', 100000, 'Dekorasi', 'default.jpg', 'Deskripsi test'))
        conn.commit()
        cursor.close()
        conn.close()

    def tearDown(self):
        # Hapus produk dummy
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM products WHERE product_id = %s", (999,))
        conn.commit()
        cursor.close()
        conn.close()
        self.context.pop()

    def test_catalog_page(self):
        res = self.client.get('/catalog')
        self.assertEqual(res.status_code, 200)
        self.assertIn(b'Produk Test', res.data)

    def test_catalog_with_keyword(self):
        res = self.client.get('/catalog?q=produk')
        self.assertEqual(res.status_code, 200)
        self.assertIn(b'Produk Test', res.data)

    def test_product_detail_valid(self):
        res = self.client.get('/product/999')
        self.assertEqual(res.status_code, 200)
        self.assertIn(b'Produk Test', res.data)

    def test_product_detail_invalid(self):
        res = self.client.get('/product/9999')
        self.assertEqual(res.status_code, 404)
        self.assertIn(b'Tidak Ditemukan', res.data)  # asumsi isi 404.html

if __name__ == '__main__':
    unittest.main()
