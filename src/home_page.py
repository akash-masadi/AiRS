# home_page.py
import streamlit as st
from streamlit_extras.colored_header import colored_header
from streamlit_extras.app_logo import add_logo
from streamlit_extras.streaming_write import write
from myUtils.file_utils import load_file
from myUtils import stream_gen
import time
from streamlit_lottie import st_lottie
import json
import requests
import os
from streamlit_card import card

# Cache the lottie animations and file loading for performance
# @st.cache_data
def load_lottie(url: str):
    """Load Lottie animation from URL with fallback to local file"""
    try:
        r = requests.get(url)
        if r.status_code == 200:
            return r.json()
    except Exception:
        pass
    
    # Fallback to local file
    try:
        with open("./assets/resume_lottie.json", "r") as file:
            return json.load(file)
    except Exception:
        return None

# @st.cache_data
def get_sample_resumes():
    """
    Get sample resumes with S3 URLs
    This would typically load from a database or config file
    """
    # Example data structure - replace with your actual data source
    return [
        {
            "person_name": "John Smith",
            "industry": "Technology",
            "role": "Software Engineer",
            "rating": 4.8,
            "pdf_url": "https://airs-main.s3.us-east-1.amazonaws.com/ATS+classic+HR+resume.pdf"
        },
        {
            "person_name": "Sarah Johnson",
            "industry": "Healthcare",
            "role": "Registered Nurse",
            "rating": 4.7,
            "pdf_url": "https://airs-main.s3.us-east-1.amazonaws.com/ATS+classic+HR+resume.pdf"
        },
        {
            "person_name": "Michael Chen",
            "industry": "Finance",
            "role": "Financial Analyst",
            "rating": 4.9,
            "pdf_url": "https://airs-main.s3.us-east-1.amazonaws.com/ATS+classic+HR+resume.pdf"
        },
        {
            "person_name": "Jessica Williams",
            "industry": "Marketing",
            "role": "Digital Marketing Specialist",
            "rating": 4.5,
            "pdf_url": "https://airs-main.s3.us-east-1.amazonaws.com/ATS+classic+HR+resume.pdf"
        },
        {
            "person_name": "David Rodriguez",
            "industry": "Education",
            "role": "High School Teacher",
            "rating": 4.5,
            "pdf_url": "https://airs-main.s3.us-east-1.amazonaws.com/ATS+classic+HR+resume.pdf"
        },
        {
            "person_name": "Amanda Park",
            "industry": "Technology",
            "role": "UX Designer",
            "rating": 4.8,
            "pdf_url": "https://airs-main.s3.us-east-1.amazonaws.com/ATS+classic+HR+resume.pdf"
        },
        {
            "person_name": "Robert Kim",
            "industry": "Finance",
            "role": "Investment Banker",
            "rating": 4.7,
            "pdf_url": "https://airs-main.s3.us-east-1.amazonaws.com/ATS+classic+HR+resume.pdf"
        },
        {
            "person_name": "Emily Garcia",
            "industry": "Healthcare",
            "role": "Physician Assistant",
            "rating": 4.9,
            "pdf_url": "https://airs-main.s3.us-east-1.amazonaws.com/ATS+classic+HR+resume.pdf"
        }
    ]

def loading_animation():
    """Display loading animation with progress bar"""
    with st.spinner("Processing..."):
        text = st.text("Loading...")
        progress_bar = st.progress(0)
        level = 0
        while level < 100:
            time.sleep(0.01)  # Reduced sleep time for faster loading
            level += 5  # Increased step size
            progress_bar.progress(level)
    return text, progress_bar

def remove_loading_animation(text, progress_bar):
    """Remove loading animation elements"""
    text.empty()
    progress_bar.empty()

# @st.cache_data(ttl=3600)  # Cache for 1 hour
def loading_intro():
    """Load introduction text using shared model instance"""
    intro_text = load_file("./rules/_intro_to_airs.txt")
    
    # Check if the model exists in session state
    if "gemini" in st.session_state and st.session_state.gemini:
        intro = st.session_state.gemini.model.generate_content(intro_text)
        
        # Ensure the response structure is valid
        if intro and hasattr(intro, "candidates") and intro.candidates:
            return intro.candidates[0].content.parts[0].text
        else:
            return "Welcome to AiRS - AI Resume Scorer! Our platform helps you optimize your resume for better job matches using advanced AI analysis."
    else:
        return "Welcome to AiRS - AI Resume Scorer! Our platform helps you optimize your resume for better job matches using advanced AI analysis."

