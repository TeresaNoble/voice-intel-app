import streamlit as st
from openai import OpenAI
import json
from docx import Document  # Import for Word document creation

# Initialize OpenAI client
client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])

# ---------------------- COMPLETE VOICE PROFILE ----------------------
VOICE_PROFILE = {
    "communication_style": {
        "Direct": "No fluff. Just the point.",
        "Encouraging": "Supportive and constructive.",
        "Playful": "Cheeky and casual.",
        "Witty": "Sharp with a hilarious dry English style twist.",
        "Professional": "Stick to clarity and credibility. Prioritize useful information over personality. Avoid slang, metaphors, and theatrics. Maintain a confident, modern tone — think human, not chatty.",
        "Warm": "Friendly and human.",
        "Bold": "Confident, strong statements."
    },
    "content_format": {
        "Step-by-Step": "Give me a clear numbered sequence.",
        "Quick Summary": "Just the key points, fast. No waffle.",
        "Detailed Breakdown": "Explain clearly with depth and reasons.",
        "Action List": "What do I do next? Give bullet points.",
        "Analytical": "Back it up with logic.",
        "Conversational": "Make it feel like a chat."
    },
    "generation": {
        "Gen Alpha (b.2013–2025)": "Immersed in tech. Intuitive and playful.",
        "Gen Z (b.1997–2012)": "Fast, visual, and meme-fluent. Include emojis.",
        "Millennials (b.1990–1996)": "Digital-native. Likes social and gamified tone.",
        "Wise Millennials (b.1981–1989)": "Bridges analog and digital. Values clarity and feedback.",
        "Gen X (b.1965–1980)": "Independent and direct. Prefers practical and honest tone.",
        "Boomers (b.1946–1964)": "Structured and respectful. Clear value and reliability.",
        "Silent Generation (1928–1945)": "Formal, respectful, and rooted in tradition. Responds to clarity, courtesy, and structured messaging.",
        "Mixed": "Blend tone and rhythm across generations. Focus on clarity and personality."
    },
    "length": {
        "Short": "Keep content under 100 words",
        "Medium": "100-200 word range",
        "Long": "200-500 word detailed content"
    }
}

# ---------------------- PROFILE MANAGEMENT ----------------------
def get_sidebar_profile():
    """Collect core profile through sidebar"""
    with st.sidebar:
        st.header("Define Your Audience and Style")

        # Add tone flair selector
        tone_flair = st.select_slider(
            "Tone Flair",
            options=["Nip", "Slash", "Blaze"],
            value="Slash",
            help="Choose how bold you want the writing to sound from subtle (Nip) to bold (Blaze)."
        )

        ultra_direct = st.toggle(
            "Ultra-Direct Mode",
            value=False,
            help="Override all personality settings to deliver sharp, efficient content with minimal tone."
        )

        
        return {
            "communication_style": st.selectbox("Preferred Communication Style", list(VOICE_PROFILE["communication_style"].keys()),
                              index=3,
                              help="Think, 'If I was my audience, how would I like to be spoken to?'"
            ),
            "content_format": st.selectbox("Content Format", list(VOICE_PROFILE["content_format"].keys()),
                              index=1,
                              help="What are we going with today, detailed, chatty, action?"
            ),
            "generation": st.selectbox("Audience Generation", list(VOICE_PROFILE["generation"].keys()),
                              index=7,
                              help="This adjusts tone pacing, references, and formality."
            ),
            "length": st.radio("Content Length", 
                             ["Short", "Medium", "Long"],
                             index=1
            ),  # Default to Medium
            "tone_flair": tone_flair,  # Include tone_flair in the returned profile
            "ultra_direct": ultra_direct
        }

def validate_profile(profile):
    """Ensure all profile fields are selected"""
    missing = []
    required_fields = list(VOICE_PROFILE.keys()) + ["length"]
    for field in required_fields:
        if not profile.get(field):
            missing.append(f"Please select {field.replace('_', ' ').title()}")
    return missing

if "last_response" not in st.session_state:
    st.session_state.last_response = ""


