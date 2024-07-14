from dotenv import load_dotenv
import streamlit as st
import streamlit_extras as ste
import google.generativeai as genai
from streamlit_extras.colored_header import colored_header
from streamlit_extras.app_logo import add_logo
from streamlit_extras.let_it_rain import rain
from myUtils.file_utils import load_file
from pages.resume_score_page import resume_score
import os
import time

# Load environment variables
load_dotenv()

# Configure Generative AI with API key from environment variable
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

# Initialize the generative model
model = genai.GenerativeModel(model_name='gemini-1.5-flash')
chat = model.start_chat(history=[])

# Function to simulate loading animation
def loading_animation():
    text = st.text("Loading...")
    progress_bar = st.progress(0)
    level = 0
    while(level<100):
        time.sleep(0.01)
        level=level+1
        progress_bar.progress(level)
    # Remove loading elements after completion
    return text,progress_bar
def remove_loading_animation(text,progress_bar):
    text.empty()
    progress_bar.empty()

# Main page content
def home_page():
    add_logo("./assets/logo-main.png")
    st.image("./assets/logo-main.png", width=100)
    colored_header(
        label="AiRS",
        description="Optimize Your Resume for Better Job Matches",
        color_name="blue-70",
    )
    text,progress_bar=loading_animation()
    intro = load_file("./rules/_intro_to_airs.txt")

    intro = model.generate_content(intro) 
    #removing loading animations
    remove_loading_animation(text,progress_bar)
    intro = intro.candidates[0].content.parts[0].text
    st.write(intro)
    st.image("./assets/home_page.jpeg", caption='AI Resume Scoring', use_column_width=True)

    if st.sidebar.button("Home"):
        home_page()
    if st.sidebar.button("Resume Score"):
        resume_score_page()
    if st.sidebar.button("Job Description Relevant Score"):
        job_description_score_page()

# Resume Score page
def resume_score_page():
    st.title("Resume Score")
    resume_score(st)

# Job Description Relevant Score page
def job_description_score_page():
    st.title("Job Description Relevant Score")
    st.write("This page will contain the functionality for scoring job descriptions.")
    # Add your functionality here

# Initial app setup
if __name__ == "__main__":
    home_page()
    st.sidebar.title("Follow us on")
    st.sidebar.write("Social Media Links Here")
