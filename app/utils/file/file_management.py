"""
Module for managing file formats, saving temporary files, and ensuring the
existence of necessary directories. Handles file format mapping, saving files
in different formats (PDF, DOCX, TXT), and managing temporary files.
"""

import os
import uuid
from dotenv import load_dotenv
from werkzeug.datastructures import FileStorage
from docx import Document
from fpdf import FPDF

# Load environment variables
load_dotenv()
OUTPUT_DIR = os.getenv("OUTPUT_DIR")
FONT_PATH = os.getenv("FONT_PATH")


def ensure_directory_exists(directory):
    """
    Ensures that the specified directory exists. If it doesn't exist, creates it.
    
    Args:
        directory (str): The path of the directory to check and create if needed.
    """
    if not os.path.exists(directory):
        os.makedirs(directory, exist_ok=True)


# Ensure the output directory exists
ensure_directory_exists(OUTPUT_DIR)


def get_file_suffix(filename):
    """
    Extracts and returns the file extension from a given filename.
    
    Args:
        filename (str): The filename to extract the extension from.
    
    Returns:
        str: The file extension, including the dot (e.g., '.pdf').
    """
    return os.path.splitext(filename)[-1]


def save_temporary_file(file: FileStorage, temp_dir: str):
    """
    Saves the uploaded file to a temporary directory with a unique name.
    
    Args:
        file (FileStorage): The uploaded file to save.
        temp_dir (str): The directory where the file should be saved.
    
    Returns:
        str: The path where the file was saved.
    """
    ensure_directory_exists(temp_dir)
    extension = get_file_suffix(file.filename)
    unique_filename = f"{uuid.uuid4()}{extension}"
    save_path = os.path.join(temp_dir, unique_filename)
    file.save(save_path)
    return save_path


def save_as_pdf(cover_letter):
    """
    Saves the cover letter as a PDF file using Noto Sans font (full Unicode
    support).
    
    Args:
        cover_letter (str): The cover letter text.
    
    Returns:
        str: The path to the generated PDF file.
    
    Raises:
        Exception: If an error occurs while saving the PDF.
    """
    try:
        file_id = str(uuid.uuid4())
        pdf_path = os.path.join(OUTPUT_DIR, f"{file_id}.pdf")
        pdf = FPDF()
        pdf.add_page()
        pdf.add_font("NotoSans", "", FONT_PATH, uni=True)
        pdf.set_font("NotoSans", size=12)
        pdf.multi_cell(190, 10, cover_letter)
        pdf.output(pdf_path, "F")
        return pdf_path
    except Exception as e:
        raise Exception(f"Error saving PDF file: {str(e)}")


def save_as_docx(cover_letter):
    """
    Saves the generated cover letter as a DOCX file.
    
    Args:
        cover_letter (str): The job description used to generate the cover letter.
    
    Returns:
        str: The file path of the saved DOCX file.
    
    Raises:
        Exception: If there is an error while saving the DOCX file.
    """
    try:
        file_id = str(uuid.uuid4())
        docx_path = os.path.join(OUTPUT_DIR, f"{file_id}.docx")
        doc = Document()
        doc.add_paragraph(cover_letter)
        doc.save(docx_path)
        return docx_path
    except Exception as e:
        raise Exception(f"Error saving DOCX file: {str(e)}")


def save_as_txt(cover_letter):
    """
    Saves the generated cover letter as a TXT file.
    
    Args:
        cover_letter (str): The job description used to generate the cover letter.
    
    Returns:
        str: The file path of the saved TXT file.
    
    Raises:
        Exception: If there is an error while saving the TXT file.
    """
    try:
        file_id = str(uuid.uuid4())
        txt_path = os.path.join(OUTPUT_DIR, f"{file_id}.txt")
        with open(txt_path, "w", encoding="utf-8") as f:
            f.write(cover_letter)
        return txt_path
    except Exception as e:
        raise Exception(f"Error saving TXT file: {str(e)}")


# File format functions mapping
FORMAT_FUNCTIONS = {
    "pdf": save_as_pdf,
    "docx": save_as_docx,
    "txt": save_as_txt
}


def get_format_function(file_format):
    """
    Retrieves the corresponding file saving function based on the file format.
    
    Args:
        file_format (str): The file format (e.g., 'pdf', 'docx', 'txt').
    
    Returns:
        function: The function capable of saving the file in the requested format.
    """
    return FORMAT_FUNCTIONS.get(file_format)