# @st.cache_data(ttl=3600)  # Cache for 1 hour
def get_resume_tips(category):
    """Get resume tips for different categories"""
    try:
        prompt = f"Provide 5 concise, actionable tips for creating an effective resume {category}. Format as bullet points."
        response = st.session_state.gemini.model.generate_content(prompt)
        return response.candidates[0].content.parts[0].text
    except Exception:
        # Fallback content if model fails
        return """
        * Keep your resume concise and focused on relevant experience
        * Use action verbs and quantify achievements when possible
        * Tailor your resume for each job application
        * Ensure consistent formatting throughout the document
        * Proofread carefully to eliminate errors and typos
        """

# @st.cache_data(ttl=3600)  # Cache for 1 hour
def get_industry_specific_tips(industry):
    """Get industry-specific resume tips"""
    try:
        prompt = f"Provide 5 specific resume tips for job seekers in the {industry} industry. Include industry-specific keywords and skills that should be highlighted."
        response = st.session_state.gemini.model.generate_content(prompt)
        return response.candidates[0].content.parts[0].text
    except Exception:
        # Fallback content
        return f"""
        * Research and include {industry}-specific keywords throughout your resume
        * Highlight certifications and specialized training relevant to {industry}
        * Showcase projects and achievements that demonstrate industry knowledge
        * Include metrics and results that matter in the {industry} field
        * Tailor your skills section to match job descriptions in {industry}
        """

# @st.cache_data(ttl=3600)  # Cache for 1 hour
def get_recent_trends():
    """Get recent trends in resume design and formatting"""
    try:
        prompt = "What are the 5 most recent trends in resume design and formatting for 2025? Provide brief explanations of each trend."
        response = st.session_state.gemini.model.generate_content(prompt)
        return response.candidates[0].content.parts[0].text
    except Exception:
        # Fallback content
        return """
        * **AI-Optimized Formats** - Designs specifically structured to pass ATS systems
        * **Interactive Elements** - QR codes linking to portfolios and work samples
        * **Skills Visualization** - Visual representation of skill proficiency levels
        * **Micro-Credentials Display** - Highlighting specialized mini-certifications
        * **Sustainability Section** - Showcasing environmental and social impact contributions
        """

