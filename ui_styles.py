def load_ui_styles():
    return """
    <style>
        /* Enhanced Metric Cards with Border Color Change */
        .metric-card {
            background: linear-gradient(145deg, #ffffff, #f8fafc);
            border: 2px solid transparent;
            border-radius: 1rem;
            padding: 1.5rem;
            color: #1a202c;
            transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1);
            box-shadow: 0 10px 20px rgba(0, 0, 0, 0.1);
            margin-bottom: 1rem;
            position: relative;
            overflow: hidden;
            transform: translateY(0);
            backdrop-filter: blur(10px);
        }

        .metric-card:nth-child(1) {
            background: linear-gradient(145deg, #ffffff, #f0fdf4);
            border-left: 4px solid #10B981;
        }

        .metric-card:nth-child(2) {
            background: linear-gradient(145deg, #ffffff, #eff6ff);
            border-left: 4px solid #3B82F6;
        }

        .metric-card:nth-child(3) {
            background: linear-gradient(145deg, #ffffff, #faf5ff);
            border-left: 4px solid #8B5CF6;
        }

        .metric-card:nth-child(4) {
            background: linear-gradient(145deg, #ffffff, #fff7ed);
            border-left: 4px solid #F59E0B;
        }

        .metric-card:hover {
            transform: translateY(-10px);
            box-shadow: 0 20px 30px rgba(0, 0, 0, 0.15);
        }

        .metric-card:nth-child(1):hover {
            border-color: #10B981;
        }

        .metric-card:nth-child(2):hover {
            border-color: #3B82F6;
        }

        .metric-card:nth-child(3):hover {
            border-color: #8B5CF6;
        }

        .metric-card:nth-child(4):hover {
            border-color: #F59E0B;
        }

        /* Enhanced Metric Card Content */
        .metric-card .metric-title {
            font-size: 1.1rem;
            font-weight: 600;
            margin-bottom: 0.75rem;
            color: #4B5563;
            text-transform: uppercase;
            letter-spacing: 0.5px;
            display: flex;
            align-items: center;
            gap: 0.5rem;
        }

        .metric-card .metric-icon {
            font-size: 1.5rem;
            line-height: 1;
        }

        .metric-card .metric-value {
            font-size: 2.5rem;
            font-weight: 700;
            color: #1a202c;
            margin: 0.75rem 0;
            display: flex;
            align-items: baseline;
            gap: 0.5rem;
        }

        .metric-card .metric-value .unit {
            font-size: 1rem;
            color: #6B7280;
            font-weight: 500;
        }

        /* Enhanced Action Buttons */
        .action-button {
            display: inline-flex;
            align-items: center;
            gap: 0.5rem;
            padding: 0.75rem 1.5rem;
            border-radius: 0.5rem;
            font-weight: 600;
            font-size: 0.875rem;
            transition: all 0.3s ease;
            cursor: pointer;
            text-decoration: none;
            border: none;
            background: white;
            color: #1a202c;
            box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);
        }

        .action-button.primary {
            background: linear-gradient(145deg, #10B981, #059669);
            color: white;
        }

        .action-button.secondary {
            background: linear-gradient(145deg, #3B82F6, #2563EB);
            color: white;
        }

        .action-button:hover {
            transform: translateY(-2px);
            box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
        }

        /* Button Icons */
        .button-icon {
            font-size: 1.25rem;
            display: inline-flex;
            align-items: center;
            justify-content: center;
        }

        /* Dashboard Action Buttons */
        .dashboard-actions {
            display: flex;
            gap: 1rem;
            margin: 1.5rem 0;
        }

        .dashboard-actions .action-button {
            flex: 1;
            justify-content: center;
            text-align: center;
            padding: 1rem;
            border-radius: 0.75rem;
            background: white;
            border: 1px solid #e5e7eb;
            transition: all 0.3s ease;
        }

        .dashboard-actions .action-button:hover {
            background: linear-gradient(145deg, #f8fafc, #ffffff);
            border-color: #10B981;
            transform: translateY(-3px);
            box-shadow: 0 8px 16px rgba(0, 0, 0, 0.1);
        }

        /* Enhanced Activity Cards */
        .activity-card {
            background: white;
            border-radius: 1rem;
            padding: 1.5rem;
            margin-bottom: 1rem;
            transition: all 0.3s ease;
            border: 1px solid rgba(226, 232, 240, 0.8);
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.05);
            position: relative;
            overflow: hidden;
        }

        .activity-card:hover {
            transform: translateY(-5px);
            box-shadow: 0 12px 20px rgba(0, 0, 0, 0.1);
            border-color: #10B981;
        }

        .activity-card .activity-title {
            font-size: 1.1rem;
            font-weight: 600;
            color: #1a202c;
            margin-bottom: 0.75rem;
            display: flex;
            align-items: center;
            gap: 0.75rem;
        }

        .activity-card .activity-meta {
            display: flex;
            flex-wrap: wrap;
            gap: 1rem;
            color: #64748b;
            font-size: 0.9rem;
            margin-bottom: 0.75rem;
            padding: 0.5rem;
            background: #f8fafc;
            border-radius: 0.5rem;
        }

        .activity-card .activity-details {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
            gap: 1rem;
            margin-top: 0.75rem;
            padding-top: 0.75rem;
            border-top: 1px solid #e2e8f0;
        }

        .activity-card .detail-item {
            display: flex;
            align-items: center;
            gap: 0.5rem;
            color: #475569;
            font-size: 0.875rem;
        }

        .activity-card .activity-time {
            color: #94a3b8;
            font-size: 0.875rem;
            position: absolute;
            top: 1rem;
            right: 1rem;
            background: #f8fafc;
            padding: 0.25rem 0.75rem;
            border-radius: 1rem;
        }

        /* Tab Styling */
        .stTabs [data-baseweb="tab-list"] {
            gap: 1rem;
            background: white;
            padding: 0.5rem;
            border-radius: 0.5rem;
            box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);
        }

        .stTabs [data-baseweb="tab"] {
            border-radius: 0.5rem;
            padding: 0.5rem 1rem;
            transition: all 0.2s ease;
        }

        .stTabs [data-baseweb="tab"]:hover {
            background: #f1f5f9;
        }

        /* Enhanced Table Styling */
        .stDataFrame {
            background: white;
            border-radius: 0.5rem;
            padding: 1rem;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.07);
            transition: all 0.3s ease;
        }
        
        .stDataFrame:hover {
            box-shadow: 0 8px 15px rgba(0, 0, 0, 0.1);
            transform: translateY(-2px);
        }

        /* Graph Container Enhancement */
        .element-container:has([data-testid="stPlotlyChart"]) {
            background: white;
            border-radius: 1rem;
            padding: 1rem;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.07);
            margin-bottom: 1rem;
            transition: all 0.3s ease;
        }

        .element-container:has([data-testid="stPlotlyChart"]):hover {
            box-shadow: 0 8px 15px rgba(0, 0, 0, 0.1);
            transform: translateY(-2px);
        }

        /* Keep existing styles below */
    </style>
    """