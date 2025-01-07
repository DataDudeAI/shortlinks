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
            
            /* Gradient Colors */
            --purple-gradient: linear-gradient(135deg, #4F46E5, #7C3AED);
            --blue-gradient: linear-gradient(135deg, #2563EB, #3B82F6);
            --green-gradient: linear-gradient(135deg, #059669, #10B981);
            --pink-gradient: linear-gradient(135deg, #DB2777, #EC4899);
        }

        /* Global Text Styles */
        div[data-testid="stVerticalBlock"] {
            color: var(--text-color) !important;
        }

        p, span, label, div {
            color: var(--text-color) !important;
        }

        /* Markdown Text */
        .stMarkdown p, .stMarkdown span, .stMarkdown div {
            color: var(--text-color) !important;
            font-size: 0.95rem !important;
            line-height: 1.6 !important;
        }

        /* Form Labels */
        .stTextInput label, .stSelectbox label, .stTextArea label {
            color: var(--text-color) !important;
            font-size: 0.95rem !important;
            font-weight: 500 !important;
            margin-bottom: 0.3rem !important;
        }

        /* Input Fields */
        .stTextInput input, .stSelectbox select, .stTextArea textarea {
            color: var(--text-color) !important;
            font-size: 0.95rem !important;
            background: var(--secondary-background-color) !important;
            border: 1px solid rgba(255, 255, 255, 0.1) !important;
            border-radius: 0.5rem !important;
            padding: 0.5rem 1rem !important;
        }

        /* Selectbox Text */
        .stSelectbox > div > div {
            color: var(--text-color) !important;
        }

        /* Main Header */
        .main-header {
            background: var(--purple-gradient);
            padding: 0.1rem;
            border-radius: 0.4rem;
            margin: 0;
            margin-bottom: 0.5rem;
            box-shadow: 0 4px 15px rgba(0, 0, 0, 0.1);
        }

        .main-header h1 {
            color: white !important;
            font-size: 1.1rem !important;
            font-weight: 600 !important;
            margin: 0 !important;
            text-align: center;
            line-height: 1.8 !important;
            text-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
        }

        /* Section Headers */
        h3 {
            color: white !important;
            font-size: 1rem !important;
            font-weight: 600 !important;
            margin: 1rem 0 0.75rem 0 !important;
            padding: 0.4rem 0.8rem !important;
            background: var(--blue-gradient);
            border-radius: 0.4rem;
            display: inline-block;
            box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
        }

        /* Table Styles */
        .stDataFrame {
            color: var(--text-color) !important;
        }

        .stDataFrame td {
            color: var(--text-color) !important;
            font-size: 0.9rem !important;
        }

        .stDataFrame th {
            color: white !important;
            font-size: 0.95rem !important;
            font-weight: 600 !important;
            background: var(--secondary-background-color) !important;
        }

        /* Metric Cards */
        [data-testid="stMetricLabel"] {
            color: var(--secondary-text-color) !important;
            font-size: 0.9rem !important;
            font-weight: 500 !important;
        }

        [data-testid="stMetricValue"] {
            color: white !important;
            font-size: 1.8rem !important;
            font-weight: 600 !important;
            background: var(--green-gradient);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            text-shadow: none !important;
        }

        [data-testid="stMetricDelta"] {
            color: var(--accent-color) !important;
            font-weight: 500 !important;
        }

        /* Activity Items */
        .activity-item {
            color: var(--text-color) !important;
            font-size: 0.9rem !important;
        }

        .activity-item strong {
            color: var(--accent-color) !important;
            font-weight: 600 !important;
        }

        .activity-time {
            color: var(--secondary-text-color) !important;
            font-size: 0.8rem !important;
        }

        /* Buttons */
        .stButton > button {
            color: white !important;
            font-size: 0.95rem !important;
            font-weight: 600 !important;
            background: var(--purple-gradient) !important;
        }

        /* Expander */
        .streamlit-expanderHeader {
            color: var(--text-color) !important;
            font-size: 0.95rem !important;
            font-weight: 500 !important;
        }

        /* Radio Buttons */
        .stRadio label {
            color: var(--text-color) !important;
        }

        /* Checkbox */
        .stCheckbox label {
            color: var(--text-color) !important;
        }

        /* Tabs */
        .stTabs [data-baseweb="tab"] {
            color: var(--text-color) !important;
        }

        /* Sidebar */
        .sidebar .sidebar-content {
            color: var(--text-color) !important;
        }

        /* Placeholder Text */
        ::placeholder {
            color: var(--secondary-text-color) !important;
            opacity: 0.7 !important;
        }

        /* Rest of your existing styles... */
    </style>
    """ 
