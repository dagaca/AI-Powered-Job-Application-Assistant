"""
Defines API endpoints for AI-Powered Job Application Assistant.
"""

# ======================
# Standard Library Imports
# ======================
import os
import tempfile

# ======================
# Third-party Imports
# ======================
from flask import request, jsonify, send_file
from dotenv import load_dotenv

# ======================
# Application & Configuration Imports
# ======================
from app import app, limiter
from config.log_config import configure_logging, log_request_info, log_response_info

# ======================
# Language Support Imports
# ======================
from language.supported_languages import SUPPORTED_LANGUAGES, get_language_name

# ======================
# Document Processing Imports
# ======================
from app.utils.document.cover_letter_generator import (
    generate_cover_letter,
    generate_cover_letter_with_cv
)
from app.utils.document.document_extraction import extract_text

# ======================
# Authentication & Rate Limiting Imports
# ======================
from app.utils.authentication.auth import api_key_required  # API Key authentication decorator
from app.utils.rate.rate_limiter import RATE_LIMIT

# ======================
# File Management Imports
# ======================
from app.utils.file.file_management import (
    ensure_directory_exists,
    save_temporary_file,
    get_format_function
)

# ======================
# Evaluation & Interview Preparation Imports
# ======================
from app.utils.evaluation.cv_matcher import evaluate_cv_with_openai, compute_similarity_score
from app.utils.evaluation.interview_preparation import generate_interview_questions

# Configure logging
configure_logging(app)
log_request_info(app)
log_response_info(app)

# Load environment variables
load_dotenv()
TEMP_DIR = os.getenv("TEMP_DIR")

# Ensure the temporary directory exists
ensure_directory_exists(TEMP_DIR)


@app.route("/health", methods=["GET"])
def health_check():
    """
    CLG-001 (Health Check)
    This endpoint performs a system health check to verify that the API is running correctly.

    -------
    tags:
      - System
    responses:
      '200':
        description: API is running successfully.
        content:
          application/json:
            schema:
              type: object
              properties:
                healthy:
                  type: string
                  example: "Ok"
    """
    app.logger.info("Health check endpoint accessed.")
    return jsonify({"healthy": "Ok"}), 200

@app.route('/generate_cover_letter', methods=['POST'])
@api_key_required
@limiter.limit(RATE_LIMIT)
def generate_cover_letter_endpoint():
    """
    CLG-002 (Generate Cover Letter)
    Generates a professional cover letter based on the given job description.

    -------
    tags:
      - Cover Letter
    consumes:
      - application/json
    produces:
      - application/octet-stream
    parameters:
      - in: header
        name: X-API-KEY
        required: true
        description: API Key required for authentication.
        schema:
          type: string
      - in: body
        name: body
        required: true
        description: JSON data containing the job description, file format,
          and supported language.
        schema:
          type: object
          required:
            - job_description
            - file_format
            - language
          properties:
            job_description:
              type: string
              description: "The job description text that will be used to generate "
                           "the cover letter."
              example: ("We are looking for a Python Developer with Flask "
                        "experience.")
            file_format:
              type: string
              description: "The desired output format."
              enum: ["pdf", "docx", "txt"]
              example: "pdf"
            language:
              type: string
              description: "The language in which the cover letter should be "
                           "generated."
              enum: ["en", "tr", "de", "fr", "es", "it", "nl"]
              example: "en"
    responses:
      '200':
        description: "Cover letter generated successfully and ready for download."
        content:
          application/octet-stream:
            schema:
              type: string
              format: binary
      '400':
        description: (
            "Job description, valid file format (pdf, docx, txt), and supported "
            "language (en, tr, de, fr, es, it, nl) are required."
        )
        content:
          application/json:
            schema:
              type: object
              properties:
                error:
                  type: string
                  example: (
                      "Job description, valid file format (pdf, docx, txt), and "
                      "supported language (en, tr, de, fr, es, it, nl) are required."
                  )
      '401':
        description: "Unauthorized. Missing or invalid API Key."
        content:
          application/json:
            schema:
              type: object
              properties:
                error:
                  type: string
                  example: "Invalid API Key."
      '403':
        description: "Forbidden. API key is not authorized."
        content:
          application/json:
            schema:
              type: object
              properties:
                error:
                  type: string
                  example: "Access denied."
      '500':
        description: "Internal Server Error. An unexpected error occurred."
        content:
          application/json:
            schema:
              type: object
              properties:
                error:
                  type: string
                  example: "Internal server error."
    """
    try:
        app.logger.info("Processing cover letter generation request.")

        # Validate JSON request
        if not request.is_json:
            app.logger.warning("Request must be in JSON format.")
            return jsonify({"error": "Request must be in JSON format."}), 415

        data = request.get_json()
        job_description = data.get("job_description")
        file_format = data.get("file_format", "").lower()
        language = data.get("language", "en").lower()

        # Validate job description
        if not job_description or not job_description.strip():
            app.logger.warning("Missing or empty job description.")
            return jsonify({"error": "Job description is required."}), 400

        # Validate file format
        format_function = get_format_function(file_format)
        if not format_function:
            app.logger.warning(
                f"Unsupported file format requested: {file_format}"
            )
            return jsonify(
                {"error": "Invalid file format. Choose from 'pdf', 'docx', 'txt'."}
            ), 400

        # Validate language
        language_name = get_language_name(language)
        if not language_name:
            app.logger.warning(
                f"Unsupported language requested: {language}"
            )
            return jsonify(
                {"error": f"Unsupported language. Choose from "
                          f"{list(SUPPORTED_LANGUAGES.keys())}."}
            ), 400

        # Generate cover letter
        app.logger.info("Generating cover letter with OpenAI API.")
        cover_letter = generate_cover_letter(job_description, language_name)

        # Save cover letter to specified format
        file_path = format_function(cover_letter)

        # Convert to absolute path for serving the file
        absolute_path = os.path.abspath(file_path)
        app.logger.info(
            f"Cover letter successfully generated at {absolute_path}."
        )

        return send_file(absolute_path, as_attachment=True)

    except Exception as e:
        app.logger.error(f"Internal Server Error: {str(e)}", 
                           exc_info=True)
        return jsonify({"error": "Internal server error."}), 500

