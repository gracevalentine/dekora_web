from flask import Blueprint, render_template

product_bp = Blueprint('product', __name__)

@product_bp.route('/catalog')
def catalog():
    return render_template('catalog.html')