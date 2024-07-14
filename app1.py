from dotenv import load_dotenv
import streamlit as st
import streamlit_extras as ste
import google.generativeai as genai
from streamlit_extras.colored_header import colored_header
from streamlit_extras.app_logo import add_logo
from streamlit_extras.let_it_rain import rain
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
    st.text("Loading...")
    progress_bar = st.progress(0)
    for i in range(100):
        time.sleep(0.01)
        progress_bar.progress(i + 1)

# Main page content
def home_page():
    add_logo("./assets/logo-main.png")
    st.image(r".\assets\logo-main.png", width=100)
    colored_header(
        label="AiRS",
        description="Optimize Your Resume for Better Job Matches",
        color_name="blue-70",
    )
    # rain(
    #     emoji="✨",
    #     font_size=30,
    #     falling_speed=8,
    #     animation_length="2",
    # )
    loading_animation()

    st.write("""
    AI-Resume Scorer helps you enhance your resume by providing detailed feedback and scoring based on relevance to job descriptions.
    Our advanced algorithms analyze your resume to ensure you stand out to potential employers.
    """)

    st.image(r"C:\myStuff\ML project\ATS\demo\assets\home_page.jpeg", caption='AI Resume Scoring', use_column_width=True)

    if st.button("Resume Score"):
        resume_score_page()
    if st.button("Job Description Relevant Score"):
        job_description_score_page()

# Resume Score page
def resume_score_page():
    global st, chat
    st.title("Resume Score")
    resume_score(st)

# Job Description Relevant Score page
def job_description_score_page():
    st.title("Job Description Relevant Score")
    st.write("This page will contain the functionality for scoring job descriptions.")
    # Add your functionality here

# Sidebar navigation
with st.sidebar:
    st.title("AiRS")
    # st.link_button("Resume Score",'./pages/resume_score_page.py')
    # if page == "Home":
    #     home_page()
    # elif page == "Resume Score":
    #     resume_score_page()
    # elif page == "Job Description Relevant Score":
    #     job_description_score_page()
home_page()
st.sidebar.title("Follow us on")
st.sidebar.write("Social Media Links Here")


'''
mention(
        label="streamlit-extras",
        icon="🪢",  # You can also just use an emoji
        url="https://github.com/arnaudmiribel/streamlit-extras",
    )

from streamlit_extras.switch_page_button import switch_page
def example():
    want_to_contribute = st.button("I want to contribute!")
    if want_to_contribute:
        switch_page("Contribute")
'''
