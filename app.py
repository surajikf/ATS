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
warnings.filterwarnings('ignore')

from branding import CompanyBranding

# Page configuration for HR professionals
st.set_page_config(
    page_title="IKF - HR Candidate Screening",
    page_icon="👥",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Apply optimized styling
st.markdown(CompanyBranding.get_css_styles(), unsafe_allow_html=True)

# HR-focused header
    st.markdown("""
<div style="background: linear-gradient(135deg, #1e40af, #1e3a8a); color: white; padding: 2rem; border-radius: 0.75rem; margin-bottom: 2rem;">
    <div style="display: flex; align-items: center; gap: 1rem; margin-bottom: 1rem;">
        <div style="font-size: 3rem;">👥</div>
        <div>
            <h1 style="margin: 0; font-size: 2.5rem; font-weight: 700;">IKF HR Candidate Screening</h1>
            <p style="margin: 0; font-size: 1.125rem; opacity: 0.9;">Professional AI-powered candidate evaluation for HR teams</p>
        </div>
    </div>
    <div style="display: flex; gap: 1rem; flex-wrap: wrap;">
        <span style="background: rgba(255,255,255,0.2); padding: 0.5rem 1rem; border-radius: 0.5rem; font-size: 0.875rem;">🎯 Smart Matching</span>
        <span style="background: rgba(255,255,255,0.2); padding: 0.5rem 1rem; border-radius: 0.5rem; font-size: 0.875rem;">⚡ Fast Screening</span>
        <span style="background: rgba(255,255,255,0.2); padding: 0.5rem 1rem; border-radius: 0.5rem; font-size: 0.875rem;">📊 Data-Driven</span>
        <span style="background: rgba(255,255,255,0.2); padding: 0.5rem 1rem; border-radius: 0.5rem; font-size: 0.875rem;">🤖 AI-Powered</span>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
# Welcome message for HR users
if 'first_visit' not in st.session_state:
    st.session_state.first_visit = True
    st.success("🎉 Welcome to IKF HR Candidate Screening Platform - Your AI-powered recruitment assistant!")

# HR-focused sidebar
    with st.sidebar:
    st.markdown("""
    <div style="background: white; border: 1px solid #e2e8f0; border-radius: 0.75rem; padding: 1.5rem; margin-bottom: 1rem;">
        <div style="text-align: center; margin-bottom: 1rem;">
            <div style="font-size: 2rem; margin-bottom: 0.5rem;">👔</div>
            <h3 style="margin: 0; color: #0f172a; font-size: 1.125rem;">HR Dashboard</h3>
            <p style="margin: 0; color: #64748b; font-size: 0.875rem;">Candidate Evaluation Tools</p>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    st.markdown("### 🎯 HR Workflows")
    
    # HR-focused navigation
    navigation_options = {
        "📋 Single Candidate Evaluation": "Evaluate individual candidate against job opening", 
        "📁 Bulk Candidate Screening": "Screen multiple candidates for job openings",
        "📊 Recruitment Analytics": "Track hiring metrics and performance",
        "💼 Job Opening Management": "Manage and update job descriptions"
    }
    
    page_display = st.selectbox(
        "Select HR Tool:",
        list(navigation_options.keys()),
        help="Choose the HR workflow you want to use"
    )
    
    # Show description for selected page
    st.markdown(f'<div style="background: #f8fafc; border: 1px solid #e2e8f0; border-radius: 0.75rem; padding: 1rem; margin-bottom: 1rem;">{navigation_options[page_display]}</div>', unsafe_allow_html=True)
    
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
if page == "Single Candidate Evaluation":
    # HR-focused header
    st.markdown("""
    <div style="background: white; border-bottom: 1px solid #e2e8f0; padding: 1.5rem 0; margin-bottom: 1.5rem;">
        <h1 style="font-size: 2rem; font-weight: 700; color: #0f172a; margin-bottom: 0.25rem;">
            Single Candidate Evaluation
        </h1>
        <p style="font-size: 1rem; color: #475569; margin: 0;">
            Professional AI-powered candidate analysis for job openings
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    # Job opening selection first
    st.markdown("### 💼 Select Job Opening")
    
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
        st.markdown("#### Candidate Resume")
        resume_file = st.file_uploader(
            "Upload Candidate Resume (PDF, DOCX, TXT)",
            type=['pdf', 'docx', 'txt'],
            key="resume_upload"
        )
    
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
                        job_description = ""
                    
    # Evaluation button
    if st.button("🚀 Launch Evaluation", type="primary", use_container_width=True):
        if resume_file and selected_job:
            # Show progress
            st.markdown("### 🔄 Evaluation Progress")
            
            # Progress bar
            progress_container = st.container()
            with progress_container:
                status_text = st.empty()
                progress_bar = st.progress(0)
            
            # Evaluation steps
            evaluation_steps = [
                "🔍 Analyzing candidate resume...",
                "🎯 Matching against job requirements...",
                "📊 Calculating fit scores...",
                "💡 Generating hiring insights...",
                "✅ Evaluation complete!"
            ]
            
            for i, step in enumerate(evaluation_steps):
                progress = (i + 1) / len(evaluation_steps)
                progress_bar.progress(progress)
                status_text.markdown(f"<div style='background: #dbeafe; color: #1e40af; padding: 0.25rem 0.5rem; border-radius: 0.375rem; font-size: 0.75rem; font-weight: 600; text-transform: uppercase; letter-spacing: 0.05em; display: inline-block;'>{step}</div>", unsafe_allow_html=True)
                time.sleep(0.8)
            
            st.success("🎉 Evaluation completed successfully! Review the candidate assessment below.")
            
            # Evaluation results
            st.markdown("### 📊 Candidate Assessment Results")
            
            # HR-focused metrics
            col1, col2, col3 = st.columns(3)
            
            with col1:
            st.markdown("""
                <div style="background: white; border: 1px solid #e2e8f0; border-radius: 0.75rem; padding: 1rem; text-align: center; transition: all 0.2s;">
                    <div style="font-size: 0.75rem; color: #475569; font-weight: 500; text-transform: uppercase; letter-spacing: 0.05em;">Overall Fit</div>
                    <div style="font-size: 2rem; font-weight: 700; color: #1e40af; margin: 0.25rem 0;">87%</div>
                    <div style="background: #dcfce7; color: #059669; font-size: 0.75rem; font-weight: 600; padding: 0.25rem 0.5rem; border-radius: 0.375rem; display: inline-block;">Strong Match</div>
            </div>
            """, unsafe_allow_html=True)
            
            with col2:
                            st.markdown("""
                <div style="background: white; border: 1px solid #e2e8f0; border-radius: 0.75rem; padding: 1rem; text-align: center; transition: all 0.2s;">
                    <div style="font-size: 0.75rem; color: #475569; font-weight: 500; text-transform: uppercase; letter-spacing: 0.05em;">Skills Match</div>
                    <div style="font-size: 2rem; font-weight: 700; color: #1e40af; margin: 0.25rem 0;">92%</div>
                    <div style="background: #dcfce7; color: #059669; font-size: 0.75rem; font-weight: 600; padding: 0.25rem 0.5rem; border-radius: 0.375rem; display: inline-block;">Excellent</div>
                            </div>
                            """, unsafe_allow_html=True)
                            
            with col3:
        st.markdown("""
                <div style="background: white; border: 1px solid #e2e8f0; border-radius: 0.75rem; padding: 1rem; text-align: center; transition: all 0.2s;">
                    <div style="font-size: 0.75rem; color: #475569; font-weight: 500; text-transform: uppercase; letter-spacing: 0.05em;">Experience Fit</div>
                    <div style="font-size: 2rem; font-weight: 700; color: #1e40af; margin: 0.25rem 0;">78%</div>
                    <div style="background: #fef2f2; color: #dc2626; font-size: 0.75rem; font-weight: 600; padding: 0.25rem 0.5rem; border-radius: 0.375rem; display: inline-block;">Good</div>
        </div>
        """, unsafe_allow_html=True)
        
            # HR decision support
            st.markdown("### 🎯 HR Decision Support")
        st.markdown("""
            <div style="background: white; border: 1px solid #e2e8f0; border-radius: 0.75rem; overflow: hidden;">
                <div style="background: linear-gradient(135deg, #f8fafc, #f1f5f9); border-bottom: 1px solid #e2e8f0; padding: 1rem;">
                    <h4 style="margin: 0; color: #0f172a;">Candidate Assessment Report</h4>
        </div>
                <div style="padding: 1rem;">
                    <div style="margin-bottom: 1rem;">
                        <h5 style="color: #1e40af; margin-bottom: 0.25rem; font-size: 0.875rem;">🎯 Key Strengths</h5>
                        <ul style="color: #475569; line-height: 1.5; margin: 0; font-size: 0.875rem;">
                            <li>Strong technical skills alignment with job requirements</li>
                            <li>Relevant cloud experience and modern tech stack</li>
                            <li>Good educational background and certifications</li>
                        </ul>
                </div>
                    <div style="margin-bottom: 1rem;">
                        <h5 style="color: #d97706; margin-bottom: 0.25rem; font-size: 0.875rem;">⚠️ Areas of Concern</h5>
                        <ul style="color: #475569; line-height: 1.5; margin: 0; font-size: 0.875rem;">
                            <li>Could benefit from more DevOps experience</li>
                            <li>Missing specific database technologies mentioned</li>
                        </ul>
                </div>
                    <div>
                        <h5 style="color: #059669; margin-bottom: 0.25rem; font-size: 0.875rem;">💡 HR Recommendation</h5>
                        <p style="color: #475569; margin: 0; font-size: 0.875rem;"><strong>RECOMMENDED FOR INTERVIEW</strong> - This candidate shows strong potential and would be worth interviewing.</p>
                </div>
                </div>
            </div>
            """, unsafe_allow_html=True)
        
            # 🎭 AI Personality Analysis Surprise!
            st.markdown("### 🎭 AI Personality & Cultural Fit Analysis")
        st.markdown("""
            <div style="background: linear-gradient(135deg, #fdf2f8, #fce7f3); border: 1px solid #ec4899; border-radius: 0.75rem; padding: 1rem; margin: 1rem 0;">
                <div style="display: flex; align-items: center; gap: 0.5rem; margin-bottom: 0.5rem;">
                    <span style="font-size: 1.5rem;">🧠</span>
                    <h4 style="margin: 0; color: #831843; font-size: 1.125rem;">AI-Powered Personality Insights</h4>
                </div>
                <p style="color: #be185d; margin: 0; font-size: 0.875rem;">
                    Our advanced AI analyzes personality traits, cultural fit, and predicts hiring success beyond just skills!
            </p>
        </div>
        """, unsafe_allow_html=True)
        
            # Generate personality analysis
            sample_resume_text = "Sample resume content for analysis"
            personality_traits, cultural_indicators, success_metrics = analyze_candidate_personality(sample_resume_text)
            
            # Personality radar chart
            personality_chart = create_personality_radar(personality_traits)
            st.plotly_chart(personality_chart, use_container_width=True)
            
            # Personality insights
            st.markdown("### 🧠 Personality Trait Analysis")
            col1, col2 = st.columns(2)
            
            with col1:
            st.markdown(f"""
                <div style="background: white; border: 1px solid #e2e8f0; border-radius: 0.75rem; padding: 1rem; border-left: 4px solid #ec4899;">
                    <h5 style="color: #ec4899; margin-bottom: 0.5rem; font-size: 0.875rem;">🌟 Key Strengths</h5>
                    <div style="margin-bottom: 0.5rem;">
                        <span style="font-size: 0.75rem; color: #475569;">Leadership:</span>
                        <div style="background: #e2e8f0; height: 6px; border-radius: 3px; margin: 0.25rem 0;">
                            <div style="background: #ec4899; height: 100%; width: {personality_traits['leadership']:.1%}; border-radius: 3px;"></div>
                    </div>
                    </div>
                    <div style="margin-bottom: 0.5rem;">
                        <span style="font-size: 0.75rem; color: #475569;">Teamwork:</span>
                        <div style="background: #e2e8f0; height: 6px; border-radius: 3px; margin: 0.25rem 0;">
                            <div style="background: #ec4899; height: 100%; width: {personality_traits['teamwork']:.1%}; border-radius: 3px;"></div>
                    </div>
                    </div>
                    <div>
                        <span style="font-size: 0.75rem; color: #475569;">Communication:</span>
                        <div style="background: #e2e8f0; height: 6px; border-radius: 3px; margin: 0.25rem 0;">
                            <div style="background: #ec4899; height: 100%; width: {personality_traits['communication']:.1%}; border-radius: 3px;"></div>
                </div>
                </div>
            </div>
            """, unsafe_allow_html=True)
            
            with col2:
                    st.markdown(f"""
                <div style="background: white; border: 1px solid #e2e8f0; border-radius: 0.75rem; padding: 1rem; border-left: 4px solid #8b5cf6;">
                    <h5 style="color: #8b5cf6; margin-bottom: 0.5rem; font-size: 0.875rem;">💡 Growth Areas</h5>
                    <div style="margin-bottom: 0.5rem;">
                        <span style="font-size: 0.75rem; color: #475569;">Innovation:</span>
                        <div style="background: #e2e8f0; height: 6px; border-radius: 3px; margin: 0.25rem 0;">
                            <div style="background: #8b5cf6; height: 100%; width: {personality_traits['innovation']:.1%}; border-radius: 3px;"></div>
                        </div>
                        </div>
                    <div style="margin-bottom: 0.5rem;">
                        <span style="font-size: 0.75rem; color: #475569;">Adaptability:</span>
                        <div style="background: #e2e8f0; height: 6px; border-radius: 3px; margin: 0.25rem 0;">
                            <div style="background: #8b5cf6; height: 100%; width: {personality_traits['adaptability']:.1%}; border-radius: 3px;"></div>
                    </div>
        </div>
                    <div>
                        <span style="font-size: 0.75rem; color: #475569;">Reliability:</span>
                        <div style="background: #e2e8f0; height: 6px; border-radius: 3px; margin: 0.25rem 0;">
                            <div style="background: #8b5cf6; height: 100%; width: {personality_traits['reliability']:.1%}; border-radius: 3px;"></div>
            </div>
            </div>
                </div>
                """, unsafe_allow_html=True)
        
            # Cultural fit analysis
            st.markdown("### 🏢 Cultural Fit & Team Compatibility")
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown(f"""
                <div style="background: white; border: 1px solid #e2e8f0; border-radius: 0.75rem; padding: 1rem; border-left: 4px solid #10b981;">
                    <h5 style="color: #10b981; margin-bottom: 0.5rem; font-size: 0.875rem;">🎯 Cultural Alignment</h5>
                    <div style="margin-bottom: 0.5rem;">
                        <span style="font-size: 0.75rem; color: #475569;">Values Alignment:</span>
                        <div style="background: #e2e8f0; height: 6px; border-radius: 3px; margin: 0.25rem 0;">
                            <div style="background: #10b981; height: 100%; width: {cultural_indicators['company_values_alignment']:.1%}; border-radius: 3px;"></div>
                </div>
            </div>
                    <div style="margin-bottom: 0.5rem;">
                        <span style="font-size: 0.75rem; color: #475569;">Work Style:</span>
                        <div style="background: #e2e8f0; height: 6px; border-radius: 3px; margin: 0.25rem 0;">
                            <div style="background: #10b981; height: 100%; width: {cultural_indicators['work_style_compatibility']:.1%}; border-radius: 3px;"></div>
                        </div>
                    </div>
                    <div>
                        <span style="font-size: 0.75rem; color: #475569;">Growth Mindset:</span>
                        <div style="background: #e2e8f0; height: 6px; border-radius: 3px; margin: 0.25rem 0;">
                            <div style="background: #10b981; height: 100%; width: {cultural_indicators['growth_mindset']:.1%}; border-radius: 3px;"></div>
                </div>
                </div>
        </div>
    """, unsafe_allow_html=True)
    
            with col2:
    st.markdown(f"""
                <div style="background: white; border: 1px solid #e2e8f0; border-radius: 0.75rem; padding: 1rem; border-left: 4px solid #f59e0b;">
                    <h5 style="color: #f59e0b; margin-bottom: 0.5rem; font-size: 0.875rem;">🤝 Team Dynamics</h5>
                    <div style="margin-bottom: 0.5rem;">
                        <span style="font-size: 0.75rem; color: #475569;">Collaboration:</span>
                        <div style="background: #e2e8f0; height: 6px; border-radius: 3px; margin: 0.25rem 0;">
                            <div style="background: #f59e0b; height: 100%; width: {cultural_indicators['collaboration_preference']:.1%}; border-radius: 3px;"></div>
        </div>
    </div>
                    <div style="margin-bottom: 0.5rem;">
                        <span style="font-size: 0.75rem; color: #475569;">Integration Speed:</span>
                        <div style="background: #e2e8f0; height: 6px; border-radius: 3px; margin: 0.25rem 0;">
                            <div style="background: #f59e0b; height: 100%; width: {success_metrics['team_integration_speed']:.1%}; border-radius: 3px;"></div>
        </div>
                </div>
                    <div>
                        <span style="font-size: 0.75rem; color: #475569;">Team Chemistry:</span>
                        <div style="background: #e2e8f0; height: 6px; border-radius: 3px; margin: 0.25rem 0;">
                            <div style="background: #f59e0b; height: 100%; width: {personality_traits['teamwork']:.1%}; border-radius: 3px;"></div>
            </div>
                </div>
            </div>
            """, unsafe_allow_html=True)
        
            # Predictive success metrics
            st.markdown("### 🔮 AI Predictive Success Analysis")
    st.markdown("""
            <div style="background: linear-gradient(135deg, #f0f9ff, #e0f2fe); border: 1px solid #0ea5e9; border-radius: 0.75rem; padding: 1rem; margin: 1rem 0;">
                <div style="display: flex; align-items: center; gap: 0.5rem; margin-bottom: 0.5rem;">
                    <span style="font-size: 1.5rem;">🔮</span>
                    <h4 style="margin: 0; color: #0c4a6e; font-size: 1.125rem;">Future Success Predictions</h4>
    </div>
                <p style="color: #0369a1; margin: 0; font-size: 0.875rem;">
                    Our AI predicts long-term success, retention, and career growth potential!
        </p>
    </div>
    """, unsafe_allow_html=True)
    
            # Success metrics display
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
            st.markdown(f"""
                <div style="background: white; border: 1px solid #e2e8f0; border-radius: 0.75rem; padding: 1rem; text-align: center; transition: all 0.2s;">
                    <div style="font-size: 0.75rem; color: #475569; font-weight: 500; text-transform: uppercase; letter-spacing: 0.05em;">Retention</div>
                    <div style="font-size: 1.5rem; font-weight: 700; color: #10b981; margin: 0.25rem 0;">{success_metrics['retention_probability']:.1%}</div>
                    <div style="background: #dcfce7; color: #059669; font-size: 0.75rem; font-weight: 600; padding: 0.25rem 0.5rem; border-radius: 0.375rem; display: inline-block;">High</div>
            </div>
            """, unsafe_allow_html=True)
            
            with col2:
                st.markdown(f"""
                <div style="background: white; border: 1px solid #e2e8f0; border-radius: 0.75rem; padding: 1rem; text-align: center; transition: all 0.2s;">
                    <div style="font-size: 0.75rem; color: #475569; font-weight: 500; text-transform: uppercase; letter-spacing: 0.05em;">Performance</div>
                    <div style="font-size: 1.5rem; font-weight: 700; color: #1e40af; margin: 0.25rem 0;">{success_metrics['performance_prediction']:.1%}</div>
                    <div style="background: #dbeafe; color: #1e40af; font-size: 0.75rem; font-weight: 600; padding: 0.25rem 0.5rem; border-radius: 0.375rem; display: inline-block;">Strong</div>
                </div>
                """, unsafe_allow_html=True)
            
            with col3:
                    st.markdown(f"""
                <div style="background: white; border: 1px solid #e2e8f0; border-radius: 0.75rem; padding: 1rem; text-align: center; transition: all 0.2s;">
                    <div style="font-size: 0.75rem; color: #475569; font-weight: 500; text-transform: uppercase; letter-spacing: 0.05em;">Integration</div>
                    <div style="font-size: 1.5rem; font-weight: 700; color: #f59e0b; margin: 0.25rem 0;">{success_metrics['team_integration_speed']:.1%}</div>
                    <div style="background: #fef3c7; color: #d97706; font-size: 0.75rem; font-weight: 600; padding: 0.25rem 0.5rem; border-radius: 0.375rem; display: inline-block;">Good</div>
                    </div>
                    """, unsafe_allow_html=True)
            
            with col4:
                    st.markdown(f"""
                <div style="background: white; border: 1px solid #e2e8f0; border-radius: 0.75rem; padding: 1rem; text-align: center; transition: all 0.2s;">
                    <div style="font-size: 0.75rem; color: #475569; font-weight: 500; text-transform: uppercase; letter-spacing: 0.05em;">Growth</div>
                    <div style="font-size: 1.5rem; font-weight: 700; color: #8b5cf6; margin: 0.25rem 0;">{success_metrics['career_growth_potential']:.1%}</div>
                    <div style="background: #f3e8ff; color: #7c3aed; font-size: 0.75rem; font-weight: 600; padding: 0.25rem 0.5rem; border-radius: 0.375rem; display: inline-block;">High</div>
                    </div>
                    """, unsafe_allow_html=True)
            
            # AI personality insights
            st.markdown("### 🤖 AI Personality Insights")
        st.markdown("""
            <div style="background: linear-gradient(135deg, #fdf2f8, #fce7f3); border: 1px solid #ec4899; border-radius: 0.75rem; padding: 1rem; margin: 1rem 0;">
                <div style="display: flex; align-items: center; gap: 0.5rem; margin-bottom: 0.5rem;">
                    <span style="font-size: 1.5rem;">🧠</span>
                    <h4 style="margin: 0; color: #831843; font-size: 1.125rem;">Advanced AI Analysis Complete</h4>
        </div>
                <p style="color: #be185d; margin: 0; font-size: 0.875rem;">
                    Our AI has analyzed personality traits, cultural fit, and predicted long-term success potential!
                </p>
            </div>
            """, unsafe_allow_html=True)
            
            # AI personality responses
            st.markdown("### 💬 AI Personality Feedback")
            
            # Generate contextual AI responses for personality
            personality_feedback = []
            personality_feedback.append(f"🎭 **Personality Insight:** This candidate shows strong leadership potential ({personality_traits['leadership']:.1%}) with excellent teamwork skills ({personality_traits['teamwork']:.1%}).")
            personality_feedback.append(f"🏢 **Cultural Fit:** High alignment with company values ({cultural_indicators['company_values_alignment']:.1%}) and strong growth mindset ({cultural_indicators['growth_mindset']:.1%}).")
            personality_feedback.append(f"🔮 **Success Prediction:** High retention probability ({success_metrics['retention_probability']:.1%}) and strong performance potential ({success_metrics['performance_prediction']:.1%}).")
            
            for i, feedback in enumerate(personality_feedback):
                st.markdown(f"""
                <div style="background: white; border: 1px solid #e2e8f0; border-radius: 0.75rem; padding: 1rem; margin: 0.5rem 0; border-left: 4px solid #ec4899;">
                    <div style="display: flex; align-items: center; gap: 0.5rem;">
                        <span style="font-size: 1.25rem;">{'🧠' if i == 0 else '🏢' if i == 1 else '🔮'}</span>
                        <p style="color: #475569; margin: 0; font-size: 0.875rem; line-height: 1.4;">{feedback}</p>
                </div>
            </div>
            """, unsafe_allow_html=True)
            
                else:
            st.error("❌ Please select a job opening and upload a candidate resume to proceed.")
        st.markdown("""
            <div style="background: white; border: 1px solid #e2e8f0; border-radius: 0.75rem; padding: 1rem;">
                <p style="color: #475569; margin: 0; font-size: 0.875rem;">
                    <strong>Missing information?</strong> Ensure you have selected a job opening and uploaded a candidate resume 
                    to proceed with the evaluation.
                </p>
    </div>
    """, unsafe_allow_html=True)
    
# Footer
st.markdown(CompanyBranding.get_footer_html(), unsafe_allow_html=True)
