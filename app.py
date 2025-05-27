from flask import Flask, render_template, request, redirect, url_for, session, flash
import sqlite3
import requests
from werkzeug.security import generate_password_hash, check_password_hash
from transcriber import get_transcript_from_youtube


import os


app = Flask(__name__)
app.secret_key = 'youtubai'  # ضروري للجلسات

# 🧠 دالة مساعدة لإنشاء الاتصال بالقاعدة
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

init_db()  # تشغيلها أول ما يشتغل السيرفر

# 🌐 الصفحة الرئيسية
@app.route('/')
def home():
    return render_template("home.html")


def get_video_title(video_url):
    try:
        response = requests.get("https://www.youtube.com/oembed", params={
            "url": video_url,
            "format": "json"
        })
        if response.status_code == 200:
            return response.json().get("title", "No Title")
        return "Unknown Title"
    except:
        return "Unknown Title"

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

        flash('Wrong email or password.')  # ✅ هنا الرسالة
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
            flash('Email already registered.')  # ✅ هنا الرسالة
    return render_template("signup.html")


# 🔁 إعادة تعيين كلمة المرور (واجهة فقط الآن)
@app.route('/reset-password', methods=['GET', 'POST'])
def reset_password():
    if request.method == 'POST':
        email = request.form['email']
        # هنا ممكن تضيف إرسال بريد إلكتروني أو رابط مؤقت
        flash('If this email exists, a reset link was sent.')
        return redirect(url_for('login'))
    return render_template("reset_password.html")




# 🚪 تسجيل الخروج
@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

@app.route('/summarize', methods=['GET', 'POST'])
def summarize():
    if request.method == 'POST':
        url = request.form.get('url')
        error = None
        transcript = None
        lang = None

        if not url or "youtube.com" not in url:
            error = "❌ Invalid YouTube URL."
            return render_template("summary.html", error=error)

        try:
            # 📜 احصل على السكربت + اللغة
            transcript, lang = get_transcript_from_youtube(url)

            # 🖼 الصورة المصغّرة
            from urllib.parse import urlparse, parse_qs
            video_id = parse_qs(urlparse(url).query).get("v", [None])[0]
            thumbnail = f"https://img.youtube.com/vi/{video_id}/hqdefault.jpg"

            # 🏷 عنوان الفيديو
            video_title = get_video_title(url)

            return render_template("summary.html",
                                   transcript=transcript,
                                   video_url=url,
                                   video_title=video_title,
                                   thumbnail=thumbnail,
                                   lang=lang,
                                   error=error)

        except Exception as e:
            import traceback
            print("🔥 Full Traceback:")
            traceback.print_exc()
            error = f"❌ Error: {str(e)}"
            return render_template("summary.html", error=error)

    return render_template("summarize.html")




@app.route('/my-notes')
def my_notes():
    if 'user_id' not in session:
        flash("Please log in first.")
        return redirect(url_for('login'))
    return render_template("my_notes.html")

@app.route('/ai-chat')
def ai_chat():
    if 'user_id' not in session:
        flash("Please log in first.")
        return redirect(url_for('login'))
    return render_template("ai_chat.html")

if __name__ == "__main__":
    app.run(debug=True)
