"""
Demo page showcasing the Tesla-inspired design elements.
This page demonstrates the new UI/UX components and styling.
"""

import streamlit as st
from branding import CompanyBranding

# Page configuration
st.set_page_config(
    page_title="IKF Optimized Design Demo",
    page_icon="⚡",
    layout="wide"
)

# Apply optimized styling
st.markdown(CompanyBranding.get_css_styles(), unsafe_allow_html=True)

# Header
st.markdown(CompanyBranding.get_header_html(), unsafe_allow_html=True)

# Main content
st.markdown("## ⚡ IKF Optimized Design Demo")
st.markdown("This is a highly optimized Streamlit application with performance-focused design and minimal CSS overhead, proudly powered by I Knowledge Factory.")

# Hero Section
hero_features = [
    "Unified card system with single CSS class",
    "Optimized grid layouts and reduced redundancy",
    "Minimal CSS overhead for fast loading",
    "Performance-focused design patterns by IKF"
]

st.markdown(
    CompanyBranding.get_hero_section_with_image(
        "IKF Optimized Design System",
        "Performance-focused interface with minimal CSS overhead and fast loading times, developed by I Knowledge Factory",
        "https://via.placeholder.com/800x400/2563eb/ffffff?text=IKF+Optimized+Design",
        hero_features
    ),
    unsafe_allow_html=True
)

# Enhanced Cards Section
st.markdown("## 🎯 IKF Optimized Cards Section")
st.markdown("""
<div class="opt-card">
    <h3 style="color: #0f172a; margin-bottom: 1rem; font-size: 1.75rem; font-weight: 600;">Unified Card System</h3>
    <p style="color: #64748b; line-height: 1.6; font-size: 1.1rem;">All cards now use a single CSS class (.opt-card) for consistent styling and reduced CSS overhead.</p>
    <p style="color: #64748b; line-height: 1.6;">Optimized hover effects and transitions for smooth user experience, powered by IKF technology.</p>
</div>
""", unsafe_allow_html=True)

# Grid Layout for Feature Cards
st.markdown("## 🔲 IKF Optimized Grid Layouts")
st.markdown('<div class="opt-grid opt-grid-2">', unsafe_allow_html=True)

st.markdown(
    CompanyBranding.get_feature_card_with_image(
        "IKF Performance Optimized",
        "Reduced CSS classes and unified design system for faster loading and better performance, developed by I Knowledge Factory.",
        "https://via.placeholder.com/300x200/2563eb/ffffff?text=IKF+Performance+Optimized"
    ),
    unsafe_allow_html=True
)

st.markdown(
    CompanyBranding.get_feature_card_with_image(
        "IKF Clean Architecture",
        "Simplified CSS structure with minimal redundancy and optimized responsive design, engineered by IKF experts.",
        "https://via.placeholder.com/300x200/7c3aed/ffffff?text=IKF+Clean+Architecture"
    ),
    unsafe_allow_html=True
)

st.markdown('</div>', unsafe_allow_html=True)

# Statistics Section
st.markdown("## 📊 IKF Optimized Statistics Section")
st.markdown("""
<div class="opt-card">
    <h3 style="color: #0f172a; margin-bottom: 1rem; font-size: 1.75rem; font-weight: 600;">Efficient Metrics Display</h3>
    <p style="color: #64748b; line-height: 1.6; font-size: 1.1rem;">Optimized grid system with responsive layouts and minimal CSS overhead, powered by IKF technology.</p>
</div>
""", unsafe_allow_html=True)

# Stats grid
st.markdown('<div class="opt-grid opt-grid-4">', unsafe_allow_html=True)

st.markdown("""
<div class="opt-card">
    <h4 style="color: #2563eb; margin-bottom: 0.5rem; font-size: 1.25rem;">Performance</h4>
    <p style="color: #0f172a; font-size: 2rem; font-weight: 700; margin: 0;">95%</p>
    <p style="color: #059669; font-size: 0.875rem; margin: 0;">Faster loading</p>
</div>
""", unsafe_allow_html=True)

st.markdown("""
<div class="opt-card">
    <h4 style="color: #2563eb; margin-bottom: 0.5rem; font-size: 1.25rem;">Efficiency</h4>
    <p style="color: #0f172a; font-size: 2rem; font-weight: 700; margin: 0;">60%</p>
    <p style="color: #059669; font-size: 0.875rem; margin: 0;">Less CSS</p>
</div>
""", unsafe_allow_html=True)

st.markdown("""
<div class="opt-card">
    <h4 style="color: #2563eb; margin-bottom: 0.5rem; font-size: 1.25rem;">Maintenance</h4>
    <p style="color: #0f172a; font-size: 2rem; font-weight: 700; margin: 0;">80%</p>
    <p style="color: #059669; font-size: 0.875rem; margin: 0;">Easier updates</p>
</div>
""", unsafe_allow_html=True)

