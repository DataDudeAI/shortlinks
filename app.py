import streamlit as st
from database import Database
from ui import UI
import validators
import string
import random
from urllib.parse import urlparse, parse_qs, urlencode
import logging
from typing import Optional, Dict, Any
from datetime import datetime, timedelta
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import json
from ui_styles import load_ui_styles
from organization import Organization
from streamlit.components.v1 import html
from streamlit.runtime.scriptrunner import add_script_run_ctx
import qrcode
from io import BytesIO
from PIL import Image
from streamlit.runtime.scriptrunner import get_script_run_ctx
import os
import time
from auth import Auth
from styles import get_styles
from ui_config import setup_page
from google_analytics import GoogleAnalytics
from user_journey_tracker import UserJourneyTracker, JourneyEventType
from dotenv import load_dotenv

# Load environment variables at startup
load_dotenv()

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Must be the first Streamlit command
st.set_page_config(
    page_title="Campaign Dashboard",
    page_icon="🎯",
    layout="wide",
    initial_sidebar_state="collapsed",
    menu_items={
        'Get Help': 'https://github.com/DataDudeAI/shortlinks',
        'Report a bug': "https://github.com/DataDudeAI/shortlinks/issues",
        'About': "# Campaign Dashboard\nA powerful URL shortener and campaign management tool."
    }
)

# Add near the top of your app, after st.set_page_config
st.markdown("""
    <script>
        window.addEventListener('message', function(e) {
            if (e.data.type === 'client_info') {
                window.client_detected_info = e.data;
            }
        });
    </script>
""", unsafe_allow_html=True)

# At the start of your app, after st.set_page_config
setup_page()

BASE_URL = "https://shortlinksnandan.streamlit.app/"  # For local development

CAMPAIGN_TYPES = {
    "Social Media": "🔵",
    "Email": "📧",
    "Paid Ads": "💰",
    "Blog": "📝",
    "Affiliate": "🤝",
    "Other": "🔗"
}

CAMPAIGN_FEATURES = {
    "UTM Builder": "🎯",
    "A/B Testing": "🔄",
    "QR Codes": "📱",
    "Link Retargeting": "🎪",
    "Custom Domains": "🌐",
    "Deep Links": "🔗"
}

CAMPAIGN_METRICS = {
    "Clicks": "👆",
    "Unique Visitors": "👥",
    "Conversion Rate": "📈",
    "Bounce Rate": "↩️",
    "Avg. Time": "⏱️",
    "ROI": "💰"
}

INDIAN_STATES = [
    "Andhra Pradesh",
    "Arunachal Pradesh",
    "Assam",
    "Bihar",
    "Chhattisgarh",
    "Goa",
    "Gujarat",
    "Haryana",
    "Himachal Pradesh",
    "Jharkhand",
    "Karnataka",
    "Kerala",
    "Madhya Pradesh",
    "Maharashtra",
    "Manipur",
    "Meghalaya",
    "Mizoram",
    "Nagaland",
    "Odisha",
    "Punjab",
    "Rajasthan",
    "Sikkim",
    "Tamil Nadu",
    "Telangana",
    "Tripura",
    "Uttar Pradesh",
    "Uttarakhand",
    "West Bengal",
    "Delhi",
    "Jammu and Kashmir",
    "Ladakh",
    "Puducherry",
    "Andaman and Nicobar Islands",
    "Chandigarh",
    "Dadra and Nagar Haveli and Daman and Diu",
    "Lakshadweep"
]

