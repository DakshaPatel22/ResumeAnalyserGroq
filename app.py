import streamlit as st
from pdf_parser import extract_resume_data
from resume_analyzer import ResumeAnalyzer
import os

# Page configuration
st.set_page_config(
    page_title="Resume Analyzer",
    page_icon="📄",
    layout="wide"
)

# Custom CSS for better styling
st.markdown("""
    <style>
    .main {
        padding: 2rem;
    }
    .stProgress > div > div > div > div {
        background-color: #4CAF50;
    }
    .score-box {
        padding: 20px;
        border-radius: 10px;
        background-color: #f0f2f6;
        margin: 10px 0;
    }
    </style>
""", unsafe_allow_html=True)

# Initialize analyzer
@st.cache_resource
def get_analyzer():
    return ResumeAnalyzer()

def display_ats_score(score, breakdown):
    """Display ATS score with visual representation"""
    col1, col2 = st.columns([1, 2])

    with col1:
        # Score display
        if score >= 80:
            color = "green"
            status = "Excellent"
        elif score >= 60:
            color = "orange"
            status = "Good"
        else:
            color = "red"
            status = "Needs Improvement"

        st.markdown(f"""
            <div style='text-align: center; padding: 20px; background-color: #f0f2f6; border-radius: 10px;'>
                <h1 style='color: {color}; font-size: 72px; margin: 0;'>{score}</h1>
                <h3 style='color: {color}; margin: 0;'>{status}</h3>
                <p style='color: #666; margin-top: 10px;'>ATS Score out of 100</p>
            </div>
        """, unsafe_allow_html=True)

    with col2:
        st.subheader("Score Breakdown")
        for category, points in breakdown.items():
            max_points = {
                "contact_info": 15,
                "summary": 15,
                "experience": 30,
                "education": 20,
                "skills": 15,
                "formatting": 5
            }.get(category, 10)

            percentage = (points / max_points * 100) if max_points > 0 else 0
            st.write(f"**{category.replace('_', ' ').title()}**: {points}/{max_points}")
            st.progress(percentage / 100)

def main():
    st.title("📄 AI Resume Analyzer")
    st.markdown("### Upload your resume to get detailed ATS analysis and improvement suggestions")

    # Sidebar for info
    with st.sidebar:
        st.header("About")
        st.info("""
        This tool analyzes your resume and provides:
        - ATS Score calculation
        - Detailed feedback
        - Missing sections identification
        - Actionable recommendations
        - Keyword analysis
        """)

        st.header("How to use")
        st.markdown("""
        1. Upload your resume (PDF format)
        2. Wait for analysis to complete
        3. Review your ATS score
        4. Read detailed feedback
        5. Implement suggestions
        """)

    # File uploader
    uploaded_file = st.file_uploader("Choose your resume (PDF)", type=['pdf'])

    if uploaded_file is not None:
        with st.spinner("Analyzing your resume..."):
            try:
                # Extract resume data
                st.info("Extracting text from PDF...")
                resume_data = extract_resume_data(uploaded_file)

                # Initialize analyzer
                analyzer = get_analyzer()

                # Calculate ATS score
                st.info("Calculating ATS score...")
                ats_score, score_breakdown = analyzer.calculate_ats_score(resume_data)

                # Get AI analysis
                st.info("Getting AI-powered analysis...")
                ai_analysis = analyzer.analyze_resume_with_ai(resume_data)

                # Get improvement suggestions
                suggestions = analyzer.get_improvement_suggestions(resume_data, ats_score)

                st.success("Analysis complete!")

                # Display results
                st.markdown("---")

                # ATS Score Section
                st.header("ATS Score")
                display_ats_score(ats_score, score_breakdown)

                st.markdown("---")

                # AI Analysis Section
                st.header("Detailed Analysis")

                col1, col2 = st.columns(2)

                with col1:
                    st.subheader("Strengths")
                    if ai_analysis.get("strengths"):
                        for strength in ai_analysis["strengths"]:
                            st.success(f"✓ {strength}")
                    else:
                        st.info("No specific strengths identified")

                    st.subheader("Keywords Found")
                    if ai_analysis.get("keywords_found"):
                        st.write(", ".join(ai_analysis["keywords_found"]))
                    else:
                        st.info("No specific keywords analyzed")

                with col2:
                    st.subheader("Areas for Improvement")
                    if ai_analysis.get("weaknesses"):
                        for weakness in ai_analysis["weaknesses"]:
                            st.warning(f"⚠ {weakness}")
                    else:
                        st.info("No specific weaknesses identified")

                    st.subheader("Missing Keywords")
                    if ai_analysis.get("keywords_missing"):
                        st.write(", ".join(ai_analysis["keywords_missing"]))
                    else:
                        st.info("No missing keywords identified")

                st.markdown("---")

                # Missing Sections
                if ai_analysis.get("missing_sections"):
                    st.subheader("Missing or Incomplete Sections")
                    for section in ai_analysis["missing_sections"]:
                        st.error(f"❌ {section}")

                # Recommendations
                st.markdown("---")
                st.header("Recommendations")
                st.subheader("AI-Powered Suggestions")
                if ai_analysis.get("recommendations"):
                    for i, rec in enumerate(ai_analysis["recommendations"], 1):
                        st.markdown(f"**{i}.** {rec}")

                st.subheader("Additional Improvement Tips")
                for i, suggestion in enumerate(suggestions, 1):
                    st.markdown(f"**{i}.** {suggestion}")

                # Overall Impression
                if ai_analysis.get("overall_impression"):
                    st.markdown("---")
                    st.header("Overall Impression")
                    st.info(ai_analysis["overall_impression"])

                # Resume Sections Preview
                with st.expander("View Extracted Resume Sections"):
                    for section, content in resume_data.items():
                        if section != "full_text" and content:
                            st.subheader(section.replace("_", " ").title())
                            st.text(content[:500] + ("..." if len(content) > 500 else ""))

            except Exception as e:
                st.error(f"Error analyzing resume: {str(e)}")
                st.error("Please make sure the PDF is readable and try again.")

    else:
        # Display sample information
        st.info("Please upload a PDF resume to begin analysis")

        st.markdown("### What makes a good resume?")
        col1, col2, col3 = st.columns(3)

        with col1:
            st.markdown("""
            **Contact Information**
            - Full name
            - Phone number
            - Email address
            - LinkedIn profile
            """)

        with col2:
            st.markdown("""
            **Content Quality**
            - Clear professional summary
            - Quantified achievements
            - Relevant keywords
            - Action verbs
            """)

        with col3:
            st.markdown("""
            **Structure**
            - Work experience
            - Education
            - Skills
            - Projects/Certifications
            """)

if __name__ == "__main__":
    main()
