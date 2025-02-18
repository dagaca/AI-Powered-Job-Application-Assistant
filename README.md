# AI-Powered Job Application Assistant

**AI-Powered Job Application Assistant** is a comprehensive tool designed to help job 
seekers streamline their application process. This project leverages advanced AI models 
to generate personalized and professional cover letters, evaluate CV-job description 
alignment, and generate interview questions with sample answers. Built with Flask, 
OpenAI GPT-4, and TensorFlow Hub's Universal Sentence Encoder, it integrates several 
document processing and utility modules to provide an end-to-end job application 
automation solution.

---

## Features

- **Cover Letter Generation:** Create tailored cover letters based on a job 
  description or with additional CV context.
- **CV Matching:** Analyze and compare a candidate’s CV against a job 
  description to compute a similarity score and provide professional 
  evaluation.
- **Interview Preparation:** Generate interview questions and sample 
  answers relevant to the job role.
- **Document Extraction:** Extract text from various document formats 
  (PDF, DOCX, TXT).
- **File Management:** Manage temporary file storage and save generated 
  documents in specified formats (PDF, DOCX, TXT).
- **Rate Limiting & API Security:** Secure endpoints with API key 
  authentication and enforce rate limits.

---

## Directory Structure

/AI-Powered-Job-Application-Assistant
├── app

│   ├── __init__.py                # Initializes Flask app and loads configurations

│   ├── routes.py                  # Defines all API endpoints

│   └── utils

│       ├── authentication         # Authentication utilities

│       │     └── auth.py

│       ├── document               # Document processing utilities

│       │     ├── cover_letter_generator.py

│       │     └── document_extraction.py

│       ├── evaluation             # CV matching and interview prep utilities

│       │     ├── cv_matcher.py

│       │     └── interview_preparation.py

│       ├── file                   # File management and saving utilities

│       │     ├── file_management.py

│       │     └── file_saver.py

│       └── rate                   # Rate limiting utilities

│             └── rate_limiter.py

├── config

│   ├── config.py                  # Application-wide configuration settings

│   └── log_config.py              # Logging configuration

├── language

│   └── supported_languages.py     # Supported languages and helper functions

├── fonts                          # Contains font files (e.g., NotoSans-Regular.ttf)

├── logs                           # Log files are stored here

├── output                         # Generated output files are stored here

├── temp                           # Temporary files are stored here

├── .env                           # Environment variables

├── requirements.txt               # Python dependencies

└── run.py                         # Entry point for the Flask application

---

## Environment Setup

Create a `.env` file in the project root with the following contents:

```ini
# Secret key for Flask application (used for session management)
SECRET_KEY=your-secure-secret-key

# API Key for authentication (required for accessing endpoints)
API_KEY=your-secure-api-key

# OpenAI API Key for generating cover letters
OPENAI_API_KEY=your-openai-api-key

# Directory for logs
LOG_DIR=logs
LOG_FILE=app.log

# Rate limit for API requests (e.g., "5 per minute", "10 per hour")
RATE_LIMIT=100 per minute

# Temporary directory for storing generated files
TEMP_DIR=temp

# Directory for saving generated output files
OUTPUT_DIR=output

# Font path for PDF generation
FONT_PATH=fonts/NotoSans-Regular.ttf

# Universal Sentence Encoder URL
UNIVERSAL_SENTENCE_ENCODER_URL=https://tfhub.dev/google/universal-sentence-encoder/4

---

## Installation

Clone the repository:

```bash
git clone https://github.com/yourusername/AI-Powered-Job-Application-Assistant.git
cd AI-Powered-Job-Application-Assistant

