import streamlit as st
import PyPDF2
import io
import os
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

# configure tab/page (description for the webpage)
st.set_page_config(page_title="AI Resume Critiquer", page_icon="📃", layout="centered")

# writing a title and markdown text for the webpage
st.title("AI Resume Critiquer")
st.markdown("Upload your resume and get AI-powered feedback tailored to your needs!")


# get the api key in the .env
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

uploaded_file = st.file_uploader("Upload your resume (PDF or TXT)", type=["pdf","txt"])
job_role = st.text_input("Enter the job role you're targeting (optional)")

analyze = st.button("Analyze Resume")


def extract_text_from_pdf(pdf_file):
    # load the pdf file
    pdf_reader = PyPDF2.PdfReader(pdf_file)
    text=""
    # for each page in the pdf, add the text onto the text var and return the text
    for page in pdf_reader.pages:
        text+= page.extract_text() + "\n"
    return text


def extract_text_from_file(uploaded_file):
    # if uploaded file is a pdf
    if uploaded_file.type == "application/pdf":
        # extract text from pdf
        return extract_text_from_pdf(io.BytesIO(uploaded_file.read()))
    # else, the file is a txt and just uploaded it and decode it as a utf-8
    return uploaded_file.read().decode("utf-8")

if analyze and uploaded_file:
    try:
        file_content = extract_text_from_file(uploaded_file)

        # if there isn't content in the file, stop streamlit
        if not file_content.strip():
            st.error("File does not have any content...")
            st.stop()

        prompt = f""""Please analyze this resume and provide constructive feedback.
        Focus on the following aspects:
        1. Content clarity and impact
        2. Skills presentation
        3. Experience descriptions
        4. Specific improvements for {job_role if job_role else 'general job applications'}

        Resume content:
        {file_content}

        Please provide your analysis in a clear, structured format with specific recommendations."""

        # creating a AI client
        client = OpenAI(api_key = OPENAI_API_KEY)
        # creating configuration for response
        response  = client.chat.completions.create(
            model = "gpt-4o-mini",
            messages = [
                {"role": "system", "content": "You are an expert resume reviewer with years of experience in HR and recruitment."},
                {"role": "user", "content":prompt}
            ],
            temperature = 0.7,
            max_tokens=1000
        )
        # print out the response from the AI
        st.markdown("### Analysis Results")
        # get the first sponse of the pool of possible responses from the AI
        st.markdown(response.choices[0].message.content)
    except Exception as e:
        st.error(f"An error occurred: {str(e)}")