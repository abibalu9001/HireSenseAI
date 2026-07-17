"""
Resume & JD Parser — extracts raw text from PDF/DOCX files
and parses structured fields (name, email, phone, skills, etc.)
"""

import re
import io
import logging

logger = logging.getLogger(__name__)


# ─── Text Extraction ──────────────────────────────────────────────────────────

def extract_text_from_pdf(file_path_or_obj):
    """Extract text from a PDF file. Tries pdfplumber first, PyMuPDF as fallback."""
    text = ""

    # Handle Django FieldFile / file-like objects
    if hasattr(file_path_or_obj, 'read'):
        file_bytes = file_path_or_obj.read()
        if hasattr(file_path_or_obj, 'seek'):
            file_path_or_obj.seek(0)
    else:
        with open(file_path_or_obj, 'rb') as f:
            file_bytes = f.read()

    # Try pdfplumber
    try:
        import pdfplumber
        with pdfplumber.open(io.BytesIO(file_bytes)) as pdf:
            for page in pdf.pages:
                page_text = page.extract_text()
                if page_text:
                    text += page_text + "\n"
        if text.strip():
            return text.strip()
    except Exception as e:
        logger.warning(f"pdfplumber failed: {e}")

    # Fallback: PyMuPDF
    try:
        import fitz  # PyMuPDF
        doc = fitz.open(stream=file_bytes, filetype="pdf")
        for page in doc:
            text += page.get_text() + "\n"
        doc.close()
        if text.strip():
            return text.strip()
    except Exception as e:
        logger.warning(f"PyMuPDF failed: {e}")

    logger.error("Could not extract text from PDF")
    return ""


def extract_text_from_docx(file_path_or_obj):
    """Extract text from a DOCX file using python-docx."""
    text = ""
    try:
        from docx import Document
        if hasattr(file_path_or_obj, 'read'):
            file_bytes = file_path_or_obj.read()
            if hasattr(file_path_or_obj, 'seek'):
                file_path_or_obj.seek(0)
            doc = Document(io.BytesIO(file_bytes))
        else:
            doc = Document(file_path_or_obj)

        for para in doc.paragraphs:
            text += para.text + "\n"
        # Also extract tables
        for table in doc.tables:
            for row in table.rows:
                for cell in row.cells:
                    text += cell.text + " "
                text += "\n"
    except Exception as e:
        logger.error(f"python-docx failed: {e}")
    return text.strip()


def extract_text(file_field):
    """Auto-detect file type and extract text."""
    name = file_field.name.lower()
    if name.endswith('.pdf'):
        return extract_text_from_pdf(file_field)
    elif name.endswith('.docx') or name.endswith('.doc'):
        return extract_text_from_docx(file_field)
    else:
        # Try reading as plain text
        try:
            return file_field.read().decode('utf-8', errors='ignore')
        except Exception:
            return ""


# ─── Field Parsers ────────────────────────────────────────────────────────────

def extract_email(text):
    emails = re.findall(r'[\w.+-]+@[\w-]+\.[a-zA-Z]{2,}', text)
    return emails[0] if emails else ""


def extract_phone(text):
    phones = re.findall(
        r'(?:\+91[-\s]?)?(?:\(?\d{3,5}\)?[-\s]?)?\d{3}[-\s]?\d{4}', text
    )
    return phones[0].strip() if phones else ""


def extract_name(text):
    """
    Heuristic: The candidate name is usually on one of the first 3 lines
    and looks like 'Firstname Lastname' — no numbers, short line.
    """
    lines = [l.strip() for l in text.split('\n') if l.strip()]
    for line in lines[:5]:
        # Skip lines with email, phone, URLs or common headers
        if re.search(r'[@://|•|resume|curriculum|vitae|\d{5,}]', line, re.IGNORECASE):
            continue
        words = line.split()
        if 2 <= len(words) <= 4 and all(w[0].isupper() for w in words if w.isalpha()):
            return line
    return lines[0] if lines else ""


def extract_section(text, section_keywords, next_section_keywords=None):
    """
    Extract a section of text by finding lines that match section headers.
    """
    lines = text.split('\n')
    in_section = False
    section_text = []
    next_kws = next_section_keywords or []

    for line in lines:
        line_lower = line.lower().strip()
        if any(kw in line_lower for kw in section_keywords) and len(line.strip()) < 50:
            in_section = True
            continue
        if in_section:
            if next_kws and any(kw in line_lower for kw in next_kws) and len(line.strip()) < 50:
                break
            section_text.append(line)

    return '\n'.join(section_text).strip()


def parse_resume(text):
    """
    Parse a resume text into structured fields.
    Returns a dict: name, email, phone, skills_text, education_text,
    experience_text, projects_text
    """
    if not text:
        return {}

    return {
        'name': extract_name(text),
        'email': extract_email(text),
        'phone': extract_phone(text),
        'skills_text': extract_section(
            text,
            ['skills', 'technical skills', 'core competencies', 'technologies', 'tools'],
            ['experience', 'education', 'projects', 'work', 'employment', 'certifications']
        ),
        'education_text': extract_section(
            text,
            ['education', 'academic', 'qualification', 'degree'],
            ['experience', 'skills', 'projects', 'work', 'employment']
        ),
        'experience_text': extract_section(
            text,
            ['experience', 'work experience', 'employment', 'professional experience', 'work history'],
            ['education', 'skills', 'projects', 'certifications', 'achievements']
        ),
        'projects_text': extract_section(
            text,
            ['projects', 'personal projects', 'academic projects', 'key projects'],
            ['experience', 'education', 'skills', 'certifications', 'achievements']
        ),
    }


def parse_job_description(text):
    """
    Parse a job description text to extract key fields.
    """
    return {
        'skills_text': extract_section(
            text,
            ['requirements', 'required skills', 'skills', 'qualifications', 'must have', 'technologies'],
            ['responsibilities', 'about', 'benefits', 'salary']
        ),
        'experience_text': extract_section(
            text,
            ['experience', 'years of experience'],
            ['skills', 'education', 'responsibilities']
        ),
        'education_text': extract_section(
            text,
            ['education', 'qualification', 'degree'],
            ['skills', 'experience', 'responsibilities']
        ),
    }
