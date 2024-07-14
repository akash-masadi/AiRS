import streamlit as st
from streamlit_extras.colored_header import colored_header
from streamlit_extras.app_logo import add_logo
from home_page import home_page
from resume_score_page import resume_score
from job_relevant_score_page import job_relevant_score

# Page dictionary for navigation
PAGES = {
    "Home": home_page,
    "Resume Score": resume_score,
    "Job Description Relevant Score": job_relevant_score,
}

def main():
    st.sidebar.image("./assets/logo-xx-small.png")
    with st.sidebar:
        colored_header(
            label="AI Resume Scorer",
            description="Optimize Your Resume for Better Job Matches",
            color_name="blue-70",
        )
    # Use selectbox for page selection
    page_key = st.sidebar.selectbox(
        "",
        options=list(PAGES.keys())
    )

    page_func = PAGES.get(page_key)
    if page_func:
        page_func()

    st.sidebar.title("Follow us on")
    st.sidebar.write("Social Media Links Here")

if __name__ == "__main__":
    main()
