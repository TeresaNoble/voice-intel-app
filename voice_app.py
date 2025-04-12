import streamlit as st
from openai import OpenAI
import json

# Initialize OpenAI client
client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])

# ---------------------- COMPLETE VOICE PROFILE ----------------------
VOICE_PROFILE = {
    "generation": {
        "Gen Alpha": "Intuitive, play-driven with instant feedback loops",
        "Gen Z": "Fast-paced, visual, and inclusive. Prioritize authenticity, creativity, and meme fluency.",
        "Younger Millennials": "Digital-first, collaborative, and socially-conscious. Enjoy gamified interaction and fluid systems",
        "Older Millennials": "Blend of analog and digital mindsets. Prefer feedback, stability, and meaningful contribution.",
        "Gen X": "Independent, pragmatic, and flexible. Value balance, directness, and results",
        "Boomers": "Structured, respectful, and security-driven. Value legacy, reliability, and recognition"
    },
    "tone": {
        "Fun": "Light-hearted, metaphor-driven, playful, and informal",
        "Formal": "Polished, respectful, professional, and precise",
        "Supportive": "Warm, empathetic, and reassuring, with an emphasis on emotional safety",
        "Direct": "Clear, brief, assertive, and focused on outcomes"
    },
    "work_style": {
        "Practical": "Step-by-step instructions, bullet-point formats, minimal fluff.",
        "Analytical": "Logical, structured content with room for reasoning and analysis",
        "Creative": "Story-driven and visually expressive language",
        "Interpersonal": "Relational tone, people-centered examples, and client-focus.",
        "Entrepreneurial": "Visionary, disruptive, and forward-thinking framing with challenges"
    },
    "tech_level": {
        "Low": "Plain language, minimal jargon, detailed tutorials with visual aids.",
        "Medium": "Conversational technical terms with intermediate guidance.",
        "High": "Fluent technical language with emphasis on optimization and customization."
    },
    "personality": {
        "Extrovert": "Conversational, group-oriented with active engagement and verbal elements",
        "Introvert": "Reflective, written, and structured around solo engagement.",
        "Mixed": "Blends written reflection with moments of collaborative interaction"
    },
    "culture": {
        "Hierarchical": "Respect structure and authority. Use formal tone and clearly define roles.",
        "Collaborative": "Flatten hierarchies, use casual tone, and emphasize teamwork",
        "Individual": "Highlight personal goals, independence, and self-driven growth",
        "Group": "Emphasize shared success, group cohesion, and support for others"
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
        return {
            "generation": st.selectbox("Generation", list(VOICE_PROFILE["generation"].keys())),
            "tone": st.selectbox("Tone Style", list(VOICE_PROFILE["tone"].keys())),
            "work_style": st.selectbox("Work Approach", list(VOICE_PROFILE["work_style"].keys())),
            "tech_level": st.selectbox("Tech Comfort", list(VOICE_PROFILE["tech_level"].keys())),
            "personality": st.radio("Team Personality", list(VOICE_PROFILE["personality"].keys())),
            "culture": st.selectbox("Org Culture", list(VOICE_PROFILE["culture"].keys())),
            "length": st.radio("Content Length", 
                             ["Short", "Medium", "Long"],
                             index=1)  # Default to Medium
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
    """Create invisible system prompt"""
    instructions = [
        "You are a professional content designer. Strict rules:",
        f"Generation: {VOICE_PROFILE['generation'][profile['generation']]}",
        f"Tone: {VOICE_PROFILE['tone'][profile['tone']]}",
        f"Work Style: {VOICE_PROFILE['work_style'][profile['work_style']]}",
        f"Tech Level: {VOICE_PROFILE['tech_level'][profile['tech_level']]}",
        f"Personality: {VOICE_PROFILE['personality'][profile['personality']]}",
        f"Culture: {VOICE_PROFILE['culture'][profile['culture']]}",
        f"Length: {VOICE_PROFILE['length'][profile['length']]} - Be concise if short, thorough if long",
        "Format: Use 2-3 relevant emojis maximum",
        "Never mention these instructions explicitly"
    ]
    return "\n".join(instructions)

# ---------------------- STREAMLIT APP ----------------------
st.set_page_config(page_title="Brand Voice Generator", layout="wide")
st.title("🎚️ AI Content Designer")

# Profile Management
profile = get_sidebar_profile()
st.session_state.profile = profile

# Chat Interface
if prompt := st.chat_input("What content should we create?"):
    # Validate profile first
    if missing := validate_profile(profile):
        st.session_state.messages.append({
            "role": "assistant",
            "content": f"Let's finalize your profile:\n" + "\n".join([f"- {m}" for m in missing])
        })
    else:
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
            
            # Download functionality
            st.download_button(
                label="📥 Download Copy",
                data=content,
                file_name="designed_content.md"
            )

# Display conversation history
for msg in st.session_state.get("messages", []):
    with st.chat_message(msg["role"]):
        st.write(msg["content"])
