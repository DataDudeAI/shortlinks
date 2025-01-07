def load_ui_styles():
    return """
    <style>
        /* Modern Dark Theme Colors */
        :root {
            --background-color: #0B0F19;
            --secondary-background-color: #151B28;
            --card-background: #1A2332;
            --text-color: #E2E8F0;
            --secondary-text-color: #94A3B8;
            --accent-color: #10B981;
            --accent-hover: #34D399;
            --gradient-start: #34D399;
            --gradient-end: #10B981;
            --border-color: rgba(255, 255, 255, 0.1);
            --hover-color: rgba(16, 185, 129, 0.1);
        }

        /* Force Light Text on Dark Background */
        .stApp {
            background-color: var(--background-color);
        }

        /* All Text Elements */
        .stApp, .stApp p, .stApp div, .stApp label, .stApp span {
            color: var(--text-color) !important;
        }

        /* Main Header */
        .main-header {
            background: linear-gradient(135deg, #4F46E5, #7C3AED);
            padding: 0.8rem;
            border-radius: 0.5rem;
            margin-bottom: 1rem;
            box-shadow: 0 4px 15px rgba(0, 0, 0, 0.1);
        }

        .main-header h1 {
            color: white !important;
            font-size: 1.2rem !important;
            font-weight: 600 !important;
            text-align: center;
            margin: 0 !important;
        }

        /* Section Headers */
        h3 {
            color: white !important;
            font-size: 1rem !important;
            font-weight: 600 !important;
            padding: 0.5rem 1rem !important;
            background: linear-gradient(135deg, #2563EB, #3B82F6);
            border-radius: 0.5rem;
            margin: 1rem 0 !important;
        }

        /* Cards */
        .card {
            background: var(--card-background);
            padding: 1rem;
            border-radius: 0.5rem;
            border: 1px solid var(--border-color);
            margin-bottom: 1rem;
        }

        /* Metrics */
        [data-testid="stMetric"] {
            background: var(--card-background);
            padding: 1rem !important;
            border-radius: 0.5rem !important;
            border: 1px solid var(--border-color);
        }

        [data-testid="stMetricLabel"] {
            color: var(--text-color) !important;
            font-size: 0.9rem !important;
        }

        [data-testid="stMetricValue"] {
            color: var(--accent-color) !important;
            font-size: 1.5rem !important;
            font-weight: 600 !important;
        }

        [data-testid="stMetricDelta"] {
            color: var(--accent-color) !important;
        }

        /* Form Elements */
        .stTextInput input, .stSelectbox select, .stTextArea textarea {
            background: var(--secondary-background-color) !important;
            color: var(--text-color) !important;
            border: 1px solid var(--border-color) !important;
            border-radius: 0.5rem !important;
            padding: 0.5rem !important;
        }

        .stTextInput label, .stSelectbox label, .stTextArea label {
            color: var(--text-color) !important;
            font-weight: 500 !important;
        }

        /* Buttons */
        .stButton > button {
            background: linear-gradient(135deg, #4F46E5, #7C3AED) !important;
            color: white !important;
            border: none !important;
            padding: 0.5rem 1rem !important;
            border-radius: 0.5rem !important;
        }

        /* Tables */
        .stDataFrame {
            background: var(--card-background) !important;
            border-radius: 0.5rem !important;
            border: 1px solid var(--border-color) !important;
        }

        .stDataFrame th {
            background: var(--secondary-background-color) !important;
            color: var(--text-color) !important;
            font-weight: 600 !important;
        }

        .stDataFrame td {
            color: var(--text-color) !important;
        }

        /* Activity Items */
        .activity-item {
            background: var(--card-background);
            padding: 0.8rem;
            border-radius: 0.5rem;
            margin: 0.5rem 0;
            border: 1px solid var(--border-color);
        }

        .activity-item strong {
            color: var(--accent-color) !important;
        }

        .activity-time {
            color: var(--secondary-text-color) !important;
            font-size: 0.8rem;
        }

        /* Charts */
        [data-testid="stPlotlyChart"] {
            background: var(--card-background) !important;
            border-radius: 0.5rem !important;
            border: 1px solid var(--border-color) !important;
            padding: 1rem !important;
        }

        /* Sidebar */
        section[data-testid="stSidebar"] {
            background-color: var(--secondary-background-color);
            border-right: 1px solid var(--border-color);
        }

        section[data-testid="stSidebar"] .stRadio label {
            color: var(--text-color) !important;
        }

        /* Tabs */
        .stTabs [data-baseweb="tab-list"] {
            background-color: var(--secondary-background-color);
        }

        .stTabs [data-baseweb="tab"] {
            color: var(--text-color) !important;
        }

        /* Expander */
        .streamlit-expanderHeader {
            background-color: var(--secondary-background-color) !important;
            color: var(--text-color) !important;
        }

        /* Remove extra spacing */
        .main .block-container {
            padding-top: 1rem !important;
        }

        /* Checkbox and Radio */
        .stCheckbox label, .stRadio label {
            color: var(--text-color) !important;
        }

        /* Selectbox */
        .stSelectbox > div > div {
            color: var(--text-color) !important;
        }
    </style>
    """ 