@app.route('/generate_cover_letter_with_cv', methods=['POST'])
@api_key_required
@limiter.limit(RATE_LIMIT)
def generate_cover_letter_with_cv_endpoint():
    """
    CLG-003 (Generate Cover Letter with CV)
    Generates a professional cover letter based on both the job description
    and CV content.
    
    -------
    tags:
      - Cover Letter
    consumes:
      - multipart/form-data
    parameters:
      - in: header
        name: X-API-KEY
        required: true
        description: API Key required for authentication.
        schema:
          type: string
      - in: formData
        name: cv_file
        required: true
        description: The user's CV file in `pdf`, `docx`, or `txt` format.
        type: file
      - in: formData
        name: job_description
        required: true
        description: The job description text used for generating the cover
          letter.
        type: string
      - in: formData
        name: file_format
        required: true
        description: The desired output format.
        type: string
        enum: ["pdf", "docx", "txt"]
      - in: formData
        name: language
        required: true
        description: The language in which the cover letter should be
          generated.
        type: string
        enum: ["en", "tr", "de", "fr", "es", "it", "nl"]
    responses:
      '200':
        description: File download starts automatically.
        content:
          application/octet-stream:
            schema:
              type: string
              format: binary
      '400':
        description: Bad Request. The CV file or job description is missing/
          invalid.
        content:
          application/json:
            schema:
              type: object
              properties:
                error:
                  type: string
                  example: (
                      "CV file and job description are required."
                  )
      '415':
        description: Unsupported Media Type. The request body must be 
          multipart/form-data.
        content:
          application/json:
            schema:
              type: object
              properties:
                error:
                  type: string
                  example: "Request must be in multipart/form-data format."
      '500':
        description: Internal server error.
        content:
          application/json:
            schema:
              type: object
              properties:
                error:
                  type: string
                  example: "Internal server error."
    """
    try:
        app.logger.info("Processing cover letter generation with CV.")

        job_description = request.form.get("job_description")
        file_format = request.form.get("file_format", "").lower()
        language = request.form.get("language", "en").lower()
        cv_file = request.files.get("cv_file")

        if not cv_file or not job_description:
            app.logger.warning("Missing CV file or job description.")
            return jsonify({"error": "CV file and job description are required."}
                           ), 400

        # Ensure the temp folder exists
        ensure_directory_exists(TEMP_DIR)

        # Process file within a temporary directory
        with tempfile.TemporaryDirectory(dir=TEMP_DIR) as temp_dir:
            temp_file_path = save_temporary_file(cv_file, temp_dir)
            cv_text = extract_text(temp_file_path)
            app.logger.info("CV text extracted successfully.")

            # Validate language input
            language_name = get_language_name(language)
            if not language_name:
                app.logger.error(f"Unsupported language: {language}")
                return jsonify(
                    {"error": ("Unsupported language. Choose from " +
                               "['en', 'tr', 'de', 'fr', 'es', 'it', 'nl'].")}
                ), 400

            # Generate cover letter using OpenAI
            app.logger.info(
                "Generating cover letter using OpenAI with job description and CV text."
            )
            cover_letter = generate_cover_letter_with_cv(
                job_description, cv_text, language_name
            )

            # Format and save cover letter in requested file format
            format_function = get_format_function(file_format)
            if not format_function:
                app.logger.error(f"Invalid file format: {file_format}")
                return jsonify(
                    {"error": ("Invalid file format. Choose from 'pdf', "
                               "'docx', 'txt'.")}
                ), 400

            file_path = format_function(cover_letter)
            absolute_path = os.path.abspath(file_path)
            app.logger.info(
                f"Cover letter successfully generated and saved at {absolute_path}"
            )

            return send_file(absolute_path, as_attachment=True)

    except Exception as e:
        app.logger.error(
            f"Internal Server Error: {str(e)}", exc_info=True
        )
        return jsonify({"error": "Internal server error."}), 500

