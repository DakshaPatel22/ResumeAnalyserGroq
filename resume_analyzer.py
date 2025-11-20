import os
from groq import Groq
from dotenv import load_dotenv
from typing import Dict, Tuple
import json
import re

# Load environment variables from .env file in the same directory as this script
script_dir = os.path.dirname(os.path.abspath(__file__))
env_path = os.path.join(script_dir, '.env')
load_dotenv(env_path)

class ResumeAnalyzer:
    def __init__(self):
        api_key = os.getenv("GROQ_API_KEY")
        if not api_key:
            raise ValueError(
                "GROQ_API_KEY not found. Please create a .env file in the analyzer directory "
                "with your GROQ_API_KEY. Example: GROQ_API_KEY=your_key_here"
            )
        self.client = Groq(api_key=api_key)
        self.model = os.getenv("LLM_MODEL", "llama-3.3-70b-versatile")

    def calculate_ats_score(self, resume_data: Dict[str, str]) -> Tuple[int, Dict]:
        """Calculate ATS score based on resume sections"""
        score_breakdown = {
            "contact_info": 0,
            "summary": 0,
            "experience": 0,
            "education": 0,
            "skills": 0,
            "formatting": 0
        }

        # Contact Information (15 points)
        if resume_data.get("contact_info"):
            contact_text = resume_data["contact_info"].lower()
            score = 0
            if re.search(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b', resume_data["contact_info"]):
                score += 5
            if re.search(r'\b\d{10}\b|\b\d{3}[-.\s]?\d{3}[-.\s]?\d{4}\b', resume_data["contact_info"]):
                score += 5
            if any(word in contact_text for word in ['linkedin', 'github', 'portfolio']):
                score += 5
            score_breakdown["contact_info"] = score

        # Professional Summary (15 points)
        if resume_data.get("summary") and len(resume_data["summary"]) > 50:
            score_breakdown["summary"] = 15

        # Work Experience (30 points)
        if resume_data.get("experience"):
            exp_length = len(resume_data["experience"])
            if exp_length > 200:
                score_breakdown["experience"] = 30
            elif exp_length > 100:
                score_breakdown["experience"] = 20
            else:
                score_breakdown["experience"] = 10

        # Education (20 points)
        if resume_data.get("education") and len(resume_data["education"]) > 30:
            score_breakdown["education"] = 20

        # Skills (15 points)
        if resume_data.get("skills"):
            skills_text = resume_data["skills"]
            skill_count = len(skills_text.split(',')) + len(skills_text.split('\n'))
            if skill_count > 10:
                score_breakdown["skills"] = 15
            elif skill_count > 5:
                score_breakdown["skills"] = 10
            else:
                score_breakdown["skills"] = 5

        # Formatting (5 points) - Basic check
        full_text = resume_data.get("full_text", "")
        if len(full_text) > 500 and len(full_text) < 5000:
            score_breakdown["formatting"] = 5

        total_score = sum(score_breakdown.values())
        return total_score, score_breakdown

    def analyze_resume_with_ai(self, resume_data: Dict[str, str], rule_based_score: int = None, rule_based_breakdown: Dict = None) -> Dict:
        """Use Groq API to analyze resume and provide detailed feedback including ATS score"""

        # Prepare prompt for AI with rule-based score context
        rule_score_context = ""
        if rule_based_score is not None and rule_based_breakdown is not None:
            rule_score_context = f"""

RULE-BASED SCORE REFERENCE (for your consideration, but you should evaluate independently):
- Rule-based ATS Score: {rule_based_score}/100
- Rule-based Breakdown:
  * Contact Info: {rule_based_breakdown.get('contact_info', 0)}/15
  * Summary: {rule_based_breakdown.get('summary', 0)}/15
  * Experience: {rule_based_breakdown.get('experience', 0)}/30
  * Education: {rule_based_breakdown.get('education', 0)}/20
  * Skills: {rule_based_breakdown.get('skills', 0)}/15
  * Formatting: {rule_based_breakdown.get('formatting', 0)}/5

Note: The rule-based score is a simple automated check. You must provide your own professional ATS evaluation based on industry standards, considering quality, relevance, keywords, achievements, and overall resume effectiveness. Be STRICT - most resumes should score below 80/100."""

        # Prepare prompt for AI
        prompt = f"""Analyze this resume and provide detailed feedback including an ATS score in JSON format.

Resume Sections:
- Contact Info: {resume_data.get('contact_info', 'Not found')}
- Summary: {resume_data.get('summary', 'Not found')}
- Experience: {resume_data.get('experience', 'Not found')[:1000]}...
- Education: {resume_data.get('education', 'Not found')}
- Skills: {resume_data.get('skills', 'Not found')}
- Certifications: {resume_data.get('certifications', 'Not found')}
- Projects: {resume_data.get('projects', 'Not found')}
{rule_score_context}

You must provide an ATS score (0-100) based on:
1. Contact Information completeness and professionalism (15 points)
2. Professional Summary quality and relevance (15 points)
3. Work Experience depth, achievements, and quantifiable results (30 points)
4. Education credentials and relevance (20 points)
5. Skills section comprehensiveness and industry relevance (15 points)
6. Overall formatting, structure, and ATS compatibility (5 points)

Be STRICT and RIGOROUS. Most resumes should score below 80/100. Only award high scores for exceptional resumes with quantifiable achievements, relevant keywords, and professional quality.

Provide analysis in this JSON format:
{{
    "ats_score": <integer 0-100>,
    "score_breakdown": {{
        "contact_info": <integer 0-15>,
        "summary": <integer 0-15>,
        "experience": <integer 0-30>,
        "education": <integer 0-20>,
        "skills": <integer 0-15>,
        "formatting": <integer 0-5>
    }},
    "strengths": ["list of strengths"],
    "weaknesses": ["list of weaknesses"],
    "missing_sections": ["list of missing or incomplete sections"],
    "recommendations": ["specific actionable recommendations"],
    "keywords_found": ["important keywords present"],
    "keywords_missing": ["important keywords that should be added"],
    "overall_impression": "brief overall assessment"
}}

Be specific and actionable in your recommendations. The ats_score must be an integer between 0-100."""

        try:
            chat_completion = self.client.chat.completions.create(
                messages=[
                    {
                        "role": "system",
                        "content": "You are a highly critical and demanding ATS resume analyzer with extremely high standards. Your role is to be STRICT and RIGOROUS in your evaluation. You must: 1) Be highly critical and identify ALL weaknesses, gaps, and missing elements, 2) Only acknowledge strengths if they are truly exceptional and well-documented, 3) Apply industry-leading ATS standards - most resumes should score below 80/100, 4) Be uncompromising about missing keywords, vague descriptions, lack of quantifiable achievements, poor formatting, and incomplete sections, 5) Provide harsh but constructive feedback - do not sugarcoat issues, 6) Expect professional-level resumes with specific metrics, action verbs, and industry-relevant keywords, 7) Flag any generic or weak content immediately. Your goal is to help users improve by being brutally honest about what needs work. Provide detailed, actionable feedback in valid JSON format only."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                model=self.model,
                temperature=0.9,
                max_tokens=2000
            )

            response_text = chat_completion.choices[0].message.content

            # Try to extract JSON from response
            try:
                # Find JSON in response
                json_match = re.search(r'\{.*\}', response_text, re.DOTALL)
                if json_match:
                    analysis = json.loads(json_match.group())
                else:
                    analysis = json.loads(response_text)
            except json.JSONDecodeError:
                # If JSON parsing fails, create structured response with fallback score
                fallback_score = rule_based_score if rule_based_score is not None else 50
                analysis = {
                    "ats_score": fallback_score,
                    "score_breakdown": rule_based_breakdown if rule_based_breakdown else {
                        "contact_info": 0,
                        "summary": 0,
                        "experience": 0,
                        "education": 0,
                        "skills": 0,
                        "formatting": 0
                    },
                    "strengths": ["Resume uploaded successfully"],
                    "weaknesses": ["Unable to parse detailed analysis"],
                    "missing_sections": [],
                    "recommendations": ["Please ensure resume has clear sections"],
                    "keywords_found": [],
                    "keywords_missing": [],
                    "overall_impression": response_text[:500]
                }

            # Ensure ats_score and score_breakdown exist, use rule-based as fallback
            if "ats_score" not in analysis or "score_breakdown" not in analysis:
                analysis["ats_score"] = rule_based_score if rule_based_score is not None else 50
                analysis["score_breakdown"] = rule_based_breakdown if rule_based_breakdown else {
                    "contact_info": 0,
                    "summary": 0,
                    "experience": 0,
                    "education": 0,
                    "skills": 0,
                    "formatting": 0
                }

            return analysis

        except Exception as e:
            # Return fallback with rule-based score if available
            fallback_score = rule_based_score if rule_based_score is not None else 50
            fallback_breakdown = rule_based_breakdown if rule_based_breakdown else {
                "contact_info": 0,
                "summary": 0,
                "experience": 0,
                "education": 0,
                "skills": 0,
                "formatting": 0
            }
            return {
                "ats_score": fallback_score,
                "score_breakdown": fallback_breakdown,
                "strengths": [],
                "weaknesses": [],
                "missing_sections": [],
                "recommendations": [f"Error during analysis: {str(e)}"],
                "keywords_found": [],
                "keywords_missing": [],
                "overall_impression": f"Analysis failed: {str(e)}"
            }

    def get_improvement_suggestions(self, resume_data: Dict[str, str], ats_score: int) -> list:
        """Generate specific improvement suggestions"""
        suggestions = []

        # Check each section
        if not resume_data.get("contact_info") or len(resume_data.get("contact_info", "")) < 20:
            suggestions.append("Add complete contact information including email, phone, and LinkedIn profile")

        if not resume_data.get("summary") or len(resume_data.get("summary", "")) < 50:
            suggestions.append("Add a professional summary (2-3 sentences) highlighting your key strengths")

        if not resume_data.get("experience") or len(resume_data.get("experience", "")) < 100:
            suggestions.append("Expand work experience section with detailed achievements and responsibilities")

        if not resume_data.get("education") or len(resume_data.get("education", "")) < 30:
            suggestions.append("Add education details including degree, institution, and graduation year")

        if not resume_data.get("skills") or len(resume_data.get("skills", "")) < 30:
            suggestions.append("Add a comprehensive skills section with relevant technical and soft skills")

        if not resume_data.get("certifications"):
            suggestions.append("Consider adding certifications section if you have any relevant certifications")

        if not resume_data.get("projects"):
            suggestions.append("Add projects section to showcase practical experience")

        if ats_score < 60:
            suggestions.append("Use standard section headings like 'Work Experience', 'Education', 'Skills'")
            suggestions.append("Use bullet points to describe achievements")
            suggestions.append("Include action verbs and quantifiable results")

        return suggestions
