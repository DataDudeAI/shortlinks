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
        """Render enhanced sidebar navigation"""
        with st.sidebar:
            # Clean, modern header
            st.markdown("""
                <div style='text-align: left; padding: 1.5rem 1rem; border-bottom: 1px solid rgba(0,0,0,0.1)'>
                    <div style='font-size: 1.2rem; font-weight: 600; color: #1E293B;'>
                        🎯 Campaign Hub
                    </div>
                </div>
            """, unsafe_allow_html=True)

            # Navigation styling
            st.markdown("""
                <style>
                    section[data-testid="stSidebar"] > div {
                        background-color: #FFFFFF;
                    }
                    
                    .stRadio [role='radiogroup'] {
                        gap: 0.5rem;
                    }
                    
                    .stRadio label {
                        background: transparent;
                        padding: 0.75rem 1rem;
                        border-radius: 0.5rem;
                        border: 1px solid rgba(0,0,0,0.1);
                        color: #1E293B !important;
                        width: 100%;
                        transition: all 0.2s ease;
                    }
                    
                    .stRadio label:hover {
                        background: rgba(16, 185, 129, 0.05);
                        border-color: #10B981;
                    }
                    
                    .stRadio label[data-checked="true"] {
                        background: #10B981 !important;
                        border-color: #10B981;
                        color: white !important;
                    }
                </style>
            """, unsafe_allow_html=True)

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
                    <h4 style='color: #1E293B;'>Quick Actions</h4>
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
