import pdfplumber
import re
from typing import Dict

def extract_text_from_pdf(pdf_file) -> str:
    """Extract all text from PDF file"""
    text = ""
    with pdfplumber.open(pdf_file) as pdf:
        for page in pdf.pages:
            text += page.extract_text() + "\n"
    return text

def parse_resume_sections(text: str) -> Dict[str, str]:
    """Parse resume text into sections"""
    sections = {
        "contact_info": "",
        "summary": "",
        "experience": "",
        "education": "",
        "skills": "",
        "certifications": "",
        "projects": "",
        "other": ""
    }

    # Common section headers patterns
    section_patterns = {
        "contact_info": r"(contact|personal information|personal details)",
        "summary": r"(summary|profile|objective|about|professional summary)",
        "experience": r"(experience|work experience|employment|work history|professional experience)",
        "education": r"(education|academic|qualification)",
        "skills": r"(skills|technical skills|core competencies|expertise)",
        "certifications": r"(certification|certificates|licenses)",
        "projects": r"(projects|personal projects|academic projects)"
    }

    # Split text into lines
    lines = text.split('\n')
    current_section = "other"
    section_content = {key: [] for key in sections.keys()}

    # Extract contact info from top (first 5 lines typically)
    section_content["contact_info"] = lines[:5]

    for line in lines:
        line_lower = line.lower().strip()

        # Check if line matches any section header
        matched = False
        for section, pattern in section_patterns.items():
            if re.search(pattern, line_lower, re.IGNORECASE):
                current_section = section
                matched = True
                break

        # Add content to current section if not a header
        if not matched and line.strip():
            section_content[current_section].append(line)

    # Convert lists to strings
    for key in sections.keys():
        sections[key] = '\n'.join(section_content[key]).strip()

    return sections

def extract_resume_data(pdf_file) -> Dict[str, str]:
    """Main function to extract and parse resume"""
    text = extract_text_from_pdf(pdf_file)
    sections = parse_resume_sections(text)
    sections["full_text"] = text
    return sections
