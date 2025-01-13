import streamlit as st

def load_ui_styles():
    """Load enhanced UI styles with animations and hover effects"""
    return """
        <style>
        /* Card Styles with Enhanced Colors and Hover Effects */
        .stat-card {
            background: linear-gradient(135deg, #ffffff 0%, #f8fafc 100%);
            border-radius: 12px;
            padding: 1.5rem;
            border: 1px solid rgba(226, 232, 240, 0.8);
            box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
            transition: all 0.3s ease;
            position: relative;
            overflow: hidden;
        }
        
        .stat-card:hover {
            transform: translateY(-5px);
            box-shadow: 0 8px 15px -3px rgba(0, 0, 0, 0.1);
            border-color: #0891b2;
        }
        
        .stat-card::before {
            content: '';
            position: absolute;
            top: 0;
            left: 0;
            width: 100%;
            height: 4px;
            background: linear-gradient(90deg, #0891b2, #0ea5e9);
            transform: scaleX(0);
            transition: transform 0.3s ease;
            transform-origin: left;
        }
        
        .stat-card:hover::before {
            transform: scaleX(1);
        }
        
        /* Activity Item with Enhanced Animation */
        .activity-item {
            background: white;
            padding: 1rem;
            border-radius: 10px;
            margin-bottom: 0.75rem;
            border: 1px solid #e2e8f0;
            box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);
            transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
            cursor: pointer;
        }
        
        .activity-item:hover {
            transform: scale(1.02);
            box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
            border-color: #0891b2;
        }
        
        /* Enhanced Button Styles */
        .custom-button {
            background: linear-gradient(135deg, #0891b2 0%, #0ea5e9 100%);
            color: white;
            padding: 0.75rem 1.5rem;
            border-radius: 8px;
            border: none;
            cursor: pointer;
            transition: all 0.3s ease;
            font-weight: 500;
            text-transform: uppercase;
            letter-spacing: 0.5px;
        }
        
        .custom-button:hover {
            transform: translateY(-2px);
            box-shadow: 0 4px 12px rgba(8, 145, 178, 0.3);
        }
        
        /* Dashboard Header with Animation */
        .main-header {
            background: linear-gradient(135deg, #f8fafc 0%, #f1f5f9 100%);
            padding: 2rem;
            border-radius: 12px;
            margin-bottom: 2rem;
            position: relative;
            overflow: hidden;
        }
        
        .main-header::after {
            content: '';
            position: absolute;
            bottom: 0;
            left: 0;
            width: 100%;
            height: 3px;
            background: linear-gradient(90deg, #0891b2, #0ea5e9);
            transform: scaleX(0.8);
            transition: transform 0.3s ease;
        }
        
        .main-header:hover::after {
            transform: scaleX(1);
        }
        
        /* Enhanced Metric Cards */
        .metric-card {
            background: white;
            padding: 1.5rem;
            border-radius: 12px;
            border: 1px solid #e2e8f0;
            transition: all 0.3s ease;
            position: relative;
            overflow: hidden;
        }
        
        .metric-card:hover {
            transform: translateY(-5px);
            box-shadow: 0 8px 16px rgba(0, 0, 0, 0.1);
        }
        
        .metric-card .value {
            font-size: 2rem;
            font-weight: bold;
            color: #0891b2;
            margin: 0.5rem 0;
            transition: color 0.3s ease;
        }
        
        .metric-card:hover .value {
            color: #0ea5e9;
        }
        
        /* Animated Loading States */
        .loading {
            position: relative;
            overflow: hidden;
        }
        
        .loading::after {
            content: '';
            position: absolute;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            background: linear-gradient(
                90deg,
                rgba(255, 255, 255, 0) 0%,
                rgba(255, 255, 255, 0.6) 50%,
                rgba(255, 255, 255, 0) 100%
            );
            animation: shimmer 1.5s infinite;
        }
        
        @keyframes shimmer {
            0% { transform: translateX(-100%); }
            100% { transform: translateX(100%); }
        }
        
        /* Enhanced Table Styles */
        .custom-table {
            border-collapse: separate;
            border-spacing: 0;
            width: 100%;
            border-radius: 8px;
            overflow: hidden;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.05);
        }
        
        .custom-table tr {
            transition: all 0.3s ease;
        }
        
        .custom-table tr:hover {
            background-color: #f8fafc;
            transform: scale(1.01);
        }
        
        /* Sidebar Enhancement */
        .sidebar-nav {
            padding: 1rem;
            background: linear-gradient(180deg, #ffffff 0%, #f8fafc 100%);
            border-radius: 12px;
            margin: 1rem 0;
            transition: all 0.3s ease;
        }
        
        .sidebar-nav:hover {
            box-shadow: 0 4px 12px rgba(0, 0, 0, 0.05);
        }
        </style>
    """

def get_theme_colors(theme='dark'):
    """Get color scheme based on theme"""
    return {
        'light': {
            'background': '#F8FAFC',
            'secondary_background': '#FFFFFF',
            'card_background': '#FFFFFF',
            'text': '#1E293B',
            'secondary_text': '#475569',
        },
        'dark': {
            'background': '#0B0F19',
            'secondary_background': '#151B28',
            'card_background': '#1A2332',
            'text': '#E2E8F0',
            'secondary_text': '#94A3B8',
        }
    }[theme] 
