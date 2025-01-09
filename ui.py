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
                ["📊 Dashboard", "🔗 Create Campaign", "📈 Analytics", "⚙️ Settings"],
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
        """Render dashboard metrics with colored cards"""
        cols = st.columns(len(metrics))
        for col, (label, value) in zip(cols, metrics.items()):
            with col:
                st.markdown(f"""
                    <div class="metric-card">
                        <div class="metric-value">{value}</div>
                        <div class="metric-label">{label}</div>
                    </div>
                """, unsafe_allow_html=True)
