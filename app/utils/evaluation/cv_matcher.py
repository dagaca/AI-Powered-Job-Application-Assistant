"""
Handles CV and job description similarity analysis using Universal 
Sentence Encoder (USE) for multilingual support.
"""

import os
import tensorflow_hub as hub
import nltk
from nltk.corpus import stopwords
from sklearn.metrics.pairwise import cosine_similarity
from dotenv import load_dotenv
import openai
from language.supported_languages import SUPPORTED_LANGUAGES

# Load environment variables
load_dotenv()
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
USE_MODEL_URL = os.getenv("UNIVERSAL_SENTENCE_ENCODER_URL")

# Load Universal Sentence Encoder (USE) from TensorFlow Hub
embed = hub.load(USE_MODEL_URL)

# Ensure NLTK stopwords are available
nltk.download('stopwords', quiet=True)


def get_stopwords(language):
    """
    Retrieves stopwords dynamically using NLTK.
    
    Args:
        language (str): Language code.
    
    Returns:
        set: A set of stopwords for the given language, or an empty set
             if not available.
    """
    try:
        if language in stopwords.fileids():
            return set(stopwords.words(language))
    except LookupError:
        nltk.download('stopwords', quiet=True)
        if language in stopwords.fileids():
            return set(stopwords.words(language))
    return set()


def preprocess_text(text, language):
    """
    Removes stopwords from the given text dynamically.
    
    Args:
        text (str): The input text.
        language (str): Language code.
    
    Returns:
        str: Processed text with stopwords removed.
    """
    stop_words = get_stopwords(language)
    words = text.split()
    filtered_words = [word for word in words 
                      if word.lower() not in stop_words]
    return " ".join(filtered_words)


def compute_similarity_score(job_description, cv_text, language="en"):
    """
    Computes similarity between a job description and a CV using the 
    Universal Sentence Encoder (USE) embeddings and cosine similarity.
    
    Args:
        job_description (str): Job description text.
        cv_text (str): Extracted CV text.
        language (str): Language code (default: 'en').
    
    Returns:
        float: Similarity score between 0.0 and 1.0.
    
    Raises:
        ValueError: If job description or CV text is empty.
        Exception: If embedding computation fails.
    """
    if not job_description.strip() or not cv_text.strip():
        raise ValueError("Job description and CV text cannot be empty.")
    
    if language not in SUPPORTED_LANGUAGES:
        raise ValueError(f"Unsupported language: {language}")
    
    try:
        job_clean = preprocess_text(job_description, language)
        cv_clean = preprocess_text(cv_text, language)
        
        job_vector = embed([job_clean]).numpy()
        cv_vector = embed([cv_clean]).numpy()
        
        similarity = cosine_similarity(job_vector, cv_vector)[0][0]
        return float(similarity)
    
    except Exception as e:
        raise Exception(f"Error computing similarity score: {str(e)}")


def evaluate_cv_with_openai(job_description, cv_text, language='english'):
    """
    Generates a professional evaluation of how well a candidate's CV matches 
    the job description using OpenAI's GPT model. The evaluation considers 
    language-specific nuances and provides insights into the candidate's 
    strengths, gaps, and overall suitability.
    
    Args:
        job_description (str): The text of the job description.
        cv_text (str): The text extracted from the candidate's CV.
        language (str): The language for generating the evaluation.
    
    Returns:
        str: An AI-generated professional evaluation report.
    
    Raises:
        Exception: If there is an error while communicating with the OpenAI API.
    """
    openai.api_key = os.getenv("OPENAI_API_KEY")
    
    prompt = (
        "As an HR manager, you are tasked with evaluating how well a candidate's "
        "CV matches the job description provided. Conduct a thorough analysis and "
        "provide feedback on:\n\n"
        "1. Key strengths that align well with the job requirements.\n"
        "2. Areas where the candidate may lack the necessary qualifications or "
        "experience.\n"
        "3. A final recommendation on the candidate's suitability for the position.\n\n"
        "Please deliver your evaluation in " + language + ".\n\n"
        "Job Description:\n" + job_description + "\n\n" +
        "CV Content:\n" + cv_text
    )
    
    try:
        response = openai.ChatCompletion.create(
            model="gpt-4-turbo",
            messages=[
                {"role": "system", 
                 "content": ("Provide a detailed professional evaluation in " +
                             language + ".")},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7,
            max_tokens=2000
        )
        evaluation = response['choices'][0]['message']['content'].strip()
        return evaluation
    except openai.error.OpenAIError as e:
        raise Exception(f"OpenAI API Error: {str(e)}")
