def get_theme_colors(theme='dark'):
    """Get color scheme based on theme"""
    return {
        'dark': {
            'background': '#0A1F1C',
            'card_bg': '#132C27',
            'text': '#E2E8F0',
            'secondary_text': '#94A3B8',
            'primary': '#064E3B',
            'primary_light': '#065F46',
            'success': '#059669',
            'border': 'rgba(6, 78, 59, 0.2)'
        }
    }

def get_styles():
    """Get base styles for the application"""
    return """
        <style>
            .stApp {
                background-color: #0A1F1C;
            }

            [data-testid="stMetricValue"] {
                background-color: #132C27;
                border-radius: 8px;
                padding: 1.5rem;
                color: white;
                font-size: 2rem;
                font-weight: 600;
                border-left: 4px solid #064E3B;
            }

            [data-testid="stMetricDelta"] {
                background-color: rgba(5, 150, 105, 0.15);
                color: #10B981;
                padding: 0.25rem 0.5rem;
                border-radius: 4px;
                font-size: 0.875rem;
            }

            [data-testid="stMetricLabel"] {
                color: #94A3B8;
                font-size: 0.875rem;
            }

            div[data-testid="stHorizontalBlock"] > div {
                background-color: #132C27;
                border-radius: 8px;
                padding: 1rem;
                border: 1px solid rgba(6, 78, 59, 0.3);
            }

            .stDataFrame {
                background-color: #132C27;
                border: 1px solid rgba(6, 78, 59, 0.3);
            }

            .stDataFrame th {
                background-color: #0F291F;
                color: #E2E8F0;
                border-bottom: 1px solid rgba(6, 78, 59, 0.3);
            }

            .stDataFrame td {
                color: #94A3B8;
            }

            .stTextInput input, .stNumberInput input {
                background-color: #132C27;
                border: 1px solid rgba(6, 78, 59, 0.3);
                color: white;
            }

            .stTextInput input:focus, .stNumberInput input:focus {
                border-color: #064E3B;
                box-shadow: 0 0 0 2px rgba(6, 78, 59, 0.3);
            }

            .stButton button {
                background-color: #064E3B;
                color: white;
                border: none;
            }

            .stButton button:hover {
                background-color: #053E2F;
            }

            .stRadio label {
                background-color: #132C27;
                color: #E2E8F0;
                border: 1px solid rgba(6, 78, 59, 0.3);
            }

            .stRadio label:hover {
                background-color: #1A3933;
                color: #10B981;
                border-color: #064E3B;
            }

            .stRadio label[data-checked="true"] {
                background-color: #064E3B;
                color: white;
                border-color: #064E3B;
            }

            .stSelectbox select {
                background-color: #132C27;
                border: 1px solid rgba(6, 78, 59, 0.3);
                color: white;
            }

            [data-testid="stSidebar"] {
                background-color: #0A1F1C;
                border-right: 1px solid rgba(6, 78, 59, 0.3);
            }

            h1, h2, h3, h4, h5, h6 {
                color: #E2E8F0;
            }

            .stMarkdown {
                color: #E2E8F0;
            }

            /* Activity items */
            .activity-item {
                background-color: #132C27;
                padding: 1rem;
                border-radius: 0.5rem;
                margin-bottom: 0.5rem;
                border: 1px solid rgba(6, 78, 59, 0.3);
            }

            .activity-item-header {
                color: #E2E8F0;
                font-weight: 600;
            }

            .activity-item-details {
                color: #94A3B8;
                font-size: 0.875rem;
            }
        </style>
    """ 
