def get_theme_colors(theme='dark'):
    """Get color scheme based on theme"""
    return {
        'dark': {
            'background': '#0A1F1C',
            'card_bg': '#132C27',
            'card_hover': '#1A3933',
            'text': '#E2E8F0',
            'secondary_text': '#94A3B8',
            'primary': '#064E3B',
            'primary_light': '#065F46',
            'success': '#059669',
            'success_light': 'rgba(5, 150, 105, 0.1)',
            'border': 'rgba(6, 78, 59, 0.2)',
            'shadow': 'rgba(0, 0, 0, 0.4)'
        }
    }

def get_styles():
    """Get base styles for the application"""
    return """
        <style>
            /* Main background */
            .stApp {
                background: linear-gradient(135deg, #0A1F1C, #0F291F) !important;
            }

            /* Metric cards styling */
            [data-testid="stMetricValue"] {
                background: linear-gradient(135deg, #132C27, #1A3933) !important;
                border-radius: 8px !important;
                padding: 1.5rem !important;
                color: white !important;
                font-size: 2rem !important;
                font-weight: 600 !important;
                border-left: 4px solid #064E3B !important;
                box-shadow: 0 4px 12px rgba(0, 0, 0, 0.4) !important;
            }

            /* Metric delta (the green up arrows) */
            [data-testid="stMetricDelta"] {
                background-color: rgba(5, 150, 105, 0.15) !important;
                color: #10B981 !important;
                padding: 0.25rem 0.5rem !important;
                border-radius: 4px !important;
                font-size: 0.875rem !important;
            }

            /* Card styling */
            div[data-testid="stHorizontalBlock"] > div {
                background: linear-gradient(135deg, #132C27, #1A3933) !important;
                border-radius: 8px !important;
                padding: 1rem !important;
                border: 1px solid rgba(6, 78, 59, 0.3) !important;
                box-shadow: 0 4px 12px rgba(0, 0, 0, 0.4) !important;
                transition: all 0.3s ease !important;
            }

            div[data-testid="stHorizontalBlock"] > div:hover {
                background: linear-gradient(135deg, #1A3933, #1F443D) !important;
                border-color: rgba(6, 78, 59, 0.5) !important;
                transform: translateY(-2px) !important;
            }

            /* Table styling */
            .stDataFrame {
                background: linear-gradient(135deg, #132C27, #1A3933) !important;
                border: 1px solid rgba(6, 78, 59, 0.3) !important;
                box-shadow: 0 4px 12px rgba(0, 0, 0, 0.4) !important;
            }

            .stDataFrame th {
                background-color: #0F291F !important;
                color: #E2E8F0 !important;
                border-bottom: 1px solid rgba(6, 78, 59, 0.3) !important;
            }

            .stDataFrame td {
                color: #94A3B8 !important;
            }

            .stDataFrame tr:hover td {
                background-color: rgba(6, 78, 59, 0.2) !important;
            }

            /* Input fields */
            .stTextInput input, .stNumberInput input {
                background-color: #132C27 !important;
                border: 1px solid rgba(6, 78, 59, 0.3) !important;
                color: white !important;
                box-shadow: 0 2px 8px rgba(0, 0, 0, 0.3) !important;
            }

            .stTextInput input:focus, .stNumberInput input:focus {
                border-color: #064E3B !important;
                box-shadow: 0 0 0 2px rgba(6, 78, 59, 0.3) !important;
            }

            /* Buttons */
            .stButton button {
                background: linear-gradient(135deg, #064E3B, #053E2F) !important;
                color: white !important;
                border: none !important;
                box-shadow: 0 4px 12px rgba(0, 0, 0, 0.4) !important;
                transition: all 0.3s ease !important;
            }

            .stButton button:hover {
                background: linear-gradient(135deg, #053E2F, #043025) !important;
                box-shadow: 0 6px 16px rgba(0, 0, 0, 0.5) !important;
                transform: translateY(-1px) !important;
            }

            /* Radio buttons */
            .stRadio label {
                background-color: #132C27 !important;
                color: #E2E8F0 !important;
                border: 1px solid rgba(6, 78, 59, 0.3) !important;
            }

            .stRadio label:hover {
                background-color: #1A3933 !important;
                color: #10B981 !important;
                border-color: #064E3B !important;
            }

            .stRadio label[data-checked="true"] {
                background: linear-gradient(135deg, #064E3B, #053E2F) !important;
                color: white !important;
                border-color: #064E3B !important;
                box-shadow: 0 4px 12px rgba(0, 0, 0, 0.4) !important;
            }

            /* Selectbox */
            .stSelectbox select {
                background-color: #132C27 !important;
                border: 1px solid rgba(6, 78, 59, 0.3) !important;
                color: white !important;
                box-shadow: 0 2px 8px rgba(0, 0, 0, 0.3) !important;
            }

            /* Sidebar */
            [data-testid="stSidebar"] {
                background: linear-gradient(180deg, #0A1F1C, #0F291F) !important;
                border-right: 1px solid rgba(6, 78, 59, 0.3) !important;
            }

            /* Headers */
            h1, h2, h3, h4, h5, h6 {
                color: #E2E8F0 !important;
                text-shadow: 0 2px 4px rgba(0, 0, 0, 0.3) !important;
            }
        </style>
    """ 
