import logging
import time
import uuid
import bson
from dotenv import load_dotenv
import streamlit as st
import google.generativeai as genai
import os
import tempfile
from connectors.mongo_connector import MongoConnector
from models.gemini_model import GeminiModel
from myUtils import extract_text
from myUtils.s3_mongodb import upload_pdf_to_s3_and_mongodb

load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger("Interview Page")

def get_interview_response(resume_text, chat_history):
    if 'gemini' not in st.session_state:
        st.session_state.gemini = GeminiModel()
    
    # Improved prompt structure
    prompt = f"""
    **Role**: Professional Technical Interviewer
    **Resume**: {resume_text[:3000]}  # Truncate to prevent token overflow
    
    **Conversation History**:
    {format_chat_history(chat_history)}
    
    **Task**:
    1. Analyze candidate's latest response
    2. Identify 1 strength and 1 improvement area
    3. Ask progressively challenging question
    4. Reference resume experiences
    
    **Response Format**:
    [Evaluation] <concise analysis>
    [Question] <next question>"""
    
    response = st.session_state.gemini._generate_content(prompt)
    return response.text

def format_chat_history(chat_history):
    return "\n".join(
        f"{'Interviewer' if msg['role'] == 'assistant' else 'Candidate'}: {msg['content']}"
        for msg in chat_history
    )

def stream_response(text):
    """Generator function for streaming response"""
    for line in text.split('\n'):
        for word in line.split():
            yield word + " "
            time.sleep(0.08)  # Natural typing speed
        yield '\n'

def display_chat(stream_write = False):
    """Display chat messages with streaming effect"""
    if not stream_write:
        for msg in st.session_state.chat_history[:-1]:
            with st.chat_message(msg["role"]):
                st.markdown(msg["content"])
        
        if st.session_state.chat_history:
            last_msg = st.session_state.chat_history[-1]
            with st.chat_message(last_msg["role"]):
                if last_msg["role"] == "assistant":
                    st.write_stream(stream_response(last_msg["content"]))
                else:
                    st.markdown(last_msg["content"])
    else:
        for msg in st.session_state.chat_history:
            with st.chat_message(msg["role"]):
                st.markdown(msg['content'])

def process_resume(uploaded_file):
    """Handle resume processing with error handling"""
    try:
        if uploaded_file.type == "application/pdf":
            with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
                tmp.write(uploaded_file.read())
                resume_text = extract_text(tmp.name)
                pdf_metadata_id = upload_pdf_to_s3_and_mongodb(
                    uploaded_file, tmp.name, "interviewer"
                )
                return resume_text
        return uploaded_file.read().decode()
    except Exception as e:
        st.error(f"Error processing resume: {str(e)}")
        return None

def interview():
    try:
        if 'session_id' not in st.session_state:
            st.session_state.session_id = str(uuid.uuid4())
        
        st.title("AI Interviewer 🎙️")
        st.markdown("---")
        
        # Initialize session states
        session_defaults = {
            'interview_started': False,
            'chat_history': [],
            'resume_text': "",
            'chat_id': str(uuid.uuid4()),
            'chat_length': 0
        }
        for key, val in session_defaults.items():
            st.session_state.setdefault(key, val)
        

        uploaded_file = st.file_uploader("Upload Resume", type=["pdf", "txt"])
        cols = st.columns(4)
        with cols[0]:
            if st.button("Start Interview") and uploaded_file:
                if resume_text := process_resume(uploaded_file):
                    st.session_state.resume_text = resume_text
                    st.session_state.interview_started = True
                    generate_first_question(resume_text)
        
        # Sidebar for controls
        with cols[3]:
            if st.button("End Interview", type="primary"):
                reset_session()
                st.success("Interview session ended successfully!")
                st.rerun()
            
        with st.sidebar:
            st.divider()
            st.subheader("Session Stats")
            st.metric("Questions Asked", len([m for m in st.session_state.chat_history if m["role"] == "assistant"]))
        
        # Main interview interface
        if st.session_state.interview_started:
            st.subheader("Live Interview Session")
            display_chat(True)
            
            # User input with enhanced validation
            if prompt := st.chat_input("Type your response..."):
                handle_user_input(prompt)
                
        else:
            st.info("Please upload your resume and click 'Start Interview' to begin")
            
    except Exception as e:
        st.error(f"Unexpected error: {str(e)}")
        logger.error(f"Interview error: {str(e)}")

def generate_first_question(resume_text):
    """Generate initial interview question"""
    with st.status("Preparing first question...", expanded=True) as status:
        prompt = f"""
        Generate an engaging opening question for a technical interview considering:
        - Resume summary: {resume_text[:2000]}
        - Should request self-introduction
        - Should reference one resume item
        - Keep under 2 sentences"""
        
        response = st.session_state.gemini._generate_content(prompt)
        st.session_state.chat_history.append({
            "role": "assistant",
            "content": response.text
        })
        post_conversation("assistant", response.text)
        status.update(label="Ready to begin!", state="complete")

def handle_user_input(prompt):
    """Process user response and generate next question"""
    st.session_state.chat_history.append({"role": "user", "content": prompt})
    post_conversation("candidate", prompt)
    
    with st.spinner("Analyzing your response..."):
        ai_response = get_interview_response(
            st.session_state.resume_text,
            st.session_state.chat_history
        )
        st.session_state.chat_history.append({
            "role": "assistant",
            "content": ai_response
        })
        post_conversation("assistant", ai_response)
    st.rerun()

def reset_session():
    """Clean reset of session state"""
    keys_to_keep = ['db', 'gemini']  # Preserve connections
    for key in list(st.session_state.keys()):
        if key not in keys_to_keep:
            del st.session_state[key]

def post_conversation(role, content):
    """Enhanced MongoDB posting with retries"""
    try:
        if "db" not in st.session_state:
            st.session_state.db = MongoConnector()
        document = {
            'chat_id': st.session_state.chat_id,
            'session_id': st.session_state.session_id,
            'role': role,
            'content': content,
            'timestamp': time.time(),
            'order': st.session_state.chat_length
        }
        
        st.session_state.db.create_document('conversations', document)
        st.session_state.chat_length += 1
    except Exception as e:
        logger.error(f'MongoDB Error: {str(e)}')
        st.toast("⚠️ Failed to save conversation progress", icon="⚠️")

if __name__ == "__main__":
    interview()