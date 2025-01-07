def load_ui_styles():
    return """
    <style>
        /* Dark Theme Colors */
        :root {
            --background-color: #0E1117;
            --secondary-background-color: #262730;
            --text-color: #FAFAFA;
            --secondary-text-color: #B0B0B0;
            --accent-color: #FF4B4B;
            --success-color: #00CC66;
            --warning-color: #FFA500;
            --error-color: #FF4B4B;
        }

        /* Main Container */
        .stApp {
            background-color: var(--background-color);
            color: var(--text-color);
        }

        /* Sidebar */
        .css-1d391kg {
            background-color: var(--secondary-background-color);
        }

        /* Cards and Containers */
        .stMarkdown, .stDataFrame {
            background-color: var(--secondary-background-color);
            padding: 1rem;
            border-radius: 0.5rem;
            border: 1px solid rgba(255, 255, 255, 0.1);
        }

        /* Metrics */
        .css-1xarl3l {
            background-color: var(--secondary-background-color);
            border: 1px solid rgba(255, 255, 255, 0.1);
            padding: 1rem;
            border-radius: 0.5rem;
        }

        /* Buttons */
        .stButton > button {
            background-color: var(--accent-color);
            color: white;
            border: none;
            border-radius: 0.3rem;
            padding: 0.5rem 1rem;
            transition: all 0.2s;
        }

        .stButton > button:hover {
            background-color: #FF6B6B;
            box-shadow: 0 0 10px rgba(255, 75, 75, 0.3);
        }

        /* Input Fields */
        .stTextInput > div > div > input,
        .stSelectbox > div > div > select {
            background-color: var(--secondary-background-color);
            color: var(--text-color);
            border: 1px solid rgba(255, 255, 255, 0.2);
        }

        /* Tables */
        .dataframe {
            background-color: var(--secondary-background-color);
            color: var(--text-color);
        }

        .dataframe th {
            background-color: var(--accent-color);
            color: white;
        }

        .dataframe td {
            background-color: var(--secondary-background-color);
            color: var(--text-color);
        }

        /* Charts */
        .js-plotly-plot {
            background-color: var(--secondary-background-color);
        }

        /* Tabs */
        .stTabs [data-baseweb="tab-list"] {
            background-color: var(--secondary-background-color);
            border-radius: 0.5rem 0.5rem 0 0;
        }

        .stTabs [data-baseweb="tab"] {
            color: var(--text-color);
        }

        .stTabs [data-baseweb="tab-panel"] {
            background-color: var(--secondary-background-color);
            border-radius: 0 0 0.5rem 0.5rem;
            padding: 1rem;
        }

        /* Success/Error Messages */
        .stSuccess {
            background-color: var(--success-color);
            color: white;
        }

        .stError {
            background-color: var(--error-color);
            color: white;
        }

        /* Links */
        a {
            color: var(--accent-color);
            text-decoration: none;
        }

        a:hover {
            color: #FF6B6B;
            text-decoration: underline;
        }

        /* Custom Components */
        .metric-card {
            background-color: var(--secondary-background-color);
            border-radius: 0.5rem;
            padding: 1rem;
            border: 1px solid rgba(255, 255, 255, 0.1);
            margin-bottom: 1rem;
        }

        .metric-card h3 {
            color: var(--text-color);
            margin: 0;
        }

        .metric-card p {
            color: var(--secondary-text-color);
            margin: 0.5rem 0 0 0;
        }

        /* Scrollbars */
        ::-webkit-scrollbar {
            width: 10px;
            height: 10px;
        }

        ::-webkit-scrollbar-track {
            background: var(--background-color);
        }

        ::-webkit-scrollbar-thumb {
            background: var(--accent-color);
            border-radius: 5px;
        }

        ::-webkit-scrollbar-thumb:hover {
            background: #FF6B6B;
        }
    </style>
    """ 
