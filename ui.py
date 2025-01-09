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
        """Render bar chart for clicks by date"""
        try:
            # Convert daily stats to DataFrame
            df = pd.DataFrame([
                {'date': date, 'clicks': clicks} 
                for date, clicks in daily_stats.items()
            ])
            
            if df.empty:
                return None
            
            # Convert date strings to datetime
            df['date'] = pd.to_datetime(df['date'])
            df = df.sort_values('date')

            # Get last 7 days range
            end_date = df['date'].max()
            start_date = end_date - timedelta(days=6)
            
            # Filter for last 7 days
            df = df[df['date'] >= start_date]

            # Create figure
            fig = go.Figure()

            # Add bar trace
            fig.add_trace(go.Bar(
                x=df['date'],
                y=df['clicks'],
                name='Clicks',
                marker=dict(
                    color='#10B981',
                    opacity=0.9,
                    line=dict(
                        color='#064E3B',
                        width=1
                    )
                ),
                hovertemplate='<b>%{x|%Y-%m-%d}</b><br>Clicks: %{y:,}<extra></extra>'
            ))

            # Update layout
            fig.update_layout(
                title="Daily Clicks (Last 7 Days)",
                plot_bgcolor='rgba(0,0,0,0)',
                paper_bgcolor='rgba(0,0,0,0)',
                margin=dict(l=20, r=20, t=40, b=20),
                showlegend=False,
                bargap=0.3,  # Gap between bars
                xaxis=dict(
                    type='date',
                    showgrid=False,
                    tickformat='%Y-%m-%d',
                    dtick='D1',  # Show every day
                    range=[start_date - timedelta(hours=12), end_date + timedelta(hours=12)],  # Add padding
                    tickangle=-45
                ),
                yaxis=dict(
                    showgrid=True,
                    gridwidth=1,
                    gridcolor='rgba(128,128,128,0.1)',
                    title='Clicks',
                    tickformat=',d',
                    zeroline=False
                ),
                hoverlabel=dict(
                    bgcolor='#132C27',
                    font=dict(color='white')
                )
            )

            # Add stats annotation
            total_clicks = df['clicks'].sum()
            daily_avg = df['clicks'].mean()
            
            fig.add_annotation(
                x=0.02,
                y=0.98,
                xref='paper',
                yref='paper',
                text=f'Total: {total_clicks:,}<br>Daily Avg: {daily_avg:.1f}',
                showarrow=False,
                font=dict(size=14, color='#E2E8F0'),
                bgcolor='#132C27',
                bordercolor='#064E3B',
                borderwidth=1,
                borderpad=4,
                align='left'
            )

            # Add value labels on top of bars
            for i in range(len(df)):
                fig.add_annotation(
                    x=df['date'].iloc[i],
                    y=df['clicks'].iloc[i],
                    text=f"{df['clicks'].iloc[i]:,}",
                    yshift=10,
                    showarrow=False,
                    font=dict(
                        size=12,
                        color='#E2E8F0'
                    )
                )

            return fig
        except Exception as e:
            logger.error(f"Error rendering trend chart: {e}")
            return None
