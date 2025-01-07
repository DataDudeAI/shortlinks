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

        /* Create Campaign Section */
        .create-campaign-form {
            background: var(--card-background);
            padding: 2rem;
            border-radius: 1rem;
            border: 1px solid var(--border-color);
            box-shadow: 0 4px 15px rgba(0, 0, 0, 0.1);
        }

        /* Form Groups */
        .form-group {
            background: var(--secondary-background-color);
            padding: 1.5rem;
            border-radius: 0.8rem;
            margin-bottom: 1.5rem;
            border: 1px solid var(--border-color);
        }

        /* Form Input Fields */
        .stTextInput input, .stSelectbox select {
            background: var(--secondary-background-color) !important;
            color: var(--text-color) !important;
            border: 1px solid var(--border-color) !important;
            border-radius: 0.5rem !important;
            padding: 0.8rem !important;
            font-size: 0.95rem !important;
            transition: all 0.2s ease;
        }

        .stTextInput input:focus, .stSelectbox select:focus {
            border-color: var(--accent-color) !important;
            box-shadow: 0 0 0 2px rgba(16, 185, 129, 0.1) !important;
            transform: translateY(-1px);
        }

        /* Form Labels */
        .stTextInput label, .stSelectbox label {
            color: var(--text-color) !important;
            font-size: 0.95rem !important;
            font-weight: 500 !important;
            margin-bottom: 0.4rem !important;
        }

        /* Section Headers in Form */
        .stForm h3 {
            color: white !important;
            font-size: 1rem !important;
            font-weight: 600 !important;
            padding: 0.5rem 1rem !important;
            background: linear-gradient(135deg, #2563EB, #3B82F6);
            border-radius: 0.5rem;
            margin: 1.5rem 0 1rem 0 !important;
            display: inline-block;
        }

        /* QR Code Section */
        .qr-options {
            background: var(--secondary-background-color);
            padding: 1.5rem;
            border-radius: 0.8rem;
            margin: 1rem 0;
            border: 1px solid var(--border-color);
        }

        /* Color Picker */
        .stColorPicker > label {
            color: var(--text-color) !important;
            font-size: 0.9rem !important;
        }

        /* Slider */
        .stSlider > label {
            color: var(--text-color) !important;
            font-size: 0.9rem !important;
        }

        .stSlider [data-baseweb="slider"] {
            margin-top: 1rem !important;
        }

        /* Submit Button */
        .stForm [data-testid="stFormSubmitButton"] > button {
            background: linear-gradient(135deg, #4F46E5, #7C3AED) !important;
            color: white !important;
            border: none !important;
            padding: 0.8rem 2rem !important;
            font-size: 1rem !important;
            font-weight: 600 !important;
            border-radius: 0.5rem !important;
            box-shadow: 0 4px 10px rgba(0, 0, 0, 0.1);
            transition: all 0.3s ease !important;
            margin-top: 1rem !important;
        }

        .stForm [data-testid="stFormSubmitButton"] > button:hover {
            transform: translateY(-2px);
            box-shadow: 0 6px 15px rgba(0, 0, 0, 0.2);
        }

        /* Success Message */
        .stSuccess {
            background: rgba(16, 185, 129, 0.1) !important;
            color: var(--accent-color) !important;
            border: 1px solid var(--accent-color) !important;
            padding: 1rem !important;
            border-radius: 0.5rem !important;
            margin: 1rem 0 !important;
        }

        /* QR Code Display */
        [data-testid="stImage"] {
            background: white;
            padding: 1.5rem;
            border-radius: 1rem;
            box-shadow: 0 4px 15px rgba(0, 0, 0, 0.1);
            margin: 1rem 0;
            transition: all 0.3s ease;
        }

        [data-testid="stImage"]:hover {
            transform: scale(1.02);
            box-shadow: 0 8px 25px rgba(0, 0, 0, 0.15);
        }

        /* Download Button */
        .stDownloadButton > button {
            background: linear-gradient(135deg, #059669, #10B981) !important;
            color: white !important;
            border: none !important;
            padding: 0.8rem 1.5rem !important;
            font-size: 0.95rem !important;
            font-weight: 600 !important;
            border-radius: 0.5rem !important;
            box-shadow: 0 4px 10px rgba(0, 0, 0, 0.1);
            transition: all 0.3s ease !important;
            margin-top: 0.5rem !important;
        }

        .stDownloadButton > button:hover {
            transform: translateY(-2px);
            box-shadow: 0 6px 15px rgba(0, 0, 0, 0.2);
        }
    </style>
    """ 
