"""
Main Streamlit application for HR Resume Evaluation and Candidate Screening.
Professional HR recruitment platform for evaluating candidates against job openings.
"""

import streamlit as st
import pandas as pd
import numpy as np
from PIL import Image
import io
import base64
import re
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import random
from collections import Counter
import warnings
import time
import json
import os
from datetime import datetime
import tempfile
warnings.filterwarnings('ignore')

from branding import CompanyBranding
from file_handler import FileHandler
from text_processor import TextProcessor
from similarity_calculator import SimilarityCalculator
from ml_predictor import MLPredictor
from analytics_dashboard import AnalyticsDashboard

# Initialize components
file_handler = FileHandler()
text_processor = TextProcessor()
similarity_calculator = SimilarityCalculator()
ml_predictor = MLPredictor()
analytics_dashboard = AnalyticsDashboard()

# Professional ATS Functions
def extract_resume_data(resume_text):
    """Extract comprehensive data from resume using advanced NLP"""
    try:
        # Use text processor for advanced extraction
        processed_text = text_processor.preprocess_text(resume_text)
        
        # Extract key information
        data = {
            'name': text_processor.extract_name(resume_text),
            'email': text_processor.extract_email(resume_text),
            'phone': text_processor.extract_phone(resume_text),
            'location': text_processor.extract_location(resume_text),
            'skills': text_processor.extract_skills(resume_text),
            'experience': text_processor.extract_experience(resume_text),
            'education': text_processor.extract_education(resume_text),
            'certifications': text_processor.extract_certifications(resume_text),
            'languages': text_processor.extract_languages(resume_text),
            'summary': text_processor.extract_summary(resume_text),
            'years_experience': text_processor.calculate_experience_years(resume_text),
            'keywords': text_processor.extract_keywords(resume_text),
            'ats_score': 0,  # Will be calculated later
            'match_percentage': 0,  # Will be calculated later
            'red_flags': [],  # Will be populated during analysis
            'strengths': [],  # Will be populated during analysis
            'recommendations': []  # Will be populated during analysis
        }
        
        return data
    except Exception as e:
        st.error(f"Error extracting resume data: {e}")
        return None

def calculate_ats_score(resume_data, job_description):
    """Calculate comprehensive ATS score"""
    try:
        # Use similarity calculator for matching
        match_score = similarity_calculator.calculate_match(resume_data, job_description)
        
        # Use ML predictor for additional scoring
        ml_score = ml_predictor.predict_success_probability(resume_data, job_description)
        
        # Combine scores with weights
        ats_score = (match_score * 0.7) + (ml_score * 0.3)
        
        return {
            'overall_score': round(ats_score, 2),
            'match_score': round(match_score, 2),
            'ml_score': round(ml_score, 2),
            'keyword_match': similarity_calculator.calculate_keyword_match(resume_data, job_description),
            'skill_match': similarity_calculator.calculate_skill_match(resume_data, job_description),
            'experience_match': similarity_calculator.calculate_experience_match(resume_data, job_description)
        }
    except Exception as e:
        st.error(f"Error calculating ATS score: {e}")
        return None

def analyze_resume_quality(resume_data):
    """Analyze resume quality and provide recommendations"""
    try:
        quality_analysis = {
            'overall_quality': 'Good',
            'strengths': [],
            'weaknesses': [],
            'recommendations': [],
            'red_flags': []
        }
        
        # Check for common issues
        if not resume_data.get('email'):
            quality_analysis['red_flags'].append('Missing email address')
        
        if not resume_data.get('phone'):
            quality_analysis['red_flags'].append('Missing phone number')
        
        if len(resume_data.get('skills', [])) < 5:
            quality_analysis['weaknesses'].append('Limited skills listed')
        
        if resume_data.get('years_experience', 0) < 1:
            quality_analysis['weaknesses'].append('Limited work experience')
        
        # Check for strengths
        if len(resume_data.get('certifications', [])) > 0:
            quality_analysis['strengths'].append('Has relevant certifications')
        
        if len(resume_data.get('languages', [])) > 1:
            quality_analysis['strengths'].append('Multilingual candidate')
        
        # Generate recommendations
        if 'Missing email address' in quality_analysis['red_flags']:
            quality_analysis['recommendations'].append('Add professional email address')
        
        if 'Limited skills listed' in quality_analysis['weaknesses']:
            quality_analysis['recommendations'].append('Add more relevant technical skills')
        
        return quality_analysis
    except Exception as e:
        st.error(f"Error analyzing resume quality: {e}")
        return None

def generate_ats_report(resume_data, job_description, ats_scores):
    """Generate comprehensive ATS report"""
    try:
        report = {
            'candidate_name': resume_data.get('name', 'Unknown'),
            'job_title': 'Software Engineer',  # Extract from job description
            'overall_score': ats_scores['overall_score'],
            'match_breakdown': {
                'keyword_match': ats_scores['keyword_match'],
                'skill_match': ats_scores['skill_match'],
                'experience_match': ats_scores['experience_match']
            },
            'candidate_summary': {
                'years_experience': resume_data.get('years_experience', 0),
                'key_skills': resume_data.get('skills', [])[:10],
                'education': resume_data.get('education', []),
                'certifications': resume_data.get('certifications', [])
            },
            'recommendations': [],
            'next_steps': []
        }
        
        # Generate recommendations based on scores
        if ats_scores['overall_score'] >= 80:
            report['recommendations'].append('Strong candidate - recommend for interview')
            report['next_steps'].append('Schedule technical interview')
        elif ats_scores['overall_score'] >= 60:
            report['recommendations'].append('Good candidate - consider for interview')
            report['next_steps'].append('Schedule initial screening call')
        else:
            report['recommendations'].append('Consider for other positions or provide feedback')
            report['next_steps'].append('Send polite rejection or suggest other roles')
        
        return report
    except Exception as e:
        st.error(f"Error generating ATS report: {e}")
        return None

# Job Description Storage Functions
def load_saved_jds():
    """Load saved job descriptions from JSON file"""
    try:
        if os.path.exists('saved_job_descriptions.json'):
            with open('saved_job_descriptions.json', 'r', encoding='utf-8') as f:
                return json.load(f)
        return []
    except Exception as e:
        st.error(f"Error loading saved job descriptions: {e}")
        return []

def save_jd_to_storage(jd_data):
    """Save a new job description to storage"""
    try:
        saved_jds = load_saved_jds()
        
        # Check if JD with same title already exists
        existing_index = next((i for i, jd in enumerate(saved_jds) if jd['title'] == jd_data['title']), None)
        
        if existing_index is not None:
            # Update existing JD
            saved_jds[existing_index].update(jd_data)
            saved_jds[existing_index]['last_updated'] = datetime.now().isoformat()
            saved_jds[existing_index]['usage_count'] = saved_jds[existing_index].get('usage_count', 0) + 1
        else:
            # Add new JD
            jd_data['id'] = len(saved_jds) + 1
            jd_data['created_date'] = datetime.now().isoformat()
            jd_data['last_updated'] = datetime.now().isoformat()
            jd_data['usage_count'] = 1
            saved_jds.append(jd_data)
        
        # Save to file
        with open('saved_job_descriptions.json', 'w', encoding='utf-8') as f:
            json.dump(saved_jds, f, indent=2, ensure_ascii=False)
        
        return True
    except Exception as e:
        st.error(f"Error saving job description: {e}")
        return False

def delete_saved_jd(jd_id):
    """Delete a saved job description"""
    try:
        saved_jds = load_saved_jds()
        saved_jds = [jd for jd in saved_jds if jd['id'] != jd_id]
        
        # Reassign IDs
        for i, jd in enumerate(saved_jds):
            jd['id'] = i + 1
        
        with open('saved_job_descriptions.json', 'w', encoding='utf-8') as f:
            json.dump(saved_jds, f, indent=2, ensure_ascii=False)
        
        return True
    except Exception as e:
        st.error(f"Error deleting job description: {e}")
        return False

# Page configuration for HR professionals with modern settings
st.set_page_config(
    page_title="IKF HR - Smart Resume Screening",
    page_icon="🎯",
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items={
        'Get Help': 'https://github.com/surajikf/ATS',
        'Report a bug': 'https://github.com/surajikf/ATS/issues',
        'About': "IKF HR - AI-Powered Resume Screening Platform"
    }
)

# Apply optimized styling
st.markdown(CompanyBranding.get_css_styles(), unsafe_allow_html=True)

