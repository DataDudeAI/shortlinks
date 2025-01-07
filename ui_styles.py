def load_ui_styles():
    return """
    <style>
        /* Dark theme enhancements */
        .stApp {
            background-color: #0e1117;
        }

        /* Card styling with dark theme */
        [data-testid="stVerticalBlock"] > [style*="flex-direction: column;"] > [data-testid="stVerticalBlock"] {
            background-color: #1e1e1e;
            padding: 20px;
            border-radius: 10px;
            box-shadow: 0 4px 15px rgba(0,0,0,0.2);
            margin-bottom: 24px;
            border: 1px solid #2d2d2d;
        }
        
        /* Enhanced metrics styling */
        [data-testid="stMetric"] {
            background-color: #262730;
            padding: 15px;
            border-radius: 8px;
            border-left: 4px solid #00ff88;
            box-shadow: 0 2px 4px rgba(0,0,0,0.2);
            transition: all 0.3s ease;
        }
        
        [data-testid="stMetric"]:hover {
            transform: translateY(-2px);
            box-shadow: 0 4px 8px rgba(0,0,0,0.3);
            border-left: 4px solid #00ff88;
        }
        
        /* Modern form styling */
        [data-testid="stTextInput"] input {
            background-color: #262730;
            border: 1px solid #404040;
            color: white;
            border-radius: 6px;
            padding: 12px;
            transition: all 0.2s ease;
        }
        
        [data-testid="stTextInput"] input:focus {
            border-color: #00ff88;
            box-shadow: 0 0 0 2px rgba(0,255,136,0.2);
        }

        /* Button enhancements */
        .stButton button {
            background-color: #262730 !important;
            color: white !important;
            border: 1px solid #404040 !important;
            border-radius: 6px;
            padding: 10px 20px;
            transition: all 0.2s ease;
        }
        
        .stButton button:hover {
            transform: translateY(-2px);
            box-shadow: 0 4px 8px rgba(0,0,0,0.2);
            border-color: #00ff88 !important;
            background-color: #2d2d2d !important;
        }

        /* Tab styling */
        .stTabs [data-baseweb="tab-list"] {
            gap: 8px;
            background-color: #1e1e1e;
            padding: 0.5rem;
            border-radius: 8px;
            border: 1px solid #2d2d2d;
        }
        
        .stTabs [data-baseweb="tab"] {
            background-color: #262730 !important;
            border-radius: 4px;
            color: white;
            padding: 10px 16px;
            transition: all 0.2s ease;
        }
        
        .stTabs [data-baseweb="tab"]:hover {
            background-color: #2d2d2d !important;
            border-color: #00ff88;
        }

        /* Headers with modern gradient */
        h1, h2, h3 {
            background: linear-gradient(90deg, #00ff88, #00bfff);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            padding: 8px 0;
        }

        /* Code block enhancement */
        pre {
            background-color: #262730 !important;
            border: 1px solid #404040;
            border-radius: 8px;
            padding: 12px;
            color: #00ff88;
        }

        /* Table/DataFrame styling */
        [data-testid="stDataFrame"] {
            background-color: #1e1e1e;
            border-radius: 10px;
            padding: 10px;
            border: 1px solid #2d2d2d;
        }

        /* Success/Error message styling */
        .stSuccess, .stError {
            background-color: #262730;
            color: white;
            padding: 16px;
            border-radius: 8px;
            border-left: 4px solid #00ff88;
        }

        .stError {
            border-left-color: #ff4444;
        }

        /* Custom scrollbar */
        ::-webkit-scrollbar {
            width: 8px;
            height: 8px;
        }
        
        ::-webkit-scrollbar-track {
            background: #1e1e1e;
            border-radius: 4px;
        }
        
        ::-webkit-scrollbar-thumb {
            background: #404040;
            border-radius: 4px;
        }
        
        ::-webkit-scrollbar-thumb:hover {
            background: #4d4d4d;
        }

        /* Recent links table enhancement */
        .dataframe {
            background-color: #262730;
            border-radius: 8px;
            border: 1px solid #404040;
        }
        
        .dataframe th {
            background-color: #1e1e1e;
            color: #00ff88;
            padding: 12px !important;
        }
        
        .dataframe td {
            padding: 12px !important;
            border-color: #404040 !important;
        }

        /* Selectbox styling */
        [data-testid="stSelectbox"] {
            background-color: #262730;
            border-radius: 6px;
            border: 1px solid #404040;
        }

        /* Form container */
        [data-testid="stForm"] {
            background-color: #262730;
            padding: 20px;
            border-radius: 10px;
            border: 1px solid #404040;
            box-shadow: 0 4px 15px rgba(0,0,0,0.2);
        }
    </style>
    """ 
