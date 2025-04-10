import openai
import streamlit as st
from docx import Document
from docx.shared import Pt
from docx.enum.text import WD_PARAGRAPH_ALIGNMENT
import io
import json

TONE_GUIDES = {
    "generation": {
        "Gen Z": "Use fast, emoji-rich, punchy language.",
        "Millennials": "Be purpose-driven, friendly, modern.",
        "Gen X": "Be efficient, practical, slightly formal.",
        "Boomers": "Use structured, clear, and respectful language."
    },
    "tech_savviness": {
        "low": "Avoid jargon. Use plain language with step-by-step phrasing.",
        "medium": "Use basic tech terms with light explanation.",
        "high": "Skip explanations. Use confident, technical terms."
    },
    "culture": {
        "individualist": "Speak to personal benefit and ownership.",
        "collectivist": "Emphasize teamwork and shared goals."
    },
    "tone_pref": {
        "fun": "Use humor, energy, and a playful twist.",
        "formal": "Stick to structured, polished phrasing.",
        "supportive": "Be warm, helpful, and gently encouraging.",
        "direct": "Be confident and get to the point."
    }
}

def blend_tone_traits(profile):
    tone_parts = []

    for trait, trait_rules in TONE_GUIDES.items():
        values = profile.get(trait, [])

        if isinstance(values, str):
            values = [values]

        for value in values:
            tone = trait_rules.get(value)
            if tone:
                tone_parts.append(tone)

    return " ".join(tone_parts)



def generate_word_file(profile_data, ai_output):
    doc = Document()

    # Title – centered, bold, large
    title = doc.add_heading("GENERATED CONTENT 📄", level=0)
    title.alignment = WD_PARAGRAPH_ALIGNMENT.CENTER

    # Helper to add a section
    def add_section(label, content):
        para_label = doc.add_paragraph()
        run = para_label.add_run(label)
        run.bold = True
        run.font.size = Pt(12)

        para_content = doc.add_paragraph(str(content))
        para_content.paragraph_format.space_after = Pt(12)

    # Step 1: Structured Key-Value Pairs
    if "company_name" in profile_data:
        add_section("Company Name:", profile_data["company_name"])

    if "content_type" in profile_data:
        add_section("Content Description:", profile_data["content_type"])

    # Step 2: AI Output Section
    add_section("AI Output:", ai_output)

    # Save to buffer
    buffer = io.BytesIO()
    doc.save(buffer)
    buffer.seek(0)
    return buffer


openai.api_key = st.secrets["OPENAI_API_KEY"]

st.title("Custom Content Assistant")

user_input = st.text_area("Hey! What’s your team working on? Need help writing something?")

if st.button("Let’s Go"):
    if not user_input.strip():
        st.warning("Give me something to chew on 🐶")
    else:
        with st.spinner("Doing some clever thinking... 🤖"):
           blended_tone = blend_tone_traits(st.session_state.profile)

system_msg = f"""
You are a content assistant. Use the following tone style, blended from the user's traits:

{blended_tone}

The user may represent a mixture of backgrounds or preferences.
Always prioritize clarity, warmth, and a voice that adapts to the described audience.
Ask for clarification if the tone is unclear or inconsistent.
"""
st.markdown("### 🧠 Current Voice Style")
st.info(blended_tone)


            )

            response = openai.ChatCompletion.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": system_msg},
                    {"role": "user", "content": user_input}
                ]
            )

            reply = response.choices[0].message["content"]
            st.markdown("### Here’s what I think:")
            st.write(reply)

export_data = {
    "Team Type": st.session_state.profile.get("team_type", "N/A"),
    "Tone Preference": st.session_state.profile.get("tone_pref", "N/A"),
    "Content Type": st.session_state.profile.get("content_type", "N/A"),
    "AI Output": reply
}

word_file = generate_word_file(export_data)
st.download_button(
    label="📄 Export as Word Doc",
    data=word_file,
    file_name="content_output.docx",
    mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
)

