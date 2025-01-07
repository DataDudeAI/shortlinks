import streamlit as st
import pandas as pd
from typing import Dict, Any, List
from datetime import datetime, timedelta
import io
import plotly.express as px
import qrcode
from PIL import Image
import json
import uuid
from io import BytesIO
import base64
import logging
from ui_styles import load_ui_styles

# Define BASE_URL
BASE_URL = "https://shortlinksnandan.streamlit.app"

# Configure logger
logger = logging.getLogger(__name__)

class UI:
    def __init__(self, url_shortener):
        """Initialize UI with URL shortener instance"""
        self.url_shortener = url_shortener

    def render_header(self):
        """Render the main header"""
        st.markdown("""
            <div class="header-accent">
                <span>🎯</span>
                <span style="background: linear-gradient(135deg, #00ff88 0%, #00bfff 100%); 
                         -webkit-background-clip: text;
                         -webkit-text-fill-color: transparent;
                         font-weight: 700;">
                    Campaign Dashboard
                </span>
            </div>
        """, unsafe_allow_html=True)

    def render_sidebar(self):
        """Render the sidebar navigation"""
        with st.sidebar:
            st.markdown("### 🎯 Campaign Manager")
            return st.radio(
                "Navigation",
                ["📊 Dashboard", "🔗 Campaign Creator", "📈 Analytics", "⚙️ Settings"],
                index=0
            )

    def render_metrics(self, active_campaigns, total_clicks):
        """Render the metrics row"""
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("🔗 Active Campaigns", 
                     len(active_campaigns),
                     f"+{len(active_campaigns)}")
        
        with col2:
            st.metric("👆 Total Clicks", 
                     f"{total_clicks:,}", 
                     f"+{total_clicks}")
        
        with col3:
            avg_clicks = total_clicks / len(active_campaigns) if active_campaigns else 0
            st.metric("📊 Avg. Clicks/Campaign", 
                     f"{avg_clicks:.1f}",
                     "+0.8%")
        
        with col4:
            recent_clicks = self.url_shortener.db.get_recent_clicks_count(hours=24)
            st.metric("🎯 Recent Activity", 
                     f"{recent_clicks:,}", 
                     f"+{recent_clicks}")

    def render_campaign_filters(self):
        """Render campaign filters"""
        col1, col2, col3 = st.columns([2,1,1])
        with col1:
            search = st.text_input("🔍 Search", placeholder="Search campaigns...")
        with col2:
            status = st.selectbox("Status", ["All", "Active", "Inactive"])
        with col3:
            sort_by = st.selectbox("Sort by", ["Created", "Clicks", "Campaign Name"])
        return search, status, sort_by
