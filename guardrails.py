import asyncio
import openai

system_prompt = "You are a helpful assistant."

# New: Guardrail for Job Description
async def jd_guardrail(jd_text):
    print("Checking JD guardrail")
    messages = [
        {
            "role": "system",
            "content": "You are a validator. If the input looks like a valid Job Description (talks about responsibilities, requirements, qualifications, skills), respond with 'allowed'. Otherwise respond with 'not_allowed'.",
        },
        {"role": "user", "content": jd_text},
    ]
    response = openai.chat.completions.create(
        model= "gpt-3.5-turbo", messages=messages, temperature=0
    )
    print("Got JD guardrail response")
    return response.choices[0].message.content

# New: Guardrail for Resume Text
async def resume_guardrail(resume_text):
    print("Checking Resume guardrail")
    messages = [
        {
            "role": "system",
            "content": "You are a validator. If the input looks like a valid Resume (talks about education, skills, experience, projects, achievements), respond with 'allowed'. Otherwise respond with 'not_allowed'.",
        },
        {"role": "user", "content": resume_text},
    ]
    response = openai.chat.completions.create(
        model= "gpt-3.5-turbo", messages=messages, temperature=0
    )
    print("Got Resume guardrail response")
    return response.choices[0].message.content

# Main chat function
async def get_chat_response(user_request):
    print("Getting LLM response")
    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_request},
    ]
    response = openai.chat.completions.create(
        model= "gpt-3.5-turbo", messages=messages, temperature=0.5
    )
    print("Got LLM response")
    return response.choices[0].message.content

# Execute full guardrail check
async def execute_chat_with_guardrails(jd_text, resume_text):
    jd_guardrail_task = asyncio.create_task(jd_guardrail(jd_text))
    resume_guardrail_task = asyncio.create_task(resume_guardrail(resume_text))

    await asyncio.wait([jd_guardrail_task, resume_guardrail_task])

    jd_result = jd_guardrail_task.result()
    resume_result = resume_guardrail_task.result()

    if jd_result == "not_allowed":
        print("Job Description guardrail triggered 🚫")
        return "The job description you entered doesn't look valid. Please enter a proper job description."

    if resume_result == "not_allowed":
        print("Resume guardrail triggered 🚫")
        return "The resume you entered doesn't look valid. Please enter a proper resume."

    # If both pass, continue to chat
    combined_request = f"Job Description:\n{jd_text}\n\nResume:\n{resume_text}\n\nNow analyze the resume based on the job description."
    chat_response = await get_chat_response(combined_request)
    return chat_response

# Main Function to run the code 
async def main():
    # Example of input
    input_text = "Example job description"
    resume_text = "Example resume content"

    response = await execute_chat_with_guardrails(input_text, resume_text)
    print(response)

# Running the main function 
if __name__ == "__main__":
    asyncio.run(main())