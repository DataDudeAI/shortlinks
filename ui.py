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
import plotly.graph_objects as go

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

    def render_trend_chart(self, daily_stats: dict):
        """Render simple line chart for clicks"""
        # Convert daily stats to DataFrame
        df = pd.DataFrame(
            [(date, clicks) for date, clicks in daily_stats.items()],
            columns=['date', 'clicks']
        )
        df['date'] = pd.to_datetime(df['date'])
        df = df.sort_values('date')

        # Create simple line chart
        fig = go.Figure()

        # Add line
        fig.add_trace(go.Scatter(
            x=df['date'],
            y=df['clicks'],
            name='Clicks',
            line=dict(
                color='#10B981',
                width=3,
            ),
            mode='lines+markers',
            marker=dict(
                size=8,
                color='#10B981',
                line=dict(
                    color='#FFFFFF',
                    width=2
                )
            ),
            hovertemplate=(
                '<b>Date:</b> %{x|%B %d}<br>' +
                '<b>Clicks:</b> %{y}<br>' +
                '<extra></extra>'
            )
        ))

        # Update layout
        fig.update_layout(
            title="Daily Clicks",
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            margin=dict(l=20, r=20, t=40, b=20),
            showlegend=False,
            xaxis=dict(
                showgrid=True,
                gridwidth=1,
                gridcolor='rgba(128,128,128,0.1)',
                title=None,
                tickformat='%b %d'
            ),
            yaxis=dict(
                showgrid=True,
                gridwidth=1,
                gridcolor='rgba(128,128,128,0.1)',
                title='Clicks',
                zeroline=False
            ),
            hoverlabel=dict(
                bgcolor='#132C27',
                font=dict(color='white')
            )
        )

        # Add range selector
        fig.update_xaxes(
            rangeslider=dict(visible=True),
            rangeselector=dict(
                buttons=list([
                    dict(count=1, label="1D", step="day", stepmode="backward"),
                    dict(count=7, label="1W", step="day", stepmode="backward"),
                    dict(count=1, label="1M", step="month", stepmode="backward"),
                    dict(step="all", label="All")
                ]),
                bgcolor='#132C27',
                activecolor='#064E3B'
            )
        )

        return fig
