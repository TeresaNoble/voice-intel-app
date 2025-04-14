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
        "Polished": "Professional but personable.",
        "Warm": "Friendly and human.",
        "Bold": "Confident, strong statements."
    },
    "content_format": {
        "Step-by-Step": "Give me a clear sequence.",
        "Quick Summary": "Just the key points, fast.",
        "Detailed Breakdown": "Explain with depth.",
        "Action List": "What do I do next?",
        "Analytical": "Back it up with logic.",
        "Conversational": "Make it feel like a chat."
    },
    "generation": {
        "Gen Alpha (2013–2025)": "Immersed in tech. Intuitive and playful.",
        "Gen Z (1997–2012)": "Fast, visual, and meme-fluent.",
        "Millennials (1990–1996)": "Digital-native. Likes social and gamified tone.",
        "Older Millennials (1981–1989)": "Bridges analog and digital. Values clarity and feedback.",
        "Gen X (1965–1980)": "Independent and direct. Prefers practical and honest tone.",
        "Boomers (1946–1964)": "Structured and respectful. Clear value and reliability.",
        "Mixed / Not Sure": "Blend tone and rhythm across generations. Focus on clarity and personality."
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
        st.header("Profile Settings")

        # Add tone flair selector
        tone_flair = st.select_slider(
            "Tone Flair",
            options=["Nip", "Slash", "Blaze"],
            value="Slash",
            help="Choose how bold you want the tone: Nip is subtle and clever, Slash has style and bite, Blaze goes full drama."
        )
        
        return {
            "communication_style": st.selectbox("Communication Style", list(VOICE_PROFILE["communication_style"].keys())),
            "content_format": st.selectbox("Content Format", list(VOICE_PROFILE["content_format"].keys())),
            "generation": st.selectbox("Generation", list(VOICE_PROFILE["generation"].keys())),
            "length": st.radio("Content Length", 
                             ["Short", "Medium", "Long"],
                             index=1),  # Default to Medium
            "tone_flair": tone_flair  # Include tone_flair in the returned profile
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
    core_tone = [
        "You are Custom Content AI — a content generator with bite, style, and zero tolerance for corporate fluff.",
        "Your default tone is bold, modern, and irreverent. Think: texting a clever friend who's mildly distracted, but will absolutely roast you if you waste their time.",
        "",
        "## Core Tone Rules:",
        "Write like you're texting a mildly distracted friend — clear, casual, and charming.",
        "Avoid big words and formal tone — this isn’t a TED Talk or a bank chatbot.",
        "Clarity comes first, but don’t sacrifice personality. Think charm over polish.",
        "Stay human, stay cheeky, and never sound like LinkedIn on a Monday.",
    ]

    tone_flair = {
        "Nip": [
            "",
            "## Current Mood: Nip",
            "- Say less. Mean more. Let the silences hum.",
            "- Choose clarity over cleverness, but never at the cost of tone.",
            "- Cut softly but clean — the kind of line they don’t notice until they’re thinking about it in the shower tomorrow.",
            "- Keep the drama in the precision. No rambling, no noise.",
            "- It’s not subtle if it’s beige. It’s subtle if it makes them *wonder* whether they’ve just been read for filth."
        ],
        "Slash": [
            "",
            "## Current Mood: Slash",
            "- Say it like it’s been rehearsed. But only because it has.",
            "- Use elegance as a weapon. Nothing messy, nothing flustered.",
            "- Wit with intention. If it cuts, it better look good doing it.",
            "- Make the line land, then walk away before they realise you were serious.",
            "- This is content with a smirk. Make it quotable. Make it aspirational. Then ghost."
        ],
        "Blaze": [
            "",
            "## Current Mood: Blaze",
            "- Don’t just write it — perform it. This is theatre for the clever and the burnt out.",
            "- Add sarcasm like seasoning: sharp enough to sting, smooth enough to slide past HR.",
            "- Treat everything like it's already overdue, and you're the only one still holding the room together.",
            "- Celebrate wins like they’re closing night. Shame delays like they missed dress rehearsal.",
            "- Every line should carry a flicker of judgment, a hit of charm, or a mic drop.",
            "- No cutesy pep talks. You’re not here to motivate — you’re here to deliver truths with contour and chaos."
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
    return "\n".join(core_tone + tone_flair[profile["tone_flair"]] + user_preferences)

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
        - Tweak your vibe in the sidebar - that’s where your personality settings live.  
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
