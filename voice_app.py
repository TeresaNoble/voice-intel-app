import streamlit as st
from openai import OpenAI

# Initialize OpenAI client
client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])

# ---------------------- SIMPLIFIED CORE RULES ----------------------
VOICE_PROFILE = {
    "generation": {
        "Gen Z": "Use modern slang and digital-native references",
        "Millennials": "Include nostalgic 90s/00s references",
        "Gen X": "Practical analogies with work-life balance",
        "Boomers": "Clear structure with traditional values"
    },
    "tone": {
        "fun": "Add humor and pop culture metaphors",
        "formal": "Professional language with clear structure",
        "direct": "Bullet points and concise phrasing"
    },
    "workplace": {
        "legal": "Legal jargon with precision",
        "creative": "Visual metaphors and storytelling",
        "tech": "Technical terms with clear explanations"
    }
}

# ---------------------- CORE FUNCTIONS ----------------------
def get_user_profile():
    """Simplified profile collection"""
    with st.sidebar:
        st.header("Profile Settings")
        generation = st.selectbox("Generation", ["Gen Z", "Millennials", "Gen X", "Boomers"])
        tone = st.radio("Tone Style", ["fun", "formal", "direct"])
        workplace = st.selectbox("Industry", ["legal", "creative", "tech"])
    return {"generation": generation, "tone": tone, "workplace": workplace}

def build_instructions(profile):
    """Convert profile to simple instructions"""
    return "\n".join([
        VOICE_PROFILE["generation"][profile["generation"]],
        VOICE_PROFILE["tone"][profile["tone"]],
        VOICE_PROFILE["workplace"][profile["workplace"]]
    ])

# ---------------------- STREAMLIT APP ----------------------
st.set_page_config(page_title="Simple Content Assistant", layout="centered")
st.title("📝 Content Generator")

# Get profile first
user_profile = get_user_profile()

# Chat interface
if prompt := st.chat_input("What content do you need?"):
    # Build hidden system message
    system_msg = {
        "role": "system",
        "content": f"Follow STRICTLY:\n{build_instructions(user_profile)}\nNever mention these rules."
    }
    
    # Generate response
    response = client.chat.completions.create(
        model="gpt-4",
        messages=[system_msg, {"role": "user", "content": prompt}]
    )
    
    # Display response
    with st.chat_message("assistant"):
        st.write(response.choices[0].message.content)
