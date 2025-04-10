import streamlit as st
import openai

openai.api_key = st.secrets["OPENAI_API_KEY"]

st.set_page_config(page_title="Voice Assistant", page_icon="🧠")
st.title("🧠 Voice-Driven Content Assistant")

user_input = st.text_area("Hey! 👋 What’s your team working on? Need help writing something?", height=150)

if st.button("Let’s Go"):
    if user_input.strip() == "":
        st.warning("Give me something to chew on 🐶")
    else:
        with st.spinner("Reading your vibes and consulting the robot overlords... 🤖"):
            system_msg = """
You are a witty, warm, helpful writing assistant who uses fun tone and creative language.
Your job is to read the user's input and reply with a short message that:
- Confirms what was understood ✅
- Asks for anything important that’s missing ❓
- Uses casual, playful language (but still clear)
"""

            response = openai.ChatCompletion.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": system_msg},
                    {"role": "user", "content": user_input}
                ]
            )

            reply = response.choices[0].message.content
            st.markdown("### ✨ Here’s what I think:")
            st.write(reply)