class URLShortener:
    def __init__(self):
        """Initialize URL shortener with database connection"""
        try:
            # Use existing database instance instead of creating new one
            self.db = st.session_state.db
            self.organization = Organization(self.db)
            logger.info("URLShortener initialized successfully")
        except Exception as e:
            logger.error(f"Error initializing URLShortener: {str(e)}", exc_info=True)
            raise
        self.ui = UI(self)

    def generate_short_code(self, length=6):
        """Generate a unique short code"""
        characters = string.ascii_letters + string.digits
        while True:
            code = ''.join(random.choice(characters) for _ in range(length))
            if not self.db.get_url_info(code):
                return code

    def create_short_url(self, url: str, campaign_name: str, campaign_type: str = None, utm_params: dict = None) -> str:
        """Create a new short URL"""
        try:
            # Validate URL
            if not validators.url(url):
                raise ValueError("Invalid URL format")

            # Create short URL using database method
            short_code = self.db.create_short_url(
                url=url,
                campaign_name=campaign_name,
                campaign_type=campaign_type,
                utm_params=utm_params
            )
            
            logger.info(f"Created short URL for {url}: {short_code}")
            return short_code

        except Exception as e:
            logger.error(f"Error creating short URL: {str(e)}")
            raise

    def handle_redirect(self, short_code: str):
        """Handle URL redirection"""
        logger.info(f"Attempting to redirect short_code: {short_code}")
        url_info = self.db.get_url_info(short_code)
        
        if url_info:
            original_url = url_info['original_url']
            logger.info(f"Redirecting to: {original_url}")
            
            # Track click before redirect
            self.db.increment_clicks(short_code)
            
            # Use JavaScript for immediate redirect with analytics parameters
            html = f"""
                <html>
                <head>
                    <title>Redirecting...</title>
                    <script>
                        // Capture basic analytics
                        var analyticsData = {{
                            userAgent: navigator.userAgent,
                            language: navigator.language,
                            platform: navigator.platform,
                            screenSize: window.screen.width + 'x' + window.screen.height
                        }};
                        
                        // Store analytics data in query params
                        var url = new URL("{original_url}");
                        url.searchParams.append('user_agent', analyticsData.userAgent);
                        url.searchParams.append('ref', document.referrer);
                        
                        // Redirect with analytics data
                        window.location.href = url.toString();
                    </script>
                    <meta http-equiv="refresh" content="0;url={original_url}">
                </head>
                <body>
                    <p>Redirecting to {original_url}...</p>
                    <p>Click <a href="{original_url}">here</a> if not redirected automatically.</p>
                </body>
                </html>
            """
            st.markdown(html, unsafe_allow_html=True)
            return True
        else:
            st.error("Invalid or expired link")
            st.markdown(f"[← Back to Campaign Dashboard]({BASE_URL})")
            return False

    def render_campaign_dashboard(self):
        """Enhanced campaign management dashboard"""
        st.title("🚀 Campaign Management")
        
        # Top-level metrics
        metrics = st.columns(4)
        with metrics[0]:
            st.metric("Active Campaigns", len(self.db.get_all_urls()), "↑2")
        with metrics[1]:
            total_clicks = sum(url['total_clicks'] for url in self.db.get_all_urls())
            st.metric("Total Clicks", f"{total_clicks:,}", "↑15%")
        with metrics[2]:
            st.metric("Conversion Rate", "4.2%", "↑0.8%")
        with metrics[3]:
            st.metric("ROI", "$1,245", "↑23%")

        # Campaign Management Tabs
        management_tabs = st.tabs(["📊 Overview", "⚙️ Settings", "📈 Analytics"])
        
        with management_tabs[0]:
            # Active Campaigns Table
            st.markdown("### 📈 Active Campaigns")
            self.render_active_campaigns()
            
        with management_tabs[1]:
            # Settings Section
            st.markdown("### ⚙️ Campaign Settings")
            col1, col2 = st.columns(2)
            with col1:
                st.selectbox("Default UTM Source", ["facebook", "twitter", "linkedin"])
                st.selectbox("Default Campaign Type", list(CAMPAIGN_TYPES.keys()))
                st.text_input("Custom Domain", placeholder="links.yourdomain.com")
            with col2:
                st.checkbox("Auto-generate QR Codes")
                st.checkbox("Enable Link Retargeting")
                st.number_input("Default Link Expiry (days)", value=30)
                
        with management_tabs[2]:
            # Analytics Section
            st.markdown("### 📊 Campaign Analytics")
            
            # Analytics filters
            col1, col2 = st.columns(2)
            with col1:
                date_range = st.date_input("Date Range", [])
            with col2:
                campaign_filter = st.multiselect("Filter Campaigns", 
                                               [c.get('campaign_name') for c in self.db.get_all_urls()])
            
            # Analytics metrics
            metrics_cols = st.columns(3)
            with metrics_cols[0]:
                st.metric("Total Clicks", total_clicks)
            with metrics_cols[1]:
                st.metric("Conversion Rate", "4.2%")
            with metrics_cols[2]:
                st.metric("Avg. Time on Page", "2m 34s")
                
            # Analytics charts
            chart_cols = st.columns(2)
            with chart_cols[0]:
                st.markdown("#### Click Distribution")
                # Add your click distribution chart here
                
            with chart_cols[1]:
                st.markdown("#### Traffic Sources")
                # Add your traffic sources chart here

    def render_active_campaigns(self):
        """Display active campaigns in a modern table view"""
        campaigns = self.db.get_all_urls()
        
        if not campaigns:
            st.info("No active campaigns yet. Create your first campaign above!")
            return

        # Filters and search
        col1, col2, col3 = st.columns([2,1,1])
        with col1:
            search = st.text_input("🔍 Search", placeholder="Search campaigns...")
        with col2:
            status_filter = st.selectbox("Status", ["All", "Active", "Inactive"])
        with col3:
            sort_by = st.selectbox("Sort by", ["Created", "Clicks", "Campaign Name"])

        # Create DataFrame for campaigns
        df = pd.DataFrame([
            {
                'Campaign Name': c.get('campaign_name', c['short_code']),
                'Original URL': c['original_url'],
                'Short URL': f"{BASE_URL}?r={c['short_code']}",
                'Created': datetime.strptime(c['created_at'], '%Y-%m-%d %H:%M:%S').strftime('%Y-%m-%d'),
                'Total Clicks': c['total_clicks'],
                'Status': 'Active',
                'Actions': c['short_code']
            } for c in campaigns
        ])

        # Apply filters and sorting
        if search:
            df = df[df['Campaign Name'].str.contains(search, case=False)]
        if sort_by == "Clicks":
            df = df.sort_values('Total Clicks', ascending=False)
        elif sort_by == "Campaign Name":
            df = df.sort_values('Campaign Name')
        else:
            df = df.sort_values('Created', ascending=False)

        # Display table
        st.dataframe(
            df,
            column_config={
                "Campaign Name": st.column_config.TextColumn("Campaign Name", width="medium"),
                "Short URL": st.column_config.LinkColumn("Short URL", width="medium"),
                "Total Clicks": st.column_config.NumberColumn("Clicks", format="%d"),
                "Created": st.column_config.DateColumn("Created", format="MMM DD, YYYY"),
                "Status": st.column_config.TextColumn("Status", width="small")
            },
            hide_index=True,
            use_container_width=True
        )

        # Action buttons for each campaign
        for _, row in df.iterrows():
            cols = st.columns([1,1,1,1])
            with cols[0]:
                if st.button("📊 Analytics", key=f"stats_{row['Actions']}"):
                    st.json(self.db.get_campaign_stats(row['Actions']))
            with cols[1]:
                if st.button("✏️ Edit", key=f"edit_{row['Actions']}"):
                    st.session_state.editing_campaign = row['Actions']
            with cols[2]:
                if st.button("🔗 Copy", key=f"copy_{row['Actions']}"):
                    st.code(row['Short URL'])
            with cols[3]:
                if st.button("🗑️ Delete", key=f"del_{row['Actions']}"):
                    if self.db.delete_campaign(row['Actions']):
                        st.success("Deleted!")
                        st.rerun()

    def render_campaign_editor(self, campaign: Dict[str, Any]):
        """Render campaign editing interface"""
        st.subheader(f"Edit Campaign: {campaign.get('campaign_name', campaign['short_code'])}")
        
        with st.form(key=f"edit_campaign_{campaign['short_code']}"):
            campaign_name = st.text_input("Campaign Name", value=campaign.get('campaign_name', ''))
            campaign_type = st.selectbox("Campaign Type", 
                                       list(CAMPAIGN_TYPES.keys()),
                                       index=list(CAMPAIGN_TYPES.keys()).index(campaign.get('campaign_type', 'Other')))
            
            # UTM Parameters
            st.markdown("### UTM Parameters")
            col1, col2 = st.columns(2)
            with col1:
                utm_source = st.text_input("Source", value=campaign.get('utm_source', ''))
                utm_medium = st.text_input("Medium", value=campaign.get('utm_medium', ''))
            with col2:
                utm_campaign = st.text_input("Campaign", value=campaign.get('utm_campaign', ''))
                utm_content = st.text_input("Content", value=campaign.get('utm_content', ''))
            
            # Additional settings
            expiry_date = st.date_input("Expiry Date", 
                                       value=datetime.strptime(campaign.get('expiry_date', '2099-12-31'), '%Y-%m-%d') if campaign.get('expiry_date') else None)
            
            notes = st.text_area("Notes", value=campaign.get('notes', ''))
            tags = st.text_input("Tags (comma-separated)", value=','.join(campaign.get('tags', [])))
            
            if st.form_submit_button("Update Campaign"):
                update_data = {
                    'campaign_name': campaign_name,
                    'campaign_type': campaign_type,
                    'utm_source': utm_source,
                    'utm_medium': utm_medium,
                    'utm_campaign': utm_campaign,
                    'utm_content': utm_content,
                    'expiry_date': expiry_date.strftime('%Y-%m-%d'),
                    'notes': notes,
                    'tags': tags
                }
                
                if self.db.update_campaign(campaign['short_code'], update_data):
                    st.success("Campaign updated successfully!")
                    st.rerun()
                else:
                    st.error("Failed to update campaign")

    def create_campaign_url(self, form_data: dict) -> Optional[str]:
        """Create a new campaign URL"""
        try:
            url = form_data['url']
            campaign_name = form_data['campaign_name']
            
            logger.info(f"Starting campaign creation process...")
            logger.info(f"URL: {url}")
            logger.info(f"Campaign Name: {campaign_name}")
            
            # Clean and validate URL
            if not url.startswith(('http://', 'https://')):
                url = 'https://' + url
                logger.info(f"Modified URL: {url}")

            # Generate short code
            short_code = form_data.get('custom_code') or self.generate_short_code()
            logger.info(f"Generated short code: {short_code}")
            
            # Prepare UTM parameters
            utm_params = {
                'utm_source': form_data.get('utm_source'),
                'utm_medium': form_data.get('utm_medium'),
                'utm_campaign': form_data.get('utm_campaign'),
                'utm_content': form_data.get('utm_content'),
                'utm_term': form_data.get('utm_term')
            }
            
            # Filter out empty UTM parameters
            utm_params = {k: v for k, v in utm_params.items() if v}
            logger.info(f"UTM parameters: {utm_params}")
            
            # Add UTM parameters to URL if any exist
            if utm_params:
                parsed_url = urlparse(url)
                existing_params = parse_qs(parsed_url.query)
                all_params = {**existing_params, **utm_params}
                new_query = urlencode(all_params, doseq=True)
                url = parsed_url._replace(query=new_query).geturl()
                logger.info(f"Final URL with UTM parameters: {url}")
            
            # Save to database
            logger.info("Attempting to save to database...")
            success = self.db.save_campaign_url(
                url=url,
                short_code=short_code,
                campaign_name=campaign_name,
                campaign_type=form_data.get('campaign_type'),
                utm_params=utm_params
            )
            
            if success:
                logger.info(f"Successfully created campaign '{campaign_name}' with short code: {short_code}")
                return short_code
            else:
                logger.error("Database save operation failed")
                return None
            
        except Exception as e:
            logger.error(f"Error creating campaign URL: {str(e)}", exc_info=True)
            return None

    def render_demographics(self, short_code: str):
        """Render demographic analytics"""
        st.subheader("📊 Visitor Demographics")
        
        # Get demographic data
        demo_data = self.db.get_demographics(short_code)
        
        col1, col2 = st.columns(2)
        with col1:
            # Country distribution
            st.markdown("### Geographic Distribution")
            country_data = pd.DataFrame(demo_data['countries'].items(), 
                                      columns=['Country', 'Visits'])
            fig = px.choropleth(country_data, 
                               locations='Country', 
                               locationmode='country names',
                               color='Visits',
                               title='Visitor Locations')
            st.plotly_chart(fig, use_container_width=True)
            
        with col2:
            # Device breakdown
            st.markdown("### Device Types")
            device_data = pd.DataFrame(demo_data['devices'].items(), 
                                     columns=['Device', 'Count'])
            fig = px.pie(device_data, values='Count', names='Device',
                        title='Device Distribution')
            st.plotly_chart(fig, use_container_width=True)
        
        # Browser and OS data
        col1, col2 = st.columns(2)
        with col1:
            st.markdown("### Browsers")
            browser_data = pd.DataFrame(demo_data['browsers'].items(),
                                      columns=['Browser', 'Count'])
            fig = px.bar(browser_data, x='Browser', y='Count',
                        title='Browser Usage')
            st.plotly_chart(fig, use_container_width=True)
            
        with col2:
            st.markdown("### Operating Systems")
            os_data = pd.DataFrame(demo_data['os'].items(),
                                 columns=['OS', 'Count'])
            fig = px.bar(os_data, x='OS', y='Count',
                        title='OS Distribution')
            st.plotly_chart(fig, use_container_width=True)

    def render_click_heatmap(self, short_code: str):
        """Render click heatmap visualization"""
        st.subheader("🎯 Click Heatmap")
        
        # Get click coordinate data
        click_data = self.db.get_click_coordinates(short_code)
        
        if click_data:
            # Create heatmap using plotly
            fig = go.Figure(data=go.Heatmap(
                x=click_data['x'],
                y=click_data['y'],
                colorscale='Viridis'
            ))
            
            fig.update_layout(
                title='Click Distribution Heatmap',
                xaxis_title='X Coordinate',
                yaxis_title='Y Coordinate',
                height=400
            )
            
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No click data available for heatmap visualization")

    def render_recent_links(self):
        """Display the most recently created links"""
        st.subheader("🕒 Recently Created Links")
        
        # Get recent links from database (last 5)
        recent_links = self.db.get_recent_links(limit=5)
        
        if not recent_links:
            st.info("No links created yet. Create your first campaign above!")
            return
        
        # Create columns for the metrics overview
        total_clicks = sum(link['total_clicks'] for link in recent_links)
        
        metrics_col1, metrics_col2 = st.columns(2)
        with metrics_col1:
            st.metric("Total Clicks (Recent)", total_clicks)
        with metrics_col2:
            st.metric("Recent Links", len(recent_links))  # Changed from unique visitors
        
        # Display recent links in a modern table
        df = pd.DataFrame([
            {
                'Campaign': link.get('campaign_name', link['short_code']),
                'Short URL': f"{BASE_URL}?r={link['short_code']}",
                'Created': datetime.strptime(link['created_at'], '%Y-%m-%d %H:%M:%S').strftime('%Y-%m-%d %H:%M'),
                'Clicks': link['total_clicks'],
                'Last Click': self.db.get_last_click_date(link['short_code']).strftime('%Y-%m-%d %H:%M') if self.db.get_last_click_date(link['short_code']) else "Never"
            } for link in recent_links
        ])
        
        st.dataframe(
            df,
            column_config={
                "Campaign": st.column_config.TextColumn("Campaign", width="medium"),
                "Short URL": st.column_config.LinkColumn("Short URL", width="medium"),
                "Created": st.column_config.DatetimeColumn("Created", format="D MMM, HH:mm"),
                "Clicks": st.column_config.NumberColumn("Clicks", format="%d"),
                "Last Click": st.column_config.DatetimeColumn("Last Activity", format="D MMM, HH:mm")
            },
            hide_index=True,
            use_container_width=True
        )

    def render_analytics_dashboard(self):
        """Render enhanced analytics dashboard with detailed insights"""
        
        # Filters Section with better styling
        with st.expander("🔍 Filter Analytics", expanded=False):
            filter_col1, filter_col2, filter_col3 = st.columns(3)
            
            with filter_col1:
                # Date Range Filter (optional)
                use_date_filter = st.checkbox("Filter by Date", value=False)
                if use_date_filter:
                    date_range = st.date_input(
                        "Select Date Range",
                        value=(datetime.now() - timedelta(days=30), datetime.now()),
                        max_value=datetime.now(),
                        help="Select date range for analysis"
                    )
                else:
                    date_range = None
            
            with filter_col2:
                # Campaign Filter (optional)
                use_campaign_filter = st.checkbox("Filter by Campaigns", value=False)
                if use_campaign_filter:
                    campaigns = [c.get('campaign_name') for c in self.db.get_all_urls()]
                    selected_campaigns = st.multiselect(
                        "Select Campaigns",
                        campaigns,
                        placeholder="Choose campaigns",
                        help="Filter by specific campaigns"
                    )
                else:
                    selected_campaigns = None
            
            with filter_col3:
                # State Filter (optional)
                use_state_filter = st.checkbox("Filter by States", value=False)
                if use_state_filter:
                    selected_states = st.multiselect(
                        "Select States",
                        INDIAN_STATES,
                        placeholder="Choose states",
                        help="Filter by geographic location"
                    )
                else:
                    selected_states = None

        # Get analytics data based on filters
        analytics_data = self.db.get_analytics_summary(
            start_date=date_range[0] if use_date_filter and date_range else None,
            end_date=date_range[1] if use_date_filter and date_range else None,
            campaigns=selected_campaigns if use_campaign_filter else None,
            states=selected_states if use_state_filter else None
        )

        # Show active filters if any
        active_filters = []
        if use_date_filter and date_range:
            active_filters.append(f"📅 Date: {date_range[0].strftime('%Y-%m-%d')} to {date_range[1].strftime('%Y-%m-%d')}")
        if use_campaign_filter and selected_campaigns:
            active_filters.append(f"🎯 Campaigns: {len(selected_campaigns)} selected")
        if use_state_filter and selected_states:
            active_filters.append(f"📍 States: {len(selected_states)} selected")
        
        if active_filters:
            st.markdown("**Active Filters:** " + " | ".join(active_filters))

        # Key Metrics Section
        st.markdown("### 📈 Key Performance Metrics")
        
        metrics_col1, metrics_col2, metrics_col3, metrics_col4 = st.columns(4)
        with metrics_col1:
            st.metric(
                "Total Clicks",
                analytics_data.get('total_clicks', 0),
                help="Total number of clicks"
            )
        with metrics_col2:
            st.metric(
                "Unique Visitors",
                analytics_data.get('unique_visitors', 0),
                help="Number of unique visitors"
            )
        with metrics_col3:
            st.metric(
                "Active Days",
                analytics_data.get('active_days', 0),
                help="Days with recorded activity"
            )
        with metrics_col4:
            engagement = analytics_data.get('engagement_rate', 0)
            st.metric(
                "Engagement Rate",
                f"{engagement:.1f}%",
                help="Unique visitors / Total clicks"
            )

        # Trends Analysis Section
        st.markdown("### 📊 Performance Analysis")
        
        trend_tab1, trend_tab2 = st.tabs(["📈 Click Trends", "🗺️ Geographic Distribution"])
        
        with trend_tab1:
            if analytics_data.get('daily_stats'):
                df_daily = pd.DataFrame(list(analytics_data['daily_stats'].items()), 
                                      columns=['Date', 'Clicks'])
                df_daily['7_Day_MA'] = df_daily['Clicks'].rolling(window=7).mean()
                
                fig = go.Figure()
                fig.add_trace(go.Scatter(
                    x=df_daily['Date'],
                    y=df_daily['Clicks'],
                    name='Daily Clicks',
                    mode='lines',
                    line=dict(color='#0891b2')
                ))
                fig.add_trace(go.Scatter(
                    x=df_daily['Date'],
                    y=df_daily['7_Day_MA'],
                    name='7-Day Average',
                    line=dict(color='#f59e0b', dash='dash')
                ))
                fig.update_layout(
                    title='Click Trends',
                    xaxis_title='Date',
                    yaxis_title='Clicks',
                    hovermode='x unified'
                )
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.info("No click data available for the selected filters")

        with trend_tab2:
            if analytics_data.get('state_stats'):
                df_state = pd.DataFrame(list(analytics_data['state_stats'].items()),
                                      columns=['State', 'Visits'])
                df_state = df_state.sort_values('Visits', ascending=True)
                
                fig = px.bar(
                    df_state,
                    x='Visits',
                    y='State',
                    orientation='h',
                    title='Geographic Distribution',
                    color='Visits',
                    color_continuous_scale='Viridis'
                )
                fig.update_layout(height=400)
                st.plotly_chart(fig, use_container_width=True)
                
                # State metrics table
                st.markdown("#### State-wise Metrics")
                df_state['Percentage'] = (df_state['Visits'] / df_state['Visits'].sum() * 100)
                st.dataframe(
                    df_state,
                    column_config={
                        "State": "State",
                        "Visits": st.column_config.NumberColumn("Visits", format="%d"),
                        "Percentage": st.column_config.NumberColumn("% of Total", format="%.1f%%")
                    },
                    hide_index=True,
                    use_container_width=True
                )
            else:
                st.info("No geographic data available for the selected filters")

        # Campaign Performance Section
        st.markdown("### 🎯 Campaign Performance")
        
        if analytics_data.get('campaign_stats'):
            df_campaigns = pd.DataFrame(analytics_data['campaign_stats'])
            st.dataframe(
                df_campaigns,
                column_config={
                    "campaign_name": "Campaign",
                    "total_clicks": st.column_config.NumberColumn("Total Clicks"),
                    "unique_visitors": st.column_config.NumberColumn("Unique Visitors"),
                    "conversion_rate": st.column_config.NumberColumn("Conversion Rate", format="%.2f%%"),
                    "avg_time_on_page": "Avg. Time",
                    "bounce_rate": st.column_config.NumberColumn("Bounce Rate", format="%.2f%%")
                },
                hide_index=True,
                use_container_width=True
            )
        else:
            st.info("No campaign data available for the selected filters")

        # Campaign Performance Metrics - Now in 3 columns with cards
        st.markdown("#### Campaign Insights")
        insight_cols = st.columns(3)
        
        with insight_cols[0]:
            avg_time = stats.get('avg_time', 0)
            st.markdown(f"""
                <div class="metric-card">
                    <div class="metric-title">
                        <span class="metric-icon">⏱️</span>
                        Engagement
                    </div>
                    <div class="metric-value">
                        {avg_time:.1f}
                        <span class="unit">seconds</span>
                    </div>
                    <div class="metric-delta positive">+12% vs last month</div>
                </div>
            """, unsafe_allow_html=True)

        with insight_cols[1]:
            bounce_rate = stats.get('bounce_rate', 0)
            st.markdown(f"""
                <div class="metric-card">
                    <div class="metric-title">
                        <span class="metric-icon">↩️</span>
                        Bounce Rate
                    </div>
                    <div class="metric-value">
                        {bounce_rate:.1f}
                        <span class="unit">%</span>
                    </div>
                    <div class="metric-delta negative">-5% vs last month</div>
                </div>
            """, unsafe_allow_html=True)

        with insight_cols[2]:
            total_clicks = stats.get('total_clicks', 0)
            impressions = stats.get('impressions', 1)
            conversion_rate = (total_clicks / max(1, impressions)) * 100
            st.markdown(f"""
                <div class="metric-card">
                    <div class="metric-title">
                        <span class="metric-icon">🎯</span>
                        Conversion Rate
                    </div>
                    <div class="metric-value">
                        {conversion_rate:.1f}
                        <span class="unit">%</span>
                    </div>
                    <div class="metric-delta positive">+15% vs last month</div>
                </div>
            """, unsafe_allow_html=True)

        # Device Analytics and Campaign Distribution
        st.markdown("### 📱 Analytics Overview")
        
        # First row - Device and Browser stats
        device_cols = st.columns(2)
        with device_cols[0]:
            # Combined Device and Browser Stats
            if stats.get('device_stats') and stats.get('browser_stats'):
                # Create tabs for different views
                device_tabs = st.tabs(["📱 Devices", "🌐 Browsers"])
                
                with device_tabs[0]:
                    device_df = pd.DataFrame(list(stats['device_stats'].items()), 
                                        columns=['Device', 'Count'])
                    fig = px.pie(
                        device_df,
                        values='Count',
                        names='Device',
                        title='Device Distribution',
                        color_discrete_sequence=['#10B981', '#3B82F6', '#8B5CF6', '#F59E0B'],
                        hole=0.4
                    )
                    fig.update_traces(textposition='outside', textinfo='percent+label')
                    fig.update_layout(
                        showlegend=True,
                        height=400,
                        margin=dict(t=30, b=0, l=0, r=0)
                    )
                    st.plotly_chart(fig, use_container_width=True)
                
                with device_tabs[1]:
                    browser_df = pd.DataFrame(list(stats['browser_stats'].items()),
                                            columns=['Browser', 'Count'])
                    fig = px.pie(
                        browser_df,
                        values='Count',
                        names='Browser',
                        title='Browser Distribution',
                        color_discrete_sequence=['#3B82F6', '#8B5CF6', '#F59E0B', '#10B981'],
                        hole=0.4
                    )
                    fig.update_traces(textposition='outside', textinfo='percent+label')
                    fig.update_layout(
                        showlegend=True,
                        height=400,
                        margin=dict(t=30, b=0, l=0, r=0)
                    )
                    st.plotly_chart(fig, use_container_width=True)
            else:
                st.info("No device/browser data available yet")

        with device_cols[1]:
            # Campaign Performance Metrics
            st.markdown("#### Campaign Insights")
            
            # Engagement Metrics as regular metrics
            st.metric(
                "Avg. Time on Page",
                f"{stats.get('avg_time', 0):.1f}s",
                delta="+12%",
                help="Average time users spend on landing pages"
            )
            st.metric(
                "Bounce Rate",
                f"{stats.get('bounce_rate', 0):.1f}%",
                delta="-5%",
                delta_color="inverse",
                help="Percentage of single-page visits"
            )
            st.metric(
                "CTR",
                f"{(stats.get('total_clicks', 0) / max(1, stats.get('impressions', 1)) * 100):.1f}%",
                delta="+8%",
                help="Click-through rate"
            )
            st.metric(
                "Conversion Rate",
                f"{stats.get('conversion_rate', 0):.1f}%",
                delta="+15%",
                help="Percentage of visitors who complete desired actions"
            )

        # Second row - Campaign Distribution and Trends
        trend_cols = st.columns(2)
        with trend_cols[0]:
            # Campaign Type Distribution
            campaign_type_query = """
                SELECT 
                    campaign_type,
                    COUNT(*) as count,
                    SUM(total_clicks) as total_clicks
                FROM urls
                GROUP BY campaign_type
            """
            campaign_type_stats = pd.DataFrame(shortener.db.execute_query(campaign_type_query))
            
            if not campaign_type_stats.empty:
                fig = px.pie(
                    campaign_type_stats,
                    values='total_clicks',  # Changed to total_clicks for better insight
                    names='campaign_type',
                    title='Campaign Performance by Type',
                    color_discrete_sequence=['#10B981', '#3B82F6', '#8B5CF6', '#F59E0B', '#EC4899', '#6366F1'],
                    hole=0.4
                )
                fig.update_traces(textposition='outside', textinfo='percent+label')
                fig.update_layout(
                    showlegend=True,
                    height=400,
                    margin=dict(t=30, b=0, l=0, r=0)
                )
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.info("No campaign data available")

        with trend_cols[1]:
            # Traffic Source Analysis
            st.markdown("#### Traffic Sources")
            traffic_data = {
                'Source': ['Direct', 'Social', 'Email', 'Referral', 'Organic'],
                'Visits': [stats.get('direct_visits', 120), 
                          stats.get('social_visits', 80),
                          stats.get('email_visits', 60),
                          stats.get('referral_visits', 40),
                          stats.get('organic_visits', 30)]
            }
            traffic_df = pd.DataFrame(traffic_data)
            fig = px.bar(
                traffic_df,
                x='Source',
                y='Visits',
                title='Traffic Distribution by Source',
                color='Source',
                color_discrete_sequence=['#10B981', '#3B82F6', '#8B5CF6', '#F59E0B', '#EC4899']
            )
            fig.update_layout(
                showlegend=False,
                height=400,
                margin=dict(t=30, b=0, l=0, r=0)
            )
            st.plotly_chart(fig, use_container_width=True)

        # Recent Activity at the very end
        st.markdown("### 📊 Recent Activity")
        activity_cols = st.columns([3, 1])
        with activity_cols[0]:
            if stats['recent_activities']:
                for activity in stats['recent_activities']:
                    st.markdown(f"""
                        <div class="activity-card">
                            <div class="activity-title">
                                <span class="activity-icon">🔗</span>
                                {activity.get('campaign_name', 'Unknown Campaign')}
                            </div>
                            <div class="activity-meta">
                                <span>📱 {activity.get('device_type', 'Unknown')}</span>
                                <span>📍 {activity.get('state', 'Unknown')}</span>
                                <span>🌐 {activity.get('browser', 'Unknown')}</span>
                                <span>🖥️ {activity.get('os', 'Unknown')}</span>
                            </div>
                            <div class="activity-details">
                                <div class="detail-item">
                                    <span>⏱️</span>
                                    <span>Time on Page: {activity.get('time_on_page', '0')}s</span>
                                </div>
                                <div class="detail-item">
                                    <span>🔄</span>
                                    <span>Return Visitor: {'Yes' if activity.get('is_return_visitor') else 'No'}</span>
                                </div>
                                <div class="detail-item">
                                    <span>📈</span>
                                    <span>Conversion: {activity.get('converted', 'No')}</span>
                                </div>
                            </div>
                            <div class="activity-time">
                                {activity.get('clicked_at', 'Unknown time')}
                            </div>
                        </div>
                    """, unsafe_allow_html=True)
            else:
                st.info("No recent activity to show")

    def render_recent_activity(self, activities):
        """Render recent campaign activities with enhanced styling"""
        st.markdown("### 📊 Recent Activity")
        
        for activity in activities:
            st.markdown(f"""
                <div class="activity-item">
                    <div class="activity-icon">🔗</div>
                    <div class="activity-content">
                        <div class="activity-title">{activity['campaign_name']}</div>
                        <div class="activity-meta">
                            <span class="activity-time">{activity['clicked_at']}</span>
                            <span class="activity-state">{activity['state']}</span>
                            <span>{activity['device_type']}</span>
                        </div>
                    </div>
                </div>
            """, unsafe_allow_html=True)

            

    def render_campaign_manager(self):
        """Render the campaign manager with full management capabilities"""
        st.markdown("### 📊 Campaign Manager")
        
        # Get all campaigns
        campaigns = self.db.get_all_urls()
        
        if not campaigns:
            st.info("No campaigns yet. Create your first campaign to get started!")
            return
        
        # Create DataFrame for campaign data
        df = pd.DataFrame(campaigns)
        
        # Convert datetime strings to datetime objects
        df['created_at'] = pd.to_datetime(df['created_at'])
        df['last_clicked'] = pd.to_datetime(df['last_clicked'])
        
        # Add short URL column
        df['short_url'] = df['short_code'].apply(lambda x: f"{BASE_URL}?r={x}")
        
        # Add filters
        col1, col2, col3 = st.columns(3)
        with col1:
            campaign_type_filter = st.multiselect(
                "Campaign Type",
                list(CAMPAIGN_TYPES.keys()),
                placeholder="Filter by type"
            )
        with col2:
            status_filter = st.multiselect(
                "Status",
                ["Active", "Inactive"],
                placeholder="Filter by status"
            )
        with col3:
            search = st.text_input("Search campaigns", placeholder="Search by name...")
        
        # Apply filters
        filtered_df = df.copy()
        if campaign_type_filter:
            filtered_df = filtered_df[filtered_df['campaign_type'].isin(campaign_type_filter)]
        if status_filter:
            filtered_df = filtered_df[filtered_df['is_active'] == ('Active' in status_filter)]
        if search:
            filtered_df = filtered_df[filtered_df['campaign_name'].str.contains(search, case=False)]
        
        # Configure columns
        columns_config = {
            "campaign_name": st.column_config.TextColumn(
                "Campaign Name",
                width="medium",
                help="Name of the campaign"
            ),
            "campaign_type": st.column_config.SelectboxColumn(
                "Type",
                width="small",
                options=list(CAMPAIGN_TYPES.keys()),
                help="Campaign type"
            ),
            "short_url": st.column_config.LinkColumn(
                "Short URL",
                width="medium",
                help="Click to copy or visit"
            ),
            "original_url": st.column_config.LinkColumn(
                "Original URL",
                width="medium"
            ),
            "total_clicks": st.column_config.NumberColumn(
                "Clicks",
                width="small",
                help="Total number of clicks",
                format="%d"
            ),
            "created_at": st.column_config.DatetimeColumn(
                "Created",
                width="medium",
                format="MMM DD, YYYY HH:mm"
            ),
            "last_clicked": st.column_config.DatetimeColumn(
                "Last Click",
                width="medium",
                format="MMM DD, YYYY HH:mm"
            ),
            "is_active": st.column_config.CheckboxColumn(
                "Active",
                width="small",
                help="Campaign status"
            )
        }
        
        # Display editable table with pagination
        edited_df = st.data_editor(
            filtered_df,
            column_config=columns_config,
            use_container_width=True,
            hide_index=True,
            num_rows="dynamic",
            key="campaign_manager_table",
            disabled=["short_url", "original_url", "total_clicks", "created_at", "last_clicked"],
            column_order=[
                "campaign_name",
                "campaign_type",
                "short_url",
                "original_url",
                "total_clicks",
                "created_at",
                "last_clicked",
                "is_active"
            ]
        )
        
        # Handle edits
        if not filtered_df.equals(edited_df):
            try:
                # Get the changed rows
                changed_mask = (filtered_df != edited_df).any(axis=1)
                changed_rows = edited_df[changed_mask]
                
                for idx, row in changed_rows.iterrows():
                    # Update campaign in database
                    self.db.update_campaign(
                        short_code=df.loc[idx, 'short_code'],
                        campaign_name=row['campaign_name'],
                        campaign_type=row['campaign_type'],
                        is_active=row['is_active']
                    )
                
                st.success("Campaign(s) updated successfully!")
                time.sleep(1)
                st.rerun()
                
            except Exception as e:
                st.error(f"Error updating campaign(s): {str(e)}")

    def generate_report(self, report_type: str, format: str, metrics: list, **kwargs):
        """Generate analytics report based on parameters"""
        try:
            # Get filtered data
            data = self.db.get_analytics_summary(**kwargs)
            
            # Create DataFrame based on report type
            if report_type == "Campaign Summary":
                df = pd.DataFrame(data['campaign_stats'])
            elif report_type == "Geographic Analysis":
                df = pd.DataFrame(list(data['state_stats'].items()), 
                                columns=['State', 'Visits'])
            elif report_type == "Time-based Analysis":
                df = pd.DataFrame(list(data['daily_stats'].items()),
                                columns=['Date', 'Clicks'])
            else:  # Custom Report
                # Combine all requested metrics
                df = pd.DataFrame()
                if "Clicks" in metrics:
                    df['Clicks'] = data['daily_stats'].values()
                if "Geographic Data" in metrics:
                    df['Geographic'] = data['state_stats'].values()
                # Add more metric combinations as needed
            
            # Generate report in requested format
            if format == "Excel":
                output = BytesIO()
                df.to_excel(output, index=False)
                return output.getvalue()
            elif format == "CSV":
                return df.to_csv(index=False).encode('utf-8')
            elif format == "PDF":
                # Implement PDF generation using reportlab or another PDF library
                pass
            
        except Exception as e:
            logger.error(f"Error generating report: {str(e)}")
            raise

