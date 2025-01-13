import streamlit as st

def load_ui_styles():
    return """
    <style>
        /* Dashboard-specific components */
        .dashboard-card {
            transition: transform 0.2s;
            cursor: pointer;
        }
        
        .dashboard-card:hover {
            transform: translateY(-2px);
        }
        
        /* Analytics components */
        .analytics-chart {
            border-radius: 8px;
            padding: 1rem;
            background: var(--background-color);
            box-shadow: 0 2px 4px var(--shadow-color);
        }
        
        /* Campaign components */
        .campaign-list {
            max-height: 600px;
            overflow-y: auto;
            scrollbar-width: thin;
        }
        
        .campaign-item {
            display: flex;
            align-items: center;
            padding: 1rem;
            border-bottom: 1px solid var(--border-color);
            transition: background-color 0.2s;
        }
        
        .campaign-item:hover {
            background-color: rgba(0,0,0,0.02);
        }
        
        /* Navigation components */
        .nav-item {
            display: flex;
            align-items: center;
            padding: 0.75rem 1rem;
            border-radius: 0.375rem;
            transition: background-color 0.2s;
            cursor: pointer;
        }
        
        .nav-item:hover {
            background-color: rgba(0,0,0,0.05);
        }
        
        .nav-item.active {
            background-color: var(--primary-color);
            color: white;
        }
        
        /* Modal components */
        .modal-overlay {
            position: fixed;
            top: 0;
            left: 0;
            right: 0;
            bottom: 0;
            background: rgba(0,0,0,0.5);
            display: flex;
            align-items: center;
            justify-content: center;
            z-index: 1000;
        }
        
        .modal-content {
            background: var(--background-color);
            padding: 2rem;
            border-radius: 0.5rem;
            max-width: 500px;
            width: 90%;
            position: relative;
        }
        
        /* Tooltip components */
        .tooltip {
            position: relative;
            display: inline-block;
        }
        
        .tooltip .tooltip-text {
            visibility: hidden;
            background-color: #333;
            color: white;
            text-align: center;
            padding: 5px;
            border-radius: 6px;
            position: absolute;
            z-index: 1;
            bottom: 125%;
            left: 50%;
            transform: translateX(-50%);
            opacity: 0;
            transition: opacity 0.3s;
        }
        
        .tooltip:hover .tooltip-text {
            visibility: visible;
            opacity: 1;
        }
        
        /* Loading animations */
        .loading-spinner {
            width: 40px;
            height: 40px;
            border: 4px solid #f3f3f3;
            border-top: 4px solid var(--primary-color);
            border-radius: 50%;
            animation: spin 1s linear infinite;
        }
        
        @keyframes spin {
            0% { transform: rotate(0deg); }
            100% { transform: rotate(360deg); }
        }
        
        /* Form animations */
        .form-input:focus {
            transform: scale(1.02);
            transition: transform 0.2s;
        }
        
        /* Success/Error animations */
        .alert {
            padding: 1rem;
            border-radius: 0.375rem;
            margin-bottom: 1rem;
            opacity: 0;
            animation: fadeIn 0.3s forwards;
        }
        
        .alert-success {
            background-color: #10B981;
            color: white;
        }
        
        .alert-error {
            background-color: #EF4444;
            color: white;
        }
        
        @keyframes fadeIn {
            from { opacity: 0; transform: translateY(-10px); }
            to { opacity: 1; transform: translateY(0); }
        }
    </style>
    
    <script>
        // UI interaction enhancements
        document.addEventListener('DOMContentLoaded', function() {
            // Add smooth scrolling
            document.querySelectorAll('a[href^="#"]').forEach(anchor => {
                anchor.addEventListener('click', function (e) {
                    e.preventDefault();
                    document.querySelector(this.getAttribute('href')).scrollIntoView({
                        behavior: 'smooth'
                    });
                });
            });
            
            // Add ripple effect to buttons
            document.querySelectorAll('.btn-primary').forEach(button => {
                button.addEventListener('click', function(e) {
                    let ripple = document.createElement('div');
                    ripple.classList.add('ripple');
                    this.appendChild(ripple);
                    let rect = this.getBoundingClientRect();
                    ripple.style.left = e.clientX - rect.left + 'px';
                    ripple.style.top = e.clientY - rect.top + 'px';
                    setTimeout(() => ripple.remove(), 600);
                });
            });
        });
    </script>
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
