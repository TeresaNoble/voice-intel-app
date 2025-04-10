import streamlit as st

st.set_page_config(page_title="Voice Intelligence Assistant", page_icon="🧠")

st.title("🧠 Voice-Driven Content Assistant")

st.write("Hey! 👋 What’s your team working on? Need help writing something?")

user_input = st.text_area("Tell me about your team and what you need:")

if st.button("Let’s Go"):
    st.write("Nice! You're cooking now. 🍳")
    st.write("I'll figure out what info we have and what we still need next.")
