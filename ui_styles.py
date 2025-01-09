def get_theme_colors(theme='light'):
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

def get_styles():
    """Get base styles for the application"""
    return """
        <style>
            /* Text colors for better visibility */
            .stMarkdown, .stMetric {
                color: #1E293B !important;
            }
            
            .stMarkdown h4 {
                color: #1E293B !important;
                font-weight: 600;
            }

            /* Button text color */
            .stButton button {
                color: #1E293B !important;
            }
            
            .stButton button:hover {
                color: white !important;
            }

            /* Table text colors */
            .stDataFrame td, .stDataFrame th {
                color: #1E293B !important;
            }

            /* Metric colors */
            [data-testid="stMetricValue"] {
                color: #1E293B !important;
            }
            
            [data-testid="stMetricLabel"] {
                color: #475569 !important;
            }

            /* Sidebar text */
            [data-testid="stSidebarNav"] {
                color: #1E293B !important;
            }
        </style>
    """ 
