import logging
import random
import uuid
import streamlit as st
from streamlit_extras.colored_header import colored_header
from streamlit_extras.app_logo import add_logo
from connectors.aws_connector import S3Connector
from src.home_page import home_page
from myUtils.file_utils import load_file

from src.resume_score_page import resume_score
from src.job_relevant_score_page import job_relevant_score

from streamlit_extras.mention import mention
from streamlit_extras.bottom_container import bottom
from src.interview_page import interview
from models.gemini_model import GeminiModel
import os
from dotenv import load_dotenv
from connectors.mongo_connector import MongoConnector

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")
logger = logging.getLogger("Main Application")
# Load environment variables
load_dotenv()

@st.cache_resource
def get_mongo_connector():
    return MongoConnector()

@st.cache_resource
def get_model():
    return GeminiModel()

@st.cache_resource
def get_aws_s3():
    return S3Connector()

@st.cache_data
def load_all_files():
    return {
        "scoring": load_file("./rules/_scoring.txt"),
        "scoring_system": load_file("./rules/_scoring_system.txt"),
        "grammar_spelling": load_file("./rules/_grammar_spelling.txt"),
        "structure": load_file("./rules/_structure.txt"),
        "action_verbs": load_file("./rules/_action_verbs.txt"),
        "quantifiable": load_file("./rules/_quantifiable.txt"),
    }

# Page mapping
PAGES = {
    "🌟 Home": home_page,
    "💡 Resume Score": resume_score,
    "🔎 Job Description Relevant Score": job_relevant_score,
    "🤖 Interview Page": interview
}

def main():
    if 'session_id' not in st.session_state:
        st.session_state.session_id = str(uuid.uuid4()) 
    
    if 'rules' not in st.session_state:
        st.session_state.rules = load_all_files()
    # Initialize session state for models and database
    if "gemini" not in st.session_state:
        st.session_state.gemini = get_model()
    
    if "db" not in st.session_state:
        # Store the MongoDB connector getter function in session state
        st.session_state.db = get_mongo_connector()
    
    if "aws_s3" not in st.session_state:
        st.session_state.aws_s3 = get_aws_s3()
    
    st.sidebar.image("./assets/logo-xx-small.png")
    with st.sidebar:
        colored_header(
            label="AI Resume Scorer 🚀",
            description="Optimize Your Resume for Better Job Matches",
            color_name="blue-70",
        )

    page_key = st.sidebar.selectbox(
        "Let's go ✨",
        options=list(PAGES.keys())
    )

    page_func = PAGES.get(page_key)
    if page_func:
        try:
            page_funca()  # The pages can access models and DB from session_state
            st.divider()
            st.sidebar.info("Check out the Repository")
            mention(
                label="AiRS",
                icon="github",
                url="https://github.com/akash-masadi",
            )
        except Exception as e:
            error_handler(e)

