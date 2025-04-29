import streamlit as st
import os
from PIL import Image
import pdf2image
import asyncio
from agents import Agent, Runner, OpenAIChatCompletionsModel, AsyncOpenAI
import openai
import ai_agents
from ai_agents import get_ai_response
from ai_agents import rate_sections_ai
from dotenv import load_dotenv
import plotly.express as px
import re
import pytesseract
from job_apply import job_apply
from guardrails import execute_chat_with_guardrails

# Load environment variables
load_dotenv()

# OpenAI API Key Setup
openai.api_key = os.getenv("OPENAI_API_KEY")
client = openai.OpenAI()

# Function to extract text from PDF using OCR
def extract_text_from_pdf(uploaded_file):
    images = pdf2image.convert_from_bytes(uploaded_file.read())
    extracted_text = ""

    for img in images:
        extracted_text += pytesseract.image_to_string(img) + "\n"

    return extracted_text.strip()

# Function to interact with OpenAI API
async def get_openai_response(input_text, resume_text, prompt):
    full_prompt = f"Prompt:{prompt}\n\nJob Description: {input_text}\n\nResume: {resume_text}"
    response = client.chat.completions.create(
        model="gpt-3.5-turbo",  
        messages=[
            {"role": "system", "content": "You are an expert Technical Human Resource Manager and Modern Tech Genius named ResTech. Just mention your name and follow the prompt"},
            {"role": "user", "content": full_prompt}
        ],
        max_tokens=500,
        temperature = 0.1
    )
    return response.choices[0].message.content.strip()

# Function to rate resume sections based on job description
def rate_sections_openai(resume_text, job_description):
    sections = ["Education", "Skills", "Experience", "Projects", "Others"]
    
    prompt = f"""
    You are a hiring expert reviewing a resume for a job application.
    Given the job description below, rate the relevance of each resume section on a scale of 1 to 10.
    Do not give all sections a high rating unless they are actually deserving of it.
    Make sure you be strict on ratings and unbiased. Be very strict.
    
    **Instructions:**
    - Only provide numerical scores.
    - Format your response strictly as follows:
      Education: X
      Skills: X
      Experience: X
      Projects: X
      Others: X

    **Job Description:**
    {job_description}

    **Resume:**
    {resume_text}
    """

    response = client.chat.completions.create(
        model= finetuned_model_id,
        messages=[
            {"role": "system", "content": "You are an expert resume evaluator."},
            {"role": "user", "content": prompt}
        ],
        temperature=0.1,
        max_tokens= 200
    )

    response_text = response.choices[0].message.content.strip()

    # Extract scores using regex
    scores = {}
    for section in sections:
        match = re.search(rf"{section}:\s*(\d+)", response_text)
        if match:
            scores[section] = int(match.group(1))
        else:
            scores[section] = 5  # Default

    return scores


# Streamlit UI
st.title("ResTech.io 🔍")
st.subheader("Resume feedback, Interview prep & Job applications! 💼")

