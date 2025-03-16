from dotenv import load_dotenv
import streamlit as st
import google.generativeai as genai
import os
import tempfile
from myUtils import extract_text
from myUtils.s3_mongodb import upload_pdf_to_s3_and_mongodb

load_dotenv()

genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))
model = genai.GenerativeModel(model_name='gemini-2.0-flash')

def get_interview_response(resume_text, chat_history):
    # Format conversation history
    convo = []
    for msg in chat_history:
        role = "Interviewer" if msg["role"] == "assistant" else "Candidate"
        convo.append(f"{role}: {msg['content']}")
    conversation_text = "\n".join(convo)
    
    # Construct structured prompt
    prompt = f"""You are a professional interviewer conducting a technical interview. Follow these steps:
    1. Analyze the candidate's resume and conversation history
    2. Evaluate their last response (highlight strengths/weaknesses)
    3. Ask a follow-up question that:
       - Is more challenging than previous questions
       - Covers different skills/experiences from their resume
       - Progresses the interview naturally
    
    Resume:
    {resume_text}
    
    Conversation:
    {conversation_text}
    
    Format your response:
    [Evaluation] ... 
    [Question] ..."""
    
    response = model.generate_content(prompt)
    return response.text

def interview():
    st.title("AI Interviewer 🎙️")
    uploaded_file = st.file_uploader("Upload your resume", type=["pdf", "txt"])
    
    # Session state management
    if 'interview_started' not in st.session_state:
        st.session_state.interview_started = False
    if 'chat_history' not in st.session_state:
        st.session_state.chat_history = []
    
    col = st.columns(5)
    with col[0]:
        if st.button("Evaluate") and uploaded_file:
            # Process resume
            if uploaded_file.type == "application/pdf":
                with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
                    tmp.write(uploaded_file.read())
                    resume_text = extract_text(tmp.name)
                    upload_pdf_to_s3_and_mongodb(uploaded_file,tmp.name,"interviewer")
            else:
                resume_text = uploaded_file.read().decode()
            
            st.session_state.resume_text = resume_text
            st.session_state.interview_started = True
            
            # Generate first question
            first_prompt = f"""Generate an opening interview question asking for self-introduction 
                            considering this resume: {resume_text}"""
            first_response = model.generate_content(first_prompt)
            st.session_state.chat_history.append({
                "role": "assistant",
                "content": first_response.text
            })
    
    with col[4]:
        if st.button("Close Interview"):
            st.session_state.clear()
            st.rerun()
    
    # Interview interface
    if st.session_state.interview_started:
        st.subheader("Interview Session")
        
        # Display chat history
        for msg in st.session_state.chat_history:
            with st.chat_message(msg["role"]):
                st.markdown(msg["content"])
        
        # User input handling
        if user_input := st.chat_input("Type your answer..."):
            st.session_state.chat_history.append({
                "role": "user",
                "content": user_input
            })
            
            # Generate AI response
            ai_response = get_interview_response(
                st.session_state.resume_text,
                st.session_state.chat_history
            )
            st.session_state.chat_history.append({
                "role": "assistant",
                "content": ai_response
            })
            st.rerun()

if __name__ == "__main__":
    interview()