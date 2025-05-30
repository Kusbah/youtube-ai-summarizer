from flask import Flask, render_template, request, redirect, url_for, session, flash
import sqlite3
import requests
from werkzeug.security import generate_password_hash, check_password_hash
from transcriber import get_transcript_from_youtube
import openai
from dotenv import load_dotenv
import os
load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")
from bs4 import BeautifulSoup


app = Flask(__name__)
app.secret_key = 'youtubai' 

#  دالة مساعدة لإنشاء الاتصال بالقاعدة
def get_db_connection():
    conn = sqlite3.connect('users.db')
    conn.row_factory = sqlite3.Row
    return conn

#  إنشاء الجدول لو مش موجود
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
    print("Database initialized.")

init_db()  # تشغيلها أول ما يشتغل السيرفر


def init_summary_table():
    with get_db_connection() as conn:
        conn.execute('''
            CREATE TABLE IF NOT EXISTS summaries (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                video_url TEXT,
                video_title TEXT,
                thumbnail TEXT,
                summary TEXT,
                transcript TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
        ''')
    print("Summary table initialized.")

init_summary_table()



#  الصفحة الرئيسية
@app.route('/')
def home():
    return render_template("home.html")

def generate_summary(text, lang):
    if lang == 'ar':
        prompt = f"""Generate an HTML-formatted Arabic summary using the following structure.

        Do NOT wrap the output in markdown backticks. Return valid HTML directly.

        <strong>📄 الملخص:</strong>
        <p>فقرة قصيرة تشرح المقطع.</p>

        <strong>📌 النقاط البارزة:</strong>
        <ol>
        <li>...</li>
        <li>...</li>
        </ol>

        <strong>💡 الاستنتاجات:</strong>
        <ol>
        <li>...</li>
        </ol>

        النص:
        {text}
        """


    else:
        prompt = f"""Generate a clean HTML-formatted summary of the following transcript using this structure:

        <strong>📝 Summary:</strong>
        <p>A short paragraph summarizing the general topic.</p>

        <strong>📌 Highlights:</strong>
        <ol>
        <li>First key highlight</li>
        <li>Second key highlight</li>
        </ol>

        <strong>💡 Key Insights:</strong>
        <ol>
        <li>Insightful point 1</li>
        <li>Insightful point 2</li>
        </ol>

        Return the full output in valid HTML only.

        Transcript:
        {text}
        """


    try:
        response = openai.ChatCompletion.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": "You are a helpful assistant that summarizes YouTube transcripts."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.5,
            max_tokens=700
        )
        return response['choices'][0]['message']['content'].strip()
    except Exception as e:
        print("Summary generation error:", e)
        return "Failed to generate summary."

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



#  تسجيل الدخول
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


# إنشاء حساب
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


#  إعادة تعيين كلمة المرور 
@app.route('/reset-password', methods=['GET', 'POST'])
def reset_password():
    if request.method == 'POST':
        email = request.form['email']
        flash('If this email exists, a reset link was sent.')
        return redirect(url_for('login'))
    return render_template("reset_password.html")




# تسجيل الخروج
@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))




