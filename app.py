import streamlit as st
from streamlit_extras.colored_header import colored_header
from streamlit_extras.app_logo import add_logo
from home_page import home_page
from resume_score_page import resume_score
from job_relevant_score_page import job_relevant_score
from streamlit_extras.mention import mention
from streamlit_extras.bottom_container import bottom

PAGES = {
    "🌟 Home": home_page,
    "💡 Resume Score": resume_score,
    "🔎 Job Description Relevant Score": job_relevant_score,
}

def main():
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
        page_func()

    with st.sidebar:
        st.divider()
        st.sidebar.info("Check out the Respository")
        mention(
            label="AiRS",
            icon="github",
            url="https://github.com/akash-masadi",
        )

if __name__ == "__main__":
    main()
