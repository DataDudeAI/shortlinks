import streamlit as st
from styles import get_styles
from ui_styles import load_ui_styles

def apply_styles():
    """Apply all styles to the app"""
    # Apply base styles
    st.markdown(get_styles(), unsafe_allow_html=True)
    
    # Apply UI-specific styles
    st.markdown(load_ui_styles(), unsafe_allow_html=True)
    
    # Enhanced UI Styles
    st.markdown("""
        <style>
            /* Global Styles */
            .stApp {
                font-family: 'Inter', sans-serif;
            }
            
            /* Login Page Styles */
            .login-container {
                max-width: 400px;
                margin: 4rem auto;
                padding: 2.5rem;
                background: linear-gradient(145deg, #ffffff, #f5f7fa);
                border-radius: 1rem;
                box-shadow: 0 10px 25px rgba(0,0,0,0.05);
            }
            
            .login-header {
                text-align: center;
                margin-bottom: 2.5rem;
            }
            
            .login-header h1 {
                font-size: 2.5rem;
                font-weight: 700;
                color: #1a202c;
                margin-bottom: 0.5rem;
            }
            
            /* Dashboard Cards */
            .metric-card {
                background: linear-gradient(145deg, #ffffff, #f8fafc);
                border: 1px solid rgba(226, 232, 240, 0.8);
                padding: 1.5rem;
                border-radius: 1rem;
                box-shadow: 0 4px 6px rgba(0,0,0,0.02);
                transition: all 0.3s ease;
            }
            
            .metric-card:hover {
                transform: translateY(-2px);
                box-shadow: 0 8px 12px rgba(0,0,0,0.05);
            }
            
            /* Navigation Sidebar */
            .sidebar .element-container {
                margin-bottom: 0.75rem;
            }
            
            .user-info {
                background: linear-gradient(145deg, #f8fafc, #ffffff);
                padding: 1.25rem;
                border-radius: 0.75rem;
                margin: 1rem 0;
                border: 1px solid rgba(226, 232, 240, 0.8);
                box-shadow: 0 2px 4px rgba(0,0,0,0.02);
            }
            
            .user-info p {
                color: #1a202c;
                font-size: 1rem;
                font-weight: 500;
                margin: 0.25rem 0;
                display: flex;
                align-items: center;
                gap: 0.5rem;
            }
            
            .user-info .user-role {
                font-size: 0.875rem;
                color: #10B981;
                font-weight: 600;
            }
            
            .user-info .org-name {
                color: #1a202c;
                font-weight: 600;
            }
            
            /* Dark mode overrides */
            [data-theme="dark"] .user-info {
                background: linear-gradient(145deg, #2d3748, #1a202c);
            }
            
            [data-theme="dark"] .user-info p {
                color: #f7fafc;
            }
            
            [data-theme="dark"] .user-info .org-name {
                color: #f7fafc;
            }
            
            /* Buttons */
            .stButton>button {
                width: 100%;
                padding: 0.625rem 1.25rem;
                border-radius: 0.5rem;
                font-weight: 500;
                transition: all 0.2s ease;
                border: none;
                background: linear-gradient(145deg, #10B981, #059669);
                color: white;
                box-shadow: 0 2px 4px rgba(16, 185, 129, 0.1);
            }
            
            .stButton>button:hover {
                transform: translateY(-1px);
                box-shadow: 0 4px 6px rgba(16, 185, 129, 0.2);
                background: linear-gradient(145deg, #059669, #047857);
            }
            
            /* Form Fields */
            .stTextInput>div>div>input,
            .stSelectbox>div>div>select {
                border-radius: 0.5rem;
                border: 1px solid #e2e8f0;
                padding: 0.625rem 1rem;
                transition: all 0.2s ease;
            }
            
            .stTextInput>div>div>input:focus,
            .stSelectbox>div>div>select:focus {
                border-color: #10B981;
                box-shadow: 0 0 0 3px rgba(16, 185, 129, 0.1);
            }
            
            /* Tables */
            .stDataFrame {
                border-radius: 0.75rem;
                overflow: hidden;
                border: 1px solid #e2e8f0;
            }
            
            .stDataFrame table {
                border-collapse: separate;
                border-spacing: 0;
            }
            
            .stDataFrame th {
                background: #f8fafc;
                padding: 0.75rem 1rem;
                font-weight: 600;
                color: #1a202c;
                border-bottom: 1px solid #e2e8f0;
            }
            
            /* Charts */
            .plot-container {
                border-radius: 0.75rem;
                overflow: hidden;
                border: 1px solid #e2e8f0;
                background: white;
                padding: 1rem;
                box-shadow: 0 2px 4px rgba(0,0,0,0.02);
            }
            
            /* Activity Feed */
            .activity-item {
                background: linear-gradient(145deg, #ffffff, #f8fafc);
                border: 1px solid rgba(226, 232, 240, 0.8);
                padding: 1.25rem;
                border-radius: 0.75rem;
                margin-bottom: 0.75rem;
                box-shadow: 0 2px 4px rgba(0,0,0,0.02);
                transition: all 0.2s ease;
            }
            
            .activity-item:hover {
                transform: translateX(2px);
                box-shadow: 0 4px 6px rgba(0,0,0,0.04);
            }
            
            /* Dark Mode Overrides */
            [data-theme="dark"] {
                .metric-card, .activity-item, .user-info {
                    background: linear-gradient(145deg, #1a202c, #2d3748);
                    border-color: #2d3748;
                }
                
                .stButton>button {
                    background: linear-gradient(145deg, #0d9488, #0f766e);
                }
                
                .stTextInput>div>div>input,
                .stSelectbox>div>div>select {
                    background: #1a202c;
                    border-color: #2d3748;
                    color: #e2e8f0;
                }
            }
            
            /* Animations */
            @keyframes fadeIn {
                from { opacity: 0; transform: translateY(-10px); }
                to { opacity: 1; transform: translateY(0); }
            }
            
            .main-content {
                animation: fadeIn 0.3s ease-out;
            }
            
            /* Loading States */
            .stSpinner {
                border-radius: 50%;
                border: 2px solid #e2e8f0;
                border-top-color: #10B981;
            }
            
            /* VBG Branding Styles */
            .vbg-branded {
                background: linear-gradient(145deg, #1a202c, #2d3748);
                border: none !important;
            }
            
            .vbg-branded p {
                color: #f7fafc !important;
            }
            
            .vbg-branded .user-role {
                color: #10B981 !important;
            }
            
            .vbg-branded .org-name {
                color: #f7fafc !important;
                font-size: 1.1rem;
                font-weight: 700;
            }
            
            .vbg-branded .domain-info {
                font-size: 0.875rem;
                color: #a0aec0 !important;
            }
            
            /* VBG Theme Colors */
            :root {
                --vbg-primary: #10B981;
                --vbg-secondary: #1a202c;
                --vbg-accent: #0891b2;
            }
        </style>
    """, unsafe_allow_html=True)

def init_theme():
    """Initialize theme settings"""
    if 'theme' not in st.session_state:
        st.session_state.theme = 'light'

def setup_page():
    """Setup page configuration and styles"""
    # Initialize theme
    init_theme()
    
    # Apply all styles
    apply_styles() 