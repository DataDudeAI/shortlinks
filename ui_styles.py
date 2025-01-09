def get_theme_colors(theme='light'):
    """Get color scheme based on theme"""
    return {
        'light': {
            'background': '#F8FAFC',
            'secondary_background': '#FFFFFF',
            'card_background': '#FFFFFF',
            'text': '#1E293B',
            'secondary_text': '#475569',
            'primary': '#10B981',  # Green theme color
            'primary_hover': '#059669',
            'border': 'rgba(0,0,0,0.1)'
        },
        'dark': {
            'background': '#0B0F19',
            'secondary_background': '#151B28',
            'card_background': '#1A2332',
            'text': '#E2E8F0',
            'secondary_text': '#94A3B8',
            'primary': '#10B981',
            'primary_hover': '#059669',
            'border': 'rgba(255,255,255,0.1)'
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

            /* Button styling */
            .stButton button {
                background-color: #10B981 !important;
                color: white !important;
                border: none !important;
                transition: all 0.3s ease !important;
            }
            
            .stButton button:hover {
                background-color: #059669 !important;
                transform: translateY(-2px) !important;
                box-shadow: 0 4px 12px rgba(16, 185, 129, 0.2) !important;
            }

            /* Card styling */
            .stCard {
                background: white !important;
                border-radius: 0.5rem !important;
                padding: 1rem !important;
                border: 1px solid rgba(0,0,0,0.1) !important;
                transition: all 0.3s ease !important;
            }
            
            .stCard:hover {
                transform: translateY(-2px) !important;
                box-shadow: 0 4px 12px rgba(0,0,0,0.1) !important;
            }

            /* Table styling */
            .stDataFrame {
                border: 1px solid rgba(0,0,0,0.1) !important;
                border-radius: 0.5rem !important;
                overflow: hidden !important;
            }
            
            .stDataFrame td, .stDataFrame th {
                color: #1E293B !important;
                padding: 0.75rem 1rem !important;
            }
            
            .stDataFrame tr:hover td {
                background-color: rgba(16, 185, 129, 0.05) !important;
            }

            /* Metric styling */
            [data-testid="stMetricValue"] {
                color: #1E293B !important;
                font-weight: 600 !important;
            }
            
            [data-testid="stMetricLabel"] {
                color: #475569 !important;
            }

            /* Sidebar styling */
            [data-testid="stSidebarNav"] {
                color: #1E293B !important;
            }
            
            .stSidebar {
                background-color: white !important;
                border-right: 1px solid rgba(0,0,0,0.1) !important;
            }
            
            /* Radio button styling */
            .stRadio label {
                padding: 0.5rem 1rem !important;
                border-radius: 0.375rem !important;
                transition: all 0.3s ease !important;
            }
            
            .stRadio label:hover {
                background-color: rgba(16, 185, 129, 0.05) !important;
                color: #10B981 !important;
            }
            
            .stRadio label[data-checked="true"] {
                background-color: #10B981 !important;
                color: white !important;
            }

            /* Input field styling */
            .stTextInput input, .stSelectbox select {
                border-radius: 0.375rem !important;
                border: 1px solid rgba(0,0,0,0.1) !important;
                transition: all 0.3s ease !important;
            }
            
            .stTextInput input:focus, .stSelectbox select:focus {
                border-color: #10B981 !important;
                box-shadow: 0 0 0 2px rgba(16, 185, 129, 0.2) !important;
            }
        </style>
    """ 