st.markdown(
    """
    <style>
        /* Set the entire background color to white */
body {
    background-color: white !important;
    margin: 0;
    padding: 0;
}

/* Set background color for Streamlit app content */
.stApp {
    background-color: white !important;
}

/* Set header background to light blue */
.stAppHeader {
    background-color: white !important;  /* White background */
}

/* Set toolbar background to light blue */
.stToolbar {
    background-color: #ADD8E6 !important;  /* Light Blue */
}

/* Footer styling */
.stBottom {
    background-color: white !important;
}

/* Set all text to black */
.stText, .stHeading, .stMarkdown, .stLabel, .stButton, .stTextInput, .stTextArea, .stSelectbox, .stSlider, .stTitle, .stSubheader {
    color: black !important;
}

/* Style the title (h1) to be black */
h1 {
    color: black !important;
    font-size: 32px;
    font-weight: bold;
}

/* Style the title (h3) to be black */
h3 {
    color: black !important;
    font-size: 14px;
    font-weight: bold;
}

/* Style the subheader */
.stApp .stMain .stHeadingWithActionElements {
    color: black !important;
    font-size: 14px !important;
}

/* Custom button styles */
.stButton > button {
    color: black !important;
    background-color: #ADD8E6 !important;  /* Light Blue */
    padding: 12px 24px;
    font-size: 14px;
    cursor: pointer;
    border: 2px solid black !important;  /* Thick black border */
    transition: background-color 0.3s ease;
}

/* Button hover effect */
.stButton > button:hover {
    background-color: white !important;
    color: #ADD8E6 !important;  /* Text color on hover */
    border: 2px solid #ADD8E6 !important;  /* Border color on hover */
}

/* Default style for the 'Browse files' button */
.stFileUploader button:not([disabled]) {
    background-color: transparent !important;  /* Transparent background */
    color: #ADD8E6 !important;  /* Light blue text */
    border: 2px solid #ADD8E6 !important;  /* Light blue border */
}

/* Style for the 'Browse files' button when enabled */
.stFileUploader button:not([disabled]):hover {
    background-color: #ADD8E6 !important;  /* Light blue background on hover */
    color: white !important;  /* White text color on hover */
    border: 3px solid #ADD8E6 !important;  /* Light blue border on hover */
}

/* Style text input and text area */
.stApp .stMain .stTextInput, .stApp .stMain .stTextArea {
    color: black !important;
    background-color: #ADD8E6 !important;  /* Light Blue */
    border: 2px solid black !important;
    padding: 10px;
    border-radius: 10px;  /* Rounded borders */
}

/* Style the job description and file upload areas */
.stApp .stMain .stTextArea, .stFileUploader {
    background-color: #ADD8E6 !important;  /* Light Blue */
    border: 2px solid black !important;
    padding: 10px;
    border-radius: 10px;  /* Rounded borders */
}

/* Job description and file upload area text */
.stApp .stMain .stTextArea p, .stFileUploader p {
    color: black !important;
}

/* Change the background color of the header button */
        [data-testid="stBaseButton-headerNoPadding"] {
            background-color: black !important;
            color: white !important;
            border: none !important;
        }

        /* Change the color of the SVG icon inside the button */
        [data-testid="stBaseButton-headerNoPadding"] svg {
            fill: white !important;
        }

        /* Change sidebar header text (h3 inside stHeading) to black */
        section[data-testid="stSidebar"] div.stHeading h2,
        section[data-testid="stSidebar"] div.stHeading h3 {
            color: black !important;
        }

        /* Sidebar background color */
        [data-testid="stSidebar"] {
            background-color: #ADD8E6  !important;
        }

        /* Sidebar Name input field */
        .stSidebar .stTextInput input {
            background-color: white !important;
            color: black !important;
        }

        /* Sidebar Name input field label */
        .stSidebar .stTextInput label {
            color: black !important;
            font-weight: bold;
        }

        /* Sidebar Job Description input field */
        .stSidebar .stTextArea textarea {
            background-color: white !important;
            color: black !important;
        }

        /* Sidebar Job Description label */
        .stSidebar .stTextArea label {
            color: black !important;
            font-weight: bold;
        }

        /* Label text color */
        label, .stMarkdown p {
        color: black !important;
        }

        /* Number input box background and text */
        input[type="number"] {
        background-color: white !important;
        color: black !important;
        border: 1px solid #ccc;
        border-radius: 5px;
        padding: 6px;
        }

        /* Style for the number input buttons */
        button[data-testid="stNumberInputStepDown"],
        button[data-testid="stNumberInputStepUp"] {
        background-color: white !important;
        border: 1px solid #ccc;
        color: black !important;
        }

       /* Make sure the icons inside are black */
       button[data-testid="stNumberInputStepDown"] svg,
       button[data-testid="stNumberInputStepUp"] svg {
       fill: black !important;
       }
    </style>
    """,
    unsafe_allow_html=True
)

# Apply for Jobs Now: Section
with st.sidebar:
    st.header("Apply for Jobs Now:")
    name = st.text_input("Name:", key="web_name")
    contact_info_num = st.text_input("Phone Number:", key="phone")
    contact_info_email = st.text_input("Email:", key="email")
    university = st.text_input("University:", key="university")
    gpa = st.text_input("GPA:", key="gpa")
    course = st.text_input("Course:", key="course")
    relevant_coursework = st.text_area("Relevant Coursework:", key="relevant_coursework")
    softwares_tools = st.text_area("Softwares/Tools:", key="softwares_tools")
    interests = st.text_area("Interests:", key="interests")
    
    st.subheader("Work Experience")
    company_1 = st.text_input("Company 1:", key="company_1")
    company_1_job_title = st.text_input("Role:", key="company_1_job_title")
    dates_1 = st.text_input("Dates of working:", key="dates_1")
    work_1 = st.text_area("Work Description:", key="work_1")
    
    company_2 = st.text_input("Company 2:", key = "company_2")
    company_2_job_title = st.text_input("Role:", key="company_2_job_title")
    dates_2 = st.text_input("Dates of working:", key="dates_2 ")
    work_2 = st.text_area("Work Description:", key="work_2")
    
    st.subheader("Projects")
    project_1_title = st.text_input("Project 1 Title:", key = "project_1_title")
    project_1_desc = st.text_area("Project 1 Description:", key = "project_1_desc")
    project_2_title = st.text_input("Project 2 Title:", key = "project_2_title")
    project_2_desc = st.text_area("Project 2 Description:", key = "project_2_desc")

    user_data = {
    "name": name,
    "contact_info_num": contact_info_num,
    "contact_info_email": contact_info_email,
    "university": university,
    "course": course,
    "gpa": gpa,
    "relevant_coursework": relevant_coursework,
    "software_tools": softwares_tools,
    "interests": interests,
    "company_1": company_1,
    "company_1_job_title": company_1_job_title,
    "dates_1": dates_1,
    "work_1": work_1,
    "company_2": company_2,
    "company_2_job_title": company_2_job_title,
    "dates_2": "May 2024 – Present",
    "work_2": work_2,
    "project_1_title": project_1_title,
    "project_1_desc": project_1_desc,
    "project_2_title": project_2_title,
    "project_2_desc": project_2_desc
    }    
    
    st.subheader("Job Application")
    job_query = st.text_area("Type of job you are interested to apply for:")
    num_jobs = st.number_input("Number of jobs to apply for:", min_value=1, step=1)

    if st.button("Apply"):
       job_apply(user_data, job_query, num_jobs) 

