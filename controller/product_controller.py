from flask import Blueprint, render_template, request
from controller.db_config import get_db_connection

product_bp = Blueprint('product', __name__)

@product_bp.route('/catalog')
def catalog():
    keyword = request.args.get('q', '').strip()
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    if keyword:
        cursor.execute("SELECT * FROM products WHERE name LIKE %s OR category LIKE %s", (f"%{keyword}%", f"%{keyword}%"))
    else:
        cursor.execute("SELECT * FROM products")
    products = cursor.fetchall()
    cursor.close()
    conn.close()
    return render_template('catalog.html', products=products, keyword=keyword)

@product_bp.route('/product/<int:product_id>')
def product_detail(product_id):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute('SELECT * FROM products WHERE product_id = %s', (product_id,))
    product = cursor.fetchone()
    cursor.close()
    conn.close()
    if not product:
        return render_template('404.html'), 404
    return render_template('product_detail.html', product=product)