from dotenv import load_dotenv
import streamlit as st
import google.generativeai as genai
import os
import tempfile
from mypdfprocessor import extract_text, load_file, extract_and_remove_component_scores  # Assuming this is your custom package
import pandas as pd

# Load environment variables
load_dotenv()

# Configure Generative AI with API key from environment variable
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

# Initialize the generative model
model = genai.GenerativeModel(model_name='gemini-1.5-flash')
chat = model.start_chat(history=[])

# Load rules from files
scoring = load_file("/rules/_scoring.txt")
scoring_system = load_file("./rules/_scoring_system.txt")
grammar_spelling = load_file("/rules/_grammar_spelling.txt")
structure = load_file("/rules/_structure.txt")
action_verbs = load_file("/rules/_action_verbs.txt")
quantifiable = load_file("/rules/_quantifiable.txt")   


# Function to get response from the model
def get_gemini_response(resume_data):
    global chat,scoring_system
    response = chat.send_message(resume_data)
    gen_score = chat.send_message(resume_data+"\n\n\n"+scoring_system)
    return [response,gen_score]


# Streamlit app configuration
st.set_page_config(page_title="Resume Evaluation Demo")
st.header("Gemini Resume Evaluator")

# File uploader for resume
uploaded_file = st.file_uploader("Upload your resume", type=["pdf"])
submit = st.button("Evaluate Resume")

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

    if submit:
        # Initialize chat session
        chat.send_message(scoring)
        
        # Get response from the generative model
        [response,gen_score] = get_gemini_response(extracted_text)
        # st.json(gen_score.to_dict())

        gen_score = gen_score.candidates[0].content.parts[0].text

        gen_score,score_dict = extract_and_remove_component_scores(gen_score)
        # Inspect the response structure
        st.json(score_dict)
        st.subheader("Response Score:")
        st.write(gen_score)  # This will print the response structure

        # Extract the text content from the response
        if hasattr(response, 'candidates'):
            content = response.candidates[0].content.parts[0].text
            st.subheader("Response:")
            st.write(content)
        else:
            st.error("Unexpected response structure")
