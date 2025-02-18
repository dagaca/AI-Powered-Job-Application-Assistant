"""
This module runs the Flask application for the AI-Powered Job Application Assistant.
"""

from app import app

if __name__ == '__main__':
    app.run(debug=True, port=8080)
