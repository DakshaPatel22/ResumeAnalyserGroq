# Resume Analyzer

AI-powered resume analyzer built with Streamlit and Groq API that provides ATS score, detailed analysis, and actionable recommendations.

## Features

- PDF resume upload and parsing
- ATS score calculation (out of 100)
- Section-wise analysis
- AI-powered feedback using Llama 3.3
- Missing sections identification
- Keyword analysis
- Actionable improvement recommendations
- Beautiful Streamlit UI

## Installation

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. The `.env` file is already configured with your API credentials

## Usage

Run the Streamlit app:
```bash
streamlit run app.py
```

Then:
1. Open the URL shown in terminal (usually http://localhost:8501)
2. Upload your resume PDF
3. Wait for analysis
4. Review your ATS score and recommendations

## Project Structure

- `app.py` - Main Streamlit application
- `pdf_parser.py` - PDF text extraction and section parsing
- `resume_analyzer.py` - ATS scoring and AI analysis using Groq API
- `requirements.txt` - Python dependencies
- `.env` - API credentials

## ATS Scoring Criteria

- Contact Information (15 points)
- Professional Summary (15 points)
- Work Experience (30 points)
- Education (20 points)
- Skills (15 points)
- Formatting (5 points)

**Total: 100 points**

## Technologies Used

- Streamlit - Web interface
- pdfplumber - PDF parsing
- Groq API - AI analysis with Llama 3.3
- Python-dotenv - Environment management