def home_page():
    # Page setup
    add_logo("./assets/logo-main.png")
    
    # Top section with logo and header
    col1, col2 = st.columns([1, 3])
    with col1:
        st.image("./assets/logo-main.png", width=100)
    with col2:
        colored_header(
            label="AiRS - AI Resume Scorer",
            description="Optimize Your Resume for Better Job Matches",
            color_name="blue-70",
        )
    
    # Main sections using tabs
    tab1, tab2, tab3 = st.tabs(["📚 About AiRS", "🧠 Resume Tips", "📄 Sample Resumes"])
    
    # Tab 1: About AiRS
    with tab1:
        col1, col2 = st.columns([3, 2])
        with col1:
            with st.spinner("Loading content..."):
                intro = loading_intro()
                write(stream_gen(intro))
        with col2:
            with st.spinner("Loading animation..."):
                lottie_resume = load_lottie("https://assets6.lottiefiles.com/packages/lf20_bpqri9h8.json")
                if lottie_resume:
                    st_lottie(lottie_resume, height=300, key="resume_animation")
                else:
                    st.image("./assets/home_page.jpeg", caption='AI Resume Scoring', use_column_width=True)
        
        # Quick start guide
        st.divider()
        st.subheader("📌 Quick Start Guide")
        col1, col2, col3 = st.columns(3)
        with col1:
            st.info("**Step 1**: Upload your resume in the 'Resume Score' tab")
        with col2:
            st.info("**Step 2**: Get detailed feedback and improvement suggestions")
        with col3:
            st.info("**Step 3**: Upload a job description to check relevance score")
    
    # Tab 2: Resume Tips with nested tabs
    with tab2:
        tip_tabs = st.tabs([
            "General Tips", 
            "Content Structure", 
            "Keywords & ATS", 
            "Industry-Specific", 
            "2025 Trends"
        ])
        
        # General Tips tab
        with tip_tabs[0]:
            st.markdown("### 📝 General Resume Best Practices")
            with st.spinner("Loading tips..."):
                tips = get_resume_tips("focusing on general best practices")
                st.markdown(tips)
            
            # Interactive checklist
            st.divider()
            st.subheader("Resume Self-Check")
            col1, col2 = st.columns(2)
            with col1:
                st.checkbox("Clear, professional font (Arial, Calibri, etc.)")
                st.checkbox("Contact information is complete and current")
                st.checkbox("No grammatical or spelling errors")
                st.checkbox("Consistent formatting throughout")
            with col2:
                st.checkbox("Appropriate length (1-2 pages)")
                st.checkbox("Quantifiable achievements included")
                st.checkbox("Education section up-to-date")
                st.checkbox("PDF format for submission")
        
        # Content Structure tab
        with tip_tabs[1]:
            st.markdown("### 🏗️ Content Structure and Organization")
            with st.spinner("Loading tips..."):
                tips = get_resume_tips("focusing on content structure and organization")
                st.markdown(tips)
            
            # Sample structure
            st.divider()
            st.subheader("Recommended Resume Structure")
            expander = st.expander("View Recommended Structure")
            with expander:
                st.markdown("""
                1. **Header** - Name and contact information
                2. **Professional Summary** - 2-3 sentence overview
                3. **Skills** - Technical and soft skills relevant to position
                4. **Work Experience** - Most recent first with accomplishments
                5. **Education** - Degrees, certifications, relevant coursework
                6. **Additional Sections** - Projects, volunteer work, languages
                """)
        
        # Keywords & ATS tab
        with tip_tabs[2]:
            st.markdown("### 🔍 Keywords and ATS Optimization")
            with st.spinner("Loading tips..."):
                tips = get_resume_tips("for passing Applicant Tracking Systems (ATS)")
                st.markdown(tips)
            
            # Keyword extractor tool teaser
            st.divider()
            st.subheader("Try Our Keyword Extractor")
            st.info("Upload a job description in the 'Job Description Relevant Score' tab to extract key skills and keywords for your resume.")
        
        # Industry-Specific tab
        with tip_tabs[3]:
            st.markdown("### 🏢 Industry-Specific Resume Tips")
            industries = ["Technology", "Healthcare", "Finance", "Marketing", "Education"]
            selected_industry = st.selectbox("Select your industry", industries)
            with st.spinner(f"Loading {selected_industry} tips..."):
                industry_tips = get_industry_specific_tips(selected_industry)
                st.markdown(industry_tips)
        
        # 2025 Trends tab
        with tip_tabs[4]:
            st.markdown("### 🚀 Resume Trends for 2025")
            with st.spinner("Loading trends..."):
                trends = get_recent_trends()
                st.markdown(trends)
    
    # Tab 3: Sample Resumes (S3 URL implementation)
    with tab3:
        st.markdown("### 📄 Sample Optimized Resumes")
        st.markdown("Browse through our collection of ATS-optimized sample resumes across different industries. Click any card to open the resume in a new tab.")
        
        # Custom CSS for cards
        st.markdown("""
        <style>
        .resume-card {
            border: 1px solid #e0e0e0;
            border-radius: 10px;
            padding: 20px;
            margin : 10px;
            background-color: white;
            box-shadow: 0 4px 8px rgba(0,0,0,0.05);
            transition: all 0.3s ease;
            height: 100%;
            display: flex;
            flex-direction: column;
        }
        .resume-card:hover {
            transform: translateY(-5px);
            box-shadow: 0 8px 16px rgba(0,0,0,0.1);
            border-color: #90caf9;
        }
        .card-header {
            margin-bottom: 15px;
        }
        .card-name {
            font-size: 1.2rem;
            font-weight: 600;
            color: #1e88e5;
            margin: 0;
        }
        .card-role {
            font-size: 0.9rem;
            color: #616161;
            margin-top: 3px;
        }
        .card-industry {
            display: inline-block;
            background-color: #e3f2fd;
            color: #1976d2;
            font-size: 0.8rem;
            padding: 3px 8px;
            border-radius: 12px;
            margin-top: 10px;
        }
        .card-rating {
            margin-top: 15px;
            color: #ffa000;
        }
        .card-button {
            margin-top: auto;
            text-align: center;
        }
        .view-button {
            background-color: #1e88e5;
            color: white;
            border: none;
            padding: 8px 16px;
            border-radius: 4px;
            cursor: pointer;
            font-size: 0.9rem;
            transition: background-color 0.2s;
            text-decoration: none;
            display: inline-block;
        }
        .view-button:hover {
            background-color: #1565c0;
        }
        .resume-filters {
            background-color: #f5f7f9;
            padding: 15px;
            border-radius: 8px;
            margin-bottom: 20px;
        }
        </style>
        """, unsafe_allow_html=True)
        
        # Get sample resumes
        sample_resumes = get_sample_resumes()
        
        # Filter section
        st.markdown('<div class="resume-filters">', unsafe_allow_html=True)
        col1, col2 = st.columns(2)
        
        with col1:
            # Get unique industries
            industries = sorted(list(set([resume["industry"] for resume in sample_resumes])))
            industries.insert(0, "All Industries")
            selected_industry = st.selectbox("Filter by Industry", industries)
        
        with col2:
            # Sort options
            sort_options = ["Name (A-Z)", "Name (Z-A)", "Rating (High to Low)", "Rating (Low to High)"]
            sort_by = st.selectbox("Sort by", sort_options)
        
        st.markdown('</div>', unsafe_allow_html=True)
        
        # Filter resumes based on selection
        if selected_industry != "All Industries":
            filtered_resumes = [r for r in sample_resumes if r["industry"] == selected_industry]
        else:
            filtered_resumes = sample_resumes
        
        # Sort resumes
        if sort_by == "Name (A-Z)":
            filtered_resumes.sort(key=lambda x: x["person_name"])
        elif sort_by == "Name (Z-A)":
            filtered_resumes.sort(key=lambda x: x["person_name"], reverse=True)
        elif sort_by == "Rating (High to Low)":
            filtered_resumes.sort(key=lambda x: x["rating"], reverse=True)
        elif sort_by == "Rating (Low to High)":
            filtered_resumes.sort(key=lambda x: x["rating"])
        
        # Display resume cards in a grid - 3 cards per row
        for i in range(0, len(filtered_resumes), 3):
            cols = st.columns(3)
            for j in range(3):
                if i+j < len(filtered_resumes):
                    resume = filtered_resumes[i+j]
                    with cols[j]:
                        # HTML for card with direct link to open PDF in new tab
                        html_card = f"""
                        <div class="resume-card">
                            <div class="card-header">
                                <h3 class="card-name">{resume["person_name"]}</h3>
                                <p class="card-role">{resume["role"]}</p>
                                <span class="card-industry">{resume["industry"]}</span>
                            </div>
                            <div class="card-rating">
                                {"★" * int(resume["rating"])}{"☆" * (5 - int(resume["rating"]))} {resume["rating"]}
                            </div>
                            <div class="card-button">
                                <a href="{resume["pdf_url"]}" target="_blank" class="view-button">View Resume</a>
                            </div>
                        </div>
                        """
                        st.markdown(html_card, unsafe_allow_html=True)

        # No results message
        if not filtered_resumes:
            st.warning(f"No resumes found for {selected_industry} industry.")
    
    # Footer with updates and newsletter signup
    st.divider()
    col1, col2 = st.columns(2)
    with col1:
        st.caption("**Latest Update:** Sample resume templates added (Feb 2025)")
    with col2:
        with st.form("newsletter_form", clear_on_submit=True):
            email = st.text_input("Subscribe to our newsletter", placeholder="Enter your email")
            submit_button = st.form_submit_button("Subscribe")
            if submit_button and email:
                st.success(f"Thanks for subscribing with {email}!")