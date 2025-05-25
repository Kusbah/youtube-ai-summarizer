import streamlit as st
import time
from streamlit_card import card
import base64

welcome = """
VideoAI is an innovative platform designed to enhance your YouTube video experience by using advanced AI technology. This application provides powerful features to summarize YouTube videos, enabling you to quickly grasp the content of any video with just a few sentences. Whether you're trying to save time or gain quick insights, the AI chatbot will provide concise and accurate summaries of videos across various categories.

In addition to summarizing, VideoAI offers the unique capability to compare multiple videos on the same topic. The AI chatbot evaluates and contrasts the content of videos, helping you determine which video provides the best information, most relevant insights, or presents the content in a more effective way.

The application also includes a video library where users can store and manage videos they've used or want to reference in the future. The library organizes videos into categories, making it easy to find and revisit your favorite content. With VideoAI, you can streamline your video consumption, save time, and improve your learning experience.
"""

def get_welcome():
    for word in welcome.split():
            yield word + " "
            time.sleep(0.05)

st.markdown(
    """
    <style>
    .block-container {
        padding: 10;
        max-width: 85%;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

st.title("VideoAI")
st.divider()

columns = st.columns(3)
images = [
    {
        "path": "./slides/one.png",
        "title": "Summarize Youtube Videos!",
        "url": "http://localhost:8501/summarizer",
        "desc": "get quick summaries",
        "col": columns[0],
    },
    {
        "path": "./slides/two.png",
        "title": "Compare Youtube Videos!",
        "url": "http://localhost:8501/comparer",
        "desc": "understand the difference",
        "col": columns[1],
    },
    {
        "path": "./slides/three.png",
        "title": "Browse Library of Videos",
        "url": "http://localhost:8501/library",
        "desc": "save your videos",
        "col": columns[2],
    },
]


for image in images:
    with open(image["path"], "rb") as f:
        data = f.read()
        encoded = base64.b64encode(data)
    data = "data:image/png;base64," + encoded.decode("utf-8")

    with image["col"]:
        hasClicked = card(
            title=image["title"],
            text=image["desc"],
            url=image["url"],
            image=data,
        )

st.write_stream(get_welcome())
