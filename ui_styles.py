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
            'success': '#4ADE80',          # Success green
            'warning': '#FBBF24',          # Warning yellow
            'warning_light': '#FDE68A',    # Light yellow
            'gradient_start': '#86EFAC',   # Gradient start
            'gradient_end': '#34D399',     # Gradient end
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
            'success': '#4ADE80',
            'warning': '#FBBF24',
            'warning_light': '#FDE68A',
            'gradient_start': '#86EFAC',
            'gradient_end': '#34D399',
            'border': 'rgba(255,255,255,0.1)'
        }
    }
    return colors[theme]

def get_styles():
    """Get base styles for the application"""
    return """
        <style>
            /* Card styling with gradients */
            [data-testid="stCard"] {
                background: linear-gradient(135deg, var(--gradient-start, #86EFAC), var(--gradient-end, #34D399)) !important;
                border-radius: 1rem !important;
                padding: 1rem !important;
                transition: all 0.3s ease !important;
            }

            [data-testid="stCard"]:hover {
                transform: translateY(-4px) !important;
                box-shadow: 0 12px 20px rgba(52, 211, 153, 0.2) !important;
            }

            /* Metric cards with light green background */
            [data-testid="metric-container"] {
                background: linear-gradient(135deg, rgba(134, 239, 172, 0.1), rgba(52, 211, 153, 0.1)) !important;
                border: 1px solid rgba(16, 185, 129, 0.2) !important;
                border-radius: 1rem !important;
                padding: 1rem !important;
                transition: all 0.3s ease !important;
            }

            [data-testid="metric-container"]:hover {
                transform: translateY(-4px) !important;
                box-shadow: 0 12px 20px rgba(52, 211, 153, 0.15) !important;
            }

            /* Button styling with gradient */
            button[kind="primary"] {
                background: linear-gradient(135deg, var(--primary-light, #34D399), var(--primary-color, #10B981)) !important;
                border: none !important;
                color: white !important;
                transition: all 0.3s ease !important;
                box-shadow: 0 4px 12px rgba(16, 185, 129, 0.2) !important;
            }
            
            button[kind="primary"]:hover {
                background: linear-gradient(135deg, var(--primary-lighter, #86EFAC), var(--primary-light, #34D399)) !important;
                transform: translateY(-2px) !important;
                box-shadow: 0 8px 16px rgba(16, 185, 129, 0.3) !important;
            }

            /* Success indicators */
            .success-indicator {
                color: var(--success, #4ADE80) !important;
                background: rgba(74, 222, 128, 0.1) !important;
                padding: 0.25rem 0.75rem !important;
                border-radius: 1rem !important;
                border: 1px solid rgba(74, 222, 128, 0.2) !important;
            }

            /* Warning indicators */
            .warning-indicator {
                color: var(--warning, #FBBF24) !important;
                background: rgba(251, 191, 36, 0.1) !important;
                padding: 0.25rem 0.75rem !important;
                border-radius: 1rem !important;
                border: 1px solid rgba(251, 191, 36, 0.2) !important;
            }

            /* Progress bars with gradient */
            .stProgress > div > div {
                background: linear-gradient(90deg, var(--primary-light, #34D399), var(--primary-color, #10B981)) !important;
            }

            /* Table row hover with light green */
            .stDataFrame tr:hover td {
                background: linear-gradient(90deg, rgba(134, 239, 172, 0.1), rgba(52, 211, 153, 0.1)) !important;
            }

            /* Input focus states with yellow highlight */
            input:focus, select:focus {
                border-color: var(--warning, #FBBF24) !important;
                box-shadow: 0 0 0 3px rgba(251, 191, 36, 0.2) !important;
            }

            /* Radio buttons with gradient when selected */
            .stRadio label[data-checked="true"] {
                background: linear-gradient(135deg, var(--primary-light, #34D399), var(--primary-color, #10B981)) !important;
                border: none !important;
                color: white !important;
            }

            /* Links with gradient hover */
            a:hover {
                background: linear-gradient(90deg, var(--primary-color, #10B981), var(--primary-light, #34D399)) !important;
                -webkit-background-clip: text !important;
                -webkit-text-fill-color: transparent !important;
            }
        </style>
    """ 
