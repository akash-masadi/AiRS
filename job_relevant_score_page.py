from dotenv import load_dotenv
import streamlit as st
import google.generativeai as genai
import os
import tempfile
import pandas as pd
import altair as alt
from myUtils import extract_and_remove_component_scores, load_file, extract_text, stream_gen
from streamlit_extras.streaming_write import write

load_dotenv()

def load_all_files():
    scoring = load_file("./rules/_scoring.txt")
    scoring_system = load_file("./rules/_scoring_system.txt")
    grammar_spelling = load_file("./rules/_grammar_spelling.txt")
    structure = load_file("./rules/_structure.txt")
    action_verbs = load_file("./rules/_action_verbs.txt")
    quantifiable = load_file("./rules/_quantifiable.txt")
    return scoring, scoring_system, grammar_spelling, structure, action_verbs, quantifiable

genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

model = genai.GenerativeModel(model_name='gemini-1.5-flash')
chat = model.start_chat(history=[])

@st.cache_data
def load_all_files():
    scoring = load_file("./rules/_scoring.txt")
    scoring_system = load_file("./rules/_scoring_system.txt")
    grammar_spelling = load_file("./rules/_grammar_spelling.txt")
    structure = load_file("./rules/_structure.txt")
    action_verbs = load_file("./rules/_action_verbs.txt")
    quantifiable = load_file("./rules/_quantifiable.txt")
    return scoring, scoring_system, grammar_spelling, structure, action_verbs, quantifiable

scoring, scoring_system, grammar_spelling, structure, action_verbs, quantifiable = load_all_files()

def get_gemini_response(resume_data, job_description):
    global chat, scoring_system
    job_response = chat.send_message(job_description)
    response = chat.send_message(resume_data)
    gen_score = chat.send_message(resume_data + "\n\n\n" + scoring_system)
    return [response, gen_score]

def plot_scores(st, score_dict):
    df = pd.DataFrame({
        'Components': list(score_dict.keys()),
        'Scores': list(score_dict.values())
    })

    total_score = sum(score_dict.values())
    max_score = 100

    bar_chart = alt.Chart(df).mark_bar().encode(
        x=alt.X('Scores:Q', title='Scores'),
        y=alt.Y('Components:O', title='Components', sort='-x'),
        tooltip=['Components', 'Scores']
    ).properties(
        width=600,
        height=400,
        title='Resume Component Scores'
    ).configure_axis(
        labelFontSize=12,
        titleFontSize=14
    )

    pie_chart = alt.Chart(df).mark_arc().encode(
        color=alt.Color('Components:N', legend=None),
        tooltip=['Components', 'Scores'],
        theta='Scores:Q',
        radius=alt.Radius(),
    ).properties(
        width=400,
        height=400,
        title='Total Score Breakdown'
    )

    total_score_data = pd.DataFrame({
        'Category': ['Total Score', 'Remaining'],
        'Value': [total_score, max_score - total_score]
    })

    total_score_pie_chart = alt.Chart(total_score_data).mark_arc().encode(
        color=alt.Color('Category:N', legend=None),
        tooltip=['Category', 'Value'],
        theta='Value:Q',
        radius=alt.Radius(),
    ).properties(
        width=400,
        height=400,
        title=f'Total Score ({total_score}) vs. Overall Score ({max_score})'
    )

    st.subheader("Total Score vs. Overall Score")
    st.altair_chart(total_score_pie_chart, use_container_width=True)

    st.subheader("Total Score Breakdown")
    st.altair_chart(pie_chart, use_container_width=True)

    st.subheader("Resume Component Scores")
    st.altair_chart(bar_chart, use_container_width=True)

def job_relevant_score():
    global chat
    uploaded_file = st.file_uploader("Upload your resume", type=["pdf", "txt"])
    job_description = st.text_area("Enter the Job Description", height=200)
    submit = st.button("Evaluate Resume")

    if uploaded_file is not None and job_description and submit:
        if uploaded_file.type == "application/pdf":
            with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as temp_file:
                temp_file.write(uploaded_file.read())
                temp_file_path = temp_file.name
            extracted_text = extract_text(temp_file_path)
        else:
            extracted_text = uploaded_file.read().decode("utf-8")

        with st.spinner('Evaluating your resume...'):
            chat.send_message(scoring)
            [response, gen_score] = get_gemini_response(extracted_text, job_description)
            gen_score, score_dict = extract_and_remove_component_scores(gen_score.candidates[0].content.parts[0].text)

        try:
            plot_scores(st, score_dict["components"])
        except Exception as e:
            st.error(f"Error plotting scores: {e}")

        if hasattr(response, 'candidates'):
            content = response.candidates[0].content.parts[0].text
            st.subheader("Response:")
            write(stream_gen(content))
        else:
            st.error("Unexpected response structure")

if __name__ == "__main__":
    try:
        st.title("Job Relevance Score Evaluation")
        job_relevant_score()
    except:
        st.error("Oops! Ran into an error.")
