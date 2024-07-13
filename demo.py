import streamlit as st
import pandas as pd
import altair as alt

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
    
    # Display the charts using Streamlit
    st.subheader("Resume Component Scores")
    st.altair_chart(bar_chart, use_container_width=True)
    
    st.subheader("Total Score Breakdown")
    st.altair_chart(pie_chart, use_container_width=True)

    st.subheader("Total Score vs. Overall Score")
    st.altair_chart(total_score_pie_chart, use_container_width=True)

# Example usage in Streamlit app
st.set_page_config(page_title="Resume Evaluation Demo")
st.header("Resume Evaluation")

# Sample score_dict (replace with your data)
score_dict = {
    "Resume Parsing and Basic Information": 10,
    "Work Experience": 20,
    "Skills": 15,
    "Education": 9,
    "Grammar and Spelling": 10,
    "Formatting and Readability": 5,
    "Additional Sections": 5
}

# Plotting scores
plot_scores(st, score_dict)