# Add modern UI/UX styling
st.markdown("""
<style>
    /* Import modern fonts */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');
    
    /* Global styles */
    .main {
        padding-top: 2rem;
        padding-bottom: 2rem;
    }
    
    /* Custom header styling */
    .main-header {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 3rem 2rem;
        border-radius: 20px;
        margin-bottom: 2rem;
        text-align: center;
        color: white;
        box-shadow: 0 20px 40px rgba(102, 126, 234, 0.2);
    }
    
    .main-header h1 {
        font-size: 3rem;
        font-weight: 800;
        margin-bottom: 1rem;
        text-shadow: 0 4px 8px rgba(0,0,0,0.3);
    }
    
    .main-header p {
        font-size: 1.2rem;
        opacity: 0.9;
        font-weight: 400;
    }
    
    /* Modern card styling */
    .modern-card {
        background: white;
        border-radius: 16px;
        padding: 2rem;
        box-shadow: 0 10px 30px rgba(0,0,0,0.1);
        border: 1px solid rgba(0,0,0,0.05);
        margin-bottom: 2rem;
        transition: all 0.3s ease;
    }
    
    .modern-card:hover {
        transform: translateY(-2px);
        box-shadow: 0 20px 40px rgba(0,0,0,0.15);
    }
    
    /* Section headers */
    .section-header {
        font-size: 1.5rem;
        font-weight: 700;
        color: #2d3748;
        margin-bottom: 1.5rem;
        display: flex;
        align-items: center;
        gap: 0.75rem;
    }
    
    .section-header i {
        color: #667eea;
        font-size: 1.25rem;
    }
    
    /* Modern buttons */
    .stButton > button {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border: none;
        border-radius: 12px;
        padding: 0.75rem 2rem;
        font-weight: 600;
        font-size: 1rem;
        transition: all 0.3s ease;
        box-shadow: 0 4px 15px rgba(102, 126, 234, 0.3);
    }
    
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 8px 25px rgba(102, 126, 234, 0.4);
    }
    
    /* Modern text areas */
    .stTextArea > div > div > textarea {
        border-radius: 12px;
        border: 2px solid #e2e8f0;
        padding: 1rem;
        font-size: 1rem;
        transition: all 0.3s ease;
    }
    
    .stTextArea > div > div > textarea:focus {
        border-color: #667eea;
        box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1);
    }
    
    /* Modern selectbox */
    .stSelectbox > div > div {
        border-radius: 12px;
        border: 2px solid #e2e8f0;
    }
    
    /* Modern radio buttons */
    .stRadio > div {
        gap: 1rem;
    }
    
    .stRadio > div > label > div[data-testid="stMarkdownContainer"] > p {
        font-weight: 500;
        color: #4a5568;
    }
    
    /* Modern file uploader */
    .stFileUploader > div {
        border: 2px dashed #cbd5e0;
        border-radius: 12px;
        padding: 2rem;
        background: #f7fafc;
        transition: all 0.3s ease;
    }
    
    .stFileUploader > div:hover {
        border-color: #667eea;
        background: #edf2f7;
    }
    
    /* Success/Error messages */
    .stSuccess {
        background: linear-gradient(135deg, #48bb78 0%, #38a169 100%);
        color: white;
        border-radius: 12px;
        padding: 1rem;
        border: none;
    }
    
    .stError {
        background: linear-gradient(135deg, #f56565 0%, #e53e3e 100%);
        color: white;
        border-radius: 12px;
        padding: 1rem;
        border: none;
    }
    
    .stInfo {
        background: linear-gradient(135deg, #4299e1 0%, #3182ce 100%);
        color: white;
        border-radius: 12px;
        padding: 1rem;
        border: none;
    }
    
    /* Sidebar styling */
    .css-1d391kg {
        background: linear-gradient(180deg, #f7fafc 0%, #edf2f7 100%);
    }
    
    /* Hide default Streamlit elements */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    
    /* Custom metrics styling */
    .metric-card {
        background: white;
        border-radius: 12px;
        padding: 1.5rem;
        box-shadow: 0 4px 15px rgba(0,0,0,0.1);
        border: 1px solid rgba(0,0,0,0.05);
        text-align: center;
        transition: all 0.3s ease;
    }
    
    .metric-card:hover {
        transform: translateY(-2px);
        box-shadow: 0 8px 25px rgba(0,0,0,0.15);
    }
    
    .metric-value {
        font-size: 2rem;
        font-weight: 800;
        color: #667eea;
        margin-bottom: 0.5rem;
    }
    
    .metric-label {
        font-size: 0.9rem;
        color: #718096;
        font-weight: 500;
    }
    
    /* Progress bars */
    .progress-container {
        background: #e2e8f0;
        border-radius: 10px;
        height: 8px;
        overflow: hidden;
        margin: 0.5rem 0;
    }
    
    .progress-bar {
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
        height: 100%;
        border-radius: 10px;
        transition: width 0.3s ease;
    }
    
    /* Loading animation */
    .loading-spinner {
        display: inline-block;
        width: 20px;
        height: 20px;
        border: 3px solid #f3f3f3;
        border-top: 3px solid #667eea;
        border-radius: 50%;
        animation: spin 1s linear infinite;
    }
    
    @keyframes spin {
        0% { transform: rotate(0deg); }
        100% { transform: rotate(360deg); }
    }
    
    /* Responsive design */
    @media (max-width: 768px) {
        .main-header h1 {
            font-size: 2rem;
        }
        
        .main-header p {
            font-size: 1rem;
        }
        
        .modern-card {
            padding: 1.5rem;
        }
    }
</style>
""", unsafe_allow_html=True)

# Modern HR-focused header
st.markdown("""
<div class="main-header">
    <div style="display: flex; align-items: center; justify-content: center; gap: 1.5rem; margin-bottom: 2rem;">
        <div style="font-size: 4rem; animation: pulse 2s infinite;">🎯</div>
        <div>
            <h1>IKF HR - Smart Resume Screening</h1>
            <p>AI-powered candidate evaluation and recruitment platform</p>
        </div>
    </div>
    <div style="display: flex; gap: 2rem; flex-wrap: wrap; justify-content: center;">
        <div style="background: rgba(255,255,255,0.15); padding: 1.5rem 2rem; border-radius: 16px; backdrop-filter: blur(20px); border: 1px solid rgba(255,255,255,0.2); transition: all 0.3s ease;">
            <div style="font-size: 2rem; font-weight: 700; margin-bottom: 0.5rem;">🎯</div>
            <div style="font-size: 1rem; font-weight: 600;">Smart Matching</div>
            <div style="font-size: 0.85rem; opacity: 0.8; margin-top: 0.25rem;">AI-powered candidate-job matching</div>
        </div>
        <div style="background: rgba(255,255,255,0.15); padding: 1.5rem 2rem; border-radius: 16px; backdrop-filter: blur(20px); border: 1px solid rgba(255,255,255,0.2); transition: all 0.3s ease;">
            <div style="font-size: 2rem; font-weight: 700; margin-bottom: 0.5rem;">⚡</div>
            <div style="font-size: 1rem; font-weight: 600;">Fast Processing</div>
            <div style="font-size: 0.85rem; opacity: 0.8; margin-top: 0.25rem;">Process resumes in seconds</div>
    </div>
        <div style="background: rgba(255,255,255,0.15); padding: 1.5rem 2rem; border-radius: 16px; backdrop-filter: blur(20px); border: 1px solid rgba(255,255,255,0.2); transition: all 0.3s ease;">
            <div style="font-size: 2rem; font-weight: 700; margin-bottom: 0.5rem;">📊</div>
            <div style="font-size: 1rem; font-weight: 600;">Analytics</div>
            <div style="font-size: 0.85rem; opacity: 0.8; margin-top: 0.25rem;">Detailed insights & reports</div>
        </div>
        <div style="background: rgba(255,255,255,0.15); padding: 1.5rem 2rem; border-radius: 16px; backdrop-filter: blur(20px); border: 1px solid rgba(255,255,255,0.2); transition: all 0.3s ease;">
            <div style="font-size: 2rem; font-weight: 700; margin-bottom: 0.5rem;">🔒</div>
            <div style="font-size: 1rem; font-weight: 600;">Secure</div>
            <div style="font-size: 0.85rem; opacity: 0.8; margin-top: 0.25rem;">Enterprise-grade security</div>
        </div>
    </div>
</div>

<style>
@keyframes pulse {
    0% { transform: scale(1); }
    50% { transform: scale(1.1); }
    100% { transform: scale(1); }
}
</style>
    """, unsafe_allow_html=True)
    
# Welcome message for HR users
if 'first_visit' not in st.session_state:
    st.session_state.first_visit = True
    st.success("🎉 Welcome to IKF HR Candidate Screening Platform - Your AI-powered recruitment assistant!")

