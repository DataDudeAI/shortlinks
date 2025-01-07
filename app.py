import streamlit as st
from database import Database
from ui import UI
import validators
import string
import random
from urllib.parse import urlparse, parse_qs, urlencode
import logging
from typing import Optional, Dict, Any
from datetime import datetime
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import json
from ui_styles import load_ui_styles

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
    initial_sidebar_state="collapsed"
)

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
        logger.info(f"Retrieved URL info: {url_info}")
        
        if url_info:
            original_url = url_info['original_url']
            logger.info(f"Redirecting to: {original_url}")
            
            # Track click
            self.db.increment_clicks(short_code)
            
            # Use JavaScript for immediate redirect
            js = f"""
                <script>
                    window.location.href = "{original_url}";
                </script>
                <noscript>
                    <meta http-equiv="refresh" content="0;url={original_url}">
                </noscript>
                <p>Redirecting to {original_url}...</p>
                <p>Click <a href="{original_url}">here</a> if not redirected automatically.</p>
            """
            st.markdown(js, unsafe_allow_html=True)
        else:
            st.error("Invalid or expired link")
            st.markdown(f"[← Back to URL Shortener]({BASE_URL})")

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

def main():
    # Initialize shortener
    shortener = URLShortener()

    # Main Header with Stats
    st.markdown("""
        <div class="header-accent">
            <span>🎯</span>
            <span style="background: linear-gradient(135deg, #00ff88 0%, #00bfff 100%); 
                     -webkit-background-clip: text;
                     -webkit-text-fill-color: transparent;
                     font-weight: 700;">
                Campaign Dashboard
            </span>
        </div>
    """, unsafe_allow_html=True)
    
    # Stats row
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        active_links = len(shortener.db.get_all_urls())
        st.metric("🔗 Active Links", active_links, f"+{active_links}")
    with col2:
        total_clicks = sum(url['total_clicks'] for url in shortener.db.get_all_urls())
        st.metric("👆 Total Clicks", f"{total_clicks:,}", "+15%")
    with col3:
        st.metric("📈 Conversion Rate", "4.2%", "+0.8%")
    with col4:
        st.metric("🎯 Active Campaigns", "5", "+2")

    # Tabs
    tab1, tab2, tab3 = st.tabs(["🎯 Create & Manage", "📊 Analytics", "⚙️ Bulk Operations"])

    with tab1:
        create_col, recent_col = st.columns([2, 1])
        
        with create_col:
            # Form for URL creation
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
                    logger.info("Form submitted - starting validation")
                    
                    if not url:
                        logger.warning("URL field is empty")
                        st.error("URL is required!")
                        return
                    
                    if not campaign_name:
                        logger.warning("Campaign name is empty")
                        st.error("Campaign name is required!")
                        return
                    
                    if not validators.url(url):
                        logger.warning(f"Invalid URL provided: {url}")
                        st.error("Please enter a valid URL!")
                        return
                    
                    logger.info(f"Creating new campaign '{campaign_name}' for URL: {url}")
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
                    
                    logger.info(f"Form data prepared: {form_data}")
                    
                    try:
                        short_code = shortener.create_campaign_url(form_data)
                        if short_code:
                            shortened_url = f"{BASE_URL}?r={short_code}"
                            logger.info(f"Campaign created successfully: {shortened_url}")
                            st.success(f"✨ Campaign '{campaign_name}' created successfully!")
                            st.code(shortened_url, language=None)
                            st.rerun()
                        else:
                            logger.error("Campaign creation failed")
                            st.error("Failed to create campaign. Please try again.")
                    except Exception as e:
                        logger.error(f"Error in form submission: {str(e)}", exc_info=True)
                        st.error("An error occurred while creating the campaign.")

        with recent_col:
            shortener.render_recent_links()

    with tab2:
        shortener.render_campaign_dashboard()

    with tab3:
        st.markdown("### Bulk Operations")
        # Add your bulk operations code here

if __name__ == "__main__":
    main() 
