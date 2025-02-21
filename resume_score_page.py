import os
import tempfile
import pandas as pd
import altair as alt
import streamlit as st
from dotenv import load_dotenv
from myUtils import extract_and_remove_component_scores, load_file, extract_text, stream_gen
from streamlit_extras.streaming_write import write

import logging
# Configure logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")
logger = logging.getLogger("Resume Scorer")


load_dotenv()

def get_gemini_response(chat, resume_data):
    """Generate response using Gemini AI."""
    if "rules" in st.session_state:
        scoring = st.session_state.rules['scoring']
        scoring_system = st.session_state.rules['scoring_system']
        response = chat.send_message(f"{scoring}\n\n Resume:\n ${resume_data}")
        gen_score = chat.send_message(f"{scoring_system}\nResume:\n{resume_data}")
        return response, gen_score

def plot_scores(st, score_dict):
    """Visualize scores using Altair charts."""
    df = pd.DataFrame({
        'Components': list(score_dict.keys()),
        'Scores': list(score_dict.values())
    })

    bar_chart = alt.Chart(df).mark_bar().encode(
        x=alt.X('Scores:Q', title='Scores'),
        y=alt.Y('Components:O', title='Components', sort='-x'),
        tooltip=['Components', 'Scores']
    ).properties(
        width=600,
        height=400,
        title='Resume Component Scores'
    )

    pie_chart = alt.Chart(df).mark_arc().encode(
        color=alt.Color('Components:N', legend=None),
        tooltip=['Components', 'Scores'],
        theta='Scores:Q',
        radius=alt.Radius(),
    ).properties(
        width=400,
        height=400,
        title='Total Score Breakdown'
    )

    st.subheader("Total Score vs. Overall Score")
    st.altair_chart(pie_chart, use_container_width=True)
    st.subheader("Resume Component Scores")
    st.altair_chart(bar_chart, use_container_width=True)

def save_to_mongodb(db, resume_data, response_text, score_dict):
    """Store extracted resume data and AI response in MongoDB."""
  
    document = {
        "resume_text": resume_data,
        "ai_response": response_text,
        "scores": score_dict,
    }
    
    newDocument = st.session_state.gemini.get_applicant_details(document)
    
    db.create_document("resumes", newDocument)

def resume_score():
    """Main function to process resume analysis."""
    session_state = st.session_state
    if "db" not in session_state or "gemini" not in session_state:
        st.error("Database or AI Model not initialized in session_state!")
        return

    db = session_state.db
    chat = session_state.gemini.model.start_chat(history=[]) 

    uploaded_file = st.file_uploader("Upload your resume", type=["pdf", "txt"])
    submit = st.button("Evaluate Resume")

    if uploaded_file and submit:
        with st.spinner('Processing resume...'):
            temp_file_path = ""
            if uploaded_file.type == "application/pdf":
                with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as temp_file:
                    temp_file.write(uploaded_file.read())
                    temp_file_path = temp_file.name
                extracted_text = extract_text(temp_file_path)
            else:
                extracted_text = uploaded_file.read().decode("utf-8")
        
            response, gen_score = get_gemini_response(chat, extracted_text)
            gen_score_text, score_dict = extract_and_remove_component_scores(gen_score.candidates[0].content.parts[0].text)
            save_to_mongodb(db, extracted_text, gen_score_text, gen_score)
            
            try:
                if score_dict.get('components'):
                    plot_scores(st, score_dict["components"])
            except Exception as e:
                st.error(f"Error plotting scores: {e}")
            
            if hasattr(response, 'candidates'):
                content = response.candidates[0].content.parts[0].text
                write(stream_gen(content))
            else:
                st.error("Unexpected response structure")

if __name__ == "__main__":
    st.title("Resume Evaluation 🪄")
    resume_score()
