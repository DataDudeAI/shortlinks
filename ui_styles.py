def get_theme_colors(theme='light'):
    """Get color scheme based on theme"""
    colors = {
        'dark': {
            'background': '#1A1D24',
            'card_bg': '#24282E',
            'text': '#E2E8F0',
            'secondary_text': '#94A3B8',
            'primary': '#10B981',
            'primary_light': '#34D399',
            'border': 'rgba(255,255,255,0.1)'
        }
    }
    return colors[theme]

def get_styles():
    """Get base styles for the application"""
    return """
        <style>
            /* Main container background */
            .main {
                background-color: #1A1D24 !important;
            }

            /* Metric cards styling - with green border */
            [data-testid="metric-container"] {
                background-color: #24282E !important;
                border-left: 4px solid #10B981 !important;
                border-radius: 8px !important;
                padding: 1rem !important;
                box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1) !important;
            }

            /* Metric value styling */
            [data-testid="stMetricValue"] {
                color: white !important;
                font-size: 24px !important;
                font-weight: 600 !important;
            }

            /* Metric label styling */
            [data-testid="stMetricLabel"] {
                color: #94A3B8 !important;
            }

            /* Metric delta styling - green arrows */
            [data-testid="stMetricDelta"] {
                color: #4ADE80 !important;
                background: rgba(74, 222, 128, 0.1) !important;
                padding: 2px 6px !important;
                border-radius: 4px !important;
            }

            /* Create Campaign section styling */
            .create-campaign {
                background-color: #24282E !important;
                border-radius: 8px !important;
                padding: 1.5rem !important;
                margin: 1rem 0 !important;
                border: 1px solid rgba(16, 185, 129, 0.2) !important;
            }

            /* Input fields */
            .stTextInput input, .stNumberInput input {
                background-color: #2A2F36 !important;
                border: 1px solid rgba(255,255,255,0.1) !important;
                color: white !important;
                border-radius: 6px !important;
                padding: 8px 12px !important;
            }

            .stTextInput input:focus, .stNumberInput input:focus {
                border-color: #10B981 !important;
                box-shadow: 0 0 0 2px rgba(16, 185, 129, 0.2) !important;
            }

            /* Select/Dropdown */
            .stSelectbox select {
                background-color: #2A2F36 !important;
                border: 1px solid rgba(255,255,255,0.1) !important;
                color: white !important;
                border-radius: 6px !important;
            }

            /* Button styling */
            .stButton button {
                background-color: #10B981 !important;
                color: white !important;
                border: none !important;
                padding: 8px 16px !important;
                border-radius: 6px !important;
                font-weight: 500 !important;
            }

            .stButton button:hover {
                background-color: #059669 !important;
                box-shadow: 0 0 12px rgba(16, 185, 129, 0.4) !important;
            }

            /* Table styling */
            .stDataFrame {
                background-color: #24282E !important;
                border-radius: 8px !important;
                overflow: hidden !important;
            }

            .stDataFrame th {
                background-color: #2A2F36 !important;
                color: #E2E8F0 !important;
                padding: 12px 16px !important;
                border-bottom: 1px solid rgba(255,255,255,0.1) !important;
            }

            .stDataFrame td {
                color: #94A3B8 !important;
                padding: 12px 16px !important;
                border-bottom: 1px solid rgba(255,255,255,0.05) !important;
            }

            .stDataFrame tr:hover td {
                background-color: rgba(16, 185, 129, 0.05) !important;
            }

            /* Headers */
            h1, h2, h3, h4 {
                color: white !important;
                font-weight: 600 !important;
            }

            /* Links */
            a {
                color: #10B981 !important;
                text-decoration: none !important;
            }

            a:hover {
                color: #34D399 !important;
            }

            /* Tabs */
            .stTabs [data-baseweb="tab"] {
                color: #94A3B8 !important;
            }

            .stTabs [data-baseweb="tab"][aria-selected="true"] {
                color: #10B981 !important;
            }

            /* Radio buttons */
            .stRadio label {
                color: #E2E8F0 !important;
            }

            .stRadio label:hover {
                color: #10B981 !important;
            }
        </style>
    """ 
