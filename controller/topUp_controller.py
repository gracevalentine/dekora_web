from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from controller.db_config import get_db_connection as get_db

topup_bp = Blueprint('topup', __name__)

@topup_bp.route('/topup', methods=['GET'])
def topup_page():
    # Tampilkan halaman top up
    return render_template('TopUp.html')

@topup_bp.route('/topup', methods=['POST'])
def process_topup():
    nominal = request.form.get('nominal')
    payment = request.form.get('payment')
    user_id = session.get('user_id')  # Pastikan user sudah login

    if not (nominal and payment and user_id):
        flash('Data tidak lengkap atau Anda belum login.', 'error')
        return redirect(url_for('topup.topup_page'))

    try:
        db = get_db()
        cursor = db.cursor()
        # Pastikan nominal bertipe integer
        nominal_int = int(nominal)
        # Update saldo wallet user
        cursor.execute(
            "UPDATE users SET wallet = wallet + %s WHERE id = %s",
            (nominal_int, user_id)
        )
        db.commit()
        flash('Top up berhasil! Saldo Anda telah bertambah.', 'success')
    except Exception as e:
        db.rollback()
        flash('Terjadi kesalahan saat top up.', 'error')
    finally:
        cursor.close()
        db.close()

    return '', 204  # Agar fetch di JS tetap sukses tanpa reload