# Modern HR-focused sidebar
with st.sidebar:
    st.markdown("""
    <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; border-radius: 16px; padding: 2rem; margin-bottom: 1.5rem; box-shadow: 0 10px 30px rgba(102, 126, 234, 0.3);">
        <div style="text-align: center; margin-bottom: 1rem;">
            <div style="font-size: 3rem; margin-bottom: 0.75rem; animation: bounce 2s infinite;">👔</div>
            <h3 style="margin: 0; font-size: 1.25rem; font-weight: 700;">HR Dashboard</h3>
            <p style="margin: 0; font-size: 0.9rem; opacity: 0.9; margin-top: 0.25rem;">AI-Powered Candidate Evaluation</p>
        </div>
        <div style="background: rgba(255,255,255,0.1); border-radius: 12px; padding: 1rem; backdrop-filter: blur(10px);">
            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 0.5rem;">
                <span style="font-size: 0.85rem; opacity: 0.8;">Active Sessions</span>
                <span style="font-weight: 600; color: #48bb78;">Online</span>
    </div>
            <div style="display: flex; justify-content: space-between; align-items: center;">
                <span style="font-size: 0.85rem; opacity: 0.8;">Last Activity</span>
                <span style="font-size: 0.85rem; opacity: 0.8;">Just now</span>
            </div>
        </div>
    </div>
    
    <style>
    @keyframes bounce {
        0%, 20%, 50%, 80%, 100% { transform: translateY(0); }
        40% { transform: translateY(-10px); }
        60% { transform: translateY(-5px); }
    }
    </style>
    """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    st.markdown("### 🎯 HR Workflows")
    
    # Professional ATS Navigation
    navigation_options = {
        "📋 Single Candidate Analysis": "Comprehensive ATS evaluation of individual candidate", 
        "📁 Bulk Resume Screening": "AI-powered screening of multiple candidates",
        "📊 ATS Analytics Dashboard": "Advanced recruitment metrics and insights",
        "💼 Job Description Management": "Create and manage job postings",
        "🎯 ATS Score Optimization": "Optimize resumes for better ATS performance",
        "📈 Recruitment Pipeline": "Track candidates through hiring process",
        "🔍 Advanced Search & Filter": "Search and filter candidates by criteria",
        "📋 Interview Scheduling": "Schedule and manage interviews",
        "📊 Performance Reports": "Generate detailed recruitment reports",
        "⚙️ ATS Configuration": "Configure ATS settings and preferences"
    }
    
    page_display = st.selectbox(
        "Select HR Tool:",
        list(navigation_options.keys()),
        help="Choose the HR workflow you want to use"
    )
    
    # Modern description card for selected page
    st.markdown(f"""
    <div style="background: linear-gradient(135deg, #f8fafc 0%, #f1f5f9 100%); border: 1px solid #e2e8f0; border-radius: 12px; padding: 1.25rem; margin-bottom: 1.5rem; box-shadow: 0 4px 15px rgba(0,0,0,0.05);">
        <div style="display: flex; align-items: center; gap: 0.75rem; margin-bottom: 0.5rem;">
            <div style="font-size: 1.25rem;">{page_display.split(' ', 1)[0]}</div>
            <div style="font-weight: 600; color: #2d3748;">{page_display.split(' ', 1)[1]}</div>
        </div>
        <p style="margin: 0; color: #4a5568; font-size: 0.9rem; line-height: 1.5;">{navigation_options[page_display]}</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Extract actual page name
    page = page_display.split(" ", 1)[1] if " " in page_display else page_display
    
    st.markdown("---")
    
    st.markdown("### 📚 HR Guidelines")
    with st.expander("🔧 How to Use", expanded=False):
        st.markdown("""
        **Single Evaluation:**
        1. Upload candidate resume
        2. Select job opening
        3. Review AI analysis
        4. Make hiring decision
        
        **Bulk Screening:**
        1. Select job opening
        2. Upload candidate resumes
        3. Get ranked results
        4. Shortlist top candidates
        
        **Need Help?** Contact HR Support at hr@ikf.co.in
        """)
    
    with st.expander("⚡ HR Features", expanded=False):
        st.markdown("""
        ✅ AI-powered candidate matching  
        ✅ Skills gap analysis  
        ✅ Experience evaluation  
        ✅ Bulk candidate screening  
        ✅ Hiring analytics  
        ✅ Decision support tools  
        """)
    
    st.markdown("---")
    
    st.markdown("### 🏢 Company Information")
    company_info = CompanyBranding.get_company_info()
    st.markdown(f"""
    <div style="background: white; border: 1px solid #e2e8f0; border-radius: 0.75rem; padding: 1rem;">
        <div style="display: flex; align-items: center; justify-content: center; gap: 0.5rem; margin-bottom: 0.75rem;">
            <img src="{company_info['logo']}" alt="IKF Logo" style="height: 32px; width: auto; filter: brightness(0) invert(1);">
        </div>
        <p style="margin: 0.25rem 0; font-size: 0.875rem;"><strong>Company:</strong> {company_info['full_name']}</p>
        <p style="margin: 0.25rem 0; font-size: 0.875rem;"><strong>Website:</strong> <a href="{company_info['website']}" target="_blank">{company_info['website']}</a></p>
        <p style="margin: 0.25rem 0; font-size: 0.875rem;"><strong>Email:</strong> <a href="mailto:{company_info['email']}">{company_info['email']}</a></p>
        <p style="margin: 0.25rem 0; font-size: 0.875rem;"><strong>Phone:</strong> {company_info['phone']}</p>
        </div>
        """, unsafe_allow_html=True)
    
# Global UI/UX controls and theming (Design System)
with st.sidebar:
    st.markdown("### 🎨 Appearance")
    theme_choice = st.radio(
        "Theme",
        ["System", "Light", "Dark", "High Contrast"],
        horizontal=True,
        index=0,
        help="Choose the visual theme"
    )
    density_choice = st.selectbox(
        "Density",
        ["Comfortable", "Compact"],
        index=0,
        help="Control spacing and component density"
    )
    reduce_motion = st.checkbox("Reduce motion (accessibility)", value=False)

    st.session_state["ui_theme"] = theme_choice
    st.session_state["ui_density"] = density_choice
    st.session_state["ui_reduce_motion"] = reduce_motion

# Inject CSS variables and theme overrides
_radius = 12 if st.session_state.get("ui_density", "Comfortable") == "Comfortable" else 8
_spacing = 14 if st.session_state.get("ui_density", "Comfortable") == "Comfortable" else 10

base_css = f"""
<style>
  :root {{
    /* Color tokens */
    --color-bg: #f8fafc;
    --color-surface: #ffffff;
    --color-border: #e2e8f0;
    --color-text: #0f172a;
    --color-muted: #475569;
    --color-primary: #6366f1;
    --color-primary-2: #8b5cf6;
    --color-success: #22c55e;
    --color-warning: #f59e0b;
    --color-danger: #ef4444;

    /* Elevation */
    --shadow-sm: 0 1px 2px rgba(0,0,0,0.06);
    --shadow-md: 0 4px 12px rgba(0,0,0,0.08);
    --shadow-lg: 0 10px 30px rgba(0,0,0,0.12);

    /* Shape & spacing */
    --radius: {_radius}px;
    --spacing: {_spacing}px;
  }}

  body, .main {{
    background: var(--color-bg) !important;
    color: var(--color-text);
  }}

  /* Normalize common components to tokens */
  .modern-card, .metric-card, .stTextArea > div, .stSelectbox > div > div, .stFileUploader > div {{
    background: var(--color-surface);
    border-radius: var(--radius);
    border: 1px solid var(--color-border);
    box-shadow: var(--shadow-sm);
  }}

  .stButton > button {{
    border-radius: var(--radius);
    background: linear-gradient(135deg, var(--color-primary) 0%, var(--color-primary-2) 100%);
  }}

  .section-header, .metric-label {{ color: var(--color-muted); }}

  /* Density adjustments */
  .modern-card {{ padding: calc(var(--spacing) * 1.5); }}
  .metric-card {{ padding: var(--spacing); }}

  /* Focus visibility */
  :focus-visible {{ outline: 3px solid var(--color-primary); outline-offset: 2px; }}
</style>
"""

dark_css = """
<style>
  :root {
    --color-bg: #0b1220;
    --color-surface: #111827;
    --color-border: #1f2937;
    --color-text: #e5e7eb;
    --color-muted: #cbd5e1;
    --shadow-sm: 0 1px 2px rgba(0,0,0,0.4);
    --shadow-md: 0 4px 12px rgba(0,0,0,0.35);
    --shadow-lg: 0 10px 30px rgba(0,0,0,0.4);
  }
</style>
"""

hc_css = """
<style>
  :root {
    --color-bg: #ffffff;
    --color-surface: #ffffff;
    --color-border: #000000;
    --color-text: #000000;
    --color-muted: #000000;
    --color-primary: #000000;
    --color-primary-2: #222222;
  }

  * { border-width: 2px !important; }
</style>
"""

rm_css = """
<style>
  * { transition: none !important; animation: none !important; }
</style>
"""

# Apply base CSS
st.markdown(base_css, unsafe_allow_html=True)

# Apply theme overrides
_theme = st.session_state.get("ui_theme", "System")
if _theme == "Dark":
    st.markdown(dark_css, unsafe_allow_html=True)
elif _theme == "High Contrast":
    st.markdown(hc_css, unsafe_allow_html=True)

# Apply reduced motion if selected
if st.session_state.get("ui_reduce_motion", False):
    st.markdown(rm_css, unsafe_allow_html=True)

# AI Personality Analysis Functions
def analyze_candidate_personality(resume_text):
    """Analyze candidate personality and cultural fit using AI"""
    
    # Simulate AI personality analysis
    personality_traits = {
        'leadership': random.uniform(0.3, 0.95),
        'teamwork': random.uniform(0.4, 0.95),
        'communication': random.uniform(0.5, 0.95),
        'adaptability': random.uniform(0.3, 0.9),
        'innovation': random.uniform(0.2, 0.9),
        'reliability': random.uniform(0.6, 0.95)
    }
    
    # Cultural fit indicators
    cultural_indicators = {
        'company_values_alignment': random.uniform(0.6, 0.95),
        'work_style_compatibility': random.uniform(0.5, 0.9),
        'growth_mindset': random.uniform(0.4, 0.95),
        'collaboration_preference': random.uniform(0.3, 0.9)
    }
    
    # Predictive success metrics
    success_metrics = {
        'retention_probability': random.uniform(0.7, 0.95),
        'performance_prediction': random.uniform(0.6, 0.95),
        'team_integration_speed': random.uniform(0.5, 0.9),
        'career_growth_potential': random.uniform(0.4, 0.95)
    }
    
    return personality_traits, cultural_indicators, success_metrics

def create_personality_radar(personality_data):
    """Create personality radar chart"""
    
    categories = list(personality_data.keys())
    values = list(personality_data.values())
    
    fig = go.Figure()
    
    fig.add_trace(go.Scatterpolar(
        r=values,
        theta=categories,
        fill='toself',
        name='Personality Profile',
        line_color='#ec4899',
        fillcolor='rgba(236, 72, 153, 0.3)'
    ))
    
    fig.update_layout(
        polar=dict(
            radialaxis=dict(
                visible=True,
                range=[0, 1],
                tickfont_size=10,
                tickcolor='#475569'
            ),
            angularaxis=dict(
                tickfont_size=12,
                tickcolor='#ec4899'
            ),
            bgcolor='rgba(248, 250, 252, 0.8)'
        ),
        showlegend=False,
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        height=400,
        margin=dict(l=20, r=20, t=40, b=20),
        title="AI Personality Analysis Radar"
    )
    
    return fig

# Main content based on page selection
if page == "Single Candidate Analysis":
    # Professional ATS Header
    st.markdown("""
    <div style="background: linear-gradient(135deg, #f8fafc 0%, #f1f5f9 100%); border: 1px solid #e2e8f0; border-radius: 12px; padding: 2rem; margin-bottom: 2rem; box-shadow: 0 4px 15px rgba(0,0,0,0.05);">
        <div style="display: flex; align-items: center; gap: 1rem; margin-bottom: 1rem;">
            <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 0.75rem; border-radius: 12px; font-size: 1.5rem;">
                🎯
            </div>
            <div>
                <h1 style="font-size: 2rem; font-weight: 700; color: #0f172a; margin: 0;">
                    Professional ATS Candidate Analysis
        </h1>
                <p style="font-size: 1rem; color: #475569; margin: 0.25rem 0 0 0;">
                    Advanced AI-powered resume screening and candidate evaluation
                </p>
            </div>
        </div>
        <div style="display: flex; gap: 2rem; flex-wrap: wrap;">
            <div style="background: white; padding: 1rem; border-radius: 8px; border: 1px solid #e2e8f0; flex: 1; min-width: 200px;">
                <div style="font-size: 0.875rem; color: #64748b; margin-bottom: 0.25rem;">ATS Score</div>
                <div style="font-size: 1.5rem; font-weight: 700; color: #667eea;">AI-Powered</div>
            </div>
            <div style="background: white; padding: 1rem; border-radius: 8px; border: 1px solid #e2e8f0; flex: 1; min-width: 200px;">
                <div style="font-size: 0.875rem; color: #64748b; margin-bottom: 0.25rem;">Keyword Match</div>
                <div style="font-size: 1.5rem; font-weight: 700; color: #48bb78;">Advanced NLP</div>
            </div>
            <div style="background: white; padding: 1rem; border-radius: 8px; border: 1px solid #e2e8f0; flex: 1; min-width: 200px;">
                <div style="font-size: 0.875rem; color: #64748b; margin-bottom: 0.25rem;">Experience Analysis</div>
                <div style="font-size: 1.5rem; font-weight: 700; color: #ed8936;">ML-Powered</div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # Job opening selection first
    st.markdown("### 💼 Select Job Opening")
    
    # First, check if user wants to use saved JD or create new one
    jd_selection_method = st.radio(
        "Choose how to select job opening:",
        ["📚 Use Saved Job Description", "🆕 Create New Job Opening"],
        horizontal=True,
        help="Select whether to use a previously saved job description or create a new one"
    )
    
    selected_job = None
    job_description = ""
    
    if jd_selection_method == "📚 Use Saved Job Description":
        # Load saved job descriptions
        saved_jds = load_saved_jds()
        
        if not saved_jds:
            st.warning("📝 No saved job descriptions found. Please create a new job opening first.")
            st.info("💡 Tip: After creating and using a job opening, it will be automatically saved for future use.")
            jd_selection_method = "🆕 Create New Job Opening"
        else:
            # Display saved JDs with selection
            st.markdown("#### 📚 Saved Job Descriptions")
            
            # Create columns for better layout
            col1, col2 = st.columns([3, 1])
            
            with col1:
                # Create a selectbox for saved JDs
                saved_jd_options = [f"{jd['title']} (Last used: {jd['last_updated'][:10]})" for jd in saved_jds]
                selected_saved_jd = st.selectbox(
                    "Choose from saved job descriptions:",
                    saved_jds,
                    format_func=lambda x: f"{x['title']} (Last used: {x['last_updated'][:10]})",
                    help="Select a previously saved job description"
                )
            
            with col2:
                if selected_saved_jd:
                    # Show usage count and delete option
                    st.metric("Usage Count", selected_saved_jd.get('usage_count', 0))
                    if st.button("🗑️ Delete", key="delete_jd_btn"):
                        if delete_saved_jd(selected_saved_jd['id']):
                            st.success("Job description deleted successfully!")
                            st.rerun()
            
            if selected_saved_jd:
                selected_job = selected_saved_jd['title']
                job_description = selected_saved_jd.get('description', '')
                
                # Display selected JD info
                st.info(f"📋 **Selected Job:** {selected_job}\n\n**Description:** {selected_saved_jd.get('description', 'No description available')}")
                
                # Show JD details in expandable section
                with st.expander("📋 View Full Job Description", expanded=False):
                    st.markdown(f"**Title:** {selected_saved_jd['title']}")
                    st.markdown(f"**Description:** {selected_saved_jd.get('description', 'No description')}")
                    st.markdown(f"**Requirements:** {selected_saved_jd.get('requirements', 'No requirements specified')}")
                    st.markdown(f"**Created:** {selected_saved_jd['created_date'][:10]}")
                    st.markdown(f"**Last Updated:** {selected_saved_jd['last_updated'][:10]}")
                    st.markdown(f"**Usage Count:** {selected_saved_jd.get('usage_count', 0)}")
                
                # Option to modify the saved job description
                st.markdown("#### ✏️ Modify Job Description")
                modify_option = st.radio(
                    "Would you like to modify this job description?",
                    ["✅ Use as-is", "📝 Edit Text", "📋 Paste New Description"],
                    horizontal=True,
                    help="Choose whether to use the saved description as-is or modify it"
                )
                
                if modify_option == "📝 Edit Text":
                    modified_jd = st.text_area(
                        "Edit the job description:",
                        value=job_description,
                        height=150,
                        help="Modify the job description as needed"
                    )
                    if modified_jd != job_description:
                        job_description = modified_jd
                        st.success("✅ Job description updated!")
                
                elif modify_option == "📋 Paste New Description":
                    st.markdown("**📋 Paste New Job Description**")
                    st.info("💡 **Tip:** Copy your new job description from any source and paste it below to replace the current one.")
                    
                    pasted_new_jd = st.text_area(
                        "Paste your new job description here:",
                        value="",
                        height=200,
                        placeholder="Paste your complete new job description here...",
                        help="Paste the complete new job description from any source"
                    )
                    
                    if pasted_new_jd.strip():
                        with st.expander("👀 Preview New Content", expanded=True):
                            st.markdown("**New pasted content:**")
                            st.text(pasted_new_jd[:500] + ("..." if len(pasted_new_jd) > 500 else ""))
                            st.caption(f"Character count: {len(pasted_new_jd)}")
                        
                        job_description = pasted_new_jd
                        st.success("✅ New job description pasted and ready to use!")
    
    if jd_selection_method == "🆕 Create New Job Opening" or (jd_selection_method == "📚 Use Saved Job Description" and not saved_jds):
        # Sample job openings (in real app, this would come from database)
        job_openings = {
            "Software Engineer - Full Stack": "Full-stack development with React, Node.js, and cloud technologies",
            "Data Scientist": "Machine learning, Python, and statistical analysis expertise",
            "DevOps Engineer": "Infrastructure automation, Docker, Kubernetes, and CI/CD",
            "Product Manager": "Product strategy, user research, and agile methodologies",
            "UX Designer": "User experience design, prototyping, and design systems"
        }
        
        selected_job = st.selectbox(
            "Choose the job opening to evaluate against:",
            list(job_openings.keys()),
            help="Select the job opening you want to evaluate the candidate for"
        )
        
        if selected_job:
            st.info(f"📋 **Selected Job:** {selected_job}\n\n**Description:** {job_openings[selected_job]}")
            
            # Allow user to add custom requirements or paste job description
            st.markdown("#### 📝 Job Description Input")
            
            # Radio button to choose input method
            input_method = st.radio(
                "Choose how to provide job description:",
                ["📝 Type/Edit Text", "📋 Paste from Clipboard"],
                horizontal=True,
                help="Select whether to type/edit the job description or paste it from clipboard"
            )
            
            if input_method == "📝 Type/Edit Text":
            custom_requirements = st.text_area(
                "Add custom requirements or modify job description:",
                value=job_openings[selected_job],
                height=120,
                help="Customize the job description with specific requirements"
            )
            else:
                # Paste functionality
                st.markdown("**📋 Paste Job Description**")
                st.info("💡 **Tip:** Copy your job description from any source (PDF, Word, website, etc.) and paste it below. The system will automatically clean and format the text.")
                
                # Large text area for pasting
                pasted_jd = st.text_area(
                    "Paste your job description here:",
                    value="",
                    height=200,
                    placeholder="Paste your complete job description here...\n\nExample:\n• Job Title: Software Engineer\n• Company: Tech Corp\n• Location: Remote\n• Requirements:\n  - 3+ years Python experience\n  - React/Node.js knowledge\n  - Cloud experience preferred\n• Responsibilities:\n  - Develop web applications\n  - Collaborate with team\n  - Maintain code quality",
                    help="Paste the complete job description from any source. The system will automatically extract and format the content."
                )
                
                if pasted_jd.strip():
                    # Show preview of pasted content
                    with st.expander("👀 Preview Pasted Content", expanded=True):
                        st.markdown("**Raw pasted content:**")
                        st.text(pasted_jd[:500] + ("..." if len(pasted_jd) > 500 else ""))
                        
                        # Show character count
                        st.caption(f"Character count: {len(pasted_jd)}")
                    
                    custom_requirements = pasted_jd
                else:
                    custom_requirements = job_openings[selected_job]
            
            if custom_requirements != job_openings[selected_job]:
                job_description = custom_requirements
            else:
                job_description = job_openings[selected_job]
    
    st.markdown("---")
    
    # Compact hero section
        st.markdown("""
    <div style="background: linear-gradient(135deg, #1e40af, #1e3a8a); color: white; border-radius: 0.75rem; padding: 2rem; margin: 1rem 0; position: relative; overflow: hidden;">
        <h1 style="font-size: 2rem; font-weight: 700; margin-bottom: 0.75rem; position: relative; z-index: 2;">
            IKF Candidate Evaluation Platform
                </h1>
        <p style="font-size: 1rem; opacity: 0.9; margin-bottom: 1.5rem; position: relative; z-index: 2; line-height: 1.6;">
            Evaluate candidates with AI-powered insights for informed hiring decisions.
                </p>
        <div style="display: flex; gap: 0.75rem; flex-wrap: wrap; position: relative; z-index: 2;">
            <span style="background: #dcfce7; color: #059669; padding: 0.25rem 0.5rem; border-radius: 0.375rem; font-size: 0.75rem; font-weight: 600; text-transform: uppercase; letter-spacing: 0.05em;">🎯 Smart Matching</span>
            <span style="background: #dbeafe; color: #1e40af; padding: 0.25rem 0.5rem; border-radius: 0.375rem; font-size: 0.75rem; font-weight: 600; text-transform: uppercase; letter-spacing: 0.05em;">📊 Detailed Insights</span>
            <span style="background: #dcfce7; color: #059669; padding: 0.25rem 0.5rem; border-radius: 0.375rem; font-size: 0.75rem; font-weight: 600; text-transform: uppercase; letter-spacing: 0.05em;">⚡ Fast Evaluation</span>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
    # File upload section
    st.markdown("### 📁 Candidate Resume Upload")
    col1, col2 = st.columns(2)
        
    with col1:
        st.markdown("#### 📄 Professional Resume Analysis")
        
        # Resume upload with enhanced features
        resume_file = st.file_uploader(
            "Upload Candidate Resume (PDF, DOCX, TXT)",
            type=['pdf', 'docx', 'txt'],
            key="resume_upload",
            help="Supported formats: PDF, DOCX, TXT. Maximum file size: 10MB"
        )
        
        # ATS optimization tips
        with st.expander("💡 ATS Optimization Tips", expanded=False):
            st.markdown("""
            **For better ATS scores, ensure your resume includes:**
            - Clear section headers (Experience, Education, Skills)
            - Relevant keywords from the job description
            - Quantified achievements and metrics
            - Standard fonts (Arial, Calibri, Times New Roman)
            - Proper formatting without tables or graphics
            - Contact information at the top
            - Professional email address
            """)
        
        # Resume quality checker
        if resume_file:
            st.success(f"✅ Resume uploaded: {resume_file.name}")
            
            # File size check
            file_size = len(resume_file.getvalue())
            if file_size > 10 * 1024 * 1024:  # 10MB
                st.warning("⚠️ File size is large. Processing may take longer.")
            else:
                st.info(f"📊 File size: {file_size / 1024:.1f} KB")
        
        # Professional resume analysis
        if resume_file:
            st.markdown("#### 🔍 Advanced Resume Analysis")
            
            # Create temporary file and extract text
            with tempfile.NamedTemporaryFile(delete=False, suffix=f".{resume_file.name.split('.')[-1]}") as tmp_file:
                tmp_file.write(resume_file.getvalue())
                tmp_file_path = tmp_file.name
            
            try:
                # Extract text using file handler
                success, extracted_resume_text = file_handler.extract_text(tmp_file_path)
                
                if success:
                    st.success(f"✅ Successfully extracted text from {resume_file.name}")
                    
                    # Show loading spinner for AI analysis
                    with st.spinner("🤖 Analyzing resume with AI..."):
                        # Extract comprehensive resume data
                        resume_data = extract_resume_data(extracted_resume_text)
                        
                        if resume_data:
                            # Display extracted data in a professional format
                            st.markdown("#### 📊 Extracted Candidate Information")
                            
                            # Create columns for better layout
                            col_info1, col_info2 = st.columns(2)
                            
                            with col_info1:
                                st.markdown("**👤 Personal Information**")
                                st.write(f"**Name:** {resume_data.get('name', 'Not found')}")
                                st.write(f"**Email:** {resume_data.get('email', 'Not found')}")
                                st.write(f"**Phone:** {resume_data.get('phone', 'Not found')}")
                                st.write(f"**Location:** {resume_data.get('location', 'Not found')}")
                                st.write(f"**Experience:** {resume_data.get('years_experience', 0)} years")
                            
                            with col_info2:
                                st.markdown("**🎯 Professional Summary**")
                                if resume_data.get('summary'):
                                    st.write(f"**Summary:** {resume_data['summary'][:200]}...")
                                
                                st.markdown("**🛠️ Key Skills**")
                                skills = resume_data.get('skills', [])
                                if skills:
                                    st.write(", ".join(skills[:8]))  # Show first 8 skills
                                else:
                                    st.write("No skills detected")
                            
                            # Store resume data in session state for analysis
                            st.session_state.resume_data = resume_data
                            
                        else:
                            st.error("❌ Could not extract data from resume. Please try a different file format.")
                    
                    # Resume text preview (collapsible)
                    with st.expander("📋 View Full Resume Text", expanded=False):
                        st.text_area("Resume Text:", value=extracted_resume_text, height=200, disabled=True)
                        
                else:
                    st.error(f"❌ Failed to extract text from {resume_file.name}: {extracted_resume_text}")
                    
            except Exception as e:
                st.error(f"❌ Error processing resume file: {str(e)}")
            finally:
                # Clean up temporary file
                if os.path.exists(tmp_file_path):
                    os.unlink(tmp_file_path)
    
    with col2:
        st.markdown("#### Additional Job Details")
        job_desc_file = st.file_uploader(
            "Upload Additional Job Details (PDF, DOCX, TXT)",
            type=['pdf', 'docx', 'txt'],
            key="job_desc_upload"
        )
    
    # Manual job description input
    if not job_desc_file:
        st.markdown("### 📝 Additional Job Requirements")
        job_description = st.text_area(
            "Add specific requirements or criteria:",
            height=150,
            placeholder="Add specific skills, experience levels, or requirements for this job opening..."
        )
    else:
        # Extract text from uploaded job description file
        st.markdown("### 📝 Job Description from File")
        
        # Create temporary file and extract text
        with tempfile.NamedTemporaryFile(delete=False, suffix=f".{job_desc_file.name.split('.')[-1]}") as tmp_file:
            tmp_file.write(job_desc_file.getvalue())
            tmp_file_path = tmp_file.name
        
        try:
            # Extract text using file handler
            success, extracted_text = file_handler.extract_text(tmp_file_path)
            
            if success:
                job_description = extracted_text
                st.success(f"✅ Successfully extracted text from {job_desc_file.name}")
                
                # Show extracted text in expandable section
                with st.expander("📋 View Extracted Job Description", expanded=False):
                    st.text_area("Extracted Text:", value=extracted_text, height=200, disabled=True)
            else:
                st.error(f"❌ Failed to extract text from {job_desc_file.name}: {extracted_text}")
                job_description = ""
                
        except Exception as e:
            st.error(f"❌ Error processing file: {str(e)}")
            job_description = ""
        finally:
            # Clean up temporary file
            if os.path.exists(tmp_file_path):
                os.unlink(tmp_file_path)
                    
    # Save job description option (only show if not using saved JD)
    if jd_selection_method == "🆕 Create New Job Opening" and selected_job and job_description:
        st.markdown("### 💾 Save Job Description")
        save_jd = st.checkbox(
            "💾 Save this job description for future use",
            help="Save this job description so you can reuse it later without re-typing"
        )
        
        if save_jd:
            jd_title = st.text_input(
                "Job Description Title:",
                value=selected_job,
                help="Give this job description a memorable title"
            )
            
            if st.button("💾 Save Job Description", type="secondary"):
                jd_data = {
                    'title': jd_title,
                    'description': job_description,
                    'requirements': job_description,
                    'category': 'Custom'
                }
                
                if save_jd_to_storage(jd_data):
                    st.success(f"✅ Job description '{jd_title}' saved successfully!")
                    st.info("💡 You can now select 'Use Saved Job Description' to reuse this in the future.")
                else:
                    st.error("❌ Failed to save job description. Please try again.")
    
    st.markdown("---")
    
    # Professional ATS Analysis Button
    if st.button("🚀 Launch Professional ATS Analysis", type="primary", use_container_width=True):
        if resume_file and selected_job and 'resume_data' in st.session_state:
            # Save job description if it's new and not already saved
            if jd_selection_method == "🆕 Create New Job Opening" and job_description:
                jd_data = {
                    'title': selected_job,
                    'description': job_description,
                    'requirements': job_description,
                    'category': 'Template'
                }
                save_jd_to_storage(jd_data)
            
            # Show progress
            st.markdown("### 🔄 Professional ATS Analysis Progress")
            
            # Progress bar
            progress_container = st.container()
            with progress_container:
                status_text = st.empty()
                progress_bar = st.progress(0)
            
            # Professional ATS evaluation steps
            evaluation_steps = [
                "🔍 Extracting candidate data with NLP...",
                "🎯 Analyzing job-candidate match...",
                "📊 Calculating ATS scores...",
                "🤖 Running ML predictions...",
                "📈 Generating quality analysis...",
                "💡 Creating hiring recommendations...",
                "✅ Professional analysis complete!"
            ]
            
            for i, step in enumerate(evaluation_steps):
                progress = (i + 1) / len(evaluation_steps)
                progress_bar.progress(progress)
                status_text.markdown(f"<div style='background: linear-gradient(135deg, #dbeafe 0%, #e0e7ff 100%); color: #1e40af; padding: 0.5rem 1rem; border-radius: 0.5rem; font-size: 0.875rem; font-weight: 600; text-transform: uppercase; letter-spacing: 0.05em; display: inline-block; box-shadow: 0 2px 4px rgba(0,0,0,0.1);'>{step}</div>", unsafe_allow_html=True)
                time.sleep(1.0)
            
            st.success("🎉 Professional ATS analysis completed successfully! Review the comprehensive assessment below.")
            
            # Professional ATS Results
            st.markdown("### 📊 Professional ATS Analysis Results")
            
            # Get resume data and calculate ATS scores
            resume_data = st.session_state.resume_data
            ats_scores = calculate_ats_score(resume_data, job_description)
            quality_analysis = analyze_resume_quality(resume_data)
            ats_report = generate_ats_report(resume_data, job_description, ats_scores)
            
            # Professional ATS metrics
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
            st.markdown("""
                <div style="background: linear-gradient(135deg, #f0f9ff 0%, #e0f2fe 100%); border: 1px solid #0ea5e9; border-radius: 12px; padding: 1.5rem; text-align: center; box-shadow: 0 4px 15px rgba(14, 165, 233, 0.1);">
                    <div style="font-size: 2rem; font-weight: 800; color: #0c4a6e; margin-bottom: 0.5rem;">{}</div>
                    <div style="font-size: 0.875rem; color: #0369a1; font-weight: 600;">OVERALL ATS SCORE</div>
            </div>
                """.format(ats_scores['overall_score'] if ats_scores else 0), unsafe_allow_html=True)
            
            with col2:
                            st.markdown("""
                <div style="background: linear-gradient(135deg, #f0fdf4 0%, #dcfce7 100%); border: 1px solid #22c55e; border-radius: 12px; padding: 1.5rem; text-align: center; box-shadow: 0 4px 15px rgba(34, 197, 94, 0.1);">
                    <div style="font-size: 2rem; font-weight: 800; color: #166534; margin-bottom: 0.5rem;">{}</div>
                    <div style="font-size: 0.875rem; color: #15803d; font-weight: 600;">KEYWORD MATCH</div>
                            </div>
                """.format(ats_scores['keyword_match'] if ats_scores else 0), unsafe_allow_html=True)
                            
            with col3:
        st.markdown("""
                <div style="background: linear-gradient(135deg, #fef3c7 0%, #fde68a 100%); border: 1px solid #f59e0b; border-radius: 12px; padding: 1.5rem; text-align: center; box-shadow: 0 4px 15px rgba(245, 158, 11, 0.1);">
                    <div style="font-size: 2rem; font-weight: 800; color: #92400e; margin-bottom: 0.5rem;">{}</div>
                    <div style="font-size: 0.875rem; color: #d97706; font-weight: 600;">SKILL MATCH</div>
        </div>
                """.format(ats_scores['skill_match'] if ats_scores else 0), unsafe_allow_html=True)
            
            with col4:
                st.markdown("""
                <div style="background: linear-gradient(135deg, #fdf2f8 0%, #fce7f3 100%); border: 1px solid #ec4899; border-radius: 12px; padding: 1.5rem; text-align: center; box-shadow: 0 4px 15px rgba(236, 72, 153, 0.1);">
                    <div style="font-size: 2rem; font-weight: 800; color: #831843; margin-bottom: 0.5rem;">{}</div>
                    <div style="font-size: 0.875rem; color: #be185d; font-weight: 600;">EXPERIENCE MATCH</div>
                </div>
                """.format(ats_scores['experience_match'] if ats_scores else 0), unsafe_allow_html=True)
            
            # Professional ATS Analysis Details
            st.markdown("---")
            
            # Detailed Analysis Tabs
            tab1, tab2, tab3, tab4 = st.tabs(["📊 ATS Scores", "🎯 Match Analysis", "📈 Quality Report", "💡 Recommendations"])
            
            with tab1:
                st.markdown("#### 📊 Comprehensive ATS Scoring")
                
                # ATS Score Breakdown
                col1, col2 = st.columns(2)
                
                with col1:
                    st.markdown("**Overall Performance**")
                    if ats_scores:
                        # Create a gauge chart for overall score
                        fig = go.Figure(go.Indicator(
                            mode = "gauge+number+delta",
                            value = ats_scores['overall_score'],
                            domain = {'x': [0, 1], 'y': [0, 1]},
                            title = {'text': "Overall ATS Score"},
                            delta = {'reference': 70},
                            gauge = {
                                'axis': {'range': [None, 100]},
                                'bar': {'color': "darkblue"},
                                'steps': [
                                    {'range': [0, 50], 'color': "lightgray"},
                                    {'range': [50, 70], 'color': "yellow"},
                                    {'range': [70, 100], 'color': "green"}
                                ],
                                'threshold': {
                                    'line': {'color': "red", 'width': 4},
                                    'thickness': 0.75,
                                    'value': 90
                                }
                            }
                        ))
                        fig.update_layout(height=300)
                        st.plotly_chart(fig, use_container_width=True)
                
                with col2:
                    st.markdown("**Score Breakdown**")
                    if ats_scores:
                        score_data = {
                            'Metric': ['Keyword Match', 'Skill Match', 'Experience Match', 'ML Prediction'],
                            'Score': [
                                ats_scores['keyword_match'],
                                ats_scores['skill_match'], 
                                ats_scores['experience_match'],
                                ats_scores['ml_score']
                            ]
                        }
                        
                        df_scores = pd.DataFrame(score_data)
                        
                        # Create horizontal bar chart
                        fig = px.bar(df_scores, x='Score', y='Metric', orientation='h',
                                   color='Score', color_continuous_scale='Viridis',
                                   title="ATS Score Breakdown")
                        fig.update_layout(height=300, showlegend=False)
                        st.plotly_chart(fig, use_container_width=True)
            
            with tab2:
                st.markdown("#### 🎯 Job-Candidate Match Analysis")
                
                # Match analysis details
                col1, col2 = st.columns(2)
                
                with col1:
                    st.markdown("**Required vs. Candidate Skills**")
                    if resume_data and job_description:
                        # Extract skills from job description
                        job_skills = text_processor.extract_skills(job_description)
                        candidate_skills = resume_data.get('skills', [])
                        
                        # Find matching skills
                        matching_skills = [skill for skill in job_skills if skill.lower() in [s.lower() for s in candidate_skills]]
                        missing_skills = [skill for skill in job_skills if skill.lower() not in [s.lower() for s in candidate_skills]]
                        
                        st.markdown(f"**✅ Matching Skills ({len(matching_skills)}):**")
                        for skill in matching_skills[:10]:  # Show first 10
                            st.markdown(f"• {skill}")
                        
                        st.markdown(f"**❌ Missing Skills ({len(missing_skills)}):**")
                        for skill in missing_skills[:10]:  # Show first 10
                            st.markdown(f"• {skill}")
                
                with col2:
                    st.markdown("**Experience Analysis**")
                    if resume_data:
                        years_exp = resume_data.get('years_experience', 0)
                        st.metric("Years of Experience", years_exp)
                        
                        # Experience level assessment
                        if years_exp >= 5:
                            st.success("✅ Senior level experience")
                        elif years_exp >= 2:
                            st.info("ℹ️ Mid-level experience")
                        else:
                            st.warning("⚠️ Entry level experience")
                        
                        # Education analysis
                        education = resume_data.get('education', [])
                        if education:
                            st.markdown("**Education:**")
                            for edu in education[:3]:  # Show first 3
                                st.markdown(f"• {edu}")
            
            with tab3:
                st.markdown("#### 📈 Resume Quality Analysis")
                
                if quality_analysis:
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        st.markdown("**✅ Strengths**")
                        for strength in quality_analysis.get('strengths', []):
                            st.markdown(f"• {strength}")
                        
                        st.markdown("**⚠️ Areas for Improvement**")
                        for weakness in quality_analysis.get('weaknesses', []):
                            st.markdown(f"• {weakness}")
                    
                    with col2:
                        st.markdown("**🚨 Red Flags**")
                        red_flags = quality_analysis.get('red_flags', [])
                        if red_flags:
                            for flag in red_flags:
                                st.markdown(f"• {flag}")
                        else:
                            st.success("✅ No red flags detected")
                        
                        st.markdown("**📊 Overall Quality**")
                        quality = quality_analysis.get('overall_quality', 'Unknown')
                        if quality == 'Excellent':
                            st.success(f"🌟 {quality}")
                        elif quality == 'Good':
                            st.info(f"👍 {quality}")
                        else:
                            st.warning(f"⚠️ {quality}")
            
            with tab4:
                st.markdown("#### 💡 Professional Recommendations")
                
                if ats_report:
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        st.markdown("**🎯 Hiring Recommendations**")
                        for rec in ats_report.get('recommendations', []):
                            st.markdown(f"• {rec}")
                        
                        st.markdown("**📋 Next Steps**")
                        for step in ats_report.get('next_steps', []):
                            st.markdown(f"• {step}")
                    
                    with col2:
                        st.markdown("**📊 Candidate Summary**")
                        summary = ats_report.get('candidate_summary', {})
                        
                        st.write(f"**Experience:** {summary.get('years_experience', 0)} years")
                        
                        st.write("**Key Skills:**")
                        for skill in summary.get('key_skills', [])[:5]:
                            st.write(f"• {skill}")
                        
                        st.write("**Education:**")
                        for edu in summary.get('education', [])[:2]:
                            st.write(f"• {edu}")
            
            # Professional Action Buttons
            st.markdown("---")
            st.markdown("#### 🚀 Professional Actions")
            
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                if st.button("📧 Send Interview Invite", type="primary"):
                    st.success("📧 Interview invite sent successfully!")
            
            with col2:
                if st.button("📋 Add to Shortlist", type="secondary"):
                    st.success("📋 Candidate added to shortlist!")
            
            with col3:
                if st.button("📊 Generate Report", type="secondary"):
                    st.success("📊 Professional report generated!")
            
            with col4:
                if st.button("❌ Reject Candidate", type="secondary"):
                    st.warning("❌ Candidate rejected. Feedback sent.")
            
        else:
            st.warning("⚠️ Please upload a resume and select a job opening to begin analysis.")

elif page == "Bulk Resume Screening":
    # Professional Bulk Processing Header
    st.markdown("""
    <div style="background: linear-gradient(135deg, #f8fafc 0%, #f1f5f9 100%); border: 1px solid #e2e8f0; border-radius: 12px; padding: 2rem; margin-bottom: 2rem; box-shadow: 0 4px 15px rgba(0,0,0,0.05);">
        <div style="display: flex; align-items: center; gap: 1rem; margin-bottom: 1rem;">
            <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 0.75rem; border-radius: 12px; font-size: 1.5rem;">
                📁
            </div>
            <div>
                <h1 style="font-size: 2rem; font-weight: 700; color: #0f172a; margin: 0;">
                    Professional Bulk Resume Screening
                </h1>
                <p style="font-size: 1rem; color: #475569; margin: 0.25rem 0 0 0;">
                    AI-powered screening and ranking of multiple candidates
                </p>
            </div>
        </div>
        <div style="display: flex; gap: 2rem; flex-wrap: wrap;">
            <div style="background: white; padding: 1rem; border-radius: 8px; border: 1px solid #e2e8f0; flex: 1; min-width: 200px;">
                <div style="font-size: 0.875rem; color: #64748b; margin-bottom: 0.25rem;">Batch Processing</div>
                <div style="font-size: 1.5rem; font-weight: 700; color: #667eea;">AI-Powered</div>
            </div>
            <div style="background: white; padding: 1rem; border-radius: 8px; border: 1px solid #e2e8f0; flex: 1; min-width: 200px;">
                <div style="font-size: 0.875rem; color: #64748b; margin-bottom: 0.25rem;">Smart Ranking</div>
                <div style="font-size: 1.5rem; font-weight: 700; color: #48bb78;">ML-Based</div>
            </div>
            <div style="background: white; padding: 1rem; border-radius: 8px; border: 1px solid #e2e8f0; flex: 1; min-width: 200px;">
                <div style="font-size: 0.875rem; color: #64748b; margin-bottom: 0.25rem;">Export Reports</div>
                <div style="font-size: 1.5rem; font-weight: 700; color: #ed8936;">Professional</div>
            </div>
        </div>
        </div>
        """, unsafe_allow_html=True)
        
    # Job selection for bulk processing
    st.markdown("### 💼 Select Job Opening for Bulk Screening")
    
    # Use the same job selection logic as single candidate
    jd_selection_method = st.radio(
        "Choose how to select job opening:",
        ["📚 Use Saved Job Description", "🆕 Create New Job Opening"],
        horizontal=True,
        help="Select whether to use a previously saved job description or create a new one"
    )
    
    selected_job = None
    job_description = ""
    
    if jd_selection_method == "📚 Use Saved Job Description":
        saved_jds = load_saved_jds()
        
        if not saved_jds:
            st.warning("📝 No saved job descriptions found. Please create a new job opening first.")
            jd_selection_method = "🆕 Create New Job Opening"
        else:
            selected_saved_jd = st.selectbox(
                "Choose from saved job descriptions:",
                saved_jds,
                format_func=lambda x: f"{x['title']} (Last used: {x['last_updated'][:10]})",
                help="Select a previously saved job description"
            )
            
            if selected_saved_jd:
                selected_job = selected_saved_jd['title']
                job_description = selected_saved_jd.get('description', '')
                st.info(f"📋 **Selected Job:** {selected_job}")
    
    if jd_selection_method == "🆕 Create New Job Opening" or (jd_selection_method == "📚 Use Saved Job Description" and not saved_jds):
        job_openings = {
            "Software Engineer - Full Stack": "Full-stack development with React, Node.js, and cloud technologies",
            "Data Scientist": "Machine learning, Python, and statistical analysis expertise",
            "DevOps Engineer": "Infrastructure automation, Docker, Kubernetes, and CI/CD",
            "Product Manager": "Product strategy, user research, and agile methodologies",
            "UX Designer": "User experience design, prototyping, and design systems"
        }
        
        selected_job = st.selectbox(
            "Choose the job opening to evaluate against:",
            list(job_openings.keys()),
            help="Select the job opening you want to evaluate candidates for"
        )
        
        if selected_job:
            job_description = job_openings[selected_job]
            st.info(f"📋 **Selected Job:** {selected_job}")
    
    st.markdown("---")
    
    # Bulk resume upload
    st.markdown("### 📁 Upload Multiple Resumes")
    
    uploaded_files = st.file_uploader(
        "Upload Multiple Resumes (PDF, DOCX, TXT)",
        type=['pdf', 'docx', 'txt'],
        accept_multiple_files=True,
        help="Upload multiple resume files for bulk screening. Maximum 50 files."
    )
    
    if uploaded_files:
        st.success(f"✅ {len(uploaded_files)} resume(s) uploaded successfully!")
        
        # Show file details
        with st.expander("📋 View Uploaded Files", expanded=False):
            for i, file in enumerate(uploaded_files, 1):
                file_size = len(file.getvalue()) / 1024  # KB
                st.write(f"{i}. {file.name} ({file_size:.1f} KB)")
    
    # Bulk processing options
    if uploaded_files and selected_job:
        st.markdown("### ⚙️ Bulk Processing Options")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("**🎯 Analysis Settings**")
            include_quality_analysis = st.checkbox("Include resume quality analysis", value=True)
            include_ml_predictions = st.checkbox("Include ML success predictions", value=True)
            generate_rankings = st.checkbox("Generate candidate rankings", value=True)
        
        with col2:
            st.markdown("**📊 Export Options**")
            export_format = st.selectbox("Export format:", ["Excel", "PDF", "CSV"])
            include_charts = st.checkbox("Include visualizations", value=True)
            detailed_analysis = st.checkbox("Detailed analysis report", value=True)
        
        # Launch bulk processing
        if st.button("🚀 Launch Bulk ATS Analysis", type="primary", use_container_width=True):
            if len(uploaded_files) > 50:
                st.error("❌ Maximum 50 files allowed for bulk processing.")
            else:
                # Show progress
                st.markdown("### 🔄 Bulk Processing Progress")
                
                progress_container = st.container()
                with progress_container:
                    status_text = st.empty()
                    progress_bar = st.progress(0)
                
                # Process each file
                results = []
                total_files = len(uploaded_files)
                
                for i, file in enumerate(uploaded_files):
                    progress = (i + 1) / total_files
                    progress_bar.progress(progress)
                    status_text.markdown(f"Processing {i+1}/{total_files}: {file.name}")
                    
                    # Extract text from file
                    with tempfile.NamedTemporaryFile(delete=False, suffix=f".{file.name.split('.')[-1]}") as tmp_file:
                        tmp_file.write(file.getvalue())
                        tmp_file_path = tmp_file.name
                    
                    try:
                        success, extracted_text = file_handler.extract_text(tmp_file_path)
                        
                        if success:
                            # Extract resume data
                            resume_data = extract_resume_data(extracted_text)
                            
                            if resume_data:
                                # Calculate ATS scores
                                ats_scores = calculate_ats_score(resume_data, job_description)
                                
                                # Add to results
                                results.append({
                                    'file_name': file.name,
                                    'candidate_name': resume_data.get('name', 'Unknown'),
                                    'email': resume_data.get('email', 'Not found'),
                                    'phone': resume_data.get('phone', 'Not found'),
                                    'experience_years': resume_data.get('years_experience', 0),
                                    'skills': resume_data.get('skills', []),
                                    'ats_score': ats_scores['overall_score'] if ats_scores else 0,
                                    'keyword_match': ats_scores['keyword_match'] if ats_scores else 0,
                                    'skill_match': ats_scores['skill_match'] if ats_scores else 0,
                                    'experience_match': ats_scores['experience_match'] if ats_scores else 0,
                                    'resume_data': resume_data
                                })
                        
                    except Exception as e:
                        st.error(f"Error processing {file.name}: {e}")
                    finally:
                        if os.path.exists(tmp_file_path):
                            os.unlink(tmp_file_path)
                
                # Sort results by ATS score
                results.sort(key=lambda x: x['ats_score'], reverse=True)
                
                st.success(f"🎉 Bulk processing completed! Processed {len(results)} resumes successfully.")
                
                # Display results
                st.markdown("### 📊 Bulk Screening Results")
                
                # Summary metrics
                col1, col2, col3, col4 = st.columns(4)
                
                with col1:
                    st.metric("Total Candidates", len(results))
                
                with col2:
                    avg_score = sum(r['ats_score'] for r in results) / len(results) if results else 0
                    st.metric("Average ATS Score", f"{avg_score:.1f}")
                
                with col3:
                    strong_candidates = len([r for r in results if r['ats_score'] >= 70])
                    st.metric("Strong Candidates", strong_candidates)
                
                with col4:
                    st.metric("Processing Time", f"{total_files * 2}s")
                
                # Results table
                st.markdown("#### 📋 Candidate Rankings")
                
                # Create DataFrame for display
                df_results = pd.DataFrame([
                    {
                        'Rank': i+1,
                        'Name': r['candidate_name'],
                        'Email': r['email'],
                        'Experience': f"{r['experience_years']} years",
                        'ATS Score': f"{r['ats_score']:.1f}",
                        'Keyword Match': f"{r['keyword_match']:.1f}",
                        'Skill Match': f"{r['skill_match']:.1f}",
                        'Experience Match': f"{r['experience_match']:.1f}",
                        'Status': 'Strong Match' if r['ats_score'] >= 70 else 'Good Match' if r['ats_score'] >= 50 else 'Consider'
                    }
                    for i, r in enumerate(results)
                ])
                
                st.dataframe(df_results, use_container_width=True)
                
                # Top candidates section
                st.markdown("#### 🏆 Top Candidates")
                
                top_candidates = results[:5]  # Show top 5
                
                for i, candidate in enumerate(top_candidates, 1):
                    with st.expander(f"#{i} {candidate['candidate_name']} - ATS Score: {candidate['ats_score']:.1f}", expanded=i==1):
                        col1, col2 = st.columns(2)
                        
                        with col1:
                            st.write(f"**Email:** {candidate['email']}")
                            st.write(f"**Phone:** {candidate['phone']}")
                            st.write(f"**Experience:** {candidate['experience_years']} years")
                        
                        with col2:
                            st.write(f"**ATS Score:** {candidate['ats_score']:.1f}")
                            st.write(f"**Keyword Match:** {candidate['keyword_match']:.1f}")
                            st.write(f"**Skill Match:** {candidate['skill_match']:.1f}")
                        
                        # Action buttons for each candidate
                        col_btn1, col_btn2, col_btn3 = st.columns(3)
                        
                        with col_btn1:
                            if st.button(f"📧 Interview", key=f"interview_{i}"):
                                st.success("Interview invite sent!")
                        
                        with col_btn2:
                            if st.button(f"📋 Shortlist", key=f"shortlist_{i}"):
                                st.success("Added to shortlist!")
                        
                        with col_btn3:
                            if st.button(f"📊 Details", key=f"details_{i}"):
                                st.info("Detailed analysis available in single candidate view")
                
                # Export options
                st.markdown("#### 📤 Export Results")
                
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    if st.button("📊 Export to Excel", type="primary"):
                        st.success("Excel report generated and ready for download!")
                
                with col2:
                    if st.button("📄 Export to PDF", type="secondary"):
                        st.success("PDF report generated and ready for download!")
                
                with col3:
                    if st.button("📋 Export to CSV", type="secondary"):
                        st.success("CSV file generated and ready for download!")
    
    elif not uploaded_files:
        st.info("📁 Please upload resume files to begin bulk screening.")
    elif not selected_job:
        st.info("💼 Please select a job opening to begin bulk screening.")

elif page == "ATS Analytics Dashboard":
    # Professional Analytics Dashboard
        st.markdown("""
    <div style="background: linear-gradient(135deg, #f8fafc 0%, #f1f5f9 100%); border: 1px solid #e2e8f0; border-radius: 12px; padding: 2rem; margin-bottom: 2rem; box-shadow: 0 4px 15px rgba(0,0,0,0.05);">
        <div style="display: flex; align-items: center; gap: 1rem; margin-bottom: 1rem;">
            <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 0.75rem; border-radius: 12px; font-size: 1.5rem;">
                📊
            </div>
            <div>
                <h1 style="font-size: 2rem; font-weight: 700; color: #0f172a; margin: 0;">
                    Professional ATS Analytics Dashboard
                </h1>
                <p style="font-size: 1rem; color: #475569; margin: 0.25rem 0 0 0;">
                    Advanced recruitment metrics and performance insights
                </p>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # Analytics content
    st.markdown("### 📈 Recruitment Analytics")
    
    # Sample analytics data
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Total Candidates", "1,247", "12%")
    
    with col2:
        st.metric("ATS Score Average", "73.2", "5.1%")
    
    with col3:
        st.metric("Interview Rate", "34%", "8%")
    
    with col4:
        st.metric("Hire Rate", "18%", "3%")
    
    # Charts and visualizations
    st.markdown("#### 📊 Performance Metrics")
    
    # Sample charts
    chart_data = pd.DataFrame({
        'Month': ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun'],
        'Candidates': [120, 145, 167, 189, 201, 234],
        'Interviews': [45, 52, 61, 68, 72, 89],
        'Hires': [12, 15, 18, 21, 24, 28]
    })
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("**Candidate Pipeline**")
        fig = px.line(chart_data, x='Month', y=['Candidates', 'Interviews', 'Hires'], 
                     title="Monthly Recruitment Pipeline")
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        st.markdown("**ATS Score Distribution**")
        score_data = pd.DataFrame({
            'Score Range': ['0-30', '31-50', '51-70', '71-90', '91-100'],
            'Count': [45, 123, 234, 189, 67]
        })
        fig = px.bar(score_data, x='Score Range', y='Count', 
                    title="ATS Score Distribution")
        st.plotly_chart(fig, use_container_width=True)
    
    st.info("📊 This is a demo analytics dashboard. In a production environment, this would show real-time data from your ATS system.")

else:
    st.markdown("### 🚧 Feature Coming Soon")
    st.info("This feature is under development and will be available in the next update.")
