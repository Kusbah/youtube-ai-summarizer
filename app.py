from flask import Flask, render_template, request, redirect, url_for, session, flash
import sqlite3
from werkzeug.security import generate_password_hash, check_password_hash
from functools import wraps  # ✅ لإضافة ديكوريتر login_required

app = Flask(__name__)
app.secret_key = 'youtubai'  # ضروري للجلسات

# ✅ ديكوريتر حماية الصفحات
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash("Please log in first.")
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

# 🧠 دالة لإنشاء الاتصال بالقاعدة
def get_db_connection():
    conn = sqlite3.connect('users.db')
    conn.row_factory = sqlite3.Row
    return conn

# 🧱 إنشاء الجدول لو مش موجود
def init_db():
    with get_db_connection() as conn:
        conn.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT NOT NULL,
                email TEXT NOT NULL UNIQUE,
                password TEXT NOT NULL
            );
        ''')
    print("✅ Database initialized.")

init_db()  # تشغيل عند بداية السيرفر

# 🌐 الصفحة الرئيسية - محمية
@app.route('/')
@login_required
def home():
    return render_template("home.html")

# 🔐 تسجيل الدخول
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        conn = get_db_connection()
        user = conn.execute('SELECT * FROM users WHERE email = ?', (email,)).fetchone()
        conn.close()

        if user and check_password_hash(user['password'], password):
            session['user_id'] = user['id']
            session['username'] = user['username']
            return redirect(url_for('home'))

        flash('Wrong email or password.')
    return render_template("login.html")

# 🧾 إنشاء حساب
@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']
        hashed_pw = generate_password_hash(password)

        try:
            conn = get_db_connection()
            conn.execute(
                'INSERT INTO users (username, email, password) VALUES (?, ?, ?)',
                (username, email, hashed_pw)
            )
            conn.commit()
            conn.close()
            flash('Account created successfully! Please log in.')
            return redirect(url_for('login'))
        except sqlite3.IntegrityError:
            flash('Email already registered.')
    return render_template("signup.html")

# 🔁 إعادة تعيين كلمة المرور
@app.route('/reset-password', methods=['GET', 'POST'])
def reset_password():
    if request.method == 'POST':
        email = request.form['email']
        old_pw = request.form['old_password']
        new_pw = request.form['new_password']

        conn = get_db_connection()
        user = conn.execute('SELECT * FROM users WHERE email = ?', (email,)).fetchone()

        if not user:
            flash("Email not found.")
            return redirect(url_for('reset_password'))

        if not check_password_hash(user['password'], old_pw):
            flash("Old password is incorrect.")
            return redirect(url_for('reset_password'))

        new_hashed = generate_password_hash(new_pw)
        conn.execute('UPDATE users SET password = ? WHERE email = ?', (new_hashed, email))
        conn.commit()
        conn.close()

        flash("Password updated successfully. Please log in.")
        return redirect(url_for('login'))

    return render_template("reset_password.html")



# 🚪 تسجيل الخروج
@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

# 📄 صفحة التلخيص - محمية
@app.route('/summarize')
@login_required
def summarize():
    return render_template("summarize.html")

# 🗂️ صفحة الملاحظات - محمية
@app.route('/my-notes')
@login_required
def my_notes():
    return render_template("my_notes.html")

# 🤖 صفحة AI Chat - محمية
@app.route('/ai-chat')
@login_required
def ai_chat():
    return render_template("ai_chat.html")

# ✅ تشغيل التطبيق
if __name__ == "__main__":
    app.run(debug=True)