def error_handler(e):
    logger.error(f"Error in Application: {e}")
    # List of funny error messages and relevant Giphy URLs
    error_data = [
        ("Oops! Our hamsters ran out of energy. Recharging… 🔋⚡",
        "https://media2.giphy.com/media/v1.Y2lkPTc5MGI3NjExNzh1N3Z6YWlvZHpyM2poZm82Zm9yMjM4dTVxdDh0dGtxN2lmMXgxbSZlcD12MV9pbnRlcm5hbF9naWZfYnlfaWQmY3Q9Zw/dhW1mROBRyDCcUWudr/giphy.gif"),  # Hamster collapsing on wheel

        ("Oh no! The code just faceplanted. Let’s pick it back up! 🤕",
        "https://media1.giphy.com/media/v1.Y2lkPTc5MGI3NjExM25yb2R1b2lnMXIzamx0ZTd6N3BneXVpMG53bW8xbnRxbGY0YXZiZiZlcD12MV9pbnRlcm5hbF9naWZfYnlfaWQmY3Q9Zw/cuPm4p4pClZVC/giphy.gif"),  #   

        ("Something went wrong… but hey, at least it’s not your Wi-Fi this time! 📶😂",
        "https://media3.giphy.com/media/v1.Y2lkPTc5MGI3NjExcXQ0MTE1bGYxdjlrYXo1d3RqbnF1c2RlYXg2NWJ0NWpndTcxOXZ5NyZlcD12MV9pbnRlcm5hbF9naWZfYnlfaWQmY3Q9Zw/Z5hrt4cB4A0SZqHyBH/giphy.gif"),  # Exploding router

        ("Beep boop. System confused. Please try again later! 🤖",
        "https://media4.giphy.com/media/v1.Y2lkPTc5MGI3NjExY3QzdTBnOWZvdXp3cnhqMHBxanFrMzhvdXo3a3N5eGh5MnIweTh2dyZlcD12MV9pbnRlcm5hbF9naWZfYnlfaWQmY3Q9Zw/dcH2frRmMJl0cUmCyX/giphy.gif"),  # Robot with question marks

        ("Looks like our app stepped on a LEGO. It hurts! 🦶😖",
        "https://media0.giphy.com/media/v1.Y2lkPTc5MGI3NjExZ3BzbHdnZHl4OTV3dGd4Y2ZtcDgycTR3OGw3ZGx1emJ6dHZnajhtdCZlcD12MV9pbnRlcm5hbF9naWZfYnlfaWQmY3Q9Zw/6o4OBxgrZpmgv1MDfh/giphy.gif"),  # Animated foot on LEGO

        ("Hold on… our servers just did a backflip and landed badly. 🏃‍♂️💨",
        "https://media0.giphy.com/media/v1.Y2lkPTc5MGI3NjExbHEzMHdhYzhmeGE4aWZkcjhocGp3cTd3d3F3djFsNjI1MDFiOXV1MSZlcD12MV9pbnRlcm5hbF9naWZfYnlfaWQmY3Q9Zw/6jwmW6T8uoldPYQnzb/giphy.gif"),  # Falling server rack

        ("We asked AI to fix this, but it started questioning existence instead. 🤯",
        "https://media0.giphy.com/media/v1.Y2lkPTc5MGI3NjExdnd6Z204ZjVtOXZhcGRsM2w0bnA5a25jY2QzMGowZnB3cTNkcXBidyZlcD12MV9pbnRlcm5hbF9naWZfYnlfaWQmY3Q9Zw/fZV4GZCjBOwPLz6jrk/giphy.gif"),  # Robot staring at stars

        ("Our developer spilled coffee on the code again. ☕💻",
        "https://media2.giphy.com/media/v1.Y2lkPTc5MGI3NjExaTlrNjQyN2V3Z2c1dmwwbXduMmMxYTZpM29xNnJleHE1eDlueG10bSZlcD12MV9pbnRlcm5hbF9naWZfYnlfaWQmY3Q9Zw/78XCFBGOlS6keY1Bil/giphy.gif"),  # Coffee flooding keyboard

        ("Welp, that’s awkward… even computers have bad days. 😅",
        "https://media1.giphy.com/media/v1.Y2lkPTc5MGI3NjExd3gxc2preTRieWM3bmMzMzM1aWV2MnlzOWU1Y2R2NXFkaDU4eDFodCZlcD12MV9pbnRlcm5hbF9naWZfYnlfaWQmY3Q9Zw/Qt1jk5Q49C3h5CrlBe/giphy.gif"),  # Laptop crying tears

        ("System crash… sending virtual hugs to recover! 🤗",
        "https://media0.giphy.com/media/v1.Y2lkPTc5MGI3NjExNjB3eHI5NWN1dmc3a2pqcHA3dXUzMDJ2M3hxbXh1c24yNTVnY3FmdCZlcD12MV9pbnRlcm5hbF9naWZfYnlfaWQmY3Q9Zw/T1juuTweNyFKhA8YOK/giphy.gif"),  # Penguins hugging

        ("The matrix glitched… take the blue pill and try again. 💊🌀",
        "https://media3.giphy.com/media/v1.Y2lkPTc5MGI3NjExdmczZTA3bXlqZGVqdDkybHMza2lnd2pudXRrdTl0OXF4bjVmdXE5MiZlcD12MV9pbnRlcm5hbF9naWZfYnlfaWQmY3Q9Zw/qaDbEDavgvKBs5jJc5/giphy.gif")  # Digital glitch effect
    ]
    # Randomly select an error message and corresponding Giphy
    error_message, giphy_url = random.choice(error_data)

    # Center everything using HTML & CSS
    st.markdown(
        """
        <style>
            .centered {
                display:flex;
                justify-content: center;
                align-items:center;
                text-align: center;
            }
            .retry-button {
                display: flex;
                justify-content: center;
            }
        </style>
        """, unsafe_allow_html=True
    )

    # Display error message and GIF in the center
    st.markdown('<div class="centered">', unsafe_allow_html=True)
    st.image(giphy_url, width=300)  # Display random error GIF
    st.error(error_message)  # Show error message
    st.markdown('</div>', unsafe_allow_html=True)

    # Centered retry button that clears the page
    if st.button("🔄 Try Again"):
        st.rerun()  # Refresh the app
        
if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        error_handler(e)