@app.route('/evaluate_cv_match', methods=['POST'])
@api_key_required
@limiter.limit(RATE_LIMIT)
def evaluate_cv_match_endpoint():
    """
    CLG-004 (Evaluate CV and Job Match)
    Analyzes the similarity between a job description and a candidate's CV.
    Returns a professional evaluation and a similarity score.

    -------
    tags:
      - CV Matching
    consumes:
      - multipart/form-data
    parameters:
      - in: header
        name: X-API-KEY
        required: true
        description: API Key required for authentication.
        schema:
          type: string
      - in: formData
        name: cv_file
        required: true
        description: The user's CV file in `pdf`, `docx`, or `txt` format.
        type: file
      - in: formData
        name: job_description
        required: true
        description: The job description text to compare against the CV.
        type: string
      - in: formData
        name: language
        required: true
        description: The language for the evaluation report.
        type: string
        enum: ["en", "tr", "de", "fr", "es", "it", "nl"]
    responses:
      '200':
        description: Evaluation and similarity score successfully generated.
        content:
          application/json:
            schema:
              type: object
              properties:
                similarity_score:
                  type: number
                  format: float
                  example: 0.85
                evaluation:
                  type: string
                  example: ("The candidate's experience closely matches the job "
                            "requirements, especially in AI model development.")
      '400':
        description: Bad Request. Missing CV file or job description.
        content:
          application/json:
            schema:
              type: object
              properties:
                error:
                  type: string
                  example: "CV file and job description are required."
      '415':
        description: Unsupported Media Type. The request body must be 
          multipart/form-data.
        content:
          application/json:
            schema:
              type: object
              properties:
                error:
                  type: string
                  example: "Request must be in multipart/form-data format."
      '500':
        description: Internal server error.
        content:
          application/json:
            schema:
              type: object
              properties:
                error:
                  type: string
                  example: "Internal server error."
    """
    try:
        app.logger.info(
            "Processing CV and job description similarity evaluation."
        )

        job_description = request.form.get("job_description")
        language = request.form.get("language", "en").lower()
        cv_file = request.files.get("cv_file")

        if not cv_file or not job_description:
            app.logger.warning("Missing CV file or job description.")
            return jsonify(
                {"error": "CV file and job description are required."}
            ), 400

        # Ensure the temp folder exists
        ensure_directory_exists(TEMP_DIR)

        # Process the file within a temporary directory
        with tempfile.TemporaryDirectory(dir=TEMP_DIR) as temp_dir:
            temp_file_path = save_temporary_file(cv_file, temp_dir)
            cv_text = extract_text(temp_file_path)
            app.logger.info("CV text extracted successfully.")

            # Compute similarity score
            similarity_score = compute_similarity_score(
                job_description, cv_text, language
            )

            # Validate language input
            language = get_language_name(language)
            if not language:
                app.logger.error(f"Unsupported language: {language}")
                return jsonify({
                    "error": ("Unsupported language. Choose from " +
                              "['en', 'tr', 'de', 'fr', 'es', 'it', 'nl'].")
                }), 400

            # Generate AI evaluation
            evaluation = evaluate_cv_with_openai(
                job_description, cv_text, language
            )

            response = {
                "similarity_score": round(similarity_score, 2),
                "evaluation": evaluation
            }

            return jsonify(response), 200

    except Exception as e:
        app.logger.error(
            f"Internal Server Error: {str(e)}", exc_info=True
        )
        return jsonify({"error": "Internal server error."}), 500

