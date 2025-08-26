"""
Highly optimized and appealing branding configuration for I Knowledge Factory Pvt. Ltd.
Performance-focused design with minimal CSS overhead and fast loading.
"""

class CompanyBranding:
    """Optimized company branding with performance-focused design for IKF."""
    
    # Company Information - I Knowledge Factory Pvt. Ltd
    COMPANY_NAME = "I Knowledge Factory"
    COMPANY_DESCRIPTION = "Advanced Talent Screening & AI Solutions"
    COMPANY_WEBSITE = "https://www.ikf.co.in"
    COMPANY_EMAIL = "info@ikf.co.in"
    COMPANY_PHONE = "+91 (0) 11 1234 5678"
    COMPANY_FULL_NAME = "I Knowledge Factory Pvt. Ltd"
    
    # IKF Logo URL
    LOGO_URL = "https://www.ikf.co.in/wp-content/uploads/ikf-white-logo.svg"
    
    # Optimized color palette (reduced color variations)
    PRIMARY_COLOR = "#2563eb"
    SECONDARY_COLOR = "#7c3aed"
    SUCCESS_COLOR = "#059669"
    WARNING_COLOR = "#d97706"
    ERROR_COLOR = "#dc2626"
    
    # Neutral colors (minimized)
    DARK_BG = "#0f172a"
    GRAY_BG = "#f8fafc"
    BORDER_COLOR = "#e2e8f0"
    TEXT_PRIMARY = "#0f172a"
    TEXT_SECONDARY = "#64748b"
    
    @staticmethod
    def get_company_info():
        """Get basic company information."""
        return {
            "name": CompanyBranding.COMPANY_NAME,
            "full_name": CompanyBranding.COMPANY_FULL_NAME,
            "description": CompanyBranding.COMPANY_DESCRIPTION,
            "website": CompanyBranding.COMPANY_WEBSITE,
            "email": CompanyBranding.COMPANY_EMAIL,
            "phone": CompanyBranding.COMPANY_PHONE,
            "logo": CompanyBranding.LOGO_URL
        }
    
    @staticmethod
    def get_header_html():
        """Get optimized header HTML with IKF logo."""
        return f"""
        <div style="text-align: center; padding: 2rem; background: linear-gradient(135deg, {CompanyBranding.PRIMARY_COLOR}, {CompanyBranding.SECONDARY_COLOR}); color: white; border-radius: 0 0 1rem 1rem; margin: -1rem -1rem 2rem -1rem; box-shadow: 0 2px 4px rgba(0,0,0,0.1);">
            <div style="display: flex; align-items: center; justify-content: center; gap: 1rem; margin-bottom: 1rem;">
                <img src="{CompanyBranding.LOGO_URL}" alt="IKF Logo" style="height: 60px; width: auto; filter: brightness(0) invert(1);">
            </div>
            <h1 style="margin: 0; font-size: 2.5rem; font-weight: 700;">{CompanyBranding.COMPANY_NAME}</h1>
            <p style="margin: 0.5rem 0 0 0; font-size: 1.125rem; opacity: 0.9;">{CompanyBranding.COMPANY_DESCRIPTION}</p>
            <p style="margin: 0.25rem 0 0 0; font-size: 0.875rem; opacity: 0.8;">{CompanyBranding.COMPANY_FULL_NAME}</p>
        </div>
    """
    
    @staticmethod
    def get_sidebar_header_html():
        """Get optimized sidebar header HTML with IKF logo."""
        return f"""
        <div style="text-align: center; padding: 1.5rem; background: linear-gradient(135deg, {CompanyBranding.PRIMARY_COLOR}, {CompanyBranding.SECONDARY_COLOR}); color: white; border-radius: 0.75rem; margin-bottom: 1rem; box-shadow: 0 2px 4px rgba(0,0,0,0.1);">
            <div style="display: flex; align-items: center; justify-content: center; gap: 0.5rem; margin-bottom: 0.5rem;">
                <img src="{CompanyBranding.LOGO_URL}" alt="IKF Logo" style="height: 40px; width: auto; filter: brightness(0) invert(1);">
            </div>
            <h3 style="margin: 0; font-size: 1.5rem; font-weight: 600;">{CompanyBranding.COMPANY_NAME}</h3>
            <p style="margin: 0.25rem 0 0 0; font-size: 0.875rem; opacity: 0.9;">{CompanyBranding.COMPANY_DESCRIPTION}</p>
        </div>
    """
    
    @staticmethod
    def get_footer_html():
        """Get optimized footer HTML with IKF branding."""
        return f"""
        <div style="text-align: center; padding: 2rem; background: {CompanyBranding.GRAY_BG}; border-radius: 1rem; margin-top: 3rem; border: 1px solid {CompanyBranding.BORDER_COLOR};">
            <div style="display: flex; align-items: center; justify-content: center; gap: 0.5rem; margin-bottom: 1rem;">
                <img src="{CompanyBranding.LOGO_URL}" alt="IKF Logo" style="height: 30px; width: auto;">
            </div>
            <p style="margin: 0; color: {CompanyBranding.TEXT_SECONDARY}; font-size: 0.875rem;">&copy; 2024 {CompanyBranding.COMPANY_FULL_NAME}. All rights reserved.</p>
            <p style="margin: 0.25rem 0 0 0; color: {CompanyBranding.TEXT_SECONDARY}; font-size: 0.75rem;">Advanced Talent Screening & AI Solutions</p>
        </div>
    """
    
    @staticmethod
    def get_css_styles():
        """Get highly optimized CSS styles."""
        return f"""
        <style>
        /* Optimized design system - minimal CSS overhead */
        .main .block-container {{
            padding: 1rem;
            max-width: 1200px;
        }}
        
        /* Unified card system - single class for all cards */
        .opt-card {{
            background: white;
            border: 1px solid {CompanyBranding.BORDER_COLOR};
            border-radius: 0.75rem;
            padding: 1.5rem;
            margin: 1rem 0;
            box-shadow: 0 1px 3px rgba(0,0,0,0.1);
            transition: transform 0.2s ease, box-shadow 0.2s ease;
        }}
        
        .opt-card:hover {{
            transform: translateY(-2px);
            box-shadow: 0 4px 12px rgba(0,0,0,0.15);
        }}
        
        /* Optimized grid system */
        .opt-grid {{
            display: grid;
            gap: 1rem;
            margin: 1rem 0;
        }}
        
        .opt-grid-2 {{
            grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
        }}
        
        .opt-grid-4 {{
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
        }}
        
        /* Hero section - simplified */
        .opt-hero {{
            background: linear-gradient(135deg, {CompanyBranding.GRAY_BG}, white);
            border: 1px solid {CompanyBranding.BORDER_COLOR};
            border-radius: 1rem;
            padding: 2rem;
            margin: 1.5rem 0;
            text-align: center;
        }}
        
        /* Optimized status badges */
        .opt-badge {{
            display: inline-block;
            padding: 0.5rem 1rem;
            border-radius: 2rem;
            font-size: 0.875rem;
            font-weight: 600;
            text-align: center;
            min-width: 80px;
        }}
        
        .opt-badge-success {{ background: {CompanyBranding.SUCCESS_COLOR}; color: white; }}
        .opt-badge-warning {{ background: {CompanyBranding.WARNING_COLOR}; color: white; }}
        .opt-badge-error {{ background: {CompanyBranding.ERROR_COLOR}; color: white; }}
        .opt-badge-info {{ background: {CompanyBranding.PRIMARY_COLOR}; color: white; }}
        
        /* IKF Logo styling */
        .ikf-logo {{
            filter: brightness(0) invert(1);
            transition: transform 0.2s ease;
        }}
        
        .ikf-logo:hover {{
            transform: scale(1.05);
        }}
        
        /* Responsive optimizations */
        @media (max-width: 768px) {{
            .opt-grid-2, .opt-grid-4 {{
                grid-template-columns: 1fr;
            }}
            
            .opt-card {{
                padding: 1rem;
            }}
        }}
        </style>
        """
    
    @staticmethod
    def get_image_html(image_path, alt_text="", width="100%", height="auto"):
        """Get optimized image HTML."""
        return f'<img src="{image_path}" alt="{alt_text}" style="width: {width}; height: {height}; max-width: 100%; border-radius: 0.5rem; box-shadow: 0 2px 4px rgba(0,0,0,0.1);">'
    
    @staticmethod
    def get_hero_section_with_image(title, subtitle, image_path, features=None):
        """Get optimized hero section HTML with IKF branding."""
        features_html = ""
        if features:
            features_html = '<div style="margin-top: 1.5rem;"><ul style="text-align: left; margin: 0; padding-left: 1.5rem; list-style: none;">'
            for feature in features:
                features_html += f'<li style="margin: 0.5rem 0; padding: 0.5rem 0; border-left: 3px solid {CompanyBranding.PRIMARY_COLOR}; padding-left: 1rem; background: rgba(37, 99, 235, 0.05); border-radius: 0 0.5rem 0.5rem 0;">✓ {feature}</li>'
            features_html += '</ul></div>'
        
        return f"""
        <div class="opt-hero">
            <div style="display: flex; align-items: center; justify-content: center; gap: 1rem; margin-bottom: 1rem;">
                <img src="{CompanyBranding.LOGO_URL}" alt="IKF Logo" style="height: 50px; width: auto;">
            </div>
            <h1 style="color: {CompanyBranding.TEXT_PRIMARY}; margin-bottom: 1rem; font-size: 2.25rem; font-weight: 700;">{title}</h1>
            <p style="font-size: 1.125rem; margin-bottom: 1.5rem; color: {CompanyBranding.TEXT_SECONDARY}; line-height: 1.6;">{subtitle}</p>
            <img src="{image_path}" alt="Hero Image" style="max-width: 100%; height: auto; margin: 1.5rem 0; border-radius: 0.75rem; box-shadow: 0 4px 8px rgba(0,0,0,0.1);">
            {features_html}
        </div>
        """
    
    @staticmethod
    def get_feature_card_with_image(title, description, image_path, icon_class=""):
        """Get optimized feature card HTML."""
        return f"""
        <div class="opt-card">
            <div style="display: flex; align-items: center; gap: 1.5rem;">
                <div style="flex: 1;">
                    <h3 style="color: {CompanyBranding.TEXT_PRIMARY}; margin-bottom: 1rem; font-size: 1.5rem; font-weight: 600;">{title}</h3>
                    <p style="margin-bottom: 1rem; color: {CompanyBranding.TEXT_SECONDARY}; line-height: 1.6;">{description}</p>
                </div>
                <img src="{image_path}" alt="{title}" style="max-width: 120px; height: auto; border-radius: 0.5rem;">
            </div>
        </div>
        """
    
    @staticmethod
    def get_status_badge(text, status="info"):
        """Get optimized status badge HTML."""
        return f'<span class="opt-badge opt-badge-{status}">{text}</span>'
