def load_ui_styles():
    return """
    <style>
        /* Main container and background */
        .stApp {
            background: linear-gradient(180deg, #0e1117 0%, #1a1a1a 100%);
        }

        /* Neon accent effects */
        .neon-accent {
            text-shadow: 0 0 10px #00ff88, 0 0 20px #00ff88, 0 0 30px #00ff88;
        }

        /* Header styling */
        h1, h2, h3 {
            color: #00ff88;
            font-weight: 600;
            text-shadow: 0 0 10px rgba(0,255,136,0.3);
        }

        /* Metrics cards */
        [data-testid="stMetric"] {
            background: rgba(38, 39, 48, 0.8);
            backdrop-filter: blur(10px);
            border: 1px solid rgba(0, 255, 136, 0.2);
            border-radius: 10px;
            padding: 20px;
            box-shadow: 0 4px 20px rgba(0, 255, 136, 0.1);
            transition: all 0.3s ease;
        }

        [data-testid="stMetric"]:hover {
            transform: translateY(-5px);
            border-color: #00ff88;
            box-shadow: 0 8px 25px rgba(0, 255, 136, 0.2);
        }

        [data-testid="stMetricValue"] {
            color: #00ff88 !important;
            font-size: 28px !important;
        }

        /* Form styling */
        [data-testid="stForm"] {
            background: rgba(38, 39, 48, 0.6);
            backdrop-filter: blur(10px);
            border: 1px solid rgba(255, 255, 255, 0.1);
            border-radius: 15px;
            padding: 25px;
            box-shadow: 0 4px 20px rgba(0, 0, 0, 0.2);
        }

        /* Input fields */
        [data-testid="stTextInput"] input {
            background: rgba(30, 30, 30, 0.6);
            border: 1px solid rgba(0, 255, 136, 0.2);
            border-radius: 8px;
            color: white;
            padding: 12px 16px;
            transition: all 0.2s ease;
        }

        [data-testid="stTextInput"] input:focus {
            border-color: #00ff88;
            box-shadow: 0 0 0 2px rgba(0, 255, 136, 0.2);
            background: rgba(30, 30, 30, 0.8);
        }

        /* Buttons */
        .stButton button {
            background: linear-gradient(45deg, #00ff88, #00cc70) !important;
            color: #0e1117 !important;
            border: none !important;
            border-radius: 8px;
            padding: 12px 24px;
            font-weight: 600;
            transition: all 0.3s ease;
            text-shadow: none;
            box-shadow: 0 4px 15px rgba(0, 255, 136, 0.2);
        }

        .stButton button:hover {
            transform: translateY(-2px);
            box-shadow: 0 8px 25px rgba(0, 255, 136, 0.3);
            filter: brightness(1.1);
        }

        /* Table/DataFrame styling */
        [data-testid="stDataFrame"] {
            background: rgba(38, 39, 48, 0.6);
            backdrop-filter: blur(10px);
            border: 1px solid rgba(0, 255, 136, 0.1);
            border-radius: 12px;
            overflow: hidden;
        }

        .dataframe {
            border: none !important;
        }

        .dataframe th {
            background: rgba(0, 255, 136, 0.1) !important;
            color: #00ff88 !important;
            font-weight: 600;
            padding: 15px !important;
            border-bottom: 1px solid rgba(0, 255, 136, 0.2) !important;
        }

        .dataframe td {
            color: #ffffff;
            padding: 12px 15px !important;
            border-bottom: 1px solid rgba(255, 255, 255, 0.05) !important;
        }

        /* Tabs styling */
        .stTabs [data-baseweb="tab-list"] {
            background: rgba(38, 39, 48, 0.6);
            backdrop-filter: blur(10px);
            border-radius: 10px;
            padding: 5px;
            gap: 5px;
            border: 1px solid rgba(0, 255, 136, 0.1);
        }

        .stTabs [data-baseweb="tab"] {
            background-color: transparent !important;
            border-radius: 8px;
            color: #ffffff;
            transition: all 0.2s ease;
            padding: 10px 20px;
        }

        .stTabs [data-baseweb="tab"][aria-selected="true"] {
            background: rgba(0, 255, 136, 0.2) !important;
            color: #00ff88;
        }

        /* Selectbox */
        [data-testid="stSelectbox"] {
            background: rgba(30, 30, 30, 0.6);
            border: 1px solid rgba(0, 255, 136, 0.2);
            border-radius: 8px;
            color: white;
        }

        /* Code blocks */
        pre {
            background: rgba(30, 30, 30, 0.6) !important;
            border: 1px solid rgba(0, 255, 136, 0.2);
            border-radius: 8px;
            color: #00ff88;
            padding: 15px;
        }

        /* Custom scrollbar */
        ::-webkit-scrollbar {
            width: 8px;
            height: 8px;
        }

        ::-webkit-scrollbar-track {
            background: rgba(30, 30, 30, 0.6);
        }

        ::-webkit-scrollbar-thumb {
            background: rgba(0, 255, 136, 0.2);
            border-radius: 4px;
        }

        ::-webkit-scrollbar-thumb:hover {
            background: rgba(0, 255, 136, 0.4);
        }

        /* Success/Error messages */
        .stSuccess {
            background: rgba(0, 255, 136, 0.1);
            border: 1px solid rgba(0, 255, 136, 0.2);
            color: #00ff88;
            border-radius: 8px;
        }

        .stError {
            background: rgba(255, 68, 68, 0.1);
            border: 1px solid rgba(255, 68, 68, 0.2);
            color: #ff4444;
            border-radius: 8px;
        }

        /* UTM Parameters section */
        [data-testid="stExpander"] {
            background: rgba(38, 39, 48, 0.6);
            border: 1px solid rgba(0, 255, 136, 0.1);
            border-radius: 10px;
            overflow: hidden;
        }

        .streamlit-expanderHeader {
            background: rgba(0, 255, 136, 0.1);
            color: #00ff88;
            padding: 15px;
        }
    </style>
    """ 
