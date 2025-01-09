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
            'border': 'rgba(0,0,0,0.1)'
        },
        'dark': {
            'background': '#0B0F19',
            'secondary_background': '#151B28',
            'card_background': '#1A2332',
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
            /* Button styling */
            button[kind="primary"] {
                background-color: var(--primary-color, #10B981) !important;
                border-color: var(--primary-color, #10B981) !important;
                color: white !important;
                transition: all 0.2s ease !important;
            }
            
            button[kind="primary"]:hover {
                background-color: var(--primary-hover, #059669) !important;
                border-color: var(--primary-hover, #059669) !important;
            }

            /* Radio button styling */
            div[role="radiogroup"] label:hover {
                border-color: var(--primary-color, #10B981) !important;
                background-color: var(--primary-light-transparent, rgba(16, 185, 129, 0.05)) !important;
            }

            div[role="radiogroup"] label[data-checked="true"] {
                background-color: var(--primary-color, #10B981) !important;
                border-color: var(--primary-color, #10B981) !important;
            }

            /* Input focus states */
            input:focus, select:focus {
                border-color: var(--primary-color, #10B981) !important;
                box-shadow: 0 0 0 2px var(--primary-light-transparent, rgba(16, 185, 129, 0.2)) !important;
            }

            /* Table hover states */
            tr:hover td {
                background-color: var(--primary-light-transparent, rgba(16, 185, 129, 0.05)) !important;
            }

            /* Links */
            a {
                color: var(--primary-color, #10B981) !important;
            }

            a:hover {
                color: var(--primary-hover, #059669) !important;
            }

            /* Progress bars */
            .stProgress > div > div {
                background-color: var(--primary-color, #10B981) !important;
            }

            /* Checkboxes and radio buttons */
            .stCheckbox label span[data-checked="true"],
            .stRadio label span[data-checked="true"] {
                background-color: var(--primary-color, #10B981) !important;
                border-color: var(--primary-color, #10B981) !important;
            }
        </style>
    """ 
