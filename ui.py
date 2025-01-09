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
from ui_styles import get_styles, get_theme_colors

# Define BASE_URL
BASE_URL = "https://shortlinksnandan.streamlit.app"

# Configure logger
logger = logging.getLogger(__name__)

class UI:
    def __init__(self, shortener):
        self.shortener = shortener
        # Apply base styles
        st.markdown(get_styles(), unsafe_allow_html=True)

    def render_header(self):
        """Render the main header"""
        st.markdown("""
            <div class="main-header">
                <h1>Campaign Dashboard</h1>
            </div>
        """, unsafe_allow_html=True)

    def render_sidebar(self):
        """Render the sidebar navigation"""
        with st.sidebar:
            st.markdown("""
                <div class="sidebar-header">
                    <h2>🎯 Campaign Hub</h2>
                </div>
            """, unsafe_allow_html=True)
            
            selected_page = st.radio(
                "Navigation",
                [
                    "📊 Dashboard",
                    "🔗 Create Campaign",
                    "📈 Analytics",
                    "⚙️ Settings"
                ],
                label_visibility="collapsed"
            )

            return selected_page

    def render_page_header(self, title: str):
        """Render page header without extra space"""
        st.markdown(f"""
            <div class="main-header">
                <h1>{title}</h1>
            </div>
        """, unsafe_allow_html=True)

    def render_metrics(self, metrics: dict):
        """Render dashboard metrics"""
        cols = st.columns(len(metrics))
        for col, (label, value) in zip(cols, metrics.items()):
            with col:
                # Use st.metric for built-in metric styling
                st.metric(
                    label=label,
                    value=value,
                    delta="+12" if label == "Active Links" else 
                          "+1.5%" if label == "Total Clicks" else
                          "+0.8%" if label == "Conversion Rate" else
                          "+2" if label == "Active Campaigns" else None,
                    delta_color="normal"
                )
