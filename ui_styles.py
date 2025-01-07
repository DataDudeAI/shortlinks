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

        /* Campaign Creation Form */
        [data-testid="stForm"] {
            background: var(--card-background);
            padding: 1.5rem;
            border-radius: 1rem;
            border: 1px solid rgba(255, 255, 255, 0.05);
            box-shadow: 0 4px 15px rgba(0, 0, 0, 0.1);
            margin-bottom: 1rem;
        }

        /* Form Input Fields */
        .stTextInput input, .stSelectbox select, .stTextArea textarea {
            background: var(--secondary-background-color) !important;
            border: 1px solid rgba(255, 255, 255, 0.1) !important;
            border-radius: 0.5rem !important;
            padding: 0.5rem 1rem !important;
            color: white !important;
            transition: all 0.2s ease;
        }

        .stTextInput input:focus, .stSelectbox select:focus, .stTextArea textarea:focus {
            border-color: var(--accent-color) !important;
            box-shadow: 0 0 0 2px rgba(16, 185, 129, 0.2) !important;
        }

        /* Metric Cards */
        [data-testid="stMetric"] {
            background: var(--card-background);
            padding: 1.2rem !important;
            border-radius: 1rem !important;
            border: 1px solid rgba(255, 255, 255, 0.05);
            box-shadow: 0 4px 15px rgba(0, 0, 0, 0.1);
            transition: all 0.3s ease;
        }

        [data-testid="stMetric"]:hover {
            transform: translateY(-3px);
            box-shadow: 0 8px 20px rgba(0, 0, 0, 0.15);
            border-color: var(--accent-color);
            background: linear-gradient(to bottom right, var(--card-background), rgba(16, 185, 129, 0.05));
        }

        [data-testid="stMetricValue"] {
            font-size: 2rem !important;
            font-weight: 600 !important;
            background: var(--green-gradient);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
        }

        [data-testid="stMetricDelta"] {
            color: var(--accent-color) !important;
            background: rgba(16, 185, 129, 0.1);
            padding: 0.2rem 0.6rem;
            border-radius: 1rem;
            font-size: 0.8rem !important;
        }

        /* Analytics Charts */
        [data-testid="stPlotlyChart"] {
            background: var(--card-background);
            border-radius: 1rem;
            padding: 1rem;
            border: 1px solid rgba(255, 255, 255, 0.05);
            box-shadow: 0 4px 15px rgba(0, 0, 0, 0.1);
            transition: all 0.3s ease;
        }

        [data-testid="stPlotlyChart"]:hover {
            transform: translateY(-2px);
            box-shadow: 0 8px 20px rgba(0, 0, 0, 0.15);
            border-color: var(--accent-color);
        }

        /* Activity Cards */
        .activity-item {
            background: var(--card-background);
            padding: 1rem 1.2rem;
            border-radius: 0.8rem;
            margin: 0.6rem 0;
            border: 1px solid rgba(255, 255, 255, 0.05);
            box-shadow: 0 4px 10px rgba(0, 0, 0, 0.1);
            transition: all 0.3s ease;
        }

        .activity-item:hover {
            transform: translateX(4px);
            border-color: var(--accent-color);
            box-shadow: 0 6px 15px rgba(0, 0, 0, 0.15);
            background: linear-gradient(to right, var(--card-background), rgba(16, 185, 129, 0.05));
        }

        /* Campaign Performance Table */
        [data-testid="stDataFrame"] {
            background: var(--card-background);
            border-radius: 1rem;
            border: 1px solid rgba(255, 255, 255, 0.05);
            box-shadow: 0 4px 15px rgba(0, 0, 0, 0.1);
            overflow: hidden;
            margin: 1rem 0;
        }

        .stDataFrame th {
            background: var(--secondary-background-color) !important;
            border-bottom: 2px solid var(--accent-color) !important;
            padding: 0.75rem 1rem !important;
            font-weight: 600 !important;
        }

        /* QR Code Section */
        .qr-section {
            background: var(--card-background);
            padding: 1.5rem;
            border-radius: 1rem;
            border: 1px solid rgba(255, 255, 255, 0.05);
            box-shadow: 0 4px 15px rgba(0, 0, 0, 0.1);
            margin: 1rem 0;
        }

        /* Buttons */
        .stButton > button {
            background: var(--purple-gradient) !important;
            color: white !important;
            border: none !important;
            padding: 0.6rem 1.2rem !important;
            border-radius: 0.5rem !important;
            font-weight: 600 !important;
            box-shadow: 0 4px 10px rgba(0, 0, 0, 0.1);
            transition: all 0.3s ease !important;
        }

        .stButton > button:hover {
            transform: translateY(-2px);
            box-shadow: 0 6px 15px rgba(0, 0, 0, 0.2);
        }

        /* Remove extra spacing */
        [data-testid="stVerticalBlock"] > div:first-child {
            padding-top: 0 !important;
            margin-top: 0 !important;
        }

        .main .block-container {
            padding-top: 0 !important;
            margin-top: 0 !important;
        }

        [data-testid="stVerticalBlock"] {
            gap: 0.5rem !important;
        }

        [data-testid="stMarkdownContainer"] {
            margin: 0 !important;
            padding: 0 !important;
        }
    </style>
    """ 