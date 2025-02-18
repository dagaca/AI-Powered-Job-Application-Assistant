"""
Initializes the Flask application with all modules.
"""

import os
from flask import Flask
from flasgger import Swagger
from dotenv import load_dotenv
from app.utils.rate.rate_limiter import setup_rate_limiter
from config.log_config import (
    configure_logging, log_request_info, log_response_info
)

# Load environment variables
load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY")  # Load SECRET_KEY from .env

# Swagger Configuration
app.config['SWAGGER'] = {
    'title': 'AI-Powered Job Application Assistant',
    'description': (
        "The AI-Powered Job Application Assistant provides a comprehensive suite "
        "of tools to help job seekers streamline their application process. This "
        "project leverages OpenAI to generate personalized and professional cover "
        "letters, evaluate the alignment between job descriptions and CVs, generate "
        "interview questions with sample answers, and compute similarity scores "
        "between a candidate’s experience and job postings."
    ),
    'version': '1.0.0'
}
swagger = Swagger(app)

# Rate Limiter
limiter = setup_rate_limiter(app)

# Configure Logging
configure_logging(app)
log_request_info(app)
log_response_info(app)

# Import routes
from app import routes
