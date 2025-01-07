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

    def create_short_url(self, url_data: dict) -> Optional[str]:
        """Create a shortened URL with optional UTM parameters"""
        if not url_data.get('url'):
            st.error('Please enter a URL')
            return None

        try:
            # Clean and validate URL
            cleaned_url = url_data['url'].strip()
            
            # Handle Facebook URLs
            if 'facebook.com' in cleaned_url or 'fb.com' in cleaned_url:
                if not cleaned_url.startswith(('http://', 'https://')):
                    cleaned_url = 'https://' + cleaned_url.lstrip('www.')
                logger.info(f"Processing Facebook URL: {cleaned_url}")
            else:
                if not cleaned_url.startswith(('http://', 'https://')):
                    cleaned_url = 'https://' + cleaned_url
                if not validators.url(cleaned_url):
                    st.error('Please enter a valid URL')
                    return None

            # Generate or use custom short code
            short_code = url_data.get('custom_code') or self.generate_short_code()
            
            # Save to database
            if self.db.save_url(
                url=cleaned_url,
                short_code=short_code,
                enable_tracking=url_data.get('tracking', True)
            ):
                logger.info(f"Successfully created short URL: {short_code}")
                return short_code
            else:
                st.error("Failed to save URL")
                return None

        except Exception as e:
            logger.error(f"Error creating short URL: {str(e)}")
            st.error("An error occurred while creating the short URL")
            return None

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
    capture_client_info()
    # Initialize shortener
    shortener = URLShortener()

    # Check for redirect parameter
    params = st.query_params
    if 'r' in params:
        short_code = params['r']
        shortener.handle_redirect(short_code)
        return

    # Get all campaigns data once at the start
    all_campaigns = shortener.db.get_all_urls()
    active_campaigns = [c for c in all_campaigns if c.get('is_active', True)]
    total_clicks = shortener.db.get_total_clicks()

    # Sidebar Menu
    with st.sidebar:
        st.markdown("### 🎯 Campaign Manager")
        selected_page = st.radio(
            "Navigation",
            ["📊 Dashboard", "🔗 Campaign Creator", "📈 Analytics", "⚙️ Settings"],
            index=0
        )

    # Main Header with Stats
    st.markdown("""
        <div class="main-header">
            <h1>Campaign Dashboard</h1>
        </div>
    """, unsafe_allow_html=True)

    if selected_page == "📊 Dashboard":
        # Stats row at the top
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("🔗 Active Campaigns", 
                     len(active_campaigns), 
                     f"+{len(active_campaigns)}")
        with col2:
            total_clicks = sum(campaign['total_clicks'] for campaign in active_campaigns)
            st.metric("👆 Total Clicks", 
                     f"{total_clicks:,}", 
                     f"+{total_clicks}")
        with col3:
            avg_clicks = total_clicks / len(active_campaigns) if active_campaigns else 0
            st.metric("📊 Avg. Clicks/Campaign", 
                     f"{avg_clicks:.1f}", 
                     "+0.8%")
        with col4:
            recent_clicks = shortener.db.get_recent_clicks_count(hours=24)
            st.metric("🎯 Recent Activity", 
                     f"{recent_clicks:,}", 
                     f"+{recent_clicks}")

        # Active Campaigns Section
        st.markdown("### 📈 Active Campaigns")
        
        # Filters and search
        col1, col2, col3 = st.columns([2,1,1])
        with col1:
            search = st.text_input("🔍 Search", placeholder="Search campaigns...")
        with col2:
            status_filter = st.selectbox("Status", ["All", "Active", "Inactive"])
        with col3:
            sort_by = st.selectbox("Sort by", ["Created", "Clicks", "Campaign Name"])

        # Create DataFrame for campaigns
        if active_campaigns:
            df = pd.DataFrame([
                {
                    'Campaign Name': c.get('campaign_name', c['short_code']),
                    'Original URL': c['original_url'],
                    'Short URL': f"{BASE_URL}?r={c['short_code']}",
                    'Created': datetime.strptime(c['created_at'], '%Y-%m-%d %H:%M:%S').strftime('%Y-%m-%d'),
                    'Total Clicks': c['total_clicks'],
                    'Status': 'Active',
                    'Actions': c['short_code']
                } for c in active_campaigns
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

            # Campaign Actions and Settings
            for _, row in df.iterrows():
                with st.expander(f"🎯 Campaign: {row['Campaign Name']}", expanded=False):
                    settings_tab, analytics_tab, social_tab = st.tabs(["⚙️ Settings", "📊 Analytics", "🌐 Social Media"])
                    
                    with analytics_tab:
                        st.markdown("#### Campaign Performance")
                        metric1, metric2, metric3 = st.columns(3)
                        with metric1:
                            st.metric("Total Clicks", row['Total Clicks'])
                        with metric2:
                            st.metric("Conversion Rate", "4.2%")
                        with metric3:
                            st.metric("Avg. Time on Page", "2m 34s")
                        
                        # Add click timeline chart
                        timeline_data = shortener.db.get_click_timeline(row['Actions'])
                        if not timeline_data.empty:
                            st.markdown("#### Click Timeline")
                            st.line_chart(
                                timeline_data,
                                use_container_width=True
                            )
                        else:
                            st.info("No click data available yet for this campaign")

    elif selected_page == "🔗 Campaign Creator":
        # Campaign Creation Form
        with st.form("url_shortener_form", clear_on_submit=True):
            st.markdown('<div class="section-header">Create Campaign URL</div>', unsafe_allow_html=True)
            
            # Basic URL Input
            url = st.text_input(
                "Long URL",
                placeholder="https://example.com",
                key="long_url_input"
            )
            
            # Campaign Details
            st.markdown('<div class="section-title">Campaign Details</div>', unsafe_allow_html=True)
            col1, col2, col3 = st.columns(3)
            with col1:
                campaign_name = st.text_input(
                    "Campaign Name*", 
                    placeholder="summer_sale_2024",
                    help="Campaign name must be unique",
                    key="campaign_name_input"
                )
            with col2:
                custom_code = st.text_input(
                    "Custom Short Code",
                    placeholder="summer24",
                    help="Leave empty for auto-generated code",
                    key="custom_code_input"
                )
            with col3:
                campaign_type = st.selectbox(
                    "Campaign Type",
                    options=list(CAMPAIGN_TYPES.keys()),
                    key="campaign_type_select"
                )

            # UTM Parameters
            st.markdown('<div class="section-title">UTM Parameters</div>', unsafe_allow_html=True)
            utm_col1, utm_col2, utm_col3 = st.columns(3)
            with utm_col1:
                utm_source = st.text_input(
                    "Source",
                    placeholder="facebook",
                    key="utm_source_input"
                )
                utm_medium = st.text_input(
                    "Medium",
                    placeholder="social",
                    key="utm_medium_input"
                )
            with utm_col2:
                utm_campaign = st.text_input(
                    "Campaign",
                    placeholder="summer_sale",
                    key="utm_campaign_input"
                )
                utm_content = st.text_input(
                    "Content",
                    placeholder="banner_1",
                    key="utm_content_input"
                )
            with utm_col3:
                utm_term = st.text_input(
                    "Term",
                    placeholder="summer_fashion",
                    key="utm_term_input"
                )

            submitted = st.form_submit_button(
                "Create Campaign URL",
                use_container_width=True,
                type="primary"
            )

            if submitted:
                if not url:
                    st.error("URL is required!")
                    return
                
                if not campaign_name:
                    st.error("Campaign name is required!")
                    return
                
                if not validators.url(url):
                    st.error("Please enter a valid URL!")
                    return
                
                form_data = {
                    'url': url,
                    'campaign_name': campaign_name,
                    'custom_code': custom_code,
                    'campaign_type': campaign_type,
                    'utm_source': utm_source,
                    'utm_medium': utm_medium,
                    'utm_campaign': utm_campaign,
                    'utm_content': utm_content,
                    'utm_term': utm_term
                }
                
                short_code = shortener.create_campaign_url(form_data)
                if short_code:
                    shortened_url = f"{BASE_URL}?r={short_code}"
                    st.success(f"✨ Campaign '{campaign_name}' created successfully!")
                    st.code(shortened_url, language=None)
                    st.rerun()
                else:
                    st.error("Failed to create campaign. Please try again.")

    elif selected_page == "📈 Analytics":
        st.markdown("### 📊 Analytics Dashboard")
        
        # Date Range and Campaign Selection
        col1, col2 = st.columns(2)
        with col1:
            date_range = st.date_input(
                "Date Range",
                value=[datetime.now().date() - timedelta(days=30), datetime.now().date()],
                key="analytics_date_range"
            )
        with col2:
            campaigns = shortener.db.get_all_urls()
            campaign_options = [c['campaign_name'] for c in campaigns]
            selected_campaign = st.selectbox(
                "Select Campaign",
                ["All Campaigns"] + campaign_options,
                key="analytics_campaign_select"
            )

        # Get analytics data
        short_code = next((c['short_code'] for c in campaigns 
                          if c['campaign_name'] == selected_campaign), None) \
                    if selected_campaign != "All Campaigns" else None
        
        analytics_data = shortener.db.get_analytics_summary(
            short_code=short_code,
            days=(datetime.now().date() - date_range[0]).days
        )
        
        # Performance Metrics
        st.markdown("#### 📊 Performance Overview")
        performance_df = shortener.db.get_campaign_performance(short_code)
        
        metric_cols = st.columns(4)
        with metric_cols[0]:
            total_clicks = performance_df['total_clicks'].sum()
            st.metric("Total Clicks", f"{total_clicks:,}")
        with metric_cols[1]:
            unique_visitors = performance_df['unique_visitors'].sum()
            st.metric("Unique Visitors", f"{unique_visitors:,}")
        with metric_cols[2]:
            countries = performance_df['countries_reached'].sum()
            st.metric("Countries Reached", countries)
        with metric_cols[3]:
            engagement = performance_df['engagement_rate'].mean()
            st.metric("Avg. Engagement Rate", f"{engagement:.1f}%")

        # Traffic Trends
        st.markdown("#### 📈 Traffic Trends")
        trend_tabs = st.tabs(["Daily Trend", "Hourly Distribution"])
        
        with trend_tabs[0]:
            daily_df = pd.DataFrame(
                analytics_data['daily_stats'].items(),
                columns=['Date', 'Clicks']
            )
            st.line_chart(daily_df.set_index('Date'))
            
        with trend_tabs[1]:
            hourly_df = pd.DataFrame(
                analytics_data['hourly_stats'].items(),
                columns=['Hour', 'Clicks']
            )
            fig = px.bar(hourly_df, x='Hour', y='Clicks',
                        title='Hourly Click Distribution')
            st.plotly_chart(fig, use_container_width=True)

        # Audience Insights
        st.markdown("#### 👥 Audience Insights")
        insight_cols = st.columns(3)
        
        with insight_cols[0]:
            st.markdown("**Device Breakdown**")
            device_df = pd.DataFrame(
                analytics_data['device_breakdown'].items(),
                columns=['Device', 'Count']
            )
            fig = px.pie(device_df, values='Count', names='Device',
                        title='Traffic by Device')
            st.plotly_chart(fig, use_container_width=True)
            
        with insight_cols[1]:
            st.markdown("**Browser Distribution**")
            browser_df = pd.DataFrame(
                analytics_data['browser_breakdown'].items(),
                columns=['Browser', 'Count']
            )
            fig = px.pie(browser_df, values='Count', names='Browser',
                        title='Traffic by Browser')
            st.plotly_chart(fig, use_container_width=True)
            
        with insight_cols[2]:
            st.markdown("**Top Countries**")
            country_df = pd.DataFrame(
                analytics_data['country_breakdown'].items(),
                columns=['Country', 'Visits']
            )
            fig = px.bar(country_df, x='Country', y='Visits',
                        title='Top Countries')
            st.plotly_chart(fig, use_container_width=True)

        # Campaign Details Table
        st.markdown("#### 🎯 Campaign Details")
        st.dataframe(
            performance_df,
            column_config={
                "campaign_name": "Campaign",
                "campaign_type": "Type",
                "total_clicks": st.column_config.NumberColumn("Total Clicks"),
                "unique_visitors": st.column_config.NumberColumn("Unique Visitors"),
                "countries_reached": st.column_config.NumberColumn("Countries"),
                "active_days": "Active Days",
                "engagement_rate": st.column_config.NumberColumn(
                    "Engagement Rate",
                    format="%.2f%%"
                )
            },
            hide_index=True,
            use_container_width=True
        )

    elif selected_page == "⚙️ Settings":
        st.markdown("### ⚙️ Settings")
        
        settings_tabs = st.tabs(["Overview", "Organization", "Campaign Settings", "Integrations"])
        
        with settings_tabs[0]:
            st.markdown("#### Dashboard Overview")
            
            # Organization & Campaign Stats
            overview_col1, overview_col2, overview_col3, overview_col4 = st.columns(4)
            with overview_col1:
                org_count = len(shortener.db.get_all_organizations()) if hasattr(shortener.db, 'get_all_organizations') else 0
                st.metric("Organizations", org_count)
            with overview_col2:
                connected_platforms = sum(1 for org in shortener.db.get_all_organizations() 
                                       if hasattr(shortener.db, 'get_all_organizations') 
                                       for platform, creds in org.get('social_media', {}).items() 
                                       if any(creds.values()))
                st.metric("Connected Platforms", connected_platforms)
            with overview_col3:
                active_campaigns = len([c for c in shortener.db.get_all_urls() if c.get('is_active', True)])
                st.metric("Active Campaigns", active_campaigns)
            with overview_col4:
                completed_campaigns = len([c for c in shortener.db.get_all_urls() if not c.get('is_active', True)])
                st.metric("Completed Campaigns", completed_campaigns)

        # Keep existing Organization tab
        with settings_tabs[1]:
            st.markdown("#### Organization Settings")
            # ... (keep existing organization settings code)

        with settings_tabs[2]:
            st.markdown("#### Campaign Settings")
            
            # Campaign Default Settings
            st.subheader("Default Campaign Settings")
            camp_col1, camp_col2 = st.columns(2)
            with camp_col1:
                st.selectbox("Default UTM Source", 
                            ["facebook", "twitter", "linkedin", "instagram", "email"],
                            key="default_utm_source_select")
                st.selectbox("Default Campaign Type", 
                            list(CAMPAIGN_TYPES.keys()),
                            key="default_campaign_type_select")
                st.text_input("Custom Domain", 
                            placeholder="links.yourdomain.com",
                            key="custom_domain_input")
            with camp_col2:
                st.checkbox("Auto-generate QR Codes", key="auto_qr_checkbox")
                st.checkbox("Enable Link Retargeting", key="link_retarget_checkbox")
                st.number_input("Default Link Expiry (days)", 
                              value=30,
                              key="link_expiry_input")

            # Campaign Features
            st.subheader("Campaign Features")
            feature_col1, feature_col2, feature_col3 = st.columns(3)
            with feature_col1:
                st.checkbox("Enable A/B Testing", key="ab_testing_checkbox")
                st.checkbox("Enable UTM Builder", key="utm_builder_checkbox")
            with feature_col2:
                st.checkbox("Enable QR Codes", key="qr_codes_checkbox")
                st.checkbox("Enable Deep Links", key="deep_links_checkbox")
            with feature_col3:
                st.checkbox("Enable Custom Domains", key="custom_domains_checkbox")
                st.checkbox("Enable Link Retargeting", key="retargeting_checkbox")

            # Campaign Analytics Settings
            st.subheader("Analytics Settings")
            analytics_col1, analytics_col2 = st.columns(2)
            with analytics_col1:
                st.checkbox("Track Click Location", key="track_location_checkbox")
                st.checkbox("Track Device Info", key="track_device_checkbox")
            with analytics_col2:
                st.checkbox("Track Referrer", key="track_referrer_checkbox")
                st.checkbox("Enable Conversion Tracking", key="conversion_tracking_checkbox")

        with settings_tabs[3]:
            st.markdown("#### Integrations")
            
            # Analytics Integrations
            st.subheader("Analytics Integrations")
            analytics_col1, analytics_col2 = st.columns(2)
            with analytics_col1:
                st.checkbox("Google Analytics", key="ga_checkbox")
                ga_id = st.text_input("Google Analytics ID", 
                                    type="password",
                                    key="ga_id_input")
            with analytics_col2:
                st.checkbox("Facebook Pixel", key="fb_pixel_checkbox")
                pixel_id = st.text_input("Facebook Pixel ID", 
                                       type="password",
                                       key="fb_pixel_id_input")

            # Marketing Integrations
            st.subheader("Marketing Tools")
            marketing_col1, marketing_col2, marketing_col3 = st.columns(3)
            with marketing_col1:
                st.checkbox("Mailchimp", key="mailchimp_checkbox")
                mailchimp_api = st.text_input("Mailchimp API Key", 
                                            type="password",
                                            key="mailchimp_api_input")
            with marketing_col2:
                st.checkbox("HubSpot", key="hubspot_checkbox")
                hubspot_api = st.text_input("HubSpot API Key", 
                                          type="password",
                                          key="hubspot_api_input")
            with marketing_col3:
                st.checkbox("Salesforce", key="salesforce_checkbox")
                salesforce_api = st.text_input("Salesforce API Key", 
                                             type="password",
                                             key="salesforce_api_input")

            # Automation Integrations
            st.subheader("Automation Tools")
            automation_col1, automation_col2 = st.columns(2)
            with automation_col1:
                st.checkbox("Zapier", key="zapier_checkbox")
                zapier_webhook = st.text_input("Zapier Webhook URL",
                                             key="zapier_webhook_input")
            with automation_col2:
                st.checkbox("Make.com (Integromat)", key="make_checkbox")
                make_webhook = st.text_input("Make.com Webhook URL",
                                           key="make_webhook_input")

            # Custom Webhooks
            st.subheader("Custom Webhooks")
            webhook_col1, webhook_col2 = st.columns(2)
            with webhook_col1:
                st.text_input("Webhook URL", key="webhook_url_input")
                st.multiselect(
                    "Trigger Events",
                    ["Link Created", "Link Clicked", "Campaign Updated", "Campaign Deleted"],
                    key="webhook_events_select"
                )
            with webhook_col2:
                st.selectbox("Webhook Method", 
                            ["POST", "GET", "PUT"],
                            key="webhook_method_select")
                st.text_area("Custom Headers (JSON)",
                            key="webhook_headers_input")

            # Save Integration Settings
            if st.button("Save Integration Settings", 
                        type="primary",
                        key="save_integrations_button"):
                st.success("Integration settings saved successfully!")

if __name__ == "__main__":
    main() 
