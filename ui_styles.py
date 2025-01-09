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

            /* Graph styling */
            [data-testid="stPlotlyChart"] {
                background-color: #132C27;
                border-radius: 8px;
                padding: 1rem;
                border: 1px solid rgba(6, 78, 59, 0.3);
            }

            /* Make graph lines more visible */
            .js-plotly-plot .plotly .scatter .lines path {
                stroke-width: 3px !important;
                stroke: #10B981 !important;
            }

            /* Make points more visible */
            .js-plotly-plot .plotly .scatter .points path {
                fill: #34D399 !important;
                stroke: #FFFFFF !important;
                stroke-width: 2px !important;
            }

            /* Axis labels */
            .js-plotly-plot .plotly .xtick text,
            .js-plotly-plot .plotly .ytick text {
                fill: #E2E8F0 !important;
                font-size: 12px !important;
            }

            /* Cards */
            div[data-testid="stHorizontalBlock"] > div {
                background-color: #132C27;
                border-radius: 8px;
                padding: 1rem;
                border: 1px solid rgba(6, 78, 59, 0.3);
            }

            /* Table styling */
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

            /* Inputs */
            .stTextInput input, .stNumberInput input {
                background-color: #132C27;
                border: 1px solid rgba(6, 78, 59, 0.3);
                color: white;
            }

            /* Buttons */
            .stButton button {
                background-color: #064E3B;
                color: white;
                border: none;
            }

            .stButton button:hover {
                background-color: #053E2F;
            }

            /* Radio buttons */
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

            /* Selectbox */
            .stSelectbox select {
                background-color: #132C27;
                border: 1px solid rgba(6, 78, 59, 0.3);
                color: white;
            }

            [data-testid="stSidebar"] {
                background: linear-gradient(180deg, #0A1F1C 0%, #132C27 100%);
                border-right: 2px solid #064E3B;
                box-shadow: 2px 0 10px rgba(0, 0, 0, 0.2);
            }

            /* Sidebar Header */
            .sidebar-header {
                background: linear-gradient(90deg, #064E3B, #065F46);
                padding: 1.5rem 1rem;
                margin-bottom: 1rem;
                border-bottom: 1px solid rgba(255, 255, 255, 0.1);
                box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
            }

            .sidebar-header h2 {
                color: white;
                font-size: 1.25rem;
                font-weight: 600;
                margin: 0;
                text-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
            }

            /* Sidebar Navigation Items */
            .stRadio {
                padding: 0.5rem;
            }

            .stRadio > label {
                background-color: transparent !important;
                border: none !important;
                padding: 0 !important;
            }

            .stRadio label {
                background: transparent;
                color: #94A3B8;
                padding: 0.75rem 1rem !important;
                border-radius: 8px !important;
                margin: 0.25rem 0 !important;
                border: 1px solid transparent !important;
                transition: all 0.3s ease !important;
                font-size: 0.95rem !important;
                display: flex !important;
                align-items: center !important;
                gap: 0.75rem !important;
            }

            .stRadio label:hover {
                background: rgba(6, 78, 59, 0.2) !important;
                color: #E2E8F0 !important;
                transform: translateX(5px);
                border-color: rgba(6, 78, 59, 0.5) !important;
            }

            .stRadio label[data-checked="true"] {
                background: linear-gradient(90deg, #064E3B, #065F46) !important;
                color: white !important;
                border-color: #064E3B !important;
                box-shadow: 0 4px 12px rgba(0, 0, 0, 0.2) !important;
                transform: translateX(5px);
            }

            /* Sidebar icons */
            .stRadio label::before {
                content: '';
                width: 24px;
                height: 24px;
                display: inline-block;
                margin-right: 8px;
                background-size: contain;
                background-repeat: no-repeat;
                background-position: center;
                transition: all 0.3s ease;
            }

            /* Active indicator */
            .stRadio label[data-checked="true"]::after {
                content: '';
                position: absolute;
                left: 0;
                top: 50%;
                transform: translateY(-50%);
                width: 4px;
                height: 60%;
                background: #10B981;
                border-radius: 0 4px 4px 0;
                animation: slideIn 0.3s ease;
            }

            @keyframes slideIn {
                from {
                    opacity: 0;
                    transform: translate(-10px, -50%);
                }
                to {
                    opacity: 1;
                    transform: translate(0, -50%);
                }
            }

            /* Hover animation */
            @keyframes pulse {
                0% {
                    box-shadow: 0 0 0 0 rgba(16, 185, 129, 0.4);
                }
                70% {
                    box-shadow: 0 0 0 10px rgba(16, 185, 129, 0);
                }
                100% {
                    box-shadow: 0 0 0 0 rgba(16, 185, 129, 0);
                }
            }

            .stRadio label:hover::before {
                transform: scale(1.1);
            }

            .stRadio label[data-checked="true"]:hover {
                animation: pulse 1.5s infinite;
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