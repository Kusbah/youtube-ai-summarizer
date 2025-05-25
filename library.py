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

st.title("Your Library of Videos")
st.divider()

if "library" not in st.session_state:
    st.session_state.library = set(
        [
            "https://youtu.be/48jlHaxZnig?si=27HA0nnEhe7MIDIQ",
            "https://youtu.be/zOjov-2OZ0E?si=5cdKeBIlPdmp2w-S",
            "https://www.youtube.com/watch?v=g6iyPhyc7S4",
        ]
    )

num_columns = 3
columns = st.columns(num_columns)

for index, video in enumerate(st.session_state.library):
    col = columns[index % num_columns]
    with col:
        st.video(video)
