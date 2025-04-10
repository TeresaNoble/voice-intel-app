import openai
import streamlit as st

openai.api_key = st.secrets["OPENAI_API_KEY"]

st.title("🧠 Voice-Driven Content Assistant")

user_input = st.text_area("Hey! What’s your team working on? Need help writing something?")

if st.button("Let’s Go"):
    if not user_input.strip():
        st.warning("Give me something to chew on 🐶")
    else:
        with st.spinner("Doing some clever thinking... 🤖"):
            system_msg = (
                "You're a witty, warm, helpful writing assistant. "
                "Reply with a message that confirms what was understood and asks for what’s missing. "
                "Use fun tone and clear language."
            )

            response = openai.ChatCompletion.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": system_msg},
                    {"role": "user", "content": user_input}
                ]
            )

            reply = response.choices[0].message["content"]
            st.markdown("### ✨ Here’s what I think:")
            st.write(reply)
