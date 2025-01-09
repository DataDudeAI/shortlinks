def get_theme_colors(theme='light'):
    """Get color scheme based on theme"""
    colors = {
        'light': {
            'background': '#F8FAFC',
            'secondary_background': '#FFFFFF',
            'card_background': '#FFFFFF',
            'text': '#1E293B',
            'secondary_text': '#475569',
            'primary': '#10B981',          # Base green
            'primary_light': '#34D399',    # Light green
            'primary_lighter': '#86EFAC',  # Lighter green
            'primary_dark': '#059669',     # Dark green
            'primary_hover': '#047857',    # Darker green for hover
            'border': 'rgba(255,255,255,0.1)'
        },
        'dark': {
            'background': '#1A1D24',       # Dark background
            'secondary_background': '#24282E',
            'card_background': '#2A2F36',
            'text': '#E2E8F0',
            'secondary_text': '#94A3B8',
            'primary': '#10B981',
            'primary_light': '#34D399',
            'primary_lighter': '#86EFAC',
            'primary_dark': '#059669',
            'primary_hover': '#047857',
            'border': 'rgba(255,255,255,0.1)'
        }
    }
    return colors[theme]

def get_styles():
    """Get base styles for the application"""
    return """
        <style>
            /* Metric cards styling */
            [data-testid="metric-container"] {
                background-color: #24282E !important;
                border: 1px solid rgba(52, 211, 153, 0.2) !important;
                border-radius: 0.5rem !important;
                padding: 1.5rem !important;
                color: white !important;
            }

            [data-testid="metric-container"]:hover {
                border-color: #34D399 !important;
                box-shadow: 0 0 15px rgba(52, 211, 153, 0.2) !important;
            }

            /* Metric value styling */
            [data-testid="stMetricValue"] {
                color: white !important;
                font-size: 2rem !important;
                font-weight: 600 !important;
            }

            /* Metric delta styling - for the green up arrows */
            [data-testid="stMetricDelta"] {
                color: #4ADE80 !important;
                font-size: 0.875rem !important;
                background: rgba(74, 222, 128, 0.1) !important;
                padding: 0.25rem 0.5rem !important;
                border-radius: 0.25rem !important;
            }

            /* Table styling */
            .stDataFrame {
                background-color: #24282E !important;
                border: 1px solid rgba(255,255,255,0.1) !important;
                border-radius: 0.5rem !important;
            }

            .stDataFrame th {
                background-color: #2A2F36 !important;
                color: #E2E8F0 !important;
                font-weight: 600 !important;
                padding: 1rem !important;
                border-bottom: 1px solid rgba(255,255,255,0.1) !important;
            }

            .stDataFrame td {
                color: #94A3B8 !important;
                padding: 0.75rem 1rem !important;
            }

            /* Button styling */
            button[kind="primary"] {
                background-color: #10B981 !important;
                border: none !important;
                color: white !important;
                padding: 0.5rem 1rem !important;
                border-radius: 0.375rem !important;
            }

            button[kind="primary"]:hover {
                background-color: #059669 !important;
                box-shadow: 0 0 15px rgba(16, 185, 129, 0.3) !important;
            }

            /* Input fields */
            .stTextInput input {
                background-color: #24282E !important;
                border: 1px solid rgba(255,255,255,0.1) !important;
                color: white !important;
                border-radius: 0.375rem !important;
            }

            .stTextInput input:focus {
                border-color: #10B981 !important;
                box-shadow: 0 0 0 2px rgba(16, 185, 129, 0.2) !important;
            }

            /* Dropdown/Select */
            .stSelectbox select {
                background-color: #24282E !important;
                border: 1px solid rgba(255,255,255,0.1) !important;
                color: white !important;
                border-radius: 0.375rem !important;
            }

            /* Tabs styling */
            .stTabs [data-baseweb="tab-list"] {
                background-color: #24282E !important;
                border-radius: 0.5rem !important;
                padding: 0.5rem !important;
            }

            .stTabs [data-baseweb="tab"] {
                color: #94A3B8 !important;
            }

            .stTabs [data-baseweb="tab"][aria-selected="true"] {
                color: #10B981 !important;
                background-color: rgba(16, 185, 129, 0.1) !important;
            }

            /* Headers */
            h1, h2, h3 {
                color: white !important;
            }

            /* Links */
            a {
                color: #10B981 !important;
                text-decoration: none !important;
            }

            a:hover {
                color: #34D399 !important;
            }
        </style>
    """ 