# Job Description Input
input_text = st.text_area("📝 Job Description: ", key="input")
uploaded_file = st.file_uploader("📄 Upload your resume in PDF format", type=["pdf"])

if uploaded_file is not None:
    st.write("Resume Uploaded ✅")

# Button Layout
col1, col2, col3, col4 = st.columns(4)

with col1:
    submit1 = st.button("General Summary 📋")
with col2:
    submit2 = st.button("Skill Improvement 💡")
with col3:
    submit3 = st.button("Interview Prep 📊")
with col4:
    submit4 = st.button("Visualize Evaluation 📈")

# OpenAI Prompts
input_prompt1 = """
You are an experienced Technical Human Resource Manager. Your task is to review the provided resume against the job description.
Please share your professional evaluation on whether the candidate's profile aligns with the role.
Highlight the strengths and weaknesses of the applicant in relation to the specified job requirements.
"""
input_prompt2 = """
You are an experienced Technical Human Resource Manager. Your task is to review the provided resume against the job description.
Please share your professional evaluation on whether the candidate's skills aligns with the skills required for the role.
Suggest current skills and softwares which are important for the job and highlight the ones lacking in the resume provided.
"""

input_prompt3 = """
You are an expert career coach and interview simulator with deep knowledge of job roles, technical interviews, and HR behavioral questions.

Using the provided job description and resume, generate a list of 8 technical interview questions that reflect the core skills, softwares and expectations of the job. Include coding and project-based questions that assess practical knowledge if the role is technical.

Then, generate 2–3 behavioral/HR interview questions that test the candidate’s communication, problem-solving, and teamwork abilities.

For each question, provide a strong sample answer based on the resume's content.

Format:
Question 1:
Answer:

...

Use the job description as the foundation for creating realistic, high-quality interview prep content. So total 10 questions should be generated inlcuding both technical and HR ones.
"""

# Resume Analysis
if uploaded_file is not None:
    resume_text = extract_text_from_pdf(uploaded_file)


            # If guardrail passed, now continue with the intended prompt
if submit1:
    final_response = get_ai_response(input_text, resume_text, input_prompt1)
    st.subheader("Resume Evaluation:")
    st.write(final_response)

elif submit2:
    final_response = get_ai_response(input_text, resume_text, input_prompt2)
    st.subheader("Skill Improvement Suggestions:")
    st.write(final_response)

elif submit3:
    final_response = get_ai_response(input_text, resume_text, input_prompt3)
    st.subheader("Interview Questions:")
    st.write(final_response)

elif submit4:
    scores = rate_sections_ai(resume_text, input_text)
 
              # Generate Plotly bar chart
    fig = px.bar(
               x=list(scores.keys()),
               y=list(scores.values()),
               labels={"x": "Resume Sections", "y": "Rating (0 - 10)"},
               title="Resume Section Ratings",
               color=list(scores.values()),
               color_continuous_scale="Blues",
               range_color=[0, 10] 
              )
    fig.update_layout(
              plot_bgcolor='white',
              paper_bgcolor='white',
              title_font=dict(color='black'),
              font=dict(color='black'),
              yaxis=dict(range=[0, 10]),
              xaxis_title_font=dict(color='black'),
              yaxis_title_font=dict(color='black'),
              xaxis_tickfont=dict(color='black'),
              yaxis_tickfont=dict(color='black'),
              legend_title_font=dict(color='black'),
              legend_font=dict(color='black'),
              coloraxis_colorbar_title_font=dict(color='black'),
              coloraxis_colorbar_tickfont=dict(color='black'),
              margin=dict(l=40, r=40, t=40, b=40),
              shapes=[
            dict(
            type='rect',
            x0=0, y0=0,
            x1=1, y1=1,
            xref='paper', yref='paper',
            line=dict(
                color="black",
                width=3
                ),
            layer="below"
            )
          ]
        )

    # Display the chart in Streamlit
    st.plotly_chart(fig)
