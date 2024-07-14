from dotenv import load_dotenv
import streamlit as st
import google.generativeai as genai
import os
import tempfile
from myUtils import extract_text  # Assuming this is your custom package

# Load environment variables
load_dotenv()

# Configure Generative AI with API key from environment variable
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

# Initialize the generative model
model = genai.GenerativeModel(model_name='gemini-1.5-flash')

# Function to get response from the model
def get_gemini_response(question):
    response = model.generate_content(question)
    return response.text

# Streamlit app configuration
st.set_page_config(page_title="Demo")
st.header("Gemini")

# File uploader for resume
uploaded_file = st.file_uploader("Upload your resume", type=["pdf"])
submit = st.button("Ask the question")

if uploaded_file is not None:
    # Determine file type and extract text accordingly
    if uploaded_file.type == "application/pdf":
        # Save uploaded PDF to a temporary file
        with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as temp_file:
            temp_file.write(uploaded_file.read())
            temp_file_path = temp_file.name
        # Extract text from the PDF
        extracted_text = extract_text(temp_file_path)
    else:
        # Read text file
        extracted_text = uploaded_file.read().decode("utf-8")
    
    # Read rules from file
    rules = ""
    with open("_resume_rule.txt", 'r') as file:
        rules = file.read()

    if submit:
        response = get_gemini_response(rules + "\n\n\n" + extracted_text)
        st.subheader("Response is")
        st.write(response)
