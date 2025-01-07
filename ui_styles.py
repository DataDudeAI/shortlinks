def load_ui_styles():
    return """
    <style>
        /* Modern Dark Theme Colors */
        :root {
            --background-color: #0B0F19;
            --secondary-background-color: #151B28;
            --card-background: #1A2332;
            --text-color: #FFFFFF;
            --secondary-text-color: #A1A1A1;
            --accent-color: #10B981;
            --accent-hover: #34D399;
            --gradient-start: #059669;
            --gradient-end: #10B981;
            --success-color: #10B981;
            --warning-color: #F59E0B;
            --error-color: #EF4444;
            --border-color: rgba(255, 255, 255, 0.1);
            --hover-color: rgba(16, 185, 129, 0.1);
            --shadow-color: rgba(0, 0, 0, 0.2);
        }

        /* Main Header Styling */
        .main-header {
            background: linear-gradient(135deg, var(--gradient-start), var(--gradient-end));
            padding: 1.5rem;
            border-radius: 1rem;
            margin-bottom: 2rem;
            box-shadow: 0 4px 6px var(--shadow-color);
        }

        .main-header h1 {
            color: white !important;
            font-size: 2.5rem !important;
            font-weight: 700 !important;
            margin: 0 !important;
            text-align: center;
            text-shadow: 2px 2px 4px rgba(0, 0, 0, 0.2);
            -webkit-text-fill-color: white !important;
            letter-spacing: -1px;
        }

        /* Remove header borders and backgrounds */
        [data-testid="stHeader"] {
            background-color: transparent !important;
            border: none !important;
        }

        [data-testid="stToolbar"] {
            display: none;
        }

        .stMarkdown [data-testid="stMarkdownContainer"] > h1,
        .stMarkdown [data-testid="stMarkdownContainer"] > h2,
        .stMarkdown [data-testid="stMarkdownContainer"] > h3 {
            background: none !important;
            -webkit-text-fill-color: var(--text-color) !important;
            font-size: 1.8rem;
            padding: 1rem 0;
            margin-bottom: 1.5rem;
            border: none !important;
        }

        /* Main Container */
        .stApp {
            background: linear-gradient(180deg, var(--background-color) 0%, #0A0F1F 100%);
            color: var(--text-color);
        }

        /* Sidebar */
        [data-testid="stSidebar"] {
            background-color: var(--secondary-background-color);
            border-right: 1px solid var(--border-color);
            box-shadow: 2px 0 5px var(--shadow-color);
        }

        /* Cards and Containers */
        .stMarkdown, .stDataFrame {
            background: var(--card-background);
            padding: 1.5rem;
            border-radius: 1rem;
            border: 1px solid var(--border-color);
            margin-bottom: 1rem;
            box-shadow: 0 4px 6px var(--shadow-color);
            transition: transform 0.2s, box-shadow 0.2s;
        }

        .stMarkdown:hover, .stDataFrame:hover {
            transform: translateY(-2px);
            box-shadow: 0 6px 8px var(--shadow-color);
        }

        /* Metrics */
        [data-testid="stMetric"] {
            background: var(--card-background);
            border: 1px solid var(--border-color);
            padding: 1.5rem;
            border-radius: 1rem;
            box-shadow: 0 4px 6px var(--shadow-color);
            transition: transform 0.2s;
        }

        [data-testid="stMetric"]:hover {
            transform: translateY(-2px);
            border-color: var(--accent-color);
        }

        [data-testid="stMetricValue"] {
            background: linear-gradient(45deg, var(--accent-color), var(--accent-hover));
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            font-size: 2rem !important;
            font-weight: 700 !important;
        }

        [data-testid="stMetricDelta"] {
            color: var(--success-color) !important;
            font-weight: 600 !important;
        }

        /* Buttons */
        .stButton > button {
            background: linear-gradient(45deg, var(--accent-color), var(--accent-hover));
            color: white;
            border: none;
            border-radius: 0.5rem;
            padding: 0.75rem 1.5rem;
            font-weight: 600;
            transition: all 0.3s;
            text-transform: uppercase;
            letter-spacing: 0.5px;
            box-shadow: 0 4px 6px var(--shadow-color);
        }

        .stButton > button:hover {
            transform: translateY(-2px);
            box-shadow: 0 6px 8px var(--shadow-color);
            filter: brightness(110%);
        }

        /* Input Fields */
        .stTextInput > div > div > input,
        .stSelectbox > div > div > select,
        .stNumberInput > div > div > input {
            background-color: var(--card-background) !important;
            color: var(--text-color) !important;
            border: 2px solid var(--border-color) !important;
            border-radius: 0.5rem !important;
            padding: 0.75rem !important;
            transition: all 0.3s !important;
        }

        .stTextInput > div > div > input:focus,
        .stSelectbox > div > div > select:focus,
        .stNumberInput > div > div > input:focus {
            border-color: var(--accent-color) !important;
            box-shadow: 0 0 0 2px rgba(59, 130, 246, 0.2) !important;
        }

        /* Tables */
        .dataframe {
            background-color: var(--card-background);
            color: var(--text-color);
            border-collapse: separate;
            border-spacing: 0;
            border-radius: 1rem;
            overflow: hidden;
            margin: 1rem 0;
            width: 100%;
            box-shadow: 0 4px 6px var(--shadow-color);
        }

        .dataframe th {
            background: linear-gradient(45deg, var(--accent-color), var(--accent-hover));
            color: white;
            font-weight: 600;
            padding: 1rem;
            text-align: left;
            text-transform: uppercase;
            letter-spacing: 0.5px;
        }

        .dataframe td {
            background-color: var(--card-background);
            color: var(--text-color);
            padding: 1rem;
            border-top: 1px solid var(--border-color);
            transition: background-color 0.2s;
        }

        .dataframe tr:hover td {
            background-color: var(--hover-color);
        }

        /* Charts */
        .js-plotly-plot {
            background-color: var(--card-background) !important;
            border-radius: 1rem;
            padding: 1rem;
            box-shadow: 0 4px 6px var(--shadow-color);
        }

        .js-plotly-plot .plotly .main-svg {
            background-color: transparent !important;
        }

        /* Tabs */
        .stTabs [data-baseweb="tab-list"] {
            background-color: var(--secondary-background-color);
            border-radius: 1rem 1rem 0 0;
            padding: 1rem 1rem 0 1rem;
            gap: 10px;
            border-bottom: 1px solid var(--border-color);
        }

        .stTabs [data-baseweb="tab"] {
            color: var(--text-color);
            background-color: transparent;
            border: 2px solid var(--border-color);
            border-radius: 0.5rem;
            padding: 0.75rem 1.5rem;
            font-weight: 500;
            transition: all 0.3s;
        }

        .stTabs [data-baseweb="tab"]:hover {
            border-color: var(--accent-color);
            color: var(--accent-color);
        }

        .stTabs [data-baseweb="tab"][aria-selected="true"] {
            background: linear-gradient(45deg, var(--accent-color), var(--accent-hover));
            color: white;
            border-color: transparent;
            font-weight: 600;
        }

        /* Headers */
        h1, h2, h3, h4, h5, h6 {
            color: var(--text-color);
            font-weight: 700;
            letter-spacing: -0.5px;
            margin-bottom: 1rem;
        }

        h1 {
            font-size: 2.5rem;
            background: linear-gradient(45deg, var(--accent-color), var(--accent-hover));
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
        }

        /* Custom Components */
        .metric-card {
            background: var(--card-background);
            border-radius: 1rem;
            padding: 2rem;
            border: 1px solid var(--border-color);
            margin-bottom: 1rem;
            transition: all 0.3s;
            box-shadow: 0 4px 6px var(--shadow-color);
        }

        .metric-card:hover {
            transform: translateY(-4px);
            border-color: var(--accent-color);
            box-shadow: 0 8px 12px var(--shadow-color);
        }

        /* Scrollbars */
        ::-webkit-scrollbar {
            width: 8px;
            height: 8px;
        }

        ::-webkit-scrollbar-track {
            background: var(--secondary-background-color);
            border-radius: 4px;
        }

        ::-webkit-scrollbar-thumb {
            background: linear-gradient(45deg, var(--accent-color), var(--accent-hover));
            border-radius: 4px;
            transition: all 0.3s;
        }

        ::-webkit-scrollbar-thumb:hover {
            background: var(--accent-hover);
        }

        /* Animations */
        @keyframes fadeIn {
            from { opacity: 0; transform: translateY(10px); }
            to { opacity: 1; transform: translateY(0); }
        }

        .stMarkdown, .stMetric, .dataframe, .metric-card {
            animation: fadeIn 0.5s ease-out;
        }

        /* Success/Error Messages */
        .stSuccess, .stError {
            padding: 1rem;
            border-radius: 0.5rem;
            margin: 1rem 0;
            box-shadow: 0 4px 6px var(--shadow-color);
            display: flex;
            align-items: center;
            gap: 0.5rem;
        }

        .stSuccess {
            background: linear-gradient(45deg, var(--success-color), #34D399);
            color: white;
        }

        .stError {
            background: linear-gradient(45deg, var(--error-color), #F87171);
            color: white;
        }

        /* Enhanced section headers */
        .section-header {
            color: var(--accent-color);
            font-size: 2rem;
            font-weight: 600;
            margin: 2rem 0 1rem 0;
            padding-bottom: 0.5rem;
            border-bottom: 2px solid var(--accent-color);
        }
    </style>
    """ 
