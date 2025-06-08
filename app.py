from flask import Flask, render_template, session, redirect, url_for
from controller.user_controller import user_bp
from controller.product_controller import product_bp
from controller.cart_controller import cart_bp



app = Flask(__name__, template_folder='view')
app.secret_key = '123'
app.register_blueprint(user_bp)
app.register_blueprint(product_bp)
app.register_blueprint(cart_bp)

@app.route('/')
def index():
    if not session.get('logged_in'):
        return redirect(url_for('user.login'))
    return render_template('homepage.html')

if __name__ == '__main__':
    app.run(debug=True)