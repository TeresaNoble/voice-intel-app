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
        "Witty": "Sharp with a twist.",
        "Professional": "Professional but personable.",
        "Warm": "Friendly and human.",
        "Bold": "Confident, strong statements."
    },
    "content_format": {
        "Step-by-Step": "Give me a clear numbered sequence.",
        "Quick Summary": "Just the key points, fast. No waffle.",
        "Detailed Breakdown": "Explain with depth.",
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

# ---------------------- CORE ENGINE ----------------------
def build_hidden_instructions(profile):

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

    tone_overrides = []
    
    core_tone = [
        "You are Custom Content AI — a content generator with bite, style, and zero tolerance for corporate fluff.",
        "Your default tone is bold, modern, and irreverent. Think: texting a clever friend who's mildly distracted, but will absolutely roast you if you waste their time.",
        "",
        "## Core Tone Rules:",
        "Write like you're texting a mildly distracted friend — clear, casual, and charming.",
        "Avoid big words and formal tone — this isn’t a TED Talk or a bank chatbot.",
        "Clarity comes first, but don’t sacrifice personality. Think charm over polish.",
        "Stay human, stay cheeky, and never sound like LinkedIn on a Monday."
        "Do not create themes, characters, metaphors, or narrative devices unless explicitly requested. Avoid turning simple tasks into storytelling. Keep it grounded in real-world language and tone."
,
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
            "- Sarcasm is allowed — but it better be earned.",
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
st.title("AI Content Designer")

# Instructions panel logic
if "instructions_shown" not in st.session_state:
    st.session_state.instructions_shown = True  # Show instructions by default

if st.session_state.instructions_shown:
    with st.expander("Instructions"):
        st.markdown("""
        ### Welcome to Custom Content AI
        ## This is your content styling lab. You bring the message and we’ll help you shape it to hit right.
            - **Tone Flair** This sets the overall attitude:
                - **Nip** keeps it precise and edgy.
                - **Slash** cuts sharp and stylish.
                - **Blaze** bold, direct, and impossible to ignore.
            - **Communication Style** Choose your audiences general communication vibe.
            - **Content Format** How should the content appear in its final form as?
            - **Generation** Pick the closest match for your audience or choose Mixed if you’re a crossover soul.
        - Ready to roll? Drop your request in the chat box below and watch the magic (or mild chaos) unfold.
        - Like what you see? Smash that download button before the content disappears into the void.
        - One query gets you one result. Copy or download it before it vanishes into the ether.
        """)

# Profile Management
profile = get_sidebar_profile()
st.session_state.profile = profile

# Chat Interface
if prompt := st.chat_input("What content should we create?"):
    # Hide the instructions panel after the first message
    st.session_state.instructions_shown = False
    
    # Generate content with hidden rules
    system_msg = {"role": "system", "content": build_hidden_instructions(profile)}
        
    response = client.chat.completions.create(
          model="gpt-4",
          messages=[system_msg, {"role": "user", "content": prompt}]
        )
        
    # Display response
    with st.chat_message("assistant"):
        content = response.choices[0].message.content
        st.write(content)
            
        # Download as text file
        st.download_button(
          label="📥 Download txt file",
          data=content,
          file_name="content.md"
        )
            
        # Export as Word document
        doc = Document()
        doc.add_heading("Generated Content", level=1)
        doc.add_paragraph(content)
        word_file = "designed_content.docx"
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
