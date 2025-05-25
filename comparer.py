import streamlit as st
from utils import llm, load_transcript

st.markdown(
    """
    <style>
    .block-container {
        padding: 10;
        max-width: 80%;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

if "num_videos" not in st.session_state:
    st.session_state.num_videos = 2

if "scripts" not in st.session_state:
    st.session_state.scripts = []


def compare_videos():
    prompt = f"""
    You're an intelligent AI assistant that takes in transcripts
    for YouTube videos and compares between the different transcripts.
    there are {st.session_state.num_videos} videos that you need to compare 
    please explain and compare between these videos
    """

    print(len(st.session_state.scripts))
    for i, script in enumerate(st.session_state.scripts):
        prompt += f"\n **Transcript for Video {i}:** \n{script}\n"

    with st.chat_message("assistant"):
        stream = llm.stream(prompt)
        st.write_stream(stream)


def video_container(id):
    st.header(f"Video {id}")
    if link := st.text_input(f"Video {id} link", placeholder="Insert YouTube link"):
        st.video(link)
        st.session_state.scripts.append(load_transcript(link))


st.title("Compare Videos")
st.divider()

columns = st.columns(st.session_state.num_videos)
for i, column in enumerate(columns):
    with column:
        video_container(i + 1)

st.divider()

if st.button("Compare Videos", use_container_width=True):
    compare_videos()

if st.button("Add Another Video", use_container_width=True):
    st.session_state.num_videos += 1

if st.button("Remove Video", use_container_width=True):
    if st.session_state.num_videos > 1:
        st.session_state.num_videos -= 1
