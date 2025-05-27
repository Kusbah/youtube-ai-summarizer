from youtube_transcript_api import YouTubeTranscriptApi, TranscriptsDisabled
from urllib.parse import urlparse, parse_qs
from langdetect import detect

def extract_video_id(url):
    query = urlparse(url)
    return parse_qs(query.query).get("v", [None])[0]

def get_transcript_from_youtube(url):
    video_id = extract_video_id(url)

    try:
        transcript_obj = YouTubeTranscriptApi.list_transcripts(video_id)

        # حاول تجيب أي لغة (عربي أو إنجليزي)
        try:
            transcript = transcript_obj.find_transcript(['ar'])
        except:
            try:
                transcript = transcript_obj.find_transcript(['en'])
            except:
                transcript = transcript_obj.find_transcript(['ar', 'en'])

        transcript_data = transcript.fetch()

        def format_time(seconds):
            minutes = int(seconds // 60)
            seconds = int(seconds % 60)
            return f"{minutes:02d}:{seconds:02d}"

        # ✅ تحويل كل كلمة إلى <span> بكامل تصحيح الخصائص
        html_lines = []
        buffer = []
        start_time = 0
        current_time = 0

        for entry in transcript_data:
            current_time = entry.start
            words = entry.text.split()
            word_links = " ".join([
                f'<span class="word" data-start="{int(entry.start)}">{w}</span>'
                for w in words
            ])
            buffer.append(word_links)

            if current_time - start_time >= 10:
                paragraph = " ".join(buffer)
                html_lines.append(f'<div class="line" data-start="{int(start_time)}">[{format_time(start_time)}] {paragraph}</div>')

                start_time = current_time
                buffer = []

        # لو ظل في جمل بباقي البافر
        if buffer:
            paragraph = " ".join(buffer)
            html_lines.append(f'<div class="line" data-start="{int(start_time)}">[{format_time(start_time)}] {paragraph}</div>')


        text = "\n".join(html_lines)


        # 🔍 اكتشاف اللغة (من النصوص نفسها)
        try:
            language = detect(" ".join([entry.text for entry in transcript_data]))
        except:
            language = "unknown"

        return text, language

    except TranscriptsDisabled:
        return "❌ This video has no subtitles available.", "none"
    except Exception as e:
        print("❌ Error fetching transcript:", e)
        return "❌ Failed to fetch transcript.", "none"
