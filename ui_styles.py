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
    def __init__(self, shortener):
        self.shortener = shortener

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
            st.markdown('<div class="sidebar-nav">', unsafe_allow_html=True)
            
            st.markdown("### 🎯 Campaign Manager")
            
            selected_page = st.radio(
                "Navigation",
                [
                    "📊 Dashboard",
                    "🔗 Create Campaign",
                    "📈 Analytics",
                    "⚙️ Settings"
                ],
                index=0,
                key="nav",
                label_visibility="collapsed"
            )

            st.markdown("<hr/>", unsafe_allow_html=True)

            # Quick Actions
            st.markdown("""
                <div class="sidebar-section">
                    <h4>Quick Actions</h4>
                </div>
            """, unsafe_allow_html=True)
            
            if st.button("➕ New Campaign", key="new_campaign_btn", use_container_width=True):
                st.session_state['selected_page'] = "🔗 Create Campaign"
                st.rerun()

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
                st.metric(label, value)
