from dotenv import load_dotenv
import streamlit as st
import google.generativeai as genai
import os
import tempfile
from myUtils import extract_text, load_file, extract_and_remove_component_scores
import pandas as pd
import altair as alt

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
    global chat, scoring_system
    response = chat.send_message(resume_data)
    gen_score = chat.send_message(resume_data + "\n\n\n" + scoring_system)
    return [response, gen_score]

def plot_scores(st, score_dict):
    # Convert score_dict to a DataFrame for Altair plotting
    df = pd.DataFrame({
        'Components': list(score_dict.keys()),
        'Scores': list(score_dict.values())
    })

    # Calculate total score
    total_score = sum(score_dict.values())
    max_score = 100  # Assuming the maximum possible score is 100

    # Create Altair bar chart
    bar_chart = alt.Chart(df).mark_bar().encode(
        x=alt.X('Scores:Q', title='Scores'),
        y=alt.Y('Components:O', title='Components', sort='-x'),  # Sorting components by score descending
        tooltip=['Components', 'Scores']  # Tooltip to show component and score
    ).properties(
        width=600,
        height=400,
        title='Resume Component Scores'
    ).configure_axis(
        labelFontSize=12,
        titleFontSize=14
    )

    # Create Altair pie chart for total score breakdown
    pie_chart = alt.Chart(df).mark_arc().encode(
        color=alt.Color('Components:N', legend=None),
        tooltip=['Components', 'Scores'],
        theta='Scores:Q',  # Angle encoding based on Scores
        radius=alt.Radius(),  # Adjust radius as needed
    ).properties(
        width=400,
        height=400,
        title='Total Score Breakdown'
    )

    # Data for total score vs overall score pie chart
    total_score_data = pd.DataFrame({
        'Category': ['Total Score', 'Remaining'],
        'Value': [total_score, max_score - total_score]
    })

    # Create pie chart for total score vs overall score
    total_score_pie_chart = alt.Chart(total_score_data).mark_arc().encode(
        color=alt.Color('Category:N', legend=None),
        tooltip=['Category', 'Value'],
        theta='Value:Q',  # Angle encoding based on Value
        radius=alt.Radius(),  # Adjust radius as needed
    ).properties(
        width=400,
        height=400,
        title=f'Total Score ({total_score}) vs. Overall Score ({max_score})'
    )

    st.subheader("Total Score vs. Overall Score")
    st.altair_chart(total_score_pie_chart, use_container_width=True)

    st.subheader("Total Score Breakdown")
    st.altair_chart(pie_chart, use_container_width=True)

    # Display the charts using Streamlit
    st.subheader("Resume Component Scores")
    st.altair_chart(bar_chart, use_container_width=True)

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
        with st.spinner('Evaluating your resume...'):
            # Initialize chat session
            chat.send_message(scoring)

            # Get response from the generative model
            [response, gen_score] = get_gemini_response(extracted_text)

            # Extract and remove component scores from response
            gen_score, score_dict = extract_and_remove_component_scores(gen_score.candidates[0].content.parts[0].text)

        # Display component scores plot
        plot_scores(st, score_dict["components"])

        # Display the response score and content
        st.subheader("Response Score:")
        st.write(gen_score)  # This will print the response structure

        if hasattr(response, 'candidates'):
            content = response.candidates[0].content.parts[0].text
            st.subheader("Response:")
            st.write(content)
        else:
            st.error("Unexpected response structure")
