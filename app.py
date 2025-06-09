from flask import Flask, render_template, redirect, url_for, session
from controller.user_controller import user_bp
from controller.product_controller import product_bp
from controller.cart_controller import cart_bp
from controller.topUp_controller import topup_bp



app = Flask(__name__, template_folder='view')
app.secret_key = '123'
app.register_blueprint(user_bp)
app.register_blueprint(product_bp)
app.register_blueprint(cart_bp)
app.register_blueprint(topup_bp)

@app.route('/')
def index():
    if not session.get('logged_in'):
        return redirect(url_for('user.login'))
    return render_template('Homepage.html')

@app.route('/homepage')
def homepage():
    # Hanya bisa diakses jika sudah login
    if not session.get('user_id'):
        return redirect(url_for('root'))
    return render_template('Homepage.html')

if __name__ == '__main__':
    app.run(debug=True)