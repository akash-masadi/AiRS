from dotenv import load_dotenv
import streamlit as st
import google.generativeai as genai
from streamlit_extras.colored_header import colored_header
from streamlit_extras.app_logo import add_logo
from myUtils.file_utils import load_file
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
    while level < 100:
        time.sleep(0.05)  # Increased delay for better visibility
        level += 1
        progress_bar.progress(level)
    return text, progress_bar

def remove_loading_animation(text, progress_bar):
    # Remove loading elements after completion
    text.empty()
    progress_bar.empty()

@st.cache_data
def request_intro():
    # Before requesting intro, start loading animation
    text, progress_bar = loading_animation()
    intro_text = load_file("./rules/_intro_to_airs.txt")
    intro = model.generate_content(intro_text)
    # Removing loading animations
    remove_loading_animation(text, progress_bar)
    return intro.candidates[0].content.parts[0].text

# Main page content
def home_page():
    add_logo("./assets/logo-main.png")
    st.image("./assets/logo-main.png", width=100)
    colored_header(
        label="AiRS",
        description="Optimize Your Resume for Better Job Matches",
        color_name="blue-70",
    )
    intro = request_intro()
    st.write(intro)
    st.image("./assets/home_page.jpeg", caption='AI Resume Scoring', use_column_width=True)

# Initial app setup
st.set_page_config(page_title="AiRS", page_icon=":material/edit:")

if __name__ == "__main__":
    # Page navigations
    AiRS = st.Page("app.py",title="AiRS",icon=":material/star:")
    resume_score_page = st.Page("resume_score_page.py", title="Resume Score", icon=":material/add_circle:")
    job_relevant_score = st.Page("job_relevant_score.py", title="Job Description Relevant Score", icon=":material/delete:")
    pg = st.navigation([AiRS,resume_score_page, job_relevant_score])
    home_page()
    pg.run()
    st.sidebar.title("Follow us on")
    st.sidebar.write("Social Media Links Here")
