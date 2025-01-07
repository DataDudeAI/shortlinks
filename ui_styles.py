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

        /* Card-like containers with modern styling */
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

        /* Container hover effect */
        [data-testid="stVerticalBlock"]:hover {
            border-color: rgba(0, 255, 136, 0.2);
            transform: translateY(-2px);
            transition: all 0.3s ease;
        }

        /* Campaign card styling */
        .stMarkdown {
            background: linear-gradient(145deg, rgba(30,30,30,0.6) 0%, rgba(30,30,30,0.3) 100%);
            padding: 1.2rem;
            border-radius: 12px;
            border: 1px solid rgba(0, 255, 136, 0.1);
            box-shadow: 0 4px 15px rgba(0,0,0,0.1);
            margin-bottom: 1rem;
            color: var(--text);
        }

        /* Metrics styling */
        [data-testid="stMetric"] {
            background: linear-gradient(145deg, rgba(0,255,136,0.05) 0%, rgba(30,30,30,0.2) 100%);
            padding: 1.2rem;
            border-radius: 12px;
            border: 1px solid rgba(0, 255, 136, 0.1);
            box-shadow: 0 4px 15px rgba(0,0,0,0.1);
            color: var(--text);
        }

        [data-testid="stMetricValue"] {
            color: var(--primary) !important;
            font-size: 1.8rem !important;
            font-weight: 600 !important;
            text-shadow: 0 0 10px rgba(0, 255, 136, 0.2);
        }

        [data-testid="stMetricDelta"] {
            color: var(--primary) !important;
            font-size: 0.9rem !important;
            background: rgba(0, 255, 136, 0.1);
            padding: 2px 8px;
            border-radius: 4px;
        }

        [data-testid="stMetricLabel"] {
            color: var(--text-secondary) !important;
            font-size: 1rem !important;
            font-weight: 500;
        }

        /* Dataframe/Table styling */
        [data-testid="stDataFrame"] {
            background: linear-gradient(145deg, rgba(30,30,30,0.6) 0%, rgba(30,30,30,0.3) 100%);
            border-radius: 12px;
            padding: 1rem;
            border: 1px solid rgba(0, 255, 136, 0.1);
        }

        .dataframe {
            color: var(--text) !important;
        }

        .dataframe th {
            background: rgba(0, 255, 136, 0.1) !important;
            color: var(--primary) !important;
            padding: 12px !important;
            font-weight: 600 !important;
        }

        .dataframe td {
            color: var(--text) !important;
            padding: 12px !important;
            border-bottom: 1px solid rgba(255, 255, 255, 0.05) !important;
        }

        /* Form fields styling */
        [data-testid="stTextInput"] input,
        [data-testid="stNumberInput"] input,
        .stTextArea textarea {
            background: rgba(30,30,30,0.4) !important;
            border: 1px solid rgba(0, 255, 136, 0.1) !important;
            border-radius: 8px !important;
            color: var(--text) !important;
            padding: 12px !important;
        }

        /* Code block styling */
        pre {
            background: rgba(30,30,30,0.4) !important;
            border: 1px solid rgba(0, 255, 136, 0.1) !important;
            border-radius: 8px !important;
            padding: 1rem !important;
            color: var(--primary) !important;
        }

        /* Expander styling */
        .streamlit-expanderHeader {
            background: linear-gradient(145deg, rgba(30,30,30,0.6) 0%, rgba(30,30,30,0.3) 100%);
            border-radius: 8px;
            color: var(--text) !important;
            padding: 1rem;
            border: 1px solid rgba(0, 255, 136, 0.1);
        }

        .streamlit-expanderContent {
            background: rgba(30,30,30,0.2);
            border-radius: 0 0 8px 8px;
            padding: 1rem;
            color: var(--text);
        }

        /* Keep your existing styles for header-accent, section-header, etc... */
    </style>
    """ 
