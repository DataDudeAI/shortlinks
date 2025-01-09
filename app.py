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
from ui_styles import get_styles, get_theme_colors
from organization import Organization
from streamlit.components.v1 import html
from streamlit.runtime.scriptrunner import add_script_run_ctx
import qrcode
from io import BytesIO
from PIL import Image
from streamlit.runtime.scriptrunner import get_script_run_ctx
import os
import time

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Initialize database at app startup
if 'db' not in st.session_state:
    try:
        db = Database()
        st.session_state.db = db
        logger.info("Database initialized successfully")
    except Exception as e:
        logger.error(f"Error initializing database: {str(e)}")
        st.error("Error initializing database. Please check the logs.")

# Must be the first Streamlit command
st.set_page_config(
    page_title="Campaign Dashboard",
    page_icon="🎯",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# At the start of your app, after st.set_page_config
if 'theme' not in st.session_state:
    st.session_state.theme = 'light'

# Load theme-aware styles
st.markdown(get_styles(), unsafe_allow_html=True)

# Apply theme-specific settings
if st.session_state.theme == 'dark':
    st.markdown("""
        <script>
            document.querySelector('.stApp').classList.add('dark');
        </script>
    """, unsafe_allow_html=True)

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

db = Database()  # Global database instance
ui = UI(db)  # Global UI instance

class URLShortener:
    def __init__(self):
        """Initialize URL shortener with database connection"""
        try:
            self.db = Database()
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
            campaign_type = st.selectbox(
                "Campaign Type", 
                list(CAMPAIGN_TYPES.keys()),
                index=list(CAMPAIGN_TYPES.keys()).index(campaign.get('campaign_type', 'Other'))
            )
            
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
            expiry_date = st.date_input(
                "Expiry Date", 
                value=datetime.strptime(campaign.get('expiry_date', '2099-12-31'), '%Y-%m-%d') if campaign.get('expiry_date') else None
            )
            
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

    def create_campaign_url(self, campaign_data: dict) -> Optional[str]:
        """Create a campaign URL"""
        try:
            logger.info("Starting campaign creation process...")
            logger.info(f"URL: {campaign_data['url']}")
            logger.info(f"Campaign Name: {campaign_data['campaign_name']}")
            
            # Generate short code
            short_code = self.generate_short_code()
            logger.info(f"Generated short code: {short_code}")
            
            # Extract UTM parameters
            utm_params = {
                'source': campaign_data.get('utm_source'),
                'medium': campaign_data.get('utm_medium'),
                'campaign': campaign_data.get('utm_campaign'),
                'content': campaign_data.get('utm_content')
            }
            logger.info(f"UTM parameters: {utm_params}")
            
            # Create short URL
            logger.info("Attempting to save to database...")
            short_code = self.db.create_short_url(
                url=campaign_data['url'],
                campaign_name=campaign_data['campaign_name'],
                campaign_type=campaign_data['campaign_type'],
                utm_params=utm_params
            )
            
            if short_code:
                logger.info(f"Successfully created campaign with short code: {short_code}")
                return short_code
            else:
                logger.error("Database save operation failed")
                return None
            
        except Exception as e:
            logger.error(f"Error creating campaign URL: {str(e)}")
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
        if 'client_info' not in st.session_state:
            st.session_state.client_info = {
                'client_ip': '127.0.0.1',
                'user_agent': st.get_user_agent() if hasattr(st, 'get_user_agent') else 'Unknown',
                'referrer': 'Direct',
                'state': 'Unknown',
                'device_type': 'Unknown',
                'browser': 'Unknown',
                'os': 'Unknown'
            }
            
        # Update session state
        for key, value in st.session_state.client_info.items():
            st.session_state[key] = value
            
    except Exception as e:
        logger.error(f"Error capturing client info: {str(e)}")

def render_header(title: str):
    """Render a consistent header with deep green styling"""
    st.markdown(f"""
        <div class="main-header">
            <h1>{title}</h1>
        </div>
    """, unsafe_allow_html=True)

def render_dashboard(db):
    """Render dashboard with analytics"""
    st.title("📊 Campaign Analytics")
    
    try:
        # Get dashboard stats
        stats = db.get_dashboard_stats()
        
        # Display metrics
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Total Clicks", stats['total_clicks'])
        with col2:
            st.metric("Unique Visitors", stats['unique_visitors'])
        with col3:
            st.metric("Active Campaigns", stats['active_campaigns'])
        with col4:
            engagement = (stats['unique_visitors'] / stats['total_clicks'] * 100) if stats['total_clicks'] > 0 else 0
            st.metric("Engagement Rate", f"{engagement:.1f}%")
        
        # Recent Activity
        st.subheader("📈 Recent Activity")
        if stats['recent_activities']:
            for activity in stats['recent_activities']:
                st.markdown(f"""
                    **{activity['campaign_name']}** ({activity['campaign_type']})  
                    🕒 {activity['clicked_at']} | 📍 {activity['state']} | 📱 {activity['device_type']}
                    """)
        else:
            st.info("No recent activity")
            
        # Campaign Management
        st.subheader("🎯 Campaign Management")
        render_campaign_details(db)
        
    except Exception as e:
        logger.error(f"Error rendering dashboard: {str(e)}")
        st.error("Error loading dashboard data")

def render_campaign_creation(db):
    """Render campaign creation form"""
    st.subheader("Create New Campaign")
    
    with st.form("campaign_form"):
        campaign_name = st.text_input("Campaign Name")
        campaign_type = st.selectbox("Campaign Type", list(CAMPAIGN_TYPES.keys()))
        url = st.text_input("URL")
        
        # UTM Parameters
        with st.expander("UTM Parameters"):
            utm_source = st.text_input("Source", placeholder="e.g., facebook")
            utm_medium = st.text_input("Medium", placeholder="e.g., social")
            utm_campaign = st.text_input("Campaign", placeholder="e.g., summer_sale")
            utm_content = st.text_input("Content", placeholder="e.g., banner_1")
        
        submitted = st.form_submit_button("Create Campaign")
        
        if submitted:
            try:
                if not campaign_name or not url:
                    st.error("Please fill in all required fields")
                    return
                
                # Create campaign
                short_code = db.create_short_url(
                    url=url,
                    campaign_name=campaign_name,
                    campaign_type=campaign_type,
                    utm_params={
                        'source': utm_source,
                        'medium': utm_medium,
                        'campaign': utm_campaign,
                        'content': utm_content
                    }
                )
                
                if short_code:
                    st.success("Campaign created successfully!")
                    st.markdown(f"Short URL: `{BASE_URL}?r={short_code}`")
                else:
                    st.error("Failed to create campaign")
                    
            except Exception as e:
                logger.error(f"Error creating campaign: {str(e)}")
                st.error("Error creating campaign")

def render_campaign_details(db):
    """Render campaign details section"""
    st.markdown("### 🎯 Campaign Details")

    # Get all campaigns
    campaigns = db.get_all_campaigns()
    
    if campaigns:
        # Create a DataFrame for display
        df = pd.DataFrame(campaigns)
        
        # Add short URL column
        df['short_url'] = df['short_code'].apply(lambda x: f"{BASE_URL}?r={x}")
        
        # Configure columns for editable table
        edited_df = st.data_editor(
            df,
            column_config={
                "campaign_name": st.column_config.TextColumn(
                    "Campaign",
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
                    help="Click to copy"
                ),
                "total_clicks": st.column_config.NumberColumn(
                    "Clicks",
                    width="small",
                    format="%d"
                ),
                "created_at": st.column_config.DatetimeColumn(
                    "Created",
                    width="small",
                    format="MMM DD, YYYY"
                ),
                "last_clicked": st.column_config.DatetimeColumn(
                    "Last Click",
                    width="small",
                    format="MMM DD, YYYY"
                ),
                "is_active": st.column_config.CheckboxColumn(
                    "Active",
                    width="small",
                    help="Campaign status"
                )
            },
            hide_index=True,
            use_container_width=True,
            disabled=["short_url", "total_clicks", "created_at", "last_clicked"],
            key="campaign_table"
        )

        # Handle edits to campaign details
        if not df.equals(edited_df):
            try:
                # Get the changed rows
                changed_mask = (df != edited_df).any(axis=1)
                changed_rows = edited_df[changed_mask]
                
                for idx, row in changed_rows.iterrows():
                    # Update campaign in database
                    success = db.update_campaign(
                        short_code=df.loc[idx, 'short_code'],
                        campaign_name=row['campaign_name'],
                        campaign_type=row['campaign_type'],
                        is_active=row['is_active']
                    )
                    if success:
                        st.success(f"Updated campaign: {row['campaign_name']}")
                        time.sleep(0.5)
                        st.rerun()
                    else:
                        st.error(f"Failed to update campaign: {row['campaign_name']}")
                
            except Exception as e:
                st.error(f"Error updating campaigns: {str(e)}")
    else:
        st.info("No campaigns created yet")

def main():
    try:
        # Get database instance from session state
        db = st.session_state.db
        
        # Create tabs for different sections
        tab1, tab2, tab3 = st.tabs(["📊 Dashboard", "🎯 Create Campaign", "⚙️ Settings"])
        
        with tab1:
            render_dashboard(db)
            
        with tab2:
            render_campaign_creation(db)
            
        with tab3:
            render_settings(db)
            
    except Exception as e:
        logger.error(f"Error in main: {str(e)}")
        st.error("An error occurred. Please check the logs.")

def render_settings(db):
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

if __name__ == "__main__":
    main() 
