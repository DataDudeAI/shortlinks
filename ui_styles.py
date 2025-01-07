def load_ui_styles():
    return """
    <style>
        /* Card-like containers with shadows */
        [data-testid="stVerticalBlock"] > [style*="flex-direction: column;"] > [data-testid="stVerticalBlock"] {
            background-color: white;
            padding: 20px;
            border-radius: 10px;
            box-shadow: 0 4px 6px -1px rgba(0,0,0,0.1), 0 2px 4px -1px rgba(0,0,0,0.06);
            margin-bottom: 24px;
        }
        
        /* Metrics styling */
        [data-testid="stMetric"] {
            background-color: #f8fafc;
            padding: 15px;
            border-radius: 8px;
            border-left: 4px solid #1e88e5;
            box-shadow: 0 2px 4px rgba(0,0,0,0.05);
        }
        
        /* Button styling */
        .stButton button {
            border-radius: 6px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.05);
            transition: all 0.2s ease;
        }
        .stButton button:hover {
            transform: translateY(-2px);
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        }
        
        /* Form fields styling */
        [data-testid="stTextInput"] input {
            border-radius: 6px;
            border: 1px solid #e2e8f0;
            padding: 10px;
        }
        
        /* Dataframe styling */
        [data-testid="stDataFrame"] {
            border-radius: 10px;
            box-shadow: 0 4px 6px -1px rgba(0,0,0,0.1);
            padding: 10px;
        }
        
        /* Tab styling */
        .stTabs [data-baseweb="tab-list"] {
            gap: 8px;
            padding: 0.5rem;
        }
        .stTabs [data-baseweb="tab"] {
            border-radius: 4px;
            padding: 10px 16px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.05);
        }
        
        /* Headers styling */
        h1, h2, h3 {
            color: #1e293b;
            padding: 8px 0;
        }
        
        /* Code block styling */
        pre {
            border-radius: 8px;
            padding: 12px;
            background-color: #f8fafc !important;
            border: 1px solid #e2e8f0;
        }
        
        /* Expander styling */
        .streamlit-expanderHeader {
            border-radius: 8px;
            background-color: #f8fafc;
            padding: 10px;
        }
        
        /* Success/Error message styling */
        .stSuccess, .stError {
            padding: 16px;
            border-radius: 8px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.05);
        }
        
        /* Divider styling */
        hr {
            margin: 24px 0;
            border-color: #e2e8f0;
        }
        
        /* Container hover effect */
        .element-container:hover {
            transform: translateY(-2px);
            transition: transform 0.2s ease;
        }
        
        /* Custom scrollbar */
        ::-webkit-scrollbar {
            width: 10px;
            height: 10px;
        }
        ::-webkit-scrollbar-track {
            background: #f1f1f1;
            border-radius: 5px;
        }
        ::-webkit-scrollbar-thumb {
            background: #888;
            border-radius: 5px;
        }
        ::-webkit-scrollbar-thumb:hover {
            background: #555;
        }
        
        /* Campaign card styling */
        .stMarkdown {
            background-color: white;
            padding: 1rem;
            border-radius: 8px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.05);
            margin-bottom: 1rem;
        }
        
        /* Metric animations */
        @keyframes metric-pulse {
            0% { transform: scale(1); }
            50% { transform: scale(1.02); }
            100% { transform: scale(1); }
        }
        [data-testid="stMetric"]:hover {
            animation: metric-pulse 0.5s ease-in-out;
        }
    </style>
    """ 