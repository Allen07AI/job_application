import os
import asyncio
from agents import Agent, Runner, OpenAIChatCompletionsModel, AsyncOpenAI
import openai
from dotenv import load_dotenv
import re

# Load environment variables
load_dotenv()

# OpenAI API Key Setup
openai.api_key = os.getenv("OPENAI_API_KEY")
client = openai.OpenAI()

# Define ResTech Agent
restech_agent = Agent(
    name="ResTech",
    instructions="Your name is ResTech. You are an expert Technical Human Resource Manager and Modern Tech Genius. Do not mention any designation. Just say 'My name is ResTech' and follow the prompt professionally.",
    model=OpenAIChatCompletionsModel(
        model="gpt-3.5-turbo",
        openai_client=AsyncOpenAI()
    ),
)

# Synchronous wrapper function
def get_ai_response(input_text, resume_text, prompt):
    full_prompt = (
        f"Prompt: {prompt}\n\n"
        f"Job Description: {input_text}\n\n"
        f"Resume: {resume_text}"
    )
    result = asyncio.run(Runner.run(restech_agent, input=full_prompt))
    return result.final_output

# Define the Resume Rater Agent
resume_rater_agent = Agent(
    name="Resume Rater",
    instructions=(
        "You are an expert resume evaluator.\n"
        "Given a job description and a resume, strictly rate the relevance of each resume section (Education, Skills, Experience, Projects, Others) from 1 to 10.\n"
        "Be unbiased and do not assign high scores unless well justified. Follow this strict format:\n"
        "Education: X\n"
        "Skills: X\n"
        "Experience: X\n"
        "Projects: X\n"
        "Others: X"
    ),
    model=OpenAIChatCompletionsModel(
        model="gpt-3.5-turbo",
        openai_client=AsyncOpenAI()
    ),
)

# Function to rate resume sections
def rate_sections_ai(resume_text, job_description):
    sections = ["Education", "Skills", "Experience", "Projects", "Others"]

    prompt = f"""
Job Description:
{job_description}

Resume:
{resume_text}

Rate each section strictly from 1 to 10. Be honest and rigorous.
"""

    # Run the agent
    result = asyncio.run(Runner.run(resume_rater_agent, input=prompt))
    response_text = result.final_output.strip()

    # Extract scores using regex
    scores = {}
    for section in sections:
        match = re.search(rf"{section}:\s*(\d+)", response_text)
        scores[section] = int(match.group(1)) if match else 5  

    return scores

# Define the Resume Tailoring Agent
resume_tailoring_agent = Agent(
    name="Resume Tailoring Agent",
    instructions=(
        "Your task is to modify the given resume section to match the keywords from the job description. "
        "Keep all relevant information intact while optimizing the phrasing for applicant tracking systems (ATS). "
        "Ensure each bullet point remains concise and action-driven. Always limit it to 3 points. Never do more points than 3."
        "Do not make up stuff and keep the resume poins intact but just modify according to the keywords in the job description."
    ),
    model=OpenAIChatCompletionsModel(
        model="gpt-3.5-turbo",
        openai_client= AsyncOpenAI()
    ),
)

# Function to tailor resume synchronously
def tailor_section(job_desc, resume_section, max_points):
    """Uses the resume tailoring agent to refine the resume section based on the job description."""
    input_text = (
        f"Job Description:\n{job_desc}\n\n"
        f"Resume Section to Tailor (generate at most {max_points} bullet points):\n{resume_section}\n\n"
        "Modify the resume section to align with the job description. Keep experience and domain unchanged."
        "Do not include the title of the job or working dates or position. Your job is to only edit the points."
        "Make sure to add a hyphen (-) as a bullet point for each point."
    )

    result = asyncio.run(Runner.run(resume_tailoring_agent, input=input_text))
    return result.final_output

# Define the Cover Letter Agent
cover_letter_agent = Agent(
    name="Cover Letter Generator",
    instructions="You generate concise and professional cover letter body content tailored to the job title and user experience.Write a maximum of 2 paragraphs."
    "Remember to only include actaull stuff in the resume and don't make anything up. Also, only generate the body content as mentioned.",
    model=OpenAIChatCompletionsModel(
        model="gpt-3.5-turbo",
        openai_client=AsyncOpenAI()
    ),
)

# Synchronous wrapper function
def generate_cover_letter_content(job_title, company_name, user_data):
    prompt = f"""
Write a professional cover letter for a {job_title} position at {company_name}. Keep it to a maximum of two paragraphs, and include enthusiasm for the role and relevant skills. 
Don't generate fake experience or add irrelevant stuff. Generate only the body of the Cover Letter. Do not generate anything like formats or subjects.

Start with 'I am excited to apply to'. Mention that I am currently pursuing a {user_data['course']} at {user_data['university']}. 
Highlight my experience with {', '.join(user_data['software_tools'])}, and how it applies to the role. 

Briefly reference my previous role as a {user_data['company_1_job_title']} at {user_data['company_1']}, where I worked on {user_data['work_1']}. 
Also, briefly reference my previous role as a {user_data['company_2_job_title']} at {user_data['company_2']}, where I worked on {user_data['work_2']}. 

Ensure the response is concise, engaging, and directly relevant to the role.
"""
    result = asyncio.run(Runner.run(cover_letter_agent, input=prompt))
    return result.final_output