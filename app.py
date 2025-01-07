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

# Set dark theme
st.markdown("""
    <script>
        var observer = new MutationObserver(function(mutations) {
            if (document.querySelector('.stApp')) {
                document.querySelector('.stApp').classList.add('dark');
                observer.disconnect();
            }
        });
        
        observer.observe(document, {childList: true, subtree: true});
    </script>
""", unsafe_allow_html=True)

# Load styles once at the start
st.markdown(load_ui_styles(), unsafe_allow_html=True)

BASE_URL = "https://shortlinksnandan.streamlit.app"

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

class URLShortener:
    def __init__(self):
        """Initialize URL shortener with database connection"""
        try:
            self.db = Database()
            self.organization = Organization(self.db)
            # Ensure demo data exists
            self.db.ensure_demo_data()
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

    def create_short_url(self, url: str, campaign_name: str, campaign_type: str = None, utm_params: Dict = None) -> str:
        """Create a new short URL"""
        try:
            # Validate URL
            if not validators.url(url):
                raise ValueError("Invalid URL provided")

            # Generate short code
            short_code = self.generate_short_code()

            # Add UTM parameters if provided
            if utm_params:
                parsed_url = urlparse(url)
                query_params = parse_qs(parsed_url.query)
                
                # Add UTM parameters
                if utm_params.get('source'): query_params['utm_source'] = [utm_params['source']]
                if utm_params.get('medium'): query_params['utm_medium'] = [utm_params['medium']]
                if utm_params.get('campaign'): query_params['utm_campaign'] = [utm_params['campaign']]
                if utm_params.get('content'): query_params['utm_content'] = [utm_params['content']]
                
                # Reconstruct URL with UTM parameters
                url = parsed_url._replace(query=urlencode(query_params, doseq=True)).geturl()

            # Store in database
            success = self.db.add_url(
                short_code=short_code,
                original_url=url,
                campaign_name=campaign_name,
                campaign_type=campaign_type
            )

            if not success:
                raise Exception("Failed to save URL to database")

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
        """Render the analytics dashboard"""
        # Get analytics data
        analytics_data = self.db.get_analytics_summary()
        
        # Date filter
        col1, col2 = st.columns(2)
        with col1:
            st.date_input("Date Range", [])
        with col2:
            st.multiselect("Filter Campaigns", 
                          [c.get('campaign_name') for c in self.db.get_all_urls()])
        
        # Analytics Overview
        st.markdown("### 📊 Analytics Overview")
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Total Clicks", analytics_data.get('total_clicks', 0), "↑15%")
        with col2:
            st.metric("Unique Visitors", analytics_data.get('unique_visitors', 0), "↑10%")
        with col3:
            st.metric("Avg. Time on Page", "2m 34s", "↑5%")
        with col4:
            st.metric("Bounce Rate", "32%", "↓2%")

        # Charts
        col1, col2 = st.columns(2)
        with col1:
            if analytics_data['daily_stats']:
                df = pd.DataFrame(list(analytics_data['daily_stats'].items()), 
                                columns=['Date', 'Clicks'])
                fig = px.line(df, x='Date', y='Clicks', 
                             title='Daily Click Trends')
                st.plotly_chart(fig, use_container_width=True)

        with col2:
            if analytics_data['device_breakdown']:
                df = pd.DataFrame(list(analytics_data['device_breakdown'].items()),
                                columns=['Device', 'Count'])
                fig = px.pie(df, values='Count', names='Device',
                            title='Device Distribution')
                st.plotly_chart(fig, use_container_width=True)

        # Campaign Performance Table
        st.markdown("### 🎯 Campaign Performance")
        performance_data = self.db.get_campaign_performance()
        if not performance_data.empty:
            st.dataframe(
                performance_data,
                column_config={
                    "campaign_name": "Campaign",
                    "total_clicks": st.column_config.NumberColumn("Clicks"),
                    "unique_visitors": st.column_config.NumberColumn("Unique Visitors"),
                    "engagement_rate": st.column_config.NumberColumn("Engagement", format="%.2f%%"),
                    "active_days": st.column_config.NumberColumn("Active Days")
                },
                hide_index=True,
                use_container_width=True
            )

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
        # Get client IP (in production, you'd get this from request headers)
        st.session_state['client_ip'] = '127.0.0.1'  # Default for local testing
        
        # Get user agent from query params as fallback
        params = st.query_params
        user_agent = params.get('user_agent', 'Unknown')
        st.session_state['user_agent'] = user_agent
        
        # Basic device/browser detection from user agent
        st.session_state['device_type'] = 'Mobile' if 'Mobile' in user_agent else 'Desktop'
        
        # Basic browser detection
        browsers = ['Chrome', 'Firefox', 'Safari', 'Edge']
        st.session_state['browser'] = next((b for b in browsers if b in user_agent), 'Other')
        
        # Basic OS detection
        os_list = ['Windows', 'Mac', 'Linux', 'Android', 'iOS']
        st.session_state['os'] = next((os for os in os_list if os in user_agent), 'Other')
        
        # Set default values for other fields
        st.session_state['referrer'] = params.get('ref', 'Direct')
        st.session_state['country'] = params.get('country', 'Unknown')
        st.session_state['city'] = params.get('city', 'Unknown')
        
    except Exception as e:
        logger.error(f"Error capturing client info: {str(e)}")

