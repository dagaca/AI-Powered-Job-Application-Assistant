"""
Generates interview questions and sample answers using OpenAI GPT-4 API.
"""

import openai
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

def generate_interview_questions(job_description, cv_text, language='english'):
    """
    Generates 10 potential interview questions and CV-specific answers using
    OpenAI GPT-4 API.

    Args:
        job_description (str): The job description provided by the user.
        cv_text (str): Extracted text from the user's CV.
        language (str): The language in which the interview questions and
                        answers should be generated.

    Returns:
        str: The formatted interview preparation output in Q&A format.

    Raises:
        Exception: If an error occurs while communicating with OpenAI API.
    """
    openai.api_key = OPENAI_API_KEY

    prompt = (
        "You are an AI-based career assistant specializing in interview "
        "preparation. Based on the job description and the candidate's CV, "
        "generate 10 relevant interview questions that are likely to be "
        "asked, with well-structured sample answers tailored to the candidate's "
        "profile.\n\nJob Description:\n" + job_description +
        "\n\nCandidate's CV:\n" + cv_text +
        "\n\nPlease provide responses that are professional, detailed, and "
        "aligned with the job role. Use " + language + " language for all responses."
    )

    try:
        response = openai.ChatCompletion.create(
            model="gpt-4-turbo",
            messages=[
                {
                    "role": "system",
                    "content": (
                        "You are a professional AI career assistant writing in " +
                        language + "."
                    )
                },
                {"role": "user", "content": prompt}
            ],
            temperature=0.7,
            max_tokens=2500
        )

        formatted_response = (
            response['choices'][0]['message']['content'].strip()
        )
        return formatted_response

    except openai.error.OpenAIError as e:
        raise Exception(f"OpenAI API Error: {str(e)}")
