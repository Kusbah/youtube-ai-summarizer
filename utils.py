from youtube_transcript_api import YouTubeTranscriptApi
from langchain_ollama.chat_models import ChatOllama

llm = ChatOllama(model="llama3.2:latest")


def load_transcript(link):
    video_id = link.split("v=")[-1].split("&")[0]
    transcript = YouTubeTranscriptApi.get_transcript(video_id)
    transcript_dict = {
        f"{entry['start']:.2f}s - {entry['start'] + entry['duration']:.2f}s": entry[
            "text"
        ]
        for entry in transcript
    }

    return transcript_dict
