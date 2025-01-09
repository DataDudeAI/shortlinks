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
            st.image(
                "https://via.placeholder.com/150x50?text=Logo",
                use_container_width=True
            )
            
            # Navigation
            selected_page = st.radio(
                "Navigation",
                ["🏠 Dashboard", "🔗 Create Campaign", "📈 Analytics", "⚙️ Settings"],
                label_visibility="collapsed"
            )

            # Add styling for better text visibility
            st.markdown("""
                <style>
                    .stRadio label {
                        color: #1E293B !important;
                    }
                    .stRadio label:hover {
                        color: #10B981 !important;
                    }
                    .stRadio label[data-checked="true"] {
                        color: white !important;
                    }
                </style>
            """, unsafe_allow_html=True)

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
