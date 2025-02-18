"""
Module for extracting text from various document formats including PDF, DOCX,
and TXT files. Utilizes pdfplumber for PDFs and python-docx for DOCX files.
"""

import pdfplumber
from docx import Document
from app.utils.file.file_management import get_file_suffix


def extract_text(file_path):
    """
    Extracts text from a given document based on its file extension.

    Args:
        file_path (str): The full path of the document file.

    Returns:
        str: Extracted text content.

    Raises:
        ValueError: If the file format is not supported.
    """
    file_extension = get_file_suffix(file_path).lower()

    if file_extension == '.pdf':
        return extract_text_from_pdf(file_path)
    elif file_extension == '.docx':
        return extract_text_from_docx(file_path)
    elif file_extension == '.txt':
        return extract_text_from_txt(file_path)
    else:
        raise ValueError("Unsupported file format.")


def extract_text_from_pdf(pdf_path):
    """
    Extracts text content from a PDF file using pdfplumber.

    Args:
        pdf_path (str): The path to the PDF file.

    Returns:
        str: Extracted text content from all readable pages.
    """
    with pdfplumber.open(pdf_path) as pdf:
        return "\n".join(
            page.extract_text() or '' 
            for page in pdf.pages 
            if page.extract_text()
        )


def extract_text_from_docx(docx_path):
    """
    Extracts text content from a DOCX file using python-docx.

    Args:
        docx_path (str): The path to the DOCX file.

    Returns:
        str: Extracted text content from all paragraphs.
    """
    doc = Document(docx_path)
    return "\n".join(paragraph.text for paragraph in doc.paragraphs)


def extract_text_from_txt(txt_path):
    """
    Reads and extracts text from a plain text (.txt) file.

    Args:
        txt_path (str): The path to the TXT file.

    Returns:
        str: The content of the text file.
    """
    with open(txt_path, "r", encoding="utf-8") as file:
        return file.read()
