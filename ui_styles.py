import streamlit as st

def load_ui_styles():
    theme = st.session_state.get('theme', 'light')
    
    return """
    <style>
        /* Base Theme Colors */
        :root {
            --deep-green-start: #065F46;
            --deep-green-end: #047857;
            --deep-green-light: #059669;
            --deep-green-accent: #10B981;
            --deep-green-glow: rgba(6, 95, 70, 0.25);
            --sidebar-bg: rgb(13, 28, 18);
            --sidebar-hover: rgba(16, 185, 129, 0.1);
            
            /* Card Colors */
            --card-bg: linear-gradient(145deg, rgba(6, 95, 70, 0.08), rgba(16, 185, 129, 0.05));
            --card-border: rgba(16, 185, 129, 0.2);
            --card-hover-bg: linear-gradient(145deg, rgba(6, 95, 70, 0.12), rgba(16, 185, 129, 0.08));
            --card-hover-border: rgba(16, 185, 129, 0.5);
            --card-shadow: 0 4px 20px rgba(6, 95, 70, 0.15);
            --card-hover-shadow: 0 8px 30px rgba(6, 95, 70, 0.25);
            
            /* Text Colors */
            --text-primary: #F3EDED;
            --text-secondary: #E2E8F0;
            --background-dark: #101414;
        }

        /* Global Styles */
        .stApp {
            background: var(--background-dark);
            color: var(--text-primary);
        }

        /* Enhanced Metric Cards */
        [data-testid="stMetric"] {
            background: var(--card-bg);
            padding: 2rem !important;
            border-radius: 1.2rem !important;
            border: 1px solid var(--card-border) !important;
            box-shadow: var(--card-shadow);
            position: relative;
            overflow: hidden;
            transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1);
            backdrop-filter: blur(10px);
        }

        [data-testid="stMetric"]::before {
            content: '';
            position: absolute;
            top: 0;
            left: 0;
            width: 100%;
            height: 4px;
            background: linear-gradient(90deg, var(--deep-green-accent), var(--deep-green-light));
            opacity: 0;
            transition: opacity 0.3s ease;
        }

        [data-testid="stMetric"]:hover {
            transform: translateY(-5px) scale(1.02);
            border-color: var(--card-hover-border) !important;
            background: var(--card-hover-bg);
            box-shadow: var(--card-hover-shadow);
        }

        [data-testid="stMetric"]:hover::before {
            opacity: 1;
        }

        /* Metric Text Styles */
        [data-testid="stMetricLabel"] > div {
            color: var(--deep-green-accent) !important;
            font-size: 1.1rem !important;
            font-weight: 600 !important;
            letter-spacing: 0.02em;
            text-transform: uppercase;
        }

        [data-testid="stMetricValue"] {
            font-size: 2.8rem !important;
            font-weight: 800 !important;
            background: linear-gradient(90deg, var(--deep-green-light), var(--deep-green-accent));
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            letter-spacing: -0.02em;
        }

        [data-testid="stMetricDelta"] {
            background: linear-gradient(90deg, #059669, #10B981);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            font-weight: 700 !important;
            font-size: 1.1rem !important;
            padding: 0.3rem 0.8rem;
            border-radius: 1rem;
            border: 1px solid rgba(16, 185, 129, 0.2);
        }

        /* Enhanced Sidebar */
        [data-testid="stSidebar"] {
            background: var(--sidebar-bg) !important;
            border-right: 1px solid rgba(16, 185, 129, 0.1);
        }

        /* Sidebar Navigation */
        [data-testid="stSidebar"] [data-testid="stVerticalBlock"] {
            padding: 1.5rem 1rem;
        }

        [data-testid="stSidebar"] button {
            width: 100%;
            padding: 0.75rem 1rem !important;
            border-radius: 0.8rem !important;
            background: transparent !important;
            color: #E2E8F0 !important;
            border: 1px solid transparent !important;
            transition: all 0.3s ease !important;
        }

        [data-testid="stSidebar"] button:hover {
            background: var(--sidebar-hover) !important;
            border-color: rgba(16, 185, 129, 0.2) !important;
            transform: translateX(5px);
        }

        /* Chart Container */
        .js-plotly-plot {
            background: var(--card-bg);
            border: 1px solid var(--card-border) !important;
            border-radius: 1.2rem !important;
            padding: 1.5rem !important;
            box-shadow: var(--card-shadow);
            transition: all 0.3s ease;
            backdrop-filter: blur(10px);
        }

        .js-plotly-plot:hover {
            transform: translateY(-3px);
            border-color: var(--card-hover-border) !important;
            box-shadow: var(--card-hover-shadow);
        }

        /* Tables */
        .stDataFrame {
            border: 1px solid var(--card-border) !important;
            border-radius: 1rem !important;
            overflow: hidden !important;
        }

        .stDataFrame thead tr th {
            background: var(--card-bg) !important;
            color: var(--text-primary) !important;
        }

        .stDataFrame tbody tr:hover td {
            background: var(--card-hover-bg) !important;
        }

        /* Forms and Inputs */
        .stTextInput input,
        .stSelectbox select,
        .stDateInput input {
            background: var(--card-bg) !important;
            border-color: var(--card-border) !important;
            color: var(--text-primary) !important;
            border-radius: 0.8rem !important;
        }

        .stTextInput input:focus,
        .stSelectbox select:focus,
        .stDateInput input:focus {
            border-color: var(--deep-green-accent) !important;
            box-shadow: 0 0 0 3px rgba(16, 185, 129, 0.2) !important;
        }

        /* Buttons */
        .stButton > button {
            background: var(--deep-green-start) !important;
            color: white !important;
            border: none !important;
            padding: 0.75rem 1.5rem !important;
            border-radius: 0.8rem !important;
            font-weight: 600 !important;
            transition: all 0.3s ease !important;
        }

        .stButton > button:hover {
            background: var(--deep-green-end) !important;
            transform: translateY(-2px);
            box-shadow: 0 4px 12px rgba(6, 95, 70, 0.3);
        }

        /* Recent Campaign Styles */
        .recent-activity {
            background: var(--card-bg);
            border: 1px solid var(--card-border);
            border-radius: 1.2rem;
            padding: 1.5rem;
            margin: 1rem 0;
            transition: all 0.3s ease;
        }

        .activity-item {
            display: flex;
            align-items: center;
            padding: 1rem;
            margin: 0.5rem 0;
            border-radius: 0.8rem;
            background: rgba(6, 95, 70, 0.05);
            border: 1px solid rgba(16, 185, 129, 0.1);
            transition: all 0.3s ease;
        }

        .activity-item:hover {
            transform: translateX(5px);
            background: rgba(6, 95, 70, 0.1);
            border-color: var(--deep-green-accent);
            box-shadow: 0 4px 12px rgba(6, 95, 70, 0.1);
        }

        .activity-icon {
            background: var(--deep-green-start);
            color: white;
            width: 40px;
            height: 40px;
            border-radius: 50%;
            display: flex;
            align-items: center;
            justify-content: center;
            margin-right: 1rem;
            font-size: 1.2rem;
        }

        .activity-content {
            flex: 1;
        }

        .activity-title {
            color: var(--text-primary);
            font-weight: 600;
            font-size: 1rem;
            margin-bottom: 0.25rem;
        }

        .activity-meta {
            color: var(--text-secondary);
            font-size: 0.875rem;
            display: flex;
            align-items: center;
            gap: 1rem;
        }

        .activity-time {
            color: var(--deep-green-accent);
            font-weight: 500;
        }

        .activity-state {
            background: rgba(16, 185, 129, 0.1);
            color: var(--deep-green-accent);
            padding: 0.25rem 0.75rem;
            border-radius: 1rem;
            font-size: 0.875rem;
            font-weight: 500;
        }

        /* Activity List Animation */
        @keyframes slideIn {
            from {
                opacity: 0;
                transform: translateX(-10px);
            }
            to {
                opacity: 1;
                transform: translateX(0);
            }
        }

        .activity-item {
            animation: slideIn 0.3s ease-out forwards;
        }

        .activity-item:nth-child(2) {
            animation-delay: 0.1s;
        }

        .activity-item:nth-child(3) {
            animation-delay: 0.2s;
        }
    </style>
    """

def get_theme_colors(theme='dark'):
    """Get color scheme based on theme"""
    return {
        'light': {
            'background': '#F8FAFC',
            'secondary_background': '#FFFFFF',
            'card_background': '#FFFFFF',
            'text': '#1E293B',
            'secondary_text': '#475569',
        },
        'dark': {
            'background': '#0B0F19',
            'secondary_background': '#151B28',
            'card_background': '#1A2332',
            'text': '#E2E8F0',
            'secondary_text': '#94A3B8',
        }
    }[theme] 