def auto_collapse_sidebar():
    """Add JavaScript to automatically collapse the sidebar after selection"""
    js_code = """
        <script>
            function waitForElement(selector, callback) {
                if (document.querySelector(selector)) {
                    callback();
                } else {
                    setTimeout(() => waitForElement(selector, callback), 100);
                }
            }

            waitForElement('[data-testid="stSidebar"]', () => {
                const sidebar = window.parent.document.querySelector('[data-testid="stSidebar"]');
                const sidebarContent = sidebar.querySelector('[data-testid="stSidebarContent"]');
                
                sidebarContent.addEventListener('click', (e) => {
                    // Check if click is on a navigation item
                    if (e.target.closest('.stRadio') || e.target.closest('.stButton')) {
                        // Wait for the next tick to ensure state is updated
                        setTimeout(() => {
                            const collapseButton = sidebar.querySelector('[data-testid="collapsedControl"]');
                            if (collapseButton) {
                                collapseButton.click();
                            }
                        }, 100);
                    }
                });
            });
        </script>
    """
    html(js_code)

def capture_client_info():
    """Capture client information for analytics"""
    try:
        ctx = get_script_run_ctx()
        if ctx is not None:
            # Basic client info without user agent
            client_info = {
                'ip_address': ctx.session_id,  # Using session ID as proxy for IP
                'user_agent': None,
                'referrer': None,
                'state': None,
                'device_type': 'Unknown',  # Default values
                'browser': 'Unknown',
                'os': 'Unknown'
            }
            
            # Try to get user agent info if available
            try:
                import streamlit.components.v1 as components
                # Inject JavaScript to get user agent
                ua_html = """
                    <script>
                        var ua = navigator.userAgent;
                        var device = 'Desktop';
                        if (/mobile/i.test(ua)) device = 'Mobile';
                        else if (/tablet/i.test(ua)) device = 'Tablet';
                        
                        var browser = 'Unknown';
                        if (/firefox/i.test(ua)) browser = 'Firefox';
                        else if (/chrome/i.test(ua)) browser = 'Chrome';
                        else if (/safari/i.test(ua)) browser = 'Safari';
                        else if (/edge/i.test(ua)) browser = 'Edge';
                        
                        var os = 'Unknown';
                        if (/windows/i.test(ua)) os = 'Windows';
                        else if (/macintosh/i.test(ua)) os = 'MacOS';
                        else if (/linux/i.test(ua)) os = 'Linux';
                        else if (/android/i.test(ua)) os = 'Android';
                        else if (/ios/i.test(ua)) os = 'iOS';
                        
                        window.parent.postMessage({
                            type: 'client_info',
                            device: device,
                            browser: browser,
                            os: os,
                            ua: ua
                        }, '*');
                    </script>
                """
                components.html(ua_html, height=0)
                
                # Update client info with detected values
                if 'client_detected_info' in st.session_state:
                    detected = st.session_state.client_detected_info
                    client_info.update({
                        'device_type': detected.get('device', 'Unknown'),
                        'browser': detected.get('browser', 'Unknown'),
                        'os': detected.get('os', 'Unknown'),
                        'user_agent': detected.get('ua', None)
                    })
            except Exception as e:
                logger.warning(f"Could not detect detailed client info: {str(e)}")
            
            # Store in session state
            st.session_state.client_info = client_info
            logger.info("Client info captured with basic data")
            
    except Exception as e:
        logger.error(f"Error capturing client info: {str(e)}")