st.markdown("""
<div class="opt-card">
    <h4 style="color: #2563eb; margin-bottom: 0.5rem; font-size: 1.25rem;">Responsiveness</h4>
    <p style="color: #0f172a; font-size: 2rem; font-weight: 700; margin: 0;">100%</p>
    <p style="color: #059669; font-size: 0.875rem; margin: 0;">Mobile optimized</p>
</div>
""", unsafe_allow_html=True)

st.markdown('</div>', unsafe_allow_html=True)

# Status Badges Section
st.markdown("## 🏷️ IKF Optimized Status Badges")
st.markdown("""
<div class="opt-card">
    <h3 style="color: #0f172a; margin-bottom: 1rem; font-size: 1.75rem; font-weight: 600;">Unified Badge System</h3>
    <p style="color: #64748b; line-height: 1.6; font-size: 1.1rem;">All status badges use optimized CSS classes for consistent styling and better performance, developed by I Knowledge Factory.</p>
</div>
""", unsafe_allow_html=True)

# Badge columns
badge_col1, badge_col2, badge_col3, badge_col4 = st.columns(4)

with badge_col1:
    st.markdown(CompanyBranding.get_status_badge("Active", "success"), unsafe_allow_html=True)

with badge_col2:
    st.markdown(CompanyBranding.get_status_badge("Pending", "warning"), unsafe_allow_html=True)

with badge_col3:
    st.markdown(CompanyBranding.get_status_badge("Error", "error"), unsafe_allow_html=True)

with badge_col4:
    st.markdown(CompanyBranding.get_status_badge("Info", "info"), unsafe_allow_html=True)

# Interactive Elements Section
st.markdown("## 🎮 IKF Optimized Interactive Elements")
st.markdown("""
<div class="opt-card">
    <h3 style="color: #0f172a; margin-bottom: 1rem; font-size: 1.75rem; font-weight: 600;">Streamlined Components</h3>
    <p style="color: #64748b; line-height: 1.6; font-size: 1.1rem;">Using enhanced Streamlit widgets with beautiful styling and smooth interactions, powered by IKF technology.</p>
</div>
""", unsafe_allow_html=True)

# Form controls
col1, col2 = st.columns(2)

with col1:
    st.text_input("Enter your name:", placeholder="John Doe")
    st.selectbox("Choose an option:", ["Option 1", "Option 2", "Option 3"])
    st.checkbox("Agree to terms")

with col2:
    st.slider("Select a value:", 0, 100, 50)
    st.button("Submit", type="primary", use_container_width=True)
    st.progress(0.7)

# Sidebar
with st.sidebar:
    st.markdown(CompanyBranding.get_sidebar_header_html(), unsafe_allow_html=True)
    
    st.markdown("---")
    
    st.markdown("### ⚡ IKF Optimization Features")
    st.markdown("""
    <div class="opt-card">
        <h4 style="color: #0f172a; margin-bottom: 1rem;">🚀 Performance</h4>
        <ul style="color: #64748b; line-height: 1.6; font-size: 0.9rem;">
            <li>Unified CSS classes</li>
            <li>Reduced redundancy</li>
            <li>Minimal overhead</li>
            <li>Fast loading</li>
        </ul>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    st.markdown("### 🎯 IKF Design Benefits")
    st.markdown("""
    <div class="opt-card">
        <h4 style="color: #0f172a; margin-bottom: 1rem;">✨ Improvements</h4>
        <ul style="color: #64748b; line-height: 1.6; font-size: 0.9rem;">
            <li>Consistent styling</li>
            <li>Easy maintenance</li>
            <li>Responsive design</li>
            <li>Clean code</li>
        </ul>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    st.markdown("### 🏢 About I Knowledge Factory")
    company_info = CompanyBranding.get_company_info()
    st.markdown(f"""
    <div class="opt-card">
        <h4 style="color: #0f172a; margin-bottom: 1rem;">🏢 Company Info</h4>
        <p style="color: #64748b; font-size: 0.9rem;"><strong>Company:</strong> {company_info['full_name']}</p>
        <p style="color: #64748b; font-size: 0.9rem;"><strong>Description:</strong> {company_info['description']}</p>
        <p style="color: #64748b; font-size: 0.9rem;"><strong>Website:</strong> {company_info['website']}</p>
        <p style="color: #64748b; font-size: 0.9rem;"><strong>Email:</strong> {company_info['email']}</p>
    </div>
    """, unsafe_allow_html=True)

# Footer
st.markdown(CompanyBranding.get_footer_html(), unsafe_allow_html=True)
