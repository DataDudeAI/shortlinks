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
            /* Base text colors */
            div[data-testid="stMarkdown"] p,
            div[data-testid="stMarkdown"] span,
            div[data-testid="stMarkdown"] li,
            div[data-testid="stText"] p {
                color: #1E293B !important;
            }
            
            /* Headings */
            div[data-testid="stMarkdown"] h1,
            div[data-testid="stMarkdown"] h2,
            div[data-testid="stMarkdown"] h3,
            div[data-testid="stMarkdown"] h4 {
                color: #1E293B !important;
                font-weight: 600 !important;
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

            /* Table styling */
            .stDataFrame {
                border: 1px solid rgba(0,0,0,0.1) !important;
                border-radius: 0.5rem !important;
                overflow: hidden !important;
            }
            
            div[data-testid="stDataFrame"] td,
            div[data-testid="stDataFrame"] th {
                color: #1E293B !important;
                padding: 0.75rem 1rem !important;
            }
            
            div[data-testid="stDataFrame"] tr:hover td {
                background-color: rgba(16, 185, 129, 0.05) !important;
            }

            /* Metric styling */
            div[data-testid="stMetricValue"] {
                color: #1E293B !important;
                font-weight: 600 !important;
            }
            
            div[data-testid="stMetricLabel"] {
                color: #475569 !important;
            }

            /* Sidebar styling */
            section[data-testid="stSidebar"] {
                background-color: white !important;
                border-right: 1px solid rgba(0,0,0,0.1) !important;
            }
            
            section[data-testid="stSidebar"] div[data-testid="stMarkdown"] {
                color: #1E293B !important;
            }

            /* Radio button styling */
            div[data-testid="stRadio"] label {
                color: #1E293B !important;
                padding: 0.5rem 1rem !important;
                border-radius: 0.375rem !important;
                transition: all 0.3s ease !important;
            }
            
            div[data-testid="stRadio"] label:hover {
                background-color: rgba(16, 185, 129, 0.05) !important;
                color: #10B981 !important;
            }
            
            div[data-testid="stRadio"] label[data-checked="true"] {
                background-color: #10B981 !important;
                color: white !important;
            }

            /* Input field styling */
            div[data-testid="stTextInput"] input,
            div[data-testid="stSelectbox"] select {
                color: #1E293B !important;
                border-radius: 0.375rem !important;
                border: 1px solid rgba(0,0,0,0.1) !important;
                transition: all 0.3s ease !important;
            }
            
            div[data-testid="stTextInput"] input:focus,
            div[data-testid="stSelectbox"] select:focus {
                border-color: #10B981 !important;
                box-shadow: 0 0 0 2px rgba(16, 185, 129, 0.2) !important;
            }

            /* Card styling */
            div[data-testid="stCard"] {
                background: white !important;
                border-radius: 0.5rem !important;
                padding: 1rem !important;
                border: 1px solid rgba(0,0,0,0.1) !important;
                transition: all 0.3s ease !important;
            }
            
            div[data-testid="stCard"]:hover {
                transform: translateY(-2px) !important;
                box-shadow: 0 4px 12px rgba(0,0,0,0.1) !important;
            }
        </style>
    """ 
