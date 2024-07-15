from dotenv import load_dotenv
import streamlit as st
import google.generativeai as genai
from streamlit_extras.colored_header import colored_header
from streamlit_extras.app_logo import add_logo
from myUtils.file_utils import load_file
from streamlit_extras.streaming_write import write
from myUtils import stream_gen
import os
import time

load_dotenv()

genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

model = genai.GenerativeModel(model_name='gemini-1.5-flash')
chat = model.start_chat(history=[])

def loading_animation():
    text = st.text("Loading...")
    progress_bar = st.progress(0)
    level = 0
    while level < 100:
        time.sleep(0.05)
        level += 1
        progress_bar.progress(level)
    return text, progress_bar

def remove_loading_animation(text, progress_bar):
    text.empty()
    progress_bar.empty()

# @st.cache_data
def loading_intro():
    text, progress_bar = loading_animation()
    intro_text = load_file("./rules/_intro_to_airs.txt")
    intro = model.generate_content(intro_text)
    remove_loading_animation(text, progress_bar)
    return intro.candidates[0].content.parts[0].text

def home_page():
    add_logo("./assets/logo-main.png")
    st.image("./assets/logo-main.png", width=100)
    colored_header(
        label="AiRS",
        description="Optimize Your Resume for Better Job Matches",
        color_name="blue-70",
    )
    intro = loading_intro()
    write(stream_gen(intro))
    st.image("./assets/home_page.jpeg", caption='AI Resume Scoring', use_column_width=True)

if __name__ == "__main__":
    home_page()