@app.route('/summarize', methods=['GET', 'POST'])
def summarize():
    if 'user_id' not in session:
        flash("Please log in first.")
        return redirect(url_for('login'))

    if request.method == 'POST':
        url = request.form.get('url')
        error = None
        transcript = None
        lang = None

        if not url or "youtube.com" not in url:
            error = "❌ Invalid YouTube URL."
            return render_template("summary.html", error=error)

        try:
            # 📝 استخراج السكربت واللغة
            transcript, lang = get_transcript_from_youtube(url)

            # ✅ التحقق من فشل الترانسكريبت
            if not transcript or transcript.strip() == "" or "Failed to fetch transcript" in transcript:
                error = "❌ Couldn't fetch transcript. Video won't be saved."
                return render_template("summary.html", error=error)

            # 🧹 تنظيف النص
            soup = BeautifulSoup(transcript, "html.parser")
            clean_text = soup.get_text(separator=' ', strip=True)

            # 🧠 التلخيص
            summary = generate_summary(clean_text, lang)

            # 📷 الصورة المصغّرة
            from urllib.parse import urlparse, parse_qs
            video_id = parse_qs(urlparse(url).query).get("v", [None])[0]
            thumbnail = f"https://img.youtube.com/vi/{video_id}/hqdefault.jpg"

            # 🏷 عنوان الفيديو
            video_title = get_video_title(url)

            # حفظ الترانسكريبت في السيشن
            session['transcript'] = clean_text

            # 🗃 التخزين في قاعدة البيانات
            conn = get_db_connection()

            # 🚫 تحقق من التكرار
            existing = conn.execute(
                'SELECT * FROM summaries WHERE user_id = ? AND video_url = ?',
                (session['user_id'], url)
            ).fetchone()

            if existing:
                flash("⚠️ This video was already summarized before. It won't be saved again.")
            else:
                conn.execute('''
                    INSERT INTO summaries (user_id, video_url, video_title, thumbnail, summary, transcript)
                    VALUES (?, ?, ?, ?, ?, ?)
                ''', (session['user_id'], url, video_title, thumbnail, summary, clean_text))
                conn.commit()

            conn.close()

            return render_template("summary.html",
                                   transcript=transcript,
                                   video_url=url,
                                   video_title=video_title,
                                   thumbnail=thumbnail,
                                   lang=lang,
                                   summary=summary,
                                   error=error)

        except Exception as e:
            import traceback
            print("🔥 Full Traceback:")
            traceback.print_exc()
            error = f"❌ Error while summarizing: {str(e)}"
            return render_template("summary.html", error=error)

    return render_template("summarize.html")








@app.route('/chat-with-transcript', methods=['POST'])
def chat_with_transcript():
    data = request.get_json()
    question = data.get("question")
    transcript = data.get("transcript")
    lang = data.get("lang", "en")

    if not question or not transcript:
        return {"error": "Missing transcript or question"}, 400

    try:
        if lang == "ar":
            prompt = f"بناءً على هذا النص:\n\n{transcript}\n\nأجب على هذا السؤال:\n{question}"
        else:
            prompt = f"Based on the following transcript:\n\n{transcript}\n\nAnswer this question:\n{question}"

        response = openai.ChatCompletion.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": "You are a helpful assistant answering questions based on a YouTube transcript."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7,
            max_tokens=500
        )

        reply = response["choices"][0]["message"]["content"].strip()
        return {"reply": reply}

    except Exception as e:
        return {"error": f"Exception: {str(e)}"}, 500




@app.route('/compare-chat', methods=['POST'])
def compare_chat():
    data = request.get_json()
    q = data.get("question")
    t1 = data.get("transcript1")
    t2 = data.get("transcript2")
    is_first = data.get("is_first", False)

    if not t1 or not t2:
        return {"reply": "❌ One of the transcripts is missing. Please make sure both videos have valid transcripts."}, 400

    if is_first:
        # الرد الأول: جدول HTML فقط
        prompt = f"""Compare the following two video transcripts by creating an HTML table with 3 columns:
- Topic
- Video 1 Insight
- Video 2 Insight

Focus on differences in concepts, examples, and clarity. Return a well-formatted HTML table only without extra explanations.

Transcript 1:
{t1}

Transcript 2:
{t2}
"""
    else:
        # ردود لاحقة بناء على اللغة
        if "عربي" in q or "بالعربي" in q or "احكي" in q:
            prompt = f"""بناءً على نص الفيديوهين، أجب على السؤال التالي باللغة العربية:

السؤال: {q}

النص الأول:
{t1}

النص الثاني:
{t2}
"""
        else:
            prompt = f"""Based on the two transcripts below, answer the user's question:

Question: {q}

Transcript 1:
{t1}

Transcript 2:
{t2}
"""

    try:
        response = openai.ChatCompletion.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": "You are a comparison expert who answers user questions using two video transcripts."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.5,
            max_tokens=900
        )
        return {"reply": response['choices'][0]['message']['content']}
    except Exception as e:
        print("🔥 Chat error:", str(e))
        return {"reply": "❌ Error occurred."}, 500







# @app.route("/compare-chat", methods=["POST"])
# def compare_chat():
#     data = request.get_json()
#     q = data.get("question", "")
#     t1 = data.get("transcript1", "")
#     t2 = data.get("transcript2", "")
#     is_first = data.get("is_first", False)