# ---------------------- CORE ENGINE ----------------------
def build_hidden_instructions(profile):
    tone_overrides = []
    
    if profile.get("ultra_direct", False):
        return "\n".join([
            "Ultra-Direct Mode is ON.",
            "Write as if you’re a real person who wants to help — quickly.",
            "Drop the charm. Avoid metaphors, intros, or creative phrasing.",
            "Be concise, direct, and blunt — with just enough human edge to not sound robotic.",
            "No warm-ups. No analogies. No fluff.",
            "",
            f"Content Format: {VOICE_PROFILE['content_format'][profile['content_format']]}",
            f"Generation: {VOICE_PROFILE['generation'][profile['generation']]}",
            f"Length: {VOICE_PROFILE['length'][profile['length']]}",
        ])

    if profile["tone_flair"] == "Blaze" and profile["communication_style"] in ["Professional", "Direct"]:
        return "\n".join([
            "Blaze Mode — Executive edition.",
            "Tone must be bold, direct, and human. Skip metaphors, branded sign-offs, or dramatic flourishes.",
            "Keep sentences short. Prioritize frictionless clarity with a confident edge.",
            "Sarcasm is welcome — if it stings, not sings.",
            "No wordplay. No pep talk. This isn’t advertising — it’s communication.",
            "",
            f"Content Format: {VOICE_PROFILE['content_format'][profile['content_format']]}",
            f"Generation: {VOICE_PROFILE['generation'][profile['generation']]}",
            f"Length: {VOICE_PROFILE['length'][profile['length']]}",
        ])
    
    if profile["communication_style"] in ["Professional", "Direct"]:
        tone_overrides.append(
            "Deliver bold, decisive statements. Skip the jokes, metaphors, or quirky analogies. Be assertive without being performative. No emojis, no theatrics — just charisma and clarity."
        )

    core_tone = [
        "You are Custom Content AI — a content generator with bite, style, and zero tolerance for corporate fluff.",
        "Your default tone is bold, modern, and irreverent. Think: texting a clever friend who's mildly distracted, but will absolutely roast you if you waste their time.",
        "",
        "## Core Tone Rules:",
        "Write like you're texting a mildly distracted friend — clear, casual, and charming.",
        "Avoid big words and formal tone — this isn’t a TED Talk or a bank chatbot.",
        "Clarity comes first, but don’t sacrifice personality. Think charm over polish.",
        "Stay human, stay cheeky, and never sound like LinkedIn on a Monday."
        "Do not create themes, characters, metaphors, or narrative devices unless explicitly requested. Avoid turning simple tasks into storytelling. Keep it grounded in real-world language and tone.",
    ]

    tone_flair = {
        "Nip": [
            "",
            "## Current Mood: Nip",
            "- Keep it clean, cut, and clever.",
            "- Say less, mean more — let the space between lines do some of the talking.",
            "- Dry wit wins. No sparkle, no fluff, no obvious jokes.",
            "- Use precision like a scalpel, not a spotlight.",
            "- If the line lingers in their mind later, you nailed it."
        ],
        "Slash": [
            "",
            "## Current Mood: Slash",
            "- Stylish. Smart. Intentional. Think editorial, not emotional.",
            "- If it cuts, it better look good doing it.",
            "- Irony is allowed, but never silly. Glossy and sharp, not shiny and loud.",
            "- Leave quotable lines — not punchlines.",
            "- Deliver like you're unfazed, not unimpressed."
        ],
        "Blaze": [
            "",
            "## Current Mood: Blaze",
            "- Confidence is the baseline. The tone should command, not beg.",
            "- Be bold, but don’t perform. Drop truths, not punchlines.",
            "- No hand-holding, no padding. Every line should feel like a decision.",
            "- Sarcasm is essential.",
            "- Cut the theatrics. You’re not on stage, you’re in charge."
        ]        
    }
 
    user_preferences = [
        "",
        "## User Preferences (flavor, not framework):",
        f"Communication Style: {VOICE_PROFILE['communication_style'][profile['communication_style']]}",
        f"Content Format: {VOICE_PROFILE['content_format'][profile['content_format']]}",
        f"Generation: {VOICE_PROFILE['generation'][profile['generation']]}",
        f"Length: {VOICE_PROFILE['length'][profile['length']]} - Be concise if short, thorough if long",
    ]
    

    return "\n".join(core_tone + tone_flair[profile["tone_flair"]] + tone_overrides + [""] + user_preferences)

# ---------------------- STREAMLIT APP ----------------------
st.set_page_config(page_title="Custom Content AI", layout="wide")
st.title("AI Writing Assistant")
st.markdown(
    "This tool helps you write any message fast.",
    unsafe_allow_html=True
)


# Instructions panel logic
if "instructions_shown" not in st.session_state:
    st.session_state.instructions_shown = True  # Show instructions by default

if st.session_state.instructions_shown:
    with st.expander("Instructions"):
        st.markdown("""
        ### How It Works
        Let me know your audience in the sidebar, then type your message idea below. This could be:
        - A short email to your boss  
        - A Slack announcement for your team  
        - An explainer for a doc or workflow  
        - Even a birthday card line (no judgement)
        
        #### What the settings mean:
        - **Tone Flair** – This sets the overall attitude:
          &nbsp;&nbsp;- **Nip** keeps it precise and edgy  
          &nbsp;&nbsp;- **Slash** cuts sharp and stylish  
          &nbsp;&nbsp;- **Blaze** bold, direct, and impossible to ignore  
        - **Communication Style** – Choose your audience's preferred tone
        - **Content Format** – Should it be chatty, listy, or structured?
        - **Generation** – Choose the closest match for your reader (or 'Mixed')
                
        Once you type your message idea below, I’ll rewrite it for your audience, or it'll be something you can be inspired by!
        """, unsafe_allow_html=True)


# Profile Management
profile = get_sidebar_profile()
st.session_state.profile = profile

# Chat Interface
# Chat interface and response rendering
if "last_prompt" not in st.session_state:
    st.session_state.last_prompt = ""
if "last_response" not in st.session_state:
    st.session_state.last_response = ""

prompt = st.chat_input("What are we writing?")

if prompt:
    st.session_state.instructions_shown = False
    st.session_state.last_prompt = prompt

    system_msg = {"role": "system", "content": build_hidden_instructions(profile)}
    response = client.chat.completions.create(
        model="gpt-4",
        messages=[system_msg, {"role": "user", "content": prompt}]
    )

    content = response.choices[0].message.content
    st.session_state.last_response = content

# Display last result
if st.session_state.last_response:
    st.markdown(f"**Original Request:** _{st.session_state.last_prompt}_")
    st.markdown(st.session_state.last_response)

    # Add button to reuse last prompt
    if st.button("↩️ Reuse Last Prompt"):
        st.chat_input("What are we writing?", value=st.session_state.last_prompt)

    # Download buttons
    st.download_button(
        label="📥 Download txt file",
        data=st.session_state.last_response,
        file_name="AI Writing.md"
    )

    doc = Document()
    doc.add_heading("Your AI Writing", level=1)
    doc.add_paragraph(st.session_state.last_response)
    word_file = "response.docx"
    doc.save(word_file)

    with open(word_file, "rb") as file:
        st.download_button(
            label="📥 Download Word file",
            data=file,
            file_name=word_file,
            mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
        )
          



# Display conversation history
for msg in st.session_state.get("messages", []):
    with st.chat_message(msg["role"]):
        st.write(msg["content"])
