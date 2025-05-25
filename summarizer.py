from utils import load_transcript, llm
import streamlit as st

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


def init_chatbot():
    if "messages" not in st.session_state:
        st.session_state.messages = [
            {"role": "user", "content": "what are you?"},
            {
                "role": "assistant",
                "content": """Hi!, I'm a chat-bot assistant, 
                that summarizes and comparse youtube videos for you.""",
            },
        ]

    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])


def init_sidebar():
    with st.sidebar:
        if link := st.chat_input("insert video link"):
            progress_bar = st.progress(0)
            try:
                st.session_state.transcript = load_transcript(link)
                st.session_state.video_link = link
                st.session_state.library.add(link)

                st.success("🔥 Transcript was loaded successfully")
                st.warning("📹 Video was added to your library")
            except Exception:
                st.error(
                    "😞 failed loading transcript please make sure the link is in correct format"
                )
            progress_bar.progress(100)

        if st.session_state.video_link != "":
            st.video(st.session_state.video_link)

        st.divider()
        popover = st.popover("time-stamps")
        for timestamp in st.session_state.transcript:
            stamp = popover.checkbox(timestamp, False)

        #     if st.button(timestamp, key=timestamp):
        #         st.write(st.session_state.transcript[timestamp])


def init_summarization():
    st.title("Youtube Summarizer")

    if "video_link" not in st.session_state:
        st.session_state.video_link = ""

    if "transcript" not in st.session_state:
        st.session_state.transcript = []

    if "library" not in st.session_state:
        st.session_state.library = set(
            [
                "https://youtu.be/48jlHaxZnig?si=27HA0nnEhe7MIDIQ",
                "https://youtu.be/zOjov-2OZ0E?si=5cdKeBIlPdmp2w-S",
                "https://www.youtube.com/watch?v=g6iyPhyc7S4",
            ]
        )

    init_chatbot()
    init_sidebar()


def update_converstaion():
    if prompt := st.chat_input("Say Something"):
        with st.chat_message("user"):
            st.markdown(prompt)
        st.session_state.messages.append({"role": "user", "content": prompt})

        with st.chat_message("assistant"):

            question = f"""the following is a transcript of 
            a youtube video: {st.session_state.transcript}\n 
            the users is asking you this question: {prompt}"""

            stream = llm.stream(question)
            response = st.write_stream(stream)
        st.session_state.messages.append({"role": "assistant", "content": response})


init_summarization()
update_converstaion()