def main():
    # Initialize components
    auto_collapse_sidebar()
    capture_client_info()
    
    # Initialize shortener
    shortener = URLShortener()
    
    # Get all campaigns data once at the start
    all_campaigns = shortener.db.get_all_urls()
    active_campaigns = [c for c in all_campaigns if c.get('is_active', True)]
    dashboard_metrics = shortener.db.get_dashboard_metrics()
    
    # Sidebar Menu
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

    # Main Content Area
    if selected_page == "📊 Dashboard":
        st.markdown("""
            <div class="main-header">
                <h1>Campaign Dashboard</h1>
            </div>
        """, unsafe_allow_html=True)

        # Top Metrics
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Active Campaigns", 
                     dashboard_metrics["active_campaigns"]["value"],
                     dashboard_metrics["active_campaigns"]["growth"])
        with col2:
            st.metric("Total Clicks", 
                     dashboard_metrics["total_clicks"]["value"],
                     dashboard_metrics["total_clicks"]["growth"])
        with col3:
            st.metric("Conversion Rate", 
                     dashboard_metrics["conversion_rate"]["value"],
                     dashboard_metrics["conversion_rate"]["growth"])
        with col4:
            st.metric("ROI", 
                     dashboard_metrics["roi"]["value"],
                     dashboard_metrics["roi"]["growth"])

        # Recent Activity and Campaign Performance
        col1, col2 = st.columns([2,1])
        
        with col1:
            st.markdown("### 📈 Recent Activity")
            recent_activities = shortener.db.get_recent_activity()
            if recent_activities:
                for activity in recent_activities:
                    clicked_at = datetime.strptime(activity['clicked_at'], '%Y-%m-%d %H:%M:%S')
                    now = datetime.now()
                    time_diff = now - clicked_at
                    
                    if time_diff.days > 0:
                        time_ago = f"{time_diff.days} days ago"
                    elif time_diff.seconds > 3600:
                        hours = time_diff.seconds // 3600
                        time_ago = f"{hours} hours ago"
                    elif time_diff.seconds > 60:
                        minutes = time_diff.seconds // 60
                        time_ago = f"{minutes} minutes ago"
                    else:
                        time_ago = "just now"
                    
                    st.markdown(f"""
                        <div class="activity-item">
                            🔗 <strong>{activity['campaign_name']}</strong> was clicked from 
                            {activity['country']} on {activity['device_type']}
                            <span class="activity-time">({time_ago})</span>
                        </div>
                    """, unsafe_allow_html=True)
            else:
                st.info("No recent activity to display")

        with col2:
            st.markdown("### 🌍 Top Countries")
            analytics_data = shortener.db.get_analytics_summary()
            if analytics_data.get('country_breakdown'):
                df = pd.DataFrame(list(analytics_data['country_breakdown'].items()),
                                columns=['Country', 'Visits'])
                df = df.sort_values('Visits', ascending=True).tail(5)
                fig = px.bar(df, x='Visits', y='Country', orientation='h',
                           template="plotly_dark")
                fig.update_layout(
                    plot_bgcolor='rgba(0,0,0,0)',
                    paper_bgcolor='rgba(0,0,0,0)',
                    margin=dict(l=20, r=20, t=30, b=20),
                    height=200  # Reduced height
                )
                st.plotly_chart(fig, use_container_width=True)

        # Campaign Performance
        st.markdown("### 🎯 Campaign Performance")
        performance_data = shortener.db.get_campaign_performance()
        if not performance_data.empty:
            st.dataframe(
                performance_data,
                column_config={
                    "campaign_name": "Campaign",
                    "total_clicks": st.column_config.NumberColumn("Clicks"),
                    "unique_visitors": st.column_config.NumberColumn("Unique Visitors"),
                    "engagement_rate": st.column_config.NumberColumn("Engagement", format="%.2f%%"),
                    "active_days": st.column_config.NumberColumn("Active Days")
                },
                hide_index=True,
                use_container_width=True
            )

        # Analytics Overview at the bottom
        st.markdown("### 📊 Analytics Overview")
        
        # Filters in a more compact layout
        with st.expander("📅 Filter Analytics", expanded=False):
            fcol1, fcol2 = st.columns(2)
            with fcol1:
                st.date_input("Date Range", [])
            with fcol2:
                st.multiselect("Campaigns", 
                             [c.get('campaign_name') for c in all_campaigns])

        # Analytics charts in a responsive layout
        chart_col1, chart_col2 = st.columns(2)
        
        with chart_col1:
            if analytics_data['daily_stats']:
                df = pd.DataFrame(list(analytics_data['daily_stats'].items()), 
                                columns=['Date', 'Clicks'])
                fig = px.line(df, x='Date', y='Clicks',
                            template="plotly_dark",
                            line_shape="spline")
                fig.update_layout(
                    plot_bgcolor='rgba(0,0,0,0)',
                    paper_bgcolor='rgba(0,0,0,0)',
                    margin=dict(l=20, r=20, t=30, b=20),
                    height=300,  # Fixed height
                    title={
                        'text': "Click Trends",
                        'y':0.95,
                        'x':0.5,
                        'xanchor': 'center',
                        'yanchor': 'top'
                    }
                )
                st.plotly_chart(fig, use_container_width=True)

        with chart_col2:
            if analytics_data['device_breakdown']:
                df = pd.DataFrame(list(analytics_data['device_breakdown'].items()),
                                columns=['Device', 'Count'])
                fig = px.pie(df, values='Count', names='Device',
                           template="plotly_dark",
                           hole=0.4)
                fig.update_layout(
                    plot_bgcolor='rgba(0,0,0,0)',
                    paper_bgcolor='rgba(0,0,0,0)',
                    margin=dict(l=20, r=20, t=30, b=20),
                    height=300,  # Fixed height
                    title={
                        'text': "Device Distribution",
                        'y':0.95,
                        'x':0.5,
                        'xanchor': 'center',
                        'yanchor': 'top'
                    }
                )
                st.plotly_chart(fig, use_container_width=True)

    elif selected_page == "🔗 Create Campaign":
        st.markdown("""
            <div class="main-header">
                <h1>Create Campaign</h1>
            </div>
        """, unsafe_allow_html=True)
        
        # Campaign Creation Form
        with st.form("campaign_form"):
            campaign_name = st.text_input("Campaign Name")
            original_url = st.text_input("Original URL")
            campaign_type = st.selectbox("Campaign Type", list(CAMPAIGN_TYPES.keys()))
            
            col1, col2 = st.columns(2)
            with col1:
                utm_source = st.text_input("UTM Source", placeholder="e.g., facebook")
                utm_medium = st.text_input("UTM Medium", placeholder="e.g., social")
            with col2:
                utm_campaign = st.text_input("UTM Campaign", placeholder="e.g., summer_sale")
                utm_content = st.text_input("UTM Content", placeholder="e.g., banner_1")

            # QR Code Options
            st.markdown("### 📱 QR Code Options")
            qr_col1, qr_col2 = st.columns(2)
            with qr_col1:
                generate_qr = st.checkbox("Generate QR Code", value=True)
                qr_foreground = st.color_picker("QR Code Color", "#000000")
            with qr_col2:
                qr_size = st.slider("QR Code Size", 100, 500, 200)
                qr_background = st.color_picker("Background Color", "#FFFFFF")

            submitted = st.form_submit_button("Create Campaign", type="primary", use_container_width=True)
            
            if submitted and campaign_name and original_url:
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
                
                # Show success message with short URL
                short_url = f"{BASE_URL}?r={short_code}"
                st.success(f"Campaign created successfully! Short URL: {short_url}")

                # Generate and display QR code if selected
                if generate_qr:
                    try:
                        qr = qrcode.QRCode(
                            version=1,
                            error_correction=qrcode.constants.ERROR_CORRECT_L,
                            box_size=10,
                            border=4,
                        )
                        qr.add_data(short_url)
                        qr.make(fit=True)

                        # Create QR code image with selected colors
                        qr_img = qr.make_image(
                            fill_color=qr_foreground,
                            back_color=qr_background
                        )
                        
                        # Convert PIL image to bytes for display and download
                        img_byte_arr = BytesIO()
                        qr_img.save(img_byte_arr, format='PNG')
                        img_byte_arr = img_byte_arr.getvalue()

                        # Display QR code
                        st.markdown("### 📱 Campaign QR Code")
                        col1, col2, col3 = st.columns([1,2,1])
                        with col2:
                            st.image(img_byte_arr, width=qr_size)
                            
                            # Safe filename for download
                            safe_filename = "".join(x for x in campaign_name if x.isalnum() or x in (' ', '-', '_'))
                            safe_filename = f"qr_code_{safe_filename}.png"
                            
                            # Download button with proper error handling
                            try:
                                st.download_button(
                                    label="⬇️ Download QR Code",
                                    data=img_byte_arr,
                                    file_name=safe_filename,
                                    mime="image/png",
                                    use_container_width=True
                                )
                            except Exception as e:
                                st.error(f"Error creating download button: {str(e)}")
                                logger.error(f"Download button error: {str(e)}")
                    
                    except Exception as e:
                        st.error(f"Error generating QR code: {str(e)}")
                        logger.error(f"QR code generation error: {str(e)}")

    elif selected_page == "📈 Analytics":
        shortener.render_analytics_dashboard()

    elif selected_page == "⚙️ Settings":
        st.markdown("""
            <div class="main-header">
                <h1>Settings</h1>
            </div>
        """, unsafe_allow_html=True)
        
        settings_tab1, settings_tab2 = st.tabs(["General", "Integrations"])
        
        with settings_tab1:
            st.markdown("### General Settings")
            st.text_input("Default UTM Source")
            st.text_input("Custom Domain")
            st.checkbox("Auto-generate QR Codes")
            
        with settings_tab2:
            st.markdown("### Integration Settings")
            st.text_input("API Key")
            st.text_input("Webhook URL")

if __name__ == "__main__":
    main() 
