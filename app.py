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

# Must be the first Streamlit command
st.set_page_config(
    page_title="Campaign Dashboard",
    page_icon="🎯",
    layout="wide",
    initial_sidebar_state="collapsed",
    menu_items={
        'Get Help': 'https://github.com/yourusername/shortlinks',
        'Report a bug': "https://github.com/yourusername/shortlinks/issues",
        'About': "# Campaign Dashboard\nA powerful URL shortener and campaign management tool."
    }
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

def render_dashboard(db: Database):
    """Render the main dashboard with consistent data"""
    # Get comprehensive stats
    stats = db.get_dashboard_stats()
    
    # Show empty state if no campaigns exist
    if stats['total_campaigns'] is None:
        st.info("👋 Welcome! Create your first campaign to see analytics here.")
        return
    
    # Top Metrics
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Total Clicks", stats['total_clicks'])
    with col2:
        st.metric("Unique Visitors", stats['unique_visitors'])
    with col3:
        st.metric("Active Campaigns", stats['active_campaigns'])
    with col4:
        engagement_rate = (stats['unique_visitors'] / max(1, stats['total_clicks'])) * 100 if stats['total_clicks'] else 0
        st.metric("Engagement Rate", f"{engagement_rate:.1f}%")

    # Charts
    if stats['daily_stats'] or stats['device_stats'] or stats['state_stats']:
        col1, col2 = st.columns(2)
        with col1:
            if stats['daily_stats']:
                df = pd.DataFrame(list(stats['daily_stats'].items()), columns=['Date', 'Clicks'])
                fig = px.line(df, x='Date', y='Clicks', title='Daily Click Trends')
                st.plotly_chart(fig, use_container_width=True)

        with col2:
            if stats['device_stats']:
                df = pd.DataFrame(list(stats['device_stats'].items()), columns=['Device', 'Count'])
                fig = px.pie(df, values='Count', names='Device', title='Device Distribution')
                st.plotly_chart(fig, use_container_width=True)
        
        # Create two columns for Geographic Distribution and Top Campaigns
        geo_col, top_campaigns_col = st.columns(2)
        
        # Geographic Distribution in left column
        with geo_col:
            if stats['state_stats']:
                st.markdown("### 📍 Geographic Distribution")
                state_df = pd.DataFrame(list(stats['state_stats'].items()), columns=['State', 'Visits'])
                state_df = state_df.sort_values('Visits', ascending=True)
                
                fig = px.bar(
                    state_df,
                    x='Visits',
                    y='State',
                    orientation='h',
                    title='Visits by State',
                    color='Visits',
                    color_continuous_scale='Viridis'
                )
                
                # Update layout for better readability
                fig.update_layout(
                    height=400,  # Fixed height to match top campaigns table
                    xaxis_title="Number of Visits",
                    yaxis_title="State",
                    showlegend=False,
                    margin=dict(l=0, r=0, t=30, b=0)  # Adjust margins
                )
                
                st.plotly_chart(fig, use_container_width=True)

        # Top Campaigns in right column
        with top_campaigns_col:
            st.markdown("### 🏆 Top Performing Campaigns")
            if stats['top_campaigns']:
                df = pd.DataFrame(stats['top_campaigns'])
                
                # Format the dataframe
                if 'last_click' in df.columns:
                    df['last_click'] = pd.to_datetime(df['last_click']).dt.strftime('%Y-%m-%d %H:%M')
                
                # Configure columns
                st.dataframe(
                    df,
                    column_config={
                        "campaign_name": st.column_config.TextColumn("Campaign"),
                        "clicks": st.column_config.NumberColumn("Clicks", format="%d"),
                        "unique_visitors": st.column_config.NumberColumn("Unique", format="%d"),
                        "campaign_type": st.column_config.TextColumn("Type"),
                        "last_click": st.column_config.TextColumn("Last Click")
                    },
                    use_container_width=True,
                    hide_index=True,
                    height=400  # Match height with geographic chart
                )
            else:
                st.info("No campaign data available yet")

    # Recent Activity (Limited to 5)
    st.markdown("### 📊 Recent Activity")
    
    # Show only 5 most recent activities
    recent_activities = stats['recent_activities'][:5]
    
    if recent_activities:
        for activity in recent_activities:
            render_activity_item(activity)
            
        # Add "View All" button
        if len(stats['recent_activities']) > 5:
            if st.button("View All Activities"):
                st.session_state.show_all_activities = True
                
        # Show all activities in a modal/expander if requested
        if st.session_state.get('show_all_activities', False):
            with st.expander("All Activities", expanded=True):
                for activity in stats['recent_activities'][5:]:
                    render_activity_item(activity)
                if st.button("Show Less"):
                    st.session_state.show_all_activities = False
    else:
        st.info("No recent activity to show")

    col1, col2 = st.columns([2, 1])
    with col1:
        st.markdown("### Click Trends")
        if stats['daily_stats']:
            trend_chart = ui.render_trend_chart(stats['daily_stats'])
            if trend_chart:
                st.plotly_chart(trend_chart, use_container_width=True)
            else:
                st.info("Unable to render trend chart")
        else:
            st.info("No click data available yet")

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
        # Initialize global state
        if 'initialized' not in st.session_state:
            st.session_state.initialized = True
            st.session_state.shortener = None
        
        # Initialize components
        if not st.session_state.shortener:
            st.session_state.shortener = URLShortener()
        
        global shortener
        shortener = st.session_state.shortener
        
        # Rest of your main function...
        auto_collapse_sidebar()
        capture_client_info()
        
        # Sidebar Navigation
        with st.sidebar:
            st.image(
                "https://via.placeholder.com/150x50?text=Logo",
                use_container_width=True
            )
            
            selected_page = st.radio(
                "Navigation",
                ["🏠 Dashboard", "🔗 Create Campaign", "📈 Analytics", "⚙️ Settings"],
                label_visibility="collapsed"
            )
        
        # Page routing
        if selected_page == "🏠 Dashboard":
            render_header("Campaign Dashboard")
            render_dashboard(shortener.db)  # Pass the database instance
        elif selected_page == "🔗 Create Campaign":
            render_header("Create Campaign")
            create_campaign()  # Use create_campaign instead of render_create_campaign
        elif selected_page == "📈 Analytics":
            render_header("Analytics Overview")
            render_analytics(shortener.db)  # Pass the database instance
        elif selected_page == "⚙️ Settings":
            render_header("Settings")
            render_settings(shortener.db)  # Pass the database instance

    except Exception as e:
        logger.error(f"Error in main: {str(e)}")
        st.error("An error occurred. Please try refreshing the page.")

def create_campaign():
    """Create new campaign form with green theme"""
    st.markdown("### 🎯 Create Campaign")
    
    # Add custom CSS for green theme
    st.markdown("""
        <style>
        /* Green theme styles */
        .stTextInput > div > div > input,
        .stSelectbox > div > div > select {
            border-color: #059669 !important;
        }
        .stTextInput > div > div > input:focus,
        .stSelectbox > div > div > select:focus {
            border-color: #047857 !important;
            box-shadow: 0 0 0 1px #047857 !important;
        }
        .success-card {
            background-color: #064E3B;
            border: 1px solid #059669;
            border-radius: 8px;
            padding: 1.5rem;
            margin: 1rem 0;
            color: white;
        }
        .success-card a {
            color: #34D399;
            text-decoration: none;
            word-break: break-all;
        }
        .success-card a:hover {
            text-decoration: underline;
        }
        </style>
    """, unsafe_allow_html=True)
    
    # Campaign Creation Form
    with st.form("campaign_form"):
        # Basic Information
        st.markdown("#### Campaign Details")
        campaign_name = st.text_input(
            "Campaign Name",
            placeholder="Enter a unique name",
            help="A descriptive name for your campaign"
        )
        
        campaign_type = st.selectbox(
            "Campaign Type",
            options=list(CAMPAIGN_TYPES.keys()),
            format_func=lambda x: f"{CAMPAIGN_TYPES[x]} {x}"
        )
        
        original_url = st.text_input(
            "Original URL",
            placeholder="https://your-website.com",
            help="The URL you want to track"
        )

        # UTM Parameters (in an expander)
        with st.expander("UTM Parameters", expanded=False):
            col1, col2 = st.columns(2)
            with col1:
                utm_source = st.text_input("Source", placeholder="e.g., facebook")
                utm_campaign = st.text_input("Campaign Name", placeholder="e.g., summer_sale")
            with col2:
                utm_medium = st.text_input("Medium", placeholder="e.g., social")
                utm_content = st.text_input("Content", placeholder="e.g., banner_1")

        # Options
        generate_qr = st.checkbox("Generate QR Code", value=False)

        # Submit button
        submitted = st.form_submit_button(
            "Create Campaign", 
            type="primary",
            use_container_width=True
        )

    # Handle form submission
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
            
            if short_code:
                # Show success message with green theme
                st.success("Campaign created successfully!")
                
                # Display campaign details in a green card
                short_url = f"{BASE_URL}?r={short_code}"
                
                st.markdown(f"""
                    <div class="success-card">
                        <h4>🎯 Campaign Details</h4>
                        <p><strong>Campaign Name:</strong> {campaign_name}</p>
                        <p><strong>Short URL:</strong><br>
                        <a href="{short_url}" target="_blank">{short_url}</a></p>
                        <small>Click to test or copy to share</small>
                    </div>
                """, unsafe_allow_html=True)
                
                # Generate QR code if requested
                if generate_qr:
                    qr = qrcode.QRCode(version=1, box_size=10, border=4)
                    qr.add_data(short_url)
                    qr.make(fit=True)
                    img = qr.make_image(fill_color="black", back_color="white")
                    
                    # Convert to bytes
                    img_bytes = BytesIO()
                    img.save(img_bytes, format='PNG')
                    
                    # Display QR code with download button
                    col1, col2 = st.columns([1, 2])
                    with col1:
                        st.image(img_bytes, caption="QR Code")
                    with col2:
                        st.download_button(
                            "📥 Download QR Code",
                            data=img_bytes.getvalue(),
                            file_name=f"qr_{short_code}.png",
                            mime="image/png"
                        )

        except Exception as e:
            st.error(f"Error creating campaign: {str(e)}")

    # Show existing campaigns
    st.markdown("---")
    st.markdown("### 📊 Recent Campaigns")
    
    campaigns = shortener.db.get_all_campaigns()
    if campaigns:
        df = pd.DataFrame(campaigns)
        df['short_url'] = df['short_code'].apply(lambda x: f"{BASE_URL}?r={x}")
        
        st.dataframe(
            df,
            column_config={
                "campaign_name": st.column_config.TextColumn("Campaign"),
                "campaign_type": st.column_config.TextColumn("Type"),
                "short_url": st.column_config.LinkColumn("Short URL"),
                "total_clicks": st.column_config.NumberColumn("Clicks", format="%d"),
                "created_at": st.column_config.DateColumn("Created", format="MMM DD, YYYY"),
                "last_clicked": st.column_config.DateColumn("Last Click", format="MMM DD, YYYY")
            },
            hide_index=True,
            use_container_width=True
        )
    else:
        st.info("No campaigns created yet")

def render_settings(db: Database):
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
    """Render a single activity item with styling"""
    
    # Format timestamp
    try:
        timestamp = datetime.strptime(activity['clicked_at'], '%Y-%m-%d %H:%M:%S')
        formatted_time = timestamp.strftime('%b %d, %Y %I:%M %p')
    except:
        formatted_time = activity['clicked_at']
    
    # Get emoji for campaign type
    campaign_emojis = {
        "Social Media": "🔵",
        "Email": "📧",
        "Paid Ads": "💰",
        "Blog": "📝",
        "Affiliate": "🤝",
        "Other": "🔗"
    }
    campaign_emoji = campaign_emojis.get(activity.get('campaign_type'), '🔗')
    
    # Get emoji for device type
    device_emojis = {
        "Desktop": "💻",
        "Mobile": "📱",
        "Tablet": "📱",
        "Unknown": "❓"
    }
    device_emoji = device_emojis.get(activity.get('device_type'), '❓')
    
    st.markdown(f"""
        <div class="activity-item">
            <div class="activity-item-header">
                <span style='font-size: 1.25rem; margin-right: 0.5rem;'>{campaign_emoji}</span>
                {activity['campaign_name']}
            </div>
            <div class="activity-item-details">
                <span>{device_emoji} {activity['device_type']}</span>
                <span>📍 {activity.get('state', 'Unknown')}</span>
                <span>🕒 {formatted_time}</span>
            </div>
        </div>
    """, unsafe_allow_html=True)

def render_analytics(db: Database):
    st.markdown("### 📈 Campaign Analytics")

    # Advanced Filters Section
    with st.expander("📊 Advanced Filters", expanded=True):
        col1, col2, col3 = st.columns(3)
        
        with col1:
            # Date Range Filter
            date_filter = st.radio(
                "Date Range",
                ["Last 7 days", "Last 30 days", "Custom Range", "All Time"]
            )
            
            if date_filter == "Custom Range":
                start_date = st.date_input(
                    "Start Date",
                    value=datetime.now().date() - timedelta(days=7),
                    max_value=datetime.now().date()
                )
                end_date = st.date_input(
                    "End Date",
                    value=datetime.now().date(),
                    max_value=datetime.now().date()
                )
            else:
                if date_filter == "Last 7 days":
                    start_date = datetime.now().date() - timedelta(days=7)
                elif date_filter == "Last 30 days":
                    start_date = datetime.now().date() - timedelta(days=30)
                else:  # All Time
                    start_date = None
                end_date = datetime.now().date()

        with col2:
            # Campaign Filters
            campaign_type = st.multiselect(
                "Campaign Type",
                options=list(CAMPAIGN_TYPES.keys()),
                default=[]
            )
            
            device_type = st.multiselect(
                "Device Type",
                options=["Mobile", "Desktop", "Tablet"],
                default=[]
            )

        with col3:
            # Location Filter
            states = st.multiselect(
                "States",
                options=INDIAN_STATES,
                default=[]
            )
            
            # Traffic Source
            traffic_source = st.multiselect(
                "Traffic Source",
                options=["Direct", "Google", "Facebook", "Email", "Twitter"],
                default=[]
            )

    # Apply Filters button
    col1, col2, col3 = st.columns([2, 2, 1])
    with col3:
        apply_filters = st.button("Apply Filters", type="primary")
        
    # Get filtered analytics data
    stats = db.get_analytics_summary(
        start_date=start_date,
        end_date=end_date,
        campaign_types=campaign_type if campaign_type else None,
        device_types=device_type if device_type else None,
        states=states if states else None,
        sources=traffic_source if traffic_source else None
    )

    # Download Options
    with st.expander("📥 Download Data"):
        download_col1, download_col2 = st.columns(2)
        
        with download_col1:
            # Prepare CSV data
            if st.button("Download CSV"):
                csv_data = prepare_download_data(stats, 'csv')
                st.download_button(
                    label="📥 Download CSV",
                    data=csv_data,
                    file_name=f"analytics_{datetime.now().strftime('%Y%m%d')}.csv",
                    mime="text/csv"
                )
        
        with download_col2:
            # Prepare Excel data
            if st.button("Download Excel"):
                excel_data = prepare_download_data(stats, 'excel')
                st.download_button(
                    label="📥 Download Excel",
                    data=excel_data,
                    file_name=f"analytics_{datetime.now().strftime('%Y%m%d')}.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                )

    # Display Metrics (existing code...)
    metrics_cols = st.columns(4)
    with metrics_cols[0]:
        st.metric(
            "👆 Total Clicks",
            f"{stats['total_clicks']:,}",
            delta="+12% vs prev.",
            delta_color="normal"
        )
    with metrics_cols[1]:
        st.metric(
            "👥 Unique Visitors",
            f"{stats['unique_visitors']:,}",
            delta="+8% vs prev.",
            delta_color="normal"
        )
    with metrics_cols[2]:
        st.metric(
            "📅 Active Days",
            stats['active_days'],
            delta="+2 days",
            delta_color="normal"
        )
    with metrics_cols[3]:
        st.metric(
            "💫 Engagement Rate",
            f"{stats['engagement_rate']:.1f}%",
            delta="+1.2%",
            delta_color="normal"
        )

    # Charts Section
    st.markdown("---")
    
    # Traffic Overview
    chart_col1, chart_col2 = st.columns(2)
    with chart_col1:
        st.markdown("#### 📊 Traffic Overview")
        daily_df = pd.DataFrame([
            {'date': date, 'clicks': clicks}
            for date, clicks in stats['daily_stats'].items()
        ])
        if not daily_df.empty:
            daily_df['date'] = pd.to_datetime(daily_df['date'])
            daily_df = daily_df.sort_values('date')

            # Create combination chart (bars + line)
            fig = go.Figure()
            
            # Add bars for daily clicks
            fig.add_trace(go.Bar(
                x=daily_df['date'],
                y=daily_df['clicks'],
                name='Daily Clicks',
                marker=dict(
                    color='#10B981',
                    opacity=0.7,
                    line=dict(color='#064E3B', width=1)
                ),
                hovertemplate='<b>%{x|%Y-%m-%d}</b><br>Clicks: %{y:,}<extra></extra>'
            ))
            
            # Add line for trend
            fig.add_trace(go.Scatter(
                x=daily_df['date'],
                y=daily_df['clicks'].rolling(3).mean(),
                name='Trend',
                line=dict(color='#34D399', width=2),
                hovertemplate='<b>%{x|%Y-%m-%d}</b><br>Trend: %{y:.0f}<extra></extra>'
            ))

            fig.update_layout(
                plot_bgcolor='rgba(0,0,0,0)',
                paper_bgcolor='rgba(0,0,0,0)',
                margin=dict(l=20, r=20, t=30, b=20),
                legend=dict(
                    orientation="h",
                    yanchor="bottom",
                    y=1.02,
                    xanchor="right",
                    x=1
                ),
                xaxis=dict(
                    showgrid=False,
                    tickformat='%Y-%m-%d',
                    tickangle=-45
                ),
                yaxis=dict(
                    showgrid=True,
                    gridwidth=1,
                    gridcolor='rgba(16, 185, 129, 0.1)',
                    tickformat=',d'
                ),
                hoverlabel=dict(
                    bgcolor='#132C27',
                    font=dict(color='white')
                )
            )
            st.plotly_chart(fig, use_container_width=True)

    with chart_col2:
        st.markdown("#### 🌍 Geographic Distribution")
        if stats['state_stats']:
            state_df = pd.DataFrame([
                {'state': state, 'visits': visits}
                for state, visits in stats['state_stats'].items()
            ]).sort_values('visits', ascending=True)

            # Create horizontal bar chart
            fig = go.Figure(go.Bar(
                x=state_df['visits'],
                y=state_df['state'],
                orientation='h',
                marker=dict(
                    color='#10B981',
                    opacity=0.8,
                    line=dict(color='#064E3B', width=1)
                ),
                hovertemplate='<b>%{y}</b><br>Visits: %{x:,}<extra></extra>'
            ))

            fig.update_layout(
                plot_bgcolor='rgba(0,0,0,0)',
                paper_bgcolor='rgba(0,0,0,0)',
                margin=dict(l=20, r=20, t=30, b=20),
                xaxis=dict(
                    title='Visits',
                    showgrid=True,
                    gridwidth=1,
                    gridcolor='rgba(16, 185, 129, 0.1)',
                    tickformat=',d'
                ),
                yaxis=dict(
                    title=None,
                    showgrid=False
                ),
                hoverlabel=dict(
                    bgcolor='#132C27',
                    font=dict(color='white')
                )
            )
            st.plotly_chart(fig, use_container_width=True)

    # Device & Source Analysis
    st.markdown("---")
    device_col, source_col = st.columns(2)
    
    with device_col:
        st.markdown("#### 📱 Device Analysis")
        if stats.get('device_stats'):
            device_df = pd.DataFrame([
                {'device': device, 'sessions': count}
                for device, count in stats['device_stats'].items()
            ])
            
            fig = go.Figure(data=[go.Pie(
                labels=device_df['device'],
                values=device_df['sessions'],
                hole=.4,
                marker=dict(
                    colors=['#10B981', '#34D399', '#6EE7B7'],
                    line=dict(color='#064E3B', width=1)
                ),
                textinfo='label+percent',
                hovertemplate="<b>%{label}</b><br>Sessions: %{value:,}<br>(%{percent})<extra></extra>"
            )])
            
            fig.update_layout(
                showlegend=True,
                legend=dict(orientation="h", y=-0.1),
                plot_bgcolor='rgba(0,0,0,0)',
                paper_bgcolor='rgba(0,0,0,0)',
                margin=dict(l=20, r=20, t=30, b=50)
            )
            st.plotly_chart(fig, use_container_width=True)

    with source_col:
        st.markdown("#### 🔍 Traffic Sources")
        # Add traffic sources chart here
        sources = {
            'Direct': 45,
            'Social': 30,
            'Email': 15,
            'Referral': 10
        }
        source_df = pd.DataFrame([
            {'source': source, 'visits': count}
            for source, count in sources.items()
        ])
        
        fig = go.Figure(data=[go.Pie(
            labels=source_df['source'],
            values=source_df['visits'],
            hole=.4,
            marker=dict(
                colors=['#059669', '#10B981', '#34D399', '#6EE7B7'],
                line=dict(color='#064E3B', width=1)
            ),
            textinfo='label+percent',
            hovertemplate="<b>%{label}</b><br>Visits: %{value:,}<br>(%{percent})<extra></extra>"
        )])
        
        fig.update_layout(
            showlegend=True,
            legend=dict(orientation="h", y=-0.1),
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            margin=dict(l=20, r=20, t=30, b=50)
        )
        st.plotly_chart(fig, use_container_width=True)

def prepare_download_data(stats: Dict[str, Any], format_type: str) -> bytes:
    """Prepare analytics data for download"""
    # Create DataFrame for daily stats
    daily_df = pd.DataFrame([
        {
            'date': date,
            'clicks': clicks,
            'unique_visitors': stats['unique_visitors'],
            'engagement_rate': stats['engagement_rate']
        }
        for date, clicks in stats['daily_stats'].items()
    ])

    # Create DataFrame for device stats
    device_df = pd.DataFrame([
        {'device': device, 'count': count}
        for device, count in stats['device_stats'].items()
    ])

    # Create DataFrame for state stats
    state_df = pd.DataFrame([
        {'state': state, 'visits': visits}
        for state, visits in stats['state_stats'].items()
    ])

    # Create Excel writer object
    if format_type == 'excel':
        output = BytesIO()
        with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
            daily_df.to_excel(writer, sheet_name='Daily Stats', index=False)
            device_df.to_excel(writer, sheet_name='Device Stats', index=False)
            state_df.to_excel(writer, sheet_name='Geographic Stats', index=False)
            
            # Add summary sheet
            summary_data = {
                'Metric': ['Total Clicks', 'Unique Visitors', 'Active Days', 'Engagement Rate'],
                'Value': [
                    stats['total_clicks'],
                    stats['unique_visitors'],
                    stats['active_days'],
                    f"{stats['engagement_rate']:.2f}%"
                ]
            }
            pd.DataFrame(summary_data).to_excel(writer, sheet_name='Summary', index=False)
        
        return output.getvalue()
    else:  # CSV
        # Combine all data into one CSV
        output = BytesIO()
        daily_df.to_csv(output, index=False)
        output.write(b"\n\nDevice Statistics\n")
        device_df.to_csv(output, index=False)
        output.write(b"\n\nGeographic Statistics\n")
        state_df.to_csv(output, index=False)
        
        return output.getvalue()

def render_campaign_details(db: Database):
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

if __name__ == "__main__":
    main() 