def render_header(title: str):
    """Render a consistent header with deep green styling"""
    st.markdown(f"""
        <div class="main-header">
            <h1>{title}</h1>
        </div>
    """, unsafe_allow_html=True)

def render_dashboard():
    """Render the main dashboard with enhanced details"""
    try:
        # Get comprehensive stats with defaults first
        stats = shortener.db.get_dashboard_stats() or {
            'total_clicks': 0,
            'unique_visitors': 0,
            'total_campaigns': 0,
            'active_campaigns': 0,
            'recent_activities': [],
            'top_campaigns': [],
            'device_stats': {},
            'browser_stats': {},
            'previous_clicks': 0,
            'previous_unique': 0,
            'bounce_rate': 0,
            'avg_time': 0
        }
        
        # Main Metrics Display
        st.markdown("### 📊 Key Metrics")
        metric_cols = st.columns(4)
        
        with metric_cols[0]:
            st.markdown(f"""
                <div class="metric-card">
                    <div class="metric-title">
                        <span class="metric-icon">👆</span>
                        Total Clicks
                    </div>
                    <div class="metric-value">
                        {stats.get('total_clicks', 0):,}
                        <span class="unit">clicks</span>
                    </div>
                </div>
            """, unsafe_allow_html=True)

        with metric_cols[1]:
            st.markdown(f"""
                <div class="metric-card">
                    <div class="metric-title">
                        <span class="metric-icon">👥</span>
                        Unique Users
                    </div>
                    <div class="metric-value">
                        {stats.get('unique_visitors', 0):,}
                        <span class="unit">users</span>
                    </div>
                </div>
            """, unsafe_allow_html=True)

        with metric_cols[2]:
            st.markdown(f"""
                <div class="metric-card">
                    <div class="metric-title">
                        <span class="metric-icon">📈</span>
                        Conversion Rate
                    </div>
                    <div class="metric-value">
                        {stats.get('conversion_rate', 0):.1f}
                        <span class="unit">%</span>
                    </div>
                </div>
            """, unsafe_allow_html=True)

        with metric_cols[3]:
            st.markdown(f"""
                <div class="metric-card">
                    <div class="metric-title">
                        <span class="metric-icon">⚡</span>
                        Active Campaigns
                    </div>
                    <div class="metric-value">
                        {stats.get('active_campaigns', 0)}
                        <span class="unit">active</span>
                    </div>
                </div>
            """, unsafe_allow_html=True)

        # Quick Actions Bar with Quick Link
        quick_action_cols = st.columns(3)
        with quick_action_cols[0]:
            if st.button("New Campaign", key="new_campaign", use_container_width=True):
                st.session_state.page = "create_campaign"
                
        with quick_action_cols[1]:
            if st.button("Export Report", key="export_report", use_container_width=True):
                export_analytics()

        with quick_action_cols[2]:
            # Quick Link expander - closed by default
            with st.expander("Create Quick Link", expanded=False):
                with st.form("quick_link_form", clear_on_submit=True):
                    quick_url = st.text_input("URL to Shorten", placeholder="https://")
                    quick_submitted = st.form_submit_button("Create Quick Link", use_container_width=True)
                    if quick_submitted and quick_url:
                        try:
                            short_code = shortener.create_short_url(quick_url, "Quick Link")
                            if short_code:
                                st.success(f"Short URL created: {BASE_URL}?r={short_code}")
                        except Exception as e:
                            st.error(f"Error creating short URL: {str(e)}")

        # Campaign Performance Metrics - Now in 3 columns with cards
        st.markdown("#### Campaign Insights")
        insight_cols = st.columns(3)
        
        with insight_cols[0]:
            avg_time = stats.get('avg_time', 0)
            st.markdown(f"""
                <div class="metric-card">
                    <div class="metric-title">
                        <span class="metric-icon">⏱️</span>
                        Engagement
                    </div>
                    <div class="metric-value">
                        {avg_time:.1f}
                        <span class="unit">seconds</span>
                    </div>
                    <div class="metric-delta positive">+12% vs last month</div>
                </div>
            """, unsafe_allow_html=True)

        with insight_cols[1]:
            bounce_rate = stats.get('bounce_rate', 0)
            st.markdown(f"""
                <div class="metric-card">
                    <div class="metric-title">
                        <span class="metric-icon">↩️</span>
                        Bounce Rate
                    </div>
                    <div class="metric-value">
                        {bounce_rate:.1f}
                        <span class="unit">%</span>
                    </div>
                    <div class="metric-delta negative">-5% vs last month</div>
                </div>
            """, unsafe_allow_html=True)

        with insight_cols[2]:
            total_clicks = stats.get('total_clicks', 0)
            impressions = stats.get('impressions', 0)
            conversion_rate = (total_clicks / max(1, impressions)) * 100
            st.markdown(f"""
                <div class="metric-card">
                    <div class="metric-title">
                        <span class="metric-icon">🎯</span>
                        Conversion Rate
                    </div>
                    <div class="metric-value">
                        {conversion_rate:.1f}
                        <span class="unit">%</span>
                    </div>
                    <div class="metric-delta positive">+15% vs last month</div>
                </div>
            """, unsafe_allow_html=True)

        # Device Analytics and Campaign Distribution
        st.markdown("### 📱 Analytics Overview")
        
        # First row - Device and Browser stats
        device_cols = st.columns(2)
        with device_cols[0]:
            # Combined Device and Browser Stats
            if stats.get('device_stats'):
                device_df = pd.DataFrame(list(stats['device_stats'].items()), 
                                    columns=['Device', 'Count'])
                fig = px.pie(
                    device_df,
                    values='Count',
                    names='Device',
                    title='Device Distribution',
                    color_discrete_sequence=['#10B981', '#3B82F6', '#8B5CF6', '#F59E0B'],
                    hole=0.4
                )
                fig.update_traces(textposition='outside', textinfo='percent+label')
                fig.update_layout(
                    showlegend=True,
                    height=400,
                    margin=dict(t=30, b=0, l=0, r=0)
                )
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.info("No device data available yet")

        with device_cols[1]:
            if stats.get('browser_stats'):
                browser_df = pd.DataFrame(list(stats['browser_stats'].items()),
                                        columns=['Browser', 'Count'])
                fig = px.pie(
                    browser_df,
                    values='Count',
                    names='Browser',
                    title='Browser Distribution',
                    color_discrete_sequence=['#3B82F6', '#8B5CF6', '#F59E0B', '#10B981'],
                    hole=0.4
                )
                fig.update_traces(textposition='outside', textinfo='percent+label')
                fig.update_layout(
                    showlegend=True,
                    height=400,
                    margin=dict(t=30, b=0, l=0, r=0)
                )
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.info("No browser data available yet")

        # Second row - Campaign Distribution and Trends
        trend_cols = st.columns(2)
        with trend_cols[0]:
            # Campaign Type Distribution
            campaign_type_query = """
                SELECT 
                    campaign_type,
                    COUNT(*) as count,
                    SUM(total_clicks) as total_clicks
                FROM urls
                GROUP BY campaign_type
            """
            campaign_type_stats = pd.DataFrame(shortener.db.execute_query(campaign_type_query))
            
            if not campaign_type_stats.empty:
                fig = px.pie(
                    campaign_type_stats,
                    values='total_clicks',  # Changed to total_clicks for better insight
                    names='campaign_type',
                    title='Campaign Performance by Type',
                    color_discrete_sequence=['#10B981', '#3B82F6', '#8B5CF6', '#F59E0B', '#EC4899', '#6366F1'],
                    hole=0.4
                )
                fig.update_traces(textposition='outside', textinfo='percent+label')
                fig.update_layout(
                    showlegend=True,
                    height=400,
                    margin=dict(t=30, b=0, l=0, r=0)
                )
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.info("No campaign data available")

        with trend_cols[1]:
            # Traffic Source Analysis
            st.markdown("#### Traffic Sources")
            traffic_data = {
                'Source': ['Direct', 'Social', 'Email', 'Referral', 'Organic'],
                'Visits': [stats.get('direct_visits', 120), 
                          stats.get('social_visits', 80),
                          stats.get('email_visits', 60),
                          stats.get('referral_visits', 40),
                          stats.get('organic_visits', 30)]
            }
            traffic_df = pd.DataFrame(traffic_data)
            fig = px.bar(
                traffic_df,
                x='Source',
                y='Visits',
                title='Traffic Distribution by Source',
                color='Source',
                color_discrete_sequence=['#10B981', '#3B82F6', '#8B5CF6', '#F59E0B', '#EC4899']
            )
            fig.update_layout(
                showlegend=False,
                height=400,
                margin=dict(t=30, b=0, l=0, r=0)
            )
            st.plotly_chart(fig, use_container_width=True)

        # Recent Activity at the very end
        st.markdown("### 📊 Recent Activity")
        activity_cols = st.columns([3, 1])
        with activity_cols[0]:
            if stats['recent_activities']:
                for activity in stats['recent_activities']:
                    st.markdown(f"""
                        <div class="activity-card">
                            <div class="activity-title">
                                <span class="activity-icon">🔗</span>
                                {activity.get('campaign_name', 'Unknown Campaign')}
                            </div>
                            <div class="activity-meta">
                                <span>📱 {activity.get('device_type', 'Unknown')}</span>
                                <span>📍 {activity.get('state', 'Unknown')}</span>
                                <span>🌐 {activity.get('browser', 'Unknown')}</span>
                                <span>🖥️ {activity.get('os', 'Unknown')}</span>
                            </div>
                            <div class="activity-details">
                                <div class="detail-item">
                                    <span>⏱️</span>
                                    <span>Time on Page: {activity.get('time_on_page', '0')}s</span>
                                </div>
                                <div class="detail-item">
                                    <span>🔄</span>
                                    <span>Return Visitor: {'Yes' if activity.get('is_return_visitor') else 'No'}</span>
                                </div>
                                <div class="detail-item">
                                    <span>📈</span>
                                    <span>Conversion: {activity.get('converted', 'No')}</span>
                                </div>
                            </div>
                            <div class="activity-time">
                                {activity.get('clicked_at', 'Unknown time')}
                            </div>
                        </div>
                    """, unsafe_allow_html=True)
            else:
                st.info("No recent activity to show")

    except Exception as e:
        logger.error(f"Error rendering dashboard: {str(e)}")
        st.error("Error loading dashboard data. Please try refreshing the page.")

