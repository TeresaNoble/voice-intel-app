import streamlit as st
from openai import OpenAI
import json
from docx import Document  # Import for Word document creation

# Initialize OpenAI client
client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])

# ---------------------- COMPLETE VOICE PROFILE ----------------------
VOICE_PROFILE = {
    "messaging_style": {
        "Straight Talker": "Clear, efficient, and no-nonsense. Prioritizes action over explanation.",
        "storyteller": "Uses metaphors, anecdotes, and emotion to engage. Great for persuasion and empathy.",
        "cheerleader": "Upbeat, encouraging, and motivating. Offers positive reinforcement and optimism.",
        "professional": "Polished, respectful, and structured. Ideal for formal or business contexts.",
        "playful": "Light-hearted, humorous, and casual. Best for creative or younger audiences."
    },
    "motivation_trigger": {
        "aspiration_led": "Focuses on future potential, rewards, and personal achievement. Responds to growth and possibility.",
        "security_led": "Seeks safety, reassurance, and certainty. Avoids risk and prefers trusted paths.",
        "recognition_led": "Craves visibility, celebration, and status. Likes public wins and personal praise.",
        "growth_led": "Values steady improvement, mastery, and long-term development."
    },
    "processing_style": {
        "step_by_step": "Follows clear instructions and linear logic. Prefers numbered lists, how-tos, and guided sequences.",
        "big_picture": "Needs to understand the why before the how. Connects best with themes, frameworks, and context.",
        "reflective": "Engages through introspection, personal writing, and quiet thought.",
        "interactive": "Wants engagement, conversation, or playful challenge. Prefers back-and-forth formats."
    },
    "response_type": {
        "quick_reactor": "Skims for value fast. Wants fast wins, clarity, and brevity.",
        "thinker": "Prefers nuance and layered ideas. Engages deeply with thoughtful content.",
        "tasker": "Needs action steps now. Prefers actionable, practical content over theory.",
        "skeptic": "Needs evidence, authority, or proof. Responds to logic, citations, and credentials."
    },
    "engagement_mode": {
        "solo_mode": "Prefers individual reflection, quiet reading, and solo tasks.",
        "one_to_one_mode": "Engages best in direct conversation, mentorship, or coaching-like formats.",
        "team_mode": "Thrives on group interaction, shared success, and community-based tasks.",
        "adaptive_mode": "Comfortable in any format. Flexible and adjusts to context easily."
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
            "messaging_style": st.selectbox("Messaging Style", list(VOICE_PROFILE["messaging_style"].keys())),
            "motivation_trigger": st.selectbox("Motivation Trigger", list(VOICE_PROFILE["motivation_trigger"].keys())),
            "processing_style": st.selectbox("Processing Style", list(VOICE_PROFILE["processing_style"].keys())),
            "response_type": st.selectbox("Response Type", list(VOICE_PROFILE["response_type"].keys())),
            "engagement_mode": st.selectbox("Engagement Mode", list(VOICE_PROFILE["engagement_mode"].keys())),
            "length": st.radio("Content Length", 
                             ["Short", "Medium", "Long"],
                             index=1),
            "tone_flair": tone_flair# Default to Medium
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
    base_tone = [
        "Write like you're texting a mildly distracted friend — clear, casual, and charming.",
        "Avoid big words and formal tone — this isn’t a TED Talk or a bank chatbot.",
        "Clarity comes first, but don’t sacrifice personality. Think charm over polish.",
        "Stay human, stay cheeky, and never sound like LinkedIn on a Monday.",
    ]

    tone_flair = {
        "Nip": [
            "Precision over punch. Every word should land without leaving a mark.",
            "Let the subtext do the talking — this is whispered shade, not a shout."
        ],
        "Slash": [
            "Stylish damage only — use wit like a scalpel, not a hammer.",
            "Glamorous edge required. If it doesn't cut *and* look good doing it, it's not Slash." 
        ],
        "Blaze": [
            "Maximum drama. Go big, bold, and maybe a little dangerous.",
            "Every line should sizzle with sass. Leave no souls unscorched."
        ]
    }
    profile_instructions = [
        f"Flavor your tone with {profile['messaging_style'].lower()} energy: {VOICE_PROFILE['messaging_style'][profile['messaging_style']]}",
        f"Motivation Trigger: {VOICE_PROFILE['motivation_trigger'][profile['motivation_trigger']]}",
        f"Processing Style: {VOICE_PROFILE['processing_style'][profile['processing_style']]}",
        f"Response Type: {VOICE_PROFILE['response_type'][profile['response_type']]}",
        f"Engagement Mode: {VOICE_PROFILE['engagement_mode'][profile['engagement_mode']]}",
        f"Length: {VOICE_PROFILE['length'][profile['length']]} — Be concise if short, thorough with bullet points if long"
    ]
    return "\n".join(base_tone + tone_flair[profile["tone_flair"]] + [""] + profile_instructions)

# ---------------------- STREAMLIT APP ----------------------
st.set_page_config(page_title="Custom Content AI Generator", layout="wide")
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
