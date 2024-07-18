import streamlit as st

def sidebar_content():
    st.sidebar.image("./public/img/picture.png")
    st.sidebar.header("Visit My Website")
    st.sidebar.text("https://www.atakangul.com")
    pdf = st.sidebar.file_uploader("Upload your pdf file below ", accept_multiple_files=False)
    api_key = st.sidebar.text_input("OpenAI API Key", type="password")
    temperature = st.sidebar.slider("Temperature", 0, 10, 1)
    return pdf, api_key, temperature

def display_chat_messages(chat_history):
    for i, message in enumerate(reversed(chat_history)):
        with st.chat_message("user" if i % 2 == 0 else "assistant"):
            st.write(message.content)