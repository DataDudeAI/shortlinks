def get_theme_colors(theme='dark'):
    """Get color scheme based on theme"""
    return {
        'dark': {
            'background': '#1A1D24',
            'card_bg': '#24282E',
            'text': '#E2E8F0',
            'secondary_text': '#94A3B8',
            'primary': '#10B981',
            'success': '#4ADE80',
            'border': 'rgba(255,255,255,0.1)'
        }
    }

def get_styles():
    """Get base styles for the application"""
    return """
        <style>
            /* Metric cards styling */
            [data-testid="stMetricValue"] {
                background-color: #24282E !important;
                border-radius: 8px !important;
                padding: 1rem !important;
                color: white !important;
                font-size: 2rem !important;
                font-weight: 600 !important;
            }

            /* Metric delta (the green up arrows) */
            [data-testid="stMetricDelta"] {
                background-color: rgba(74, 222, 128, 0.1) !important;
                color: #4ADE80 !important;
                padding: 0.25rem 0.5rem !important;
                border-radius: 4px !important;
                font-size: 0.875rem !important;
            }

            /* Metric label */
            [data-testid="stMetricLabel"] {
                color: #94A3B8 !important;
                font-size: 0.875rem !important;
            }

            /* Card styling */
            div[data-testid="stHorizontalBlock"] > div {
                background-color: #24282E !important;
                border-radius: 8px !important;
                padding: 1rem !important;
                border: 1px solid rgba(255,255,255,0.1) !important;
            }

            /* Text colors */
            .stMarkdown, .stText {
                color: #E2E8F0 !important;
            }

            h1, h2, h3, h4, h5, h6 {
                color: white !important;
            }

            /* Table styling */
            .stDataFrame {
                background-color: #24282E !important;
                border: 1px solid rgba(255,255,255,0.1) !important;
            }

            .stDataFrame th {
                background-color: #2A2F36 !important;
                color: #E2E8F0 !important;
            }

            .stDataFrame td {
                color: #94A3B8 !important;
            }

            /* Input fields */
            .stTextInput input, .stNumberInput input {
                background-color: #24282E !important;
                border: 1px solid rgba(255,255,255,0.1) !important;
                color: white !important;
            }

            /* Buttons */
            .stButton button {
                background-color: #10B981 !important;
                color: white !important;
            }
        </style>
    """ 
