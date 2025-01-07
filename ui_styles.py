def load_ui_styles():
    return """
    <style>
        /* Main theme colors and variables */
        :root {
            --primary: #00ff88;
            --primary-dark: #00cc70;
            --secondary: #1e88e5;
            --background: #0e1117;
            --surface: #1e1e1e;
            --text: #ffffff;
            --text-secondary: rgba(255,255,255,0.7);
            --accent: rgba(0, 255, 136, 0.1);
        }

        /* Sidebar styling */
        [data-testid="stSidebar"] {
            background-color: var(--surface);
            border-right: 1px solid rgba(0,255,136,0.1);
        }

        [data-testid="stSidebar"] .stRadio label {
            color: var(--text) !important;
            font-weight: 500;
            padding: 8px;
            border-radius: 4px;
            transition: all 0.2s;
        }

        [data-testid="stSidebar"] .stRadio label:hover {
            background: rgba(0,255,136,0.1);
        }

        /* Header styling */
        .header-accent {
            background: linear-gradient(135deg, rgba(30,30,30,0.9) 0%, rgba(45,45,45,0.9) 100%);
            padding: 1.5rem;
            border-radius: 12px;
            margin-bottom: 24px;
            border: 1px solid rgba(0, 255, 136, 0.2);
            font-size: 2rem;
            font-weight: 600;
            text-shadow: 0 0 10px rgba(0, 255, 136, 0.3);
            display: flex;
            align-items: center;
            gap: 0.5rem;
        }

        /* Card styling */
        [data-testid="stVerticalBlock"] > [style*="flex-direction: column;"] > [data-testid="stVerticalBlock"] {
            background: linear-gradient(145deg, rgba(30,30,30,0.6) 0%, rgba(30,30,30,0.3) 100%);
            border: 1px solid rgba(0, 255, 136, 0.1);
            padding: 1.5rem;
            border-radius: 12px;
            box-shadow: 0 4px 20px rgba(0,0,0,0.1);
            margin-bottom: 1rem;
            backdrop-filter: blur(10px);
            color: var(--text);
        }

        /* Tab styling */
        .stTabs [data-baseweb="tab-list"] {
            gap: 8px;
            background-color: var(--surface);
            padding: 8px;
            border-radius: 8px;
        }

        .stTabs [data-baseweb="tab"] {
            background-color: transparent !important;
            border: 1px solid rgba(0,255,136,0.1) !important;
            border-radius: 6px !important;
            color: var(--text) !important;
            padding: 8px 16px !important;
        }

        .stTabs [aria-selected="true"] {
            background-color: rgba(0,255,136,0.1) !important;
            border-color: var(--primary) !important;
        }

        /* Button styling */
        .stButton button {
            background: linear-gradient(135deg, var(--primary) 0%, var(--primary-dark) 100%);
            color: var(--background);
            border: none;
            padding: 8px 16px;
            border-radius: 6px;
            font-weight: 600;
            transition: all 0.3s;
        }

        .stButton button:hover {
            transform: translateY(-2px);
            box-shadow: 0 4px 12px rgba(0,255,136,0.2);
        }

        /* Form field styling */
        .stTextInput input,
        .stNumberInput input,
        .stSelectbox select {
            background-color: var(--surface) !important;
            border: 1px solid rgba(0,255,136,0.1) !important;
            border-radius: 6px !important;
            color: var(--text) !important;
            padding: 8px 12px !important;
        }

        /* Metric styling */
        [data-testid="stMetric"] {
            background: linear-gradient(145deg, rgba(0,255,136,0.05) 0%, rgba(30,30,30,0.2) 100%);
            padding: 1.2rem;
            border-radius: 12px;
            border: 1px solid rgba(0, 255, 136, 0.1);
            box-shadow: 0 4px 15px rgba(0,0,0,0.1);
        }

        [data-testid="stMetricValue"] {
            color: var(--primary) !important;
            font-size: 1.8rem !important;
            font-weight: 600 !important;
            text-shadow: 0 0 10px rgba(0, 255, 136, 0.2);
        }

        /* Table styling */
        .stDataFrame {
            background: linear-gradient(145deg, rgba(30,30,30,0.6) 0%, rgba(30,30,30,0.3) 100%);
            border-radius: 12px;
            border: 1px solid rgba(0, 255, 136, 0.1);
            overflow: hidden;
        }

        .stDataFrame th {
            background-color: rgba(0,255,136,0.1) !important;
            color: var(--primary) !important;
            font-weight: 600 !important;
        }

        .stDataFrame td {
            color: var(--text) !important;
            border-bottom: 1px solid rgba(255,255,255,0.05) !important;
        }

        /* Chart styling */
        [data-testid="stChart"] {
            background: linear-gradient(145deg, rgba(30,30,30,0.6) 0%, rgba(30,30,30,0.3) 100%);
            border-radius: 12px;
            border: 1px solid rgba(0, 255, 136, 0.1);
            padding: 1rem;
        }
    </style>
    """ 