"""
Defines supported languages for AI-Powered Job Application Assistant.
"""

SUPPORTED_LANGUAGES = {
    "en": "English",
    "tr": "Turkish",
    "de": "German",
    "fr": "French",
    "es": "Spanish",
    "it": "Italian",
    "nl": "Dutch"
}

def get_language_name(language_code):
    """
    Returns the full language name based on the language code.

    Args:
        language_code (str): Language code (e.g., 'en', 'tr', 'de').

    Returns:
        str: Full language name if found, otherwise None.
    """
    return SUPPORTED_LANGUAGES.get(language_code, None)