#     if not t1 or not t2:
#         return {"reply": "❌ One or both transcripts are missing."}

#     if is_first:
#         prompt = f"""قارن بين الفيديوهين التاليين باستخدام النصّين المقدمين. اعرض المقارنة على شكل جدول HTML أنيق، يتكون من الأعمدة التالية:

#     - الموضوع
#     - ملخص من الفيديو الأول
#     - ملخص من الفيديو الثاني

#     لا تكتب أي مقدمة أو شرح خارج الجدول. فقط أرسل جدول HTML الكامل.

#     نص الفيديو الأول:
#     {t1}

#     نص الفيديو الثاني:
#     {t2}
#     """
#     else:
#         # لو المستخدم طلب بالعربي
#         if "عربي" in q or "باللغة العربية" in q:
#             prompt = f"""بناءً على الفيديوهين التاليين، أجب عن السؤال التالي باللغة العربية:

#     السؤال:
#     {q}

#     نص الفيديو الأول:
#     {t1}

#     نص الفيديو الثاني:
#     {t2}"""
#         else:
#             prompt = f"""Based on the two video transcripts below, answer the user's question:

#     Question:
#     {q}

#     Transcript 1:
#     {t1}

#     Transcript 2:
#     {t2}"""

#     try:
#         response = openai.ChatCompletion.create(
#             model="gpt-3.5-turbo",
#             messages=[
#                 {"role": "system", "content": "You are a comparison assistant for YouTube videos."},
#                 {"role": "user", "content": prompt}
#             ],
#             temperature=0.6
#         )
#         reply = response['choices'][0]['message']['content']
#         return {"reply": reply}
#     except Exception as e:
#         return {"reply": f"❌ Error: {str(e)}"}







@app.route('/my-notes')
def my_notes():
    if 'user_id' not in session:
        flash("Please log in first.")
        return redirect(url_for('login'))

    conn = get_db_connection()
    summaries = conn.execute('SELECT * FROM summaries WHERE user_id = ? ORDER BY created_at DESC', (session['user_id'],)).fetchall()
    conn.close()

    return render_template("my_notes.html", summaries=summaries)



@app.route('/delete-summary/<int:summary_id>', methods=['POST'])
def delete_summary(summary_id):
    if 'user_id' not in session:
        flash("Please log in first.")
        return redirect(url_for('login'))

    conn = get_db_connection()
    conn.execute('DELETE FROM summaries WHERE id = ? AND user_id = ?', (summary_id, session['user_id']))
    conn.commit()
    conn.close()

    flash("Delete from Database")
    return redirect(url_for('my_notes'))


@app.route('/compare', methods=['POST'])
def compare():
    ids = request.form.getlist('compare_ids')
    if len(ids) != 2:
        flash("Please select exactly 2 videos.")
        return redirect(url_for('my_notes'))

    conn = get_db_connection()
    video1 = conn.execute('SELECT * FROM summaries WHERE id = ?', (ids[0],)).fetchone()
    video2 = conn.execute('SELECT * FROM summaries WHERE id = ?', (ids[1],)).fetchone()
    conn.close()

    return render_template('compare.html', video1=video1, video2=video2)





@app.route('/chat-with-compare', methods=['POST'])
def chat_with_compare():
    data = request.get_json()
    question = data.get('question')
    transcript1 = data.get('transcript1')
    transcript2 = data.get('transcript2')

    if not question or not transcript1 or not transcript2:
        return { "error": "Missing input fields." }, 400

    prompt = f"""
You are an AI assistant helping compare two educational videos.

Video 1 Transcript:
{transcript1}

Video 2 Transcript:
{transcript2}

User question:
{question}

Provide your answer clearly based on the comparison between both videos.
    """

    try:
        response = openai.ChatCompletion.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": "You are a helpful assistant that compares two video transcripts."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7,
            max_tokens=600
        )
        return { "reply": response["choices"][0]["message"]["content"].strip() }
    except Exception as e:
        return { "error": str(e) }, 500



@app.route('/ai-chat')
def ai_chat():
    if 'user_id' not in session:
        flash("Please log in first.")
        return redirect(url_for('login'))
    return render_template("ai_chat.html")

if __name__ == "__main__":
    app.run(debug=True)