def export_analytics():
    """Export analytics data to CSV"""
    stats = shortener.db.get_dashboard_stats()
    
    # Create DataFrame for export
    export_data = pd.DataFrame(stats['top_campaigns'])
    
    # Add timestamp to filename
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"campaign_analytics_{timestamp}.csv"
    
    # Convert to CSV
    csv = export_data.to_csv(index=False)
    
    # Create download button
    st.download_button(
        label="📥 Download CSV",
        data=csv,
        file_name=filename,
        mime="text/csv"
    )

def show_quick_link_creator():
    """Show quick link creation form"""
    with st.form("quick_link"):
        url = st.text_input("Enter URL")
        campaign_name = st.text_input("Campaign Name (Optional)")
        submitted = st.form_submit_button("Create Link")
        
        if submitted and url:
            short_code = shortener.create_short_url(
                url=url,
                campaign_name=campaign_name or f"Quick_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            )
            st.success(f"Short URL created: {BASE_URL}?r={short_code}")

def clear_all_cache():
    """Clear all Streamlit cache"""
    try:
        # Clear all st.cache_data
        for key in [k for k in st.session_state.keys() if k.startswith('cache_')]:
            del st.session_state[key]
        
        # Reset theme
        st.session_state.theme = 'light'
        
        # Clear any other session state
        keys_to_keep = ['theme']
        for key in [k for k in st.session_state.keys() if k not in keys_to_keep]:
            del st.session_state[key]
            
    except Exception as e:
        logger.error(f"Error clearing cache: {str(e)}")

def main():
    try:
        # Initialize database only once
        if 'db' not in st.session_state:
            st.session_state.db = Database()
            logger.info("Database initialized")

        # Check for redirect first - Move this before auth check
        params = st.query_params
        if 'r' in params:
            short_code = params['r']
            target_url = st.session_state.db.handle_redirect(short_code)
            
            if target_url:
                # Show loading message
                st.info(f"Redirecting to {target_url}...")
                
                # Use JavaScript for immediate redirect
                html_code = f"""
                    <html>
                        <head>
                            <script>
                                window.location.href = "{target_url}";
                            </script>
                        </head>
                        <body>
                            <p>If you are not redirected automatically, <a href="{target_url}">click here</a>.</p>
                        </body>
                    </html>
                """
                st.components.v1.html(html_code, height=100)
                return
            else:
                st.error("Invalid short URL")
                return

        # Initialize auth if not already done
        if 'auth' not in st.session_state:
            st.session_state.auth = Auth(st.session_state.db)
            logger.info("Auth initialized")

        # Initialize Google Analytics
        if 'ga' not in st.session_state:
            try:
                st.session_state.ga = GoogleAnalytics()
                logger.info("Google Analytics initialized successfully")
            except Exception as e:
                logger.warning(f"Google Analytics initialization failed: {str(e)}")
                st.session_state.ga = None

        # Initialize User Journey Tracker with GA client
        if 'journey_tracker' not in st.session_state:
            try:
                # Only initialize if GA is available
                if st.session_state.ga:
                    st.session_state.journey_tracker = UserJourneyTracker(
                        database=st.session_state.db,  # Changed back to 'database'
                        ga_client=st.session_state.ga  # Changed to 'ga_client'
                    )
                    logger.info("User Journey Tracker initialized successfully")
                else:
                    st.session_state.journey_tracker = None
                    logger.warning("Journey Tracker not initialized - GA not available")
            except Exception as e:
                logger.warning(f"Journey Tracker initialization failed: {str(e)}")
                st.session_state.journey_tracker = None

        # Handle logout action first
        if st.sidebar.button("Logout"):
            if 'auth' in st.session_state:
                st.session_state.auth.logout()
                st.rerun()  # Use rerun instead of reload
                return

        # Check authentication for dashboard access
        if not st.session_state.auth.is_authenticated():
            render_login_page()
            return

        # Track page view only if authenticated and GA available
        if st.session_state.ga:
            st.session_state.ga.track_page_view('Dashboard')
            st.session_state.ga.track_event(
                'page_view',
                'dashboard',
                'Dashboard View'
            )

        # Track user journey only if authenticated and tracker available
        if st.session_state.journey_tracker:
            st.session_state.journey_tracker.track_event(
                JourneyEventType.PAGE_VIEW,
                'dashboard_view',
                {
                    'page': 'dashboard',
                    'user_role': st.session_state.user.get('role', 'unknown'),
                    'organization': st.session_state.user.get('organization', 'unknown')
                }
            )

        # Initialize shortener only after authentication
        if 'shortener' not in st.session_state:
            st.session_state.shortener = URLShortener()
            
        # Use existing shortener instance
        global shortener
        shortener = st.session_state.shortener
        
        auto_collapse_sidebar()
        capture_client_info()
        
        # Sidebar Navigation
        with st.sidebar:
            # Update logo to use VBG's branding
            st.image(
                "https://virtualbattleground.in/images/VBG-Logo.png",  # VBG's official logo
                use_container_width=True
            )
            
            # Show user info with VBG styling
            st.markdown(f"""
                <div class="user-info vbg-branded">
                    <p>
                        <span>👤</span>
                        <span class="user-role">{st.session_state.user['username']}</span>
                    </p>
                    <p>
                        <span>🏢</span>
                        <span class="org-name">VBG Game Studios</span>
                    </p>
                    <p class="domain-info">
                        <span>🌐</span>
                        <span>virtualbattleground.in</span>
                    </p>
                </div>
            """, unsafe_allow_html=True)
            
            selected_page = st.radio(
                "Navigation",
                ["🏠 Dashboard", "🔗 Create Campaign", "📈 Analytics", 
                 "🏢 Organization" if st.session_state.user['role'] == 'admin' else None,
                 "⚙️ Settings"],
                format_func=lambda x: x if x else "",  # Hide None option
            )
            
        # Page routing
        if selected_page == "🏠 Dashboard":
            render_header("Campaign Dashboard")
            render_dashboard()
        elif selected_page == "🔗 Create Campaign":
            render_header("Create Campaign")
            create_campaign()
        elif selected_page == "📈 Analytics":
            render_header("Analytics Overview")
            shortener.render_analytics_dashboard()
        elif selected_page == "🏢 Organization":
            organization = Organization(st.session_state.db)
            organization.render_organization_settings()
        elif selected_page == "⚙️ Settings":
            render_header("Settings")
            render_settings()

        # Initialize tracking variables
        submitted = False
        clicked = False
        campaign_name = None
        campaign_type = None
        short_code = None
        utm_source = None
        utm_medium = None
        utm_campaign = None

        # Track campaign creation
        if submitted and short_code:
            if st.session_state.ga:
                st.session_state.ga.track_event(
                    'campaign',
                    'create',
                    'Campaign Created'
                )
            
            if st.session_state.journey_tracker:
                st.session_state.journey_tracker.track_event(
                    JourneyEventType.CAMPAIGN_CREATE,
                    'campaign_created',
                    {
                        'campaign_name': campaign_name,
                        'campaign_type': campaign_type,
                        'has_utm': bool(utm_source or utm_medium or utm_campaign)
                    }
                )

        # Track link clicks
        if clicked:
            if st.session_state.ga:
                st.session_state.ga.track_event(
                    'link',
                    'click',
                    'Link Clicked'
                )
            
            if st.session_state.journey_tracker:
                st.session_state.journey_tracker.track_event(
                    JourneyEventType.LINK_CLICK,
                    'link_clicked',
                    {
                        'short_code': short_code,
                        'campaign_name': campaign_name,
                        'device_type': st.session_state.get('device_type', 'unknown')
                    }
                )

    except Exception as e:
        logger.error(f"Error in main: {str(e)}")
        st.error("An error occurred. Please try refreshing the page.")

def track_event(event_name: str, event_params: dict = None):
    """Track event in Google Analytics and Journey"""
    try:
        # Track in GA4
        if hasattr(st.session_state, 'ga') and st.session_state.ga:
            try:
                event_category = event_params.get('category', 'general') if event_params else 'general'
                event_label = str(event_params) if event_params else None
                
                st.session_state.ga.track_event(
                    event_category=event_category,
                    event_action=event_name,
                    event_label=event_label
                )
            except Exception as e:
                logger.warning(f"GA tracking failed: {str(e)}")
        
        # Track in Journey Tracker
        if hasattr(st.session_state, 'journey_tracker') and st.session_state.journey_tracker:
            try:
                event_type = JourneyEventType.PAGE_VIEW
                if 'error' in event_name.lower():
                    event_type = JourneyEventType.ERROR
                elif 'click' in event_name.lower():
                    event_type = JourneyEventType.BUTTON_CLICK
                
                st.session_state.journey_tracker.track_event(
                    event_type=event_type,
                    event_name=event_name,
                    event_data=event_params or {}
                )
            except Exception as e:
                logger.warning(f"Journey tracking failed: {str(e)}")
                
    except Exception as e:
        logger.error(f"Error tracking event: {str(e)}")

def create_campaign():
    """Create new campaign form"""
    st.markdown("### 🎯 Campaign Details")
    
    # Add custom CSS for green button
    st.markdown("""
        <style>
        div.stButton > button[kind="primary"] {
            background-color: #10B981;
            border-color: #10B981;
        }
        div.stButton > button[kind="primary"]:hover {
            background-color: #059669;
            border-color: #059669;
        }
        div.stButton > button[kind="primary"]:active {
            background-color: #047857;
            border-color: #047857;
        }
        </style>
    """, unsafe_allow_html=True)
    
    with st.form("create_campaign", clear_on_submit=True):
        # Campaign Info Section
        st.markdown("#### Basic Information")
        campaign_name = st.text_input(
            "Campaign Name",
            key="campaign_name",
            placeholder="Enter campaign name",
            help="A unique name for your campaign"
        )
        
        campaign_type = st.selectbox(
            "Campaign Type",
            options=list(CAMPAIGN_TYPES.keys()),
            format_func=lambda x: f"{CAMPAIGN_TYPES[x]} {x}",
            help="Select the type of campaign"
        )
        
        original_url = st.text_input(
            "Original URL",
            key="original_url",
            placeholder="https://your-url.com",
            help="The URL you want to shorten"
        )

        # Add QR Code option
        generate_qr = st.checkbox("Generate QR Code", value=False, help="Create a QR code for this link")

        # UTM Parameters Section
        st.markdown("#### 🎯 UTM Parameters")
        with st.expander("Configure UTM Parameters", expanded=True):
            col1, col2 = st.columns(2)
            with col1:
                utm_source = st.text_input(
                    "Source",
                    placeholder="e.g., facebook",
                    help="The referrer (e.g., facebook, newsletter)"
                )
                utm_campaign = st.text_input(
                    "Campaign",
                    placeholder="e.g., summer_sale",
                    help="Campaign specific identifier"
                )
            with col2:
                utm_medium = st.text_input(
                    "Medium",
                    placeholder="e.g., social",
                    help="Marketing medium (e.g., cpc, social)"
                )
                utm_content = st.text_input(
                    "Content",
                    placeholder="e.g., blue_banner",
                    help="Use to differentiate ads"
                )

        # Submit button
        submitted = st.form_submit_button(
            "Create Campaign",
            type="primary",
            use_container_width=True
        )

    if submitted:
        if not campaign_name or not original_url:
            st.error("Please fill in all required fields")
            return

        try:
            # Create campaign
            short_code = shortener.create_short_url(
                url=original_url,
                campaign_name=campaign_name,
                campaign_type=campaign_type,
                utm_params={
                    'source': utm_source,
                    'medium': utm_medium,
                    'campaign': utm_campaign,
                    'content': utm_content
                }
            )
            
            # Generate short URL
            short_url = f"{BASE_URL}?r={short_code}"
            
            # Show success message with two cards side by side
            st.success("Campaign created successfully!")

            col1, col2 = st.columns(2)

            # Short URL Card
            with col1:
                st.markdown("""
                <div style='
                    background-color: #f0f9ff;
                    padding: 1rem;
                    border-radius: 0.5rem;
                    margin: 1rem 0;
                    height: 100%;
                    border: 1px solid #e2e8f0;
                    box-shadow: 0 1px 3px rgba(0,0,0,0.1);
                '>
                    <div style='display: flex; align-items: center; margin-bottom: 0.5rem;'>
                        <span style='font-size: 1.25rem; margin-right: 0.5rem;'>🔗</span>
                        <span style='font-weight: 600; color: #1a202c;'>Short URL</span>
                    </div>
                    <a href='{url}' target='_blank' style='color: #0891b2; text-decoration: none; word-break: break-all;'>{url}</a>
                    <p style='margin-top: 0.5rem; font-size: 0.875rem; color: #64748b;'>
                        Click to test the link and track analytics
                    </p>
                    <div style='display: flex; gap: 0.5rem; margin-top: 1rem;'>
                        <a href="{url}" target="_blank" style='
                            background-color: #0891b2;
                            color: white;
                            padding: 0.5rem 1rem;
                            border-radius: 0.375rem;
                            text-decoration: none;
                            font-size: 0.875rem;
                        '>Open Link</a>
                    </div>
                </div>
                """.format(url=short_url), unsafe_allow_html=True)

            # Campaign Details Card with QR Code
            with col2:
                st.markdown("""
                <div style='
                    background-color: #f0f9ff;
                    padding: 1rem;
                    border-radius: 0.5rem;
                    margin: 1rem 0;
                    height: 100%;
                    border: 1px solid #e2e8f0;
                    box-shadow: 0 1px 3px rgba(0,0,0,0.1);
                '>
                    <div style='display: flex; align-items: center; margin-bottom: 0.5rem;'>
                        <span style='font-size: 1.25rem; margin-right: 0.5rem;'>📱</span>
                        <span style='font-weight: 600; color: #1a202c;'>Campaign Details</span>
                    </div>
                    <div style='font-size: 0.875rem; color: #4b5563;'>
                        <p style='margin: 0.25rem 0;'><strong>Campaign:</strong> {name}</p>
                        <p style='margin: 0.25rem 0;'><strong>Type:</strong> {type}</p>
                        <p style='margin: 0.25rem 0;'><strong>Created:</strong> {date}</p>
                    </div>
                """.format(
                    name=campaign_name,
                    type=campaign_type,
                    date=datetime.now().strftime("%b %d, %Y")
                ), unsafe_allow_html=True)

                # Generate and display QR code if requested
                if generate_qr:
                    qr = qrcode.QRCode(
                        version=1,
                        error_correction=qrcode.constants.ERROR_CORRECT_L,
                        box_size=10,
                        border=4,
                    )
                    qr.add_data(short_url)
                    qr.make(fit=True)

                    # Create QR code image
                    img = qr.make_image(fill_color="black", back_color="white")
                    
                    # Convert to bytes
                    img_bytes = BytesIO()
                    img.save(img_bytes, format='PNG')
                    
                    # Display QR code
                    st.image(img_bytes, caption="Scan QR Code", width=200)
                
                st.markdown("""
                    <div style='display: flex; gap: 0.5rem; margin-top: 1rem;'>
                        <button onclick="navigator.clipboard.writeText('{url}')" style='
                            background-color: #0891b2;
                            color: white;
                            padding: 0.5rem 1rem;
                            border-radius: 0.375rem;
                            border: none;
                            cursor: pointer;
                            font-size: 0.875rem;
                        '>Copy Link</button>
                    </div>
                </div>
                """.format(url=short_url), unsafe_allow_html=True)

            # Test click button
            if st.button("Test Click (Record Only)", type="secondary"):
                if shortener.db.record_click(
                    short_code=short_code,
                    ip_address="127.0.0.1",
                    user_agent="Test Click",
                    referrer="Test",
                    state="Test",
                    device_type="Test",
                    browser="Test",
                    os="Test"
                ):
                    st.success("Test click recorded! Check the analytics.")
                    time.sleep(1)
                    st.rerun()

        except ValueError as e:
            st.error(str(e))
        except Exception as e:
            st.error(f"Error creating campaign: {str(e)}")

    # Add Campaign Manager Section below the form
    st.markdown("---")  # Add a divider
    st.markdown("### 📋 Manage Campaigns")
    
    # Get all campaigns
    campaigns = shortener.db.get_all_urls()
    
    if not campaigns:
        st.info("No campaigns yet. Create your first campaign above!")
        return
    
    # Create DataFrame for campaign data
    df = pd.DataFrame(campaigns)
    
    # Convert datetime strings to datetime objects
    df['created_at'] = pd.to_datetime(df['created_at'])
    df['last_clicked'] = pd.to_datetime(df['last_clicked'])
    
    # Add short URL column
    df['short_url'] = df['short_code'].apply(lambda x: f"{BASE_URL}?r={x}")
    
    # Add quick filters in a single row
    filter_col1, filter_col2, filter_col3 = st.columns(3)
    with filter_col1:
        campaign_type_filter = st.selectbox(
            "Filter by Type",
            ["All Types"] + list(CAMPAIGN_TYPES.keys())
        )
    with filter_col2:
        status_filter = st.selectbox(
            "Filter by Status",
            ["All", "Active", "Inactive"]
        )
    with filter_col3:
        search = st.text_input("Search Campaigns", placeholder="Search by name...")
    
    # Apply filters
    filtered_df = df.copy()
    if campaign_type_filter != "All Types":
        filtered_df = filtered_df[filtered_df['campaign_type'] == campaign_type_filter]
    if status_filter != "All":
        filtered_df = filtered_df[filtered_df['is_active'] == (status_filter == "Active")]
    if search:
        filtered_df = filtered_df[filtered_df['campaign_name'].str.contains(search, case=False)]
    
    # Configure columns for the data editor
    columns_config = {
        "campaign_name": st.column_config.TextColumn(
            "Campaign Name",
            width="medium",
            help="Name of the campaign"
        ),
        "campaign_type": st.column_config.SelectboxColumn(
            "Type",
            width="small",
            options=list(CAMPAIGN_TYPES.keys())
        ),
        "short_url": st.column_config.LinkColumn(
            "Short URL",
            width="medium",
            help="Click to open"
        ),
        "original_url": st.column_config.LinkColumn(
            "Original URL",
            width="medium"
        ),
        "total_clicks": st.column_config.NumberColumn(
            "Clicks",
            width="small",
            help="Total number of clicks",
            format="%d"
        ),
        "created_at": st.column_config.DatetimeColumn(
            "Created",
            width="medium",
            format="MMM DD, YYYY"
        ),
        "last_clicked": st.column_config.DatetimeColumn(
            "Last Click",
            width="medium",
            format="MMM DD, YYYY"
        ),
        "is_active": st.column_config.CheckboxColumn(
            "Active",
            width="small"
        )
    }
    
    # Display editable table
    edited_df = st.data_editor(
        filtered_df,
        column_config=columns_config,
        use_container_width=True,
        hide_index=True,
        num_rows="dynamic",
        key="campaign_table",
        disabled=["short_url", "original_url", "total_clicks", "created_at", "last_clicked"],
        column_order=[
            "campaign_name",
            "campaign_type",
            "short_url",
            "original_url",
            "total_clicks",
            "created_at",
            "last_clicked",
            "is_active"
        ]
    )
    
    # Handle edits
    if not filtered_df.equals(edited_df):
        try:
            # Get the changed rows
            changed_mask = (filtered_df != edited_df).any(axis=1)
            changed_rows = edited_df[changed_mask]
            
            for idx, row in changed_rows.iterrows():
                # Update campaign in database
                shortener.db.update_campaign(
                    short_code=df.loc[idx, 'short_code'],
                    campaign_name=row['campaign_name'],
                    campaign_type=row['campaign_type'],
                    is_active=row['is_active']
                )
            
            st.success("Campaign(s) updated successfully!")
            time.sleep(1)
            st.rerun()
            
        except Exception as e:
            st.error(f"Error updating campaign(s): {str(e)}")

def render_settings():
    """Render settings page"""
    # Create tabs for different settings
    settings_tab1, settings_tab2, settings_tab3 = st.tabs([
        "🎨 Appearance", "🔧 General", "🔌 Integrations"
    ])
    
    with settings_tab1:
        st.markdown("### Appearance Settings")
        
        # Theme Selection
        selected_theme = st.selectbox(
            "Theme",
            ["Light", "Dark"],
            index=0 if st.session_state.theme == 'light' else 1,
            help="Choose the app theme"
        )
        
        # Save theme preference
        if selected_theme:
            st.session_state.theme = selected_theme.lower()
            
        # Color Scheme
        st.color_picker(
            "Primary Color",
            "#10B981",
            help="Choose primary brand color"
        )
        
        # Layout Options
        st.selectbox(
            "Default Layout",
            ["Wide", "Centered"],
            help="Choose default page layout"
        )
        
    with settings_tab2:
        st.markdown("### General Settings")
        
        # URL Settings
        st.text_input(
            "Custom Domain",
            placeholder="your-domain.com",
            help="Enter your custom domain"
        )
        
        # Default UTM Parameters
        st.text_input(
            "Default UTM Source",
            placeholder="e.g., newsletter",
            help="Default source for campaigns"
        )
        
        # Analytics Settings
        st.checkbox(
            "Enable Advanced Analytics",
            help="Enable detailed analytics tracking"
        )
        
        # Notification Settings
        st.multiselect(
            "Email Notifications",
            ["Campaign Created", "High Traffic Alert", "Weekly Report"],
            help="Choose when to receive notifications"
        )
        
    with settings_tab3:
        st.markdown("### Integration Settings")
        
        # API Settings
        api_key = st.text_input(
            "API Key",
            type="password",
            help="Your API key for integrations"
        )
        
        # Webhook Settings
        webhook_url = st.text_input(
            "Webhook URL",
            placeholder="https://your-webhook.com/endpoint",
            help="URL for webhook notifications"
        )
        
        # Integration Options
        st.multiselect(
            "Active Integrations",
            ["Google Analytics", "Facebook Pixel", "Slack Notifications"],
            help="Choose active integrations"
        )
        
        if st.button("Save Settings", type="primary"):
            st.success("Settings saved successfully!")

def render_activity_item(activity: dict):
    """Render a single activity item with enhanced styling"""
    try:
        # Format timestamp
        try:
            timestamp = datetime.strptime(activity['clicked_at'], '%Y-%m-%d %H:%M:%S')
            formatted_time = timestamp.strftime('%b %d, %Y %I:%M %p')
        except:
            formatted_time = str(activity.get('clicked_at', 'Unknown'))
        
        campaign_emoji = CAMPAIGN_TYPES.get(activity.get('campaign_type', 'Other'), '🔗')
        device_emoji = {
            "Desktop": "💻",
            "Mobile": "📱",
            "Tablet": "📱",
            "Unknown": "❓"
        }.get(activity.get('device_type', 'Unknown'), '❓')
        
        st.markdown(f"""
            <div class="activity-item">
                <div style="display: flex; justify-content: space-between; align-items: center;">
                    <div style="display: flex; align-items: center; gap: 0.5rem;">
                        <span style="font-size: 1.5rem;">{campaign_emoji}</span>
                        <div>
                            <div style="font-weight: 600; color: #0891b2;">
                                {activity.get('campaign_name', 'Unknown Campaign')}
                            </div>
                            <div style="display: flex; gap: 1rem; color: #64748b; font-size: 0.875rem;">
                                <span>{device_emoji} {activity.get('device_type', 'Unknown')}</span>
                                <span>📍 {activity.get('state', 'Unknown')}</span>
                            </div>
                        </div>
                    </div>
                    <div style="color: #94a3b8; font-size: 0.875rem;">
                        {formatted_time}
                    </div>
                </div>
            </div>
        """, unsafe_allow_html=True)
    except Exception as e:
        logger.error(f"Error rendering activity item: {str(e)}")

def render_login_page():
    """Render the login page"""
    st.markdown("""
        <div class="login-container">
            <div class="login-header">
                <h1>🎯 Campaign Dashboard</h1>
                <p>Sign in to your account</p>
            </div>
        </div>
    """, unsafe_allow_html=True)

    col1, col2, col3 = st.columns([1,2,1])
    with col2:
        with st.form("login_form"):
            username = st.text_input("Username")
            password = st.text_input("Password", type="password")
            submitted = st.form_submit_button("Sign In", use_container_width=True)

            if submitted:
                if username and password:
                    user_data = st.session_state.auth.login(username, password)
                    if user_data:
                        # Store user data in session state
                        st.session_state.user = user_data
                        st.success("Login successful!")
                        time.sleep(1)  # Give time for success message
                        st.rerun()
                    else:
                        st.error("Invalid username or password")
                        logger.warning(f"Failed login attempt for user: {username}")
                else:
                    st.error("Please enter both username and password")

        # Show demo credentials
        st.markdown("""
            <div style="text-align: center; margin-top: 2rem;">
                <p style="color: #666;">Demo Credentials:</p>
                <p>Admin: admin / admin123</p>
                <p>User: nandan / nandan123</p>
            </div>
        """, unsafe_allow_html=True)

if __name__ == "__main__":
    main() 
