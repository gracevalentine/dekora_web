from flask import Blueprint, render_template, session, redirect, url_for

cart_bp = Blueprint('cart', __name__)

@cart_bp.route('/cart')
def cart():
    if not session.get('logged_in'):
        return redirect(url_for('user.login'))
    return render_template('cart.html')