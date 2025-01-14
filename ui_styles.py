def load_ui_styles():
    return """
    <style>
        /* Enhanced gradient backgrounds */
        .metric-card:nth-child(1) {
            background: linear-gradient(135deg, #FF6B6B, #FF8E8E);
        }
        .metric-card:nth-child(2) {
            background: linear-gradient(135deg, #4ECDC4, #45B7AF);
        }
        .metric-card:nth-child(3) {
            background: linear-gradient(135deg, #96C93D, #7BAA2F);
        }
        .metric-card:nth-child(4) {
            background: linear-gradient(135deg, #A18CD1, #FBC2EB);
        }

        /* Glowing effects on hover */
        .metric-card:hover {
            box-shadow: 0 0 20px rgba(0,0,0,0.15);
            transform: translateY(-5px) scale(1.02);
            transition: all 0.3s ease;
        }

        /* Enhanced activity cards */
        .activity-item {
            border-left: 4px solid;
            animation: slideIn 0.3s ease-out;
        }
        
        .activity-item:nth-child(5n+1) { border-color: #FF6B6B; }
        .activity-item:nth-child(5n+2) { border-color: #4ECDC4; }
        .activity-item:nth-child(5n+3) { border-color: #96C93D; }
        .activity-item:nth-child(5n+4) { border-color: #A18CD1; }
        .activity-item:nth-child(5n+5) { border-color: #FBC2EB; }

        /* Animated stats */
        @keyframes countUp {
            from { opacity: 0; transform: translateY(20px); }
            to { opacity: 1; transform: translateY(0); }
        }

        .stMetric {
            animation: countUp 0.5s ease-out;
        }

        /* Enhanced buttons */
        .stButton button {
            background: linear-gradient(45deg, #FF6B6B, #FF8E8E);
            border: none !important;
            color: white !important;
            padding: 0.6rem 1.2rem !important;
            transition: all 0.3s ease !important;
        }

        .stButton button:hover {
            background: linear-gradient(45deg, #FF8E8E, #FF6B6B);
            transform: translateY(-2px);
            box-shadow: 0 4px 15px rgba(255,107,107,0.4);
        }

        /* Colorful tabs */
        .stTabs [data-baseweb="tab-list"] {
            gap: 2rem;
            background: linear-gradient(90deg, #FF6B6B, #4ECDC4, #96C93D);
            padding: 0.5rem;
            border-radius: 0.5rem;
        }

        .stTabs [data-baseweb="tab"] {
            background: rgba(255,255,255,0.2) !important;
            border-radius: 0.5rem;
            color: white !important;
            transition: all 0.3s ease;
        }

        .stTabs [data-baseweb="tab"]:hover {
            background: rgba(255,255,255,0.3) !important;
            transform: translateY(-2px);
        }

        /* Dashboard cards with gradients */
        .dashboard-card {
            background: white;
            border-radius: 1rem;
            padding: 1.5rem;
            margin: 1rem 0;
            border: 2px solid transparent;
            background-clip: padding-box;
            position: relative;
            overflow: hidden;
        }

        .dashboard-card::before {
            content: '';
            position: absolute;
            top: 0;
            left: 0;
            right: 0;
            bottom: 0;
            border-radius: 1rem;
            padding: 2px;
            background: linear-gradient(45deg, #FF6B6B, #4ECDC4);
            -webkit-mask: linear-gradient(#fff 0 0) content-box, linear-gradient(#fff 0 0);
            mask: linear-gradient(#fff 0 0) content-box, linear-gradient(#fff 0 0);
            -webkit-mask-composite: xor;
            mask-composite: exclude;
        }

        /* Animated progress bars */
        .stProgress > div > div {
            background: linear-gradient(90deg, #FF6B6B, #4ECDC4);
            transition: all 0.3s ease;
        }

        /* Enhanced select boxes */
        .stSelectbox select {
            background: linear-gradient(45deg, #ffffff, #f8f9fa);
            border: 2px solid #e9ecef;
            border-radius: 0.5rem;
            transition: all 0.3s ease;
        }

        .stSelectbox select:hover {
            border-color: #4ECDC4;
            box-shadow: 0 0 0 4px rgba(78,205,196,0.1);
        }

        /* Pulsing effects for real-time data */
        @keyframes pulse {
            0% { transform: scale(1); }
            50% { transform: scale(1.05); }
            100% { transform: scale(1); }
        }

        .real-time-data {
            animation: pulse 2s infinite;
        }
    </style>
    """