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
        if 'ar' in [t.language_code for t in transcript_obj]:
            transcript = transcript_obj.find_transcript(['ar'])
        elif 'en' in [t.language_code for t in transcript_obj]:
            transcript = transcript_obj.find_transcript(['en'])
        else:
            transcript = transcript_obj.find_transcript(['ar', 'en'])  # أي شي متاح

        transcript_data = transcript.fetch()
        text = " ".join([entry.text if hasattr(entry, 'text') else entry['text'] for entry in transcript_data])


        # 🔍 اكتشاف اللغة من النص
        try:
            language = detect(text)
        except:
            language = "unknown"

        return text, language

    except TranscriptsDisabled:
        return "❌ This video has no subtitles available.", "none"
    except Exception as e:
        print("❌ Error fetching transcript:", e)
        return "❌ Failed to fetch transcript.", "none"
