# AiRS: AI Resume Scorer 🚀

## Overview

**AiRS (AI Resume Scorer)** is a web application designed to help users optimize their resumes for better job matches. Using advanced AI models, the tool evaluates resumes against job descriptions, providing detailed feedback and scoring based on various resume components such as grammar, structure, action verbs, and quantifiable achievements. AiRS aims to enhance your resume's effectiveness by identifying areas for improvement and aligning it more closely with job requirements.

## Features

- **Text Extraction**: Utilizes OCR technology to extract text from PDF resumes, ensuring that the AI model can evaluate content accurately.
- **AI-Powered Scoring**: Employs Google's Gemini 1.5 Flash model to analyze resumes and generate feedback, including a score based on a predefined scoring system.
- **Component-Based Scoring**: Breaks down the resume evaluation into specific components, such as grammar, structure, and use of action verbs, to provide targeted feedback.
- **Visualizations**: Provides visual representations of the resume scores using bar charts and pie charts, helping users easily identify strengths and weaknesses.
- **User-Friendly Interface**: Built using Streamlit, the application offers an intuitive interface with easy-to-use features, such as file uploads and job description inputs.
- **Customizable Evaluation Rules**: The scoring system and evaluation criteria can be modified by updating rule files, allowing for tailored feedback according to specific industry needs.

## Installation

1. **Clone the Repository**:
   ```bash
   git clone https://github.com/akash-masadi/AiRS.git
   cd AiRS
   ```

2. **Install Dependencies**:
   Ensure you have Python installed. Then, run the following command:
   ```bash
   pip install -r requirements.txt
   ```

3. **Set Up Environment Variables**:
   Create a `.env` file in the root directory and add your Google API key:
   ```
   GOOGLE_API_KEY=your_google_api_key
   ```

4. **Run the Application**:
   ```bash
   streamlit run main.py
   ```

## Project Structure

- **mypdfprocessor**: Contains utility modules for processing PDFs, extracting text, and deskewing images.
  - `ocr_utils.py`: Functions for extracting text from images and PDF files.
  - `image_utils.py`: Functions for image preprocessing, such as deskewing.
  - `file_utils.py`: Functions for loading text files that contain evaluation rules.
  - `__init__.py`: Initializes the module and imports relevant functions.

- **assets**: Contains logos and images used in the Streamlit app.

- **rules**: Directory for text files that define the scoring system and evaluation criteria, such as grammar rules, scoring systems, and more.

- **home_page.py**: Defines the layout and content of the home page, including the introduction to AiRS.

- **resume_score_page.py**: Contains the logic for evaluating the overall resume score and visualizing the results.

- **job_relevant_score_page.py**: Contains the logic for evaluating the relevance of a resume to a specific job description.

- **main.py**: The entry point of the application. It initializes the application, loads the necessary components, and routes between different pages.

## Usage

### Home Page

The home page provides an introduction to AiRS and a brief overview of its capabilities. Users can upload their resume and enter a job description for evaluation.

### Resume Score

In the **Resume Score** section, users can upload their resume in PDF or TXT format. The application will extract the text, evaluate it based on the predefined scoring system, and provide a breakdown of the scores across different components.

### Job Description Relevant Score

In the **Job Description Relevant Score** section, users can evaluate how well their resume matches a specific job description. After uploading their resume and entering the job description, the AI model will analyze the content and provide feedback on the relevance of the resume to the job.

## Future Improvements

- **Enhanced Scoring Criteria**: Add more granular scoring categories, such as industry-specific jargon and ATS compatibility.
- **User Authentication**: Implement user login to save and track resume evaluations over time.
- **Multi-Language Support**: Extend the tool's capabilities to support resumes in multiple languages.
- **API Integration**: Allow for integration with other job search platforms and resume builders via APIs.

## Contributing

Contributions are welcome! Please feel free to submit a pull request or open an issue if you have any suggestions or improvements.
