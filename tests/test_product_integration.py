import unittest
import mysql.connector
from app import app

class ProductIntegrationTest(unittest.TestCase):

    def setUp(self):
        app.config['TESTING'] = True
        self.client = app.test_client()
        self.db = mysql.connector.connect(
            host="localhost",
            user="root",
            password="",
            database="dekora"
        )
        self.cursor = self.db.cursor()
        self.insert_test_product()

    def tearDown(self):
        self.cursor.execute("DELETE FROM products WHERE name = 'Test Product'")
        self.db.commit()
        self.cursor.close()
        self.db.close()

    def insert_test_product(self):
        self.cursor.execute('''
            INSERT INTO products (name, description, price, stock_quantity, category, image_url)
            VALUES (%s, %s, %s, %s, %s, %s)
        ''', (
            "Test Product",
            "This is a test product.",
            100000,
            5,
            "Test Category",
            "test.jpg"
        ))
        self.db.commit()

    def test_catalog_integration(self):
        response = self.client.get('/catalog')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Test Product', response.data)

    def test_product_detail_integration(self):
        # Get product_id of test product
        self.cursor.execute("SELECT product_id FROM products WHERE name = 'Test Product'")
        product_id = self.cursor.fetchone()[0]
        response = self.client.get(f'/product/{product_id}')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Test Product', response.data)

    def test_product_detail_not_found(self):
        response = self.client.get('/product/999999')  # ID yang sangat besar kemungkinan tidak ada
        self.assertEqual(response.status_code, 404)

if __name__ == '__main__':
    unittest.main()
