import streamlit as st
from streamlit_extras.colored_header import colored_header
from streamlit_extras.app_logo import add_logo
from home_page import home_page
from myUtils.file_utils import load_file
from resume_score_page import resume_score
from job_relevant_score_page import job_relevant_score
from streamlit_extras.mention import mention
from streamlit_extras.bottom_container import bottom
from interview_page import interview
from models.gemini_model import GeminiModel
import os
from dotenv import load_dotenv
from connectors.mongo_connector import MongoConnector

# Load environment variables
load_dotenv()

@st.cache_resource
def get_mongo_connector():
    return MongoConnector()

@st.cache_resource
def get_model():
    return GeminiModel()

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
    if 'rules' not in st.session_state:
        st.session_state.rules = load_all_files()
    # Initialize session state for models and database
    if "gemini" not in st.session_state:
        st.session_state.gemini = get_model()
    
    if "db" not in st.session_state:
        # Store the MongoDB connector getter function in session state
        st.session_state.db = get_mongo_connector()
    
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
        page_func()  # The pages can access models and DB from session_state

    # Add MongoDB connection status to sidebar
    with st.sidebar:
        st.divider()
        
        # Add MongoDB connection status indicator
        if st.sidebar.checkbox("Show Database Status"):
            try:
                # Test connection by getting a ping
                mongo = st.session_state.db()
                mongo.client.admin.command('ping')
                st.sidebar.success("✅ Connected to MongoDB")
                
                # Show database stats if connected
                collections = mongo.db.list_collection_names()
                st.sidebar.write(f"Collections: {', '.join(collections) if collections else 'None'}")
            except Exception as e:
                st.sidebar.error(f"❌ Database Connection Error: {str(e)}")
        
        st.divider()
        st.sidebar.info("Check out the Repository")
        mention(
            label="AiRS",
            icon="github",
            url="https://github.com/akash-masadi",
        )

if __name__ == "__main__":
    main()