@app.route('/generate_interview_questions', methods=['POST'])
@api_key_required
@limiter.limit(RATE_LIMIT)
def generate_interview_questions_endpoint():
    """
    CLG-005 (Generate Interview Questions & Sample Answers)
    Generates 10 potential interview questions and CV-specific answers based on
    the provided job description.

    -------
    tags:
      - Interview Preparation
    consumes:
      - multipart/form-data
    parameters:
      - in: header
        name: X-API-KEY
        required: true
        description: API Key required for authentication.
        schema:
          type: string
      - in: formData
        name: cv_file
        required: true
        description: The user's CV file in `pdf`, `docx`, or `txt` format.
        type: file
      - in: formData
        name: job_description
        required: true
        description: The job description text used for generating 
          interview questions.
        type: string
      - in: formData
        name: language
        required: true
        description: The language for the interview preparation.
        type: string
        enum: ["en", "tr", "de", "fr", "es", "it", "nl"]
    responses:
      '200':
        description: Interview questions and sample answers successfully
          generated.
        content:
          application/json:
            schema:
              type: object
              properties:
                interview_qa:
                  type: string
                  description: "Generated interview questions and sample answers "
                               "in a structured format."
                  example: |
                    Q1: Can you describe your experience in AI model 
                        development?
                    A1: Certainly! In my previous role at XYZ Corp, I 
                        developed...
                    
                    Q2: How do you approach model optimization?
                    A2: I employ various techniques such as 
                        hyperparameter tuning...
      '400':
        description: "Bad Request. The CV file or job description is missing."
        content:
          application/json:
            schema:
              type: object
              properties:
                error:
                  type: string
                  example: "CV file and job description are required."
      '415':
        description: "Unsupported Media Type. The request body must be "
                     "multipart/form-data."
        content:
          application/json:
            schema:
              type: object
              properties:
                error:
                  type: string
                  example: "Request must be in multipart/form-data format."
      '500':
        description: "Internal Server Error."
        content:
          application/json:
            schema:
              type: object
              properties:
                error:
                  type: string
                  example: "Internal server error."
    """
    try:
        app.logger.info("Processing interview question generation request.")

        job_description = request.form.get("job_description")
        language = request.form.get("language", "en").lower()
        cv_file = request.files.get("cv_file")

        if not cv_file or not job_description:
            app.logger.warning("Missing CV file or job description.")
            return jsonify(
                {"error": "CV file and job description are required."}
            ), 400

        # Ensure the temp folder exists
        ensure_directory_exists(TEMP_DIR)

        # Process the file within a temporary directory
        with tempfile.TemporaryDirectory(dir=TEMP_DIR) as temp_dir:
            temp_file_path = save_temporary_file(cv_file, temp_dir)
            cv_text = extract_text(temp_file_path)
            app.logger.info("CV text extracted successfully.")

            # Validate language input
            language = get_language_name(language)
            if not language:
                app.logger.error(f"Unsupported language: {language}")
                return jsonify(
                    {"error": ("Unsupported language. Choose from " +
                               "['en', 'tr', 'de', 'fr', 'es', 'it', 'nl'].")}
                ), 400

            # Generate interview questions & answers using OpenAI
            interview_qa = generate_interview_questions(
                job_description, cv_text, language
            )

            response = {"interview_qa": interview_qa}

            return jsonify(response), 200

    except Exception as e:
        app.logger.error(
            f"Internal Server Error: {str(e)}", exc_info=True
        )
        return jsonify({"error": "Internal server error."}), 500
