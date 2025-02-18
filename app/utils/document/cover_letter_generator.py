"""
Generates a professional and structured cover letter using OpenAI GPT-4.
"""

import openai
import os

# Load API Key
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

def generate_cover_letter(job_description, language='english'):
    """
    Generates a structured and tailored cover letter using OpenAI GPT-4 API
    based only on the job description.

    Args:
        job_description (str): The job description provided by the user.
        language (str): The language for the cover letter.

    Returns:
        str: The generated cover letter text with personal details at the end.

    Raises:
        Exception: If an error occurs with the OpenAI API.
    """
    openai.api_key = OPENAI_API_KEY

    prompt = (
        "You are an AI-powered career assistant. Create a formal, engaging, and "
        "professional cover letter tailored to the following job description. "
        "Use " + language + " for the letter. Ensure that the letter is concise, "
        "highlights key achievements relevant to the job, and maintains a "
        "confident and professional tone. The letter should be approximately "
        "250-350 words.\n\nJob Description:\n" + job_description +
        "\n\nPlease ensure that the applicant's name, email, and phone number "
        "appear at the end of the letter. Do not include any other personal "
        "information such as address, company address, birthdate, etc."
    )

    try:
        response = openai.ChatCompletion.create(
            model="gpt-4-turbo",
            messages=[
                {
                    "role": "system",
                    "content": (
                        "Generate a professional cover letter in " + language +
                        ", with only the applicant's name, email, and phone number "
                        "at the end."
                    )
                },
                {"role": "user", "content": prompt}
            ],
            temperature=0.6,
            max_tokens=1000
        )
        return response['choices'][0]['message']['content'].strip()

    except openai.error.OpenAIError as e:
        raise Exception(f"OpenAI API Error: {str(e)}")

def generate_cover_letter_with_cv(job_description, cv_text, language='english'):
    """
    Generates a structured and tailored cover letter using OpenAI GPT-4 API
    with both job description and CV text.

    Args:
        job_description (str): The job description provided by the user.
        cv_text (str): Extracted text from the user's CV.
        language (str): The language for the cover letter.

    Returns:
        str: The generated cover letter text with personal details at the end.

    Raises:
        Exception: If an error occurs with the OpenAI API.
    """
    openai.api_key = OPENAI_API_KEY

    prompt = (
        "You are an AI-powered career assistant. Create a cover letter in " +
        language + " that analyzes and reflects both the provided job " +
        "description and the candidate's CV. Ensure that the letter is " +
        "professionally structured, emphasizing the candidate's qualifications " +
        "and experiences relevant to the job, and adheres to a confident and " +
        "professional tone. The cover letter should be between 250-350 words.\n\n" +
        "Job Description:\n" + job_description + "\n\n" +
        "CV Text:\n" + cv_text + "\n\n" +
        "Please ensure that the applicant's name, email, and phone number appear " +
        "at the end of the letter. Do not include any other personal information " +
        "such as address, company address, birthdate, etc."
    )

    try:
        response = openai.ChatCompletion.create(
            model="gpt-4-turbo",
            messages=[
                {
                    "role": "system",
                    "content": (
                        "Generate a professional cover letter in " + language +
                        ", with only the applicant's name, email, and phone number "
                        "at the end."
                    )
                },
                {"role": "user", "content": prompt}
            ],
            temperature=0.6,
            max_tokens=1000
        )
        return response['choices'][0]['message']['content'].strip()

    except openai.error.OpenAIError as e:
        raise Exception(f"OpenAI API Error: {str(e)}")
