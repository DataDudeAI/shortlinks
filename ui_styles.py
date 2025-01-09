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
            button[kind="primary"] {
                background-color: #10B981 !important;
                border-color: #10B981 !important;
                color: white !important;
                transition: all 0.2s ease !important;
            }
            
            button[kind="primary"]:hover {
                background-color: #059669 !important;
                border-color: #059669 !important;
                transform: translateY(-2px);
                box-shadow: 0 4px 12px rgba(16, 185, 129, 0.2);
            }

            /* Table styling */
            [data-testid="stTable"] {
                border: 1px solid rgba(0,0,0,0.1);
                border-radius: 8px;
                overflow: hidden;
            }

            [data-testid="stTable"] table {
                border-collapse: separate;
                border-spacing: 0;
            }

            [data-testid="stTable"] th {
                background: #F8FAFC;
                color: #1E293B;
                font-weight: 600;
                padding: 12px 24px;
                border-bottom: 1px solid rgba(0,0,0,0.1);
            }

            [data-testid="stTable"] td {
                color: #1E293B;
                padding: 12px 24px;
                transition: background-color 0.2s ease;
            }

            [data-testid="stTable"] tr:hover td {
                background-color: rgba(16, 185, 129, 0.05);
            }

            /* Card styling */
            div.element-container {
                transition: transform 0.2s ease, box-shadow 0.2s ease;
            }

            div.element-container:hover {
                transform: translateY(-2px);
                box-shadow: 0 4px 12px rgba(0,0,0,0.1);
            }

            /* Input styling */
            input[type="text"],
            input[type="number"],
            select {
                border: 1px solid rgba(0,0,0,0.1) !important;
                border-radius: 6px !important;
                padding: 8px 12px !important;
                transition: all 0.2s ease !important;
            }

            input[type="text"]:focus,
            input[type="number"]:focus,
            select:focus {
                border-color: #10B981 !important;
                box-shadow: 0 0 0 2px rgba(16, 185, 129, 0.2) !important;
                outline: none !important;
            }

            /* Radio button styling */
            div[role="radiogroup"] label {
                transition: all 0.2s ease !important;
                border: 1px solid rgba(0,0,0,0.1) !important;
                border-radius: 6px !important;
                margin: 4px 0 !important;
            }

            div[role="radiogroup"] label:hover {
                background-color: rgba(16, 185, 129, 0.05) !important;
                border-color: #10B981 !important;
            }

            div[role="radiogroup"] label[data-checked="true"] {
                background-color: #10B981 !important;
                border-color: #10B981 !important;
                color: white !important;
            }

            /* Metric styling */
            div[data-testid="metric-container"] {
                background-color: white;
                border: 1px solid rgba(0,0,0,0.1);
                border-radius: 8px;
                padding: 16px;
                transition: transform 0.2s ease, box-shadow 0.2s ease;
            }

            div[data-testid="metric-container"]:hover {
                transform: translateY(-2px);
                box-shadow: 0 4px 12px rgba(0,0,0,0.1);
            }
        </style>
    """ 
