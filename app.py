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

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Must be the first Streamlit command
st.set_page_config(
    page_title="Campaign URL Manager",
    page_icon="🎯",
    layout="wide"
)

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
        self.db = Database()
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

        # Campaign Actions
        st.markdown("### Campaign Actions")
        action_cols = st.columns(3)
        
        with action_cols[0]:
            with st.expander("🎯 New Campaign", expanded=False):
                self.render_campaign_creator()
                
        with action_cols[1]:
            with st.expander("📊 Analytics", expanded=False):
                self.render_campaign_analytics()
                
        with action_cols[2]:
            with st.expander("⚙️ Settings", expanded=False):
                self.render_campaign_settings()

        # Active Campaigns Table
        st.markdown("### 📈 Active Campaigns")
        self.render_active_campaigns()

    def render_campaign_creator(self):
        """Enhanced campaign creation interface"""
        campaign_type = st.selectbox(
            "Campaign Type",
            ["Social Media", "Email", "Paid Ads", "Blog", "Affiliate"]
        )
        
        # Campaign Details
        st.text_input("Campaign Name", placeholder="Summer Sale 2024")
        cols = st.columns(2)
        with cols[0]:
            st.date_input("Start Date")
        with cols[1]:
            st.date_input("End Date")
            
        # UTM Parameters
        st.markdown("#### UTM Parameters")
        utm_cols = st.columns(2)
        with utm_cols[0]:
            st.text_input("Source", placeholder="facebook")
            st.text_input("Campaign", placeholder="summer_sale")
        with utm_cols[1]:
            st.text_input("Medium", placeholder="social")
            st.text_input("Content", placeholder="banner_1")
            
        # Advanced Options
        with st.expander("🔧 Advanced Options"):
            st.checkbox("Enable A/B Testing")
            st.checkbox("Generate QR Code")
            st.checkbox("Enable Link Retargeting")
            st.selectbox("Link Expiry", ["Never", "24 hours", "7 days", "30 days", "Custom"])
            
        if st.button("Create Campaign", type="primary", use_container_width=True):
            st.success("Campaign created successfully!")

    def render_campaign_analytics(self):
        """Enhanced analytics dashboard"""
        # Time Range Selector
        col1, col2 = st.columns([3, 1])
        with col1:
            st.date_input("Date Range", value=[datetime.now(), datetime.now()])
        with col2:
            st.selectbox("Preset", ["Last 7 days", "Last 30 days", "Custom"])
            
        # Performance Metrics
        for metric, icon in CAMPAIGN_METRICS.items():
            st.metric(f"{icon} {metric}", "1,234", "↑12%")
            
        # Charts would go here (using Plotly or other libraries)
        st.line_chart({"data": [1, 5, 2, 6, 2, 1]})

    def render_campaign_settings(self):
        """Campaign settings interface"""
        st.selectbox("Default UTM Source", ["facebook", "twitter", "linkedin"])
        st.selectbox("Default Campaign Type", list(CAMPAIGN_TYPES.keys()))
        st.text_input("Custom Domain", placeholder="links.yourdomain.com")
        st.checkbox("Auto-generate QR Codes")
        st.checkbox("Enable Link Retargeting")
        st.number_input("Default Link Expiry (days)", value=30)

    def render_active_campaigns(self):
        """Display active campaigns in a modern table view"""
        campaigns = self.db.get_all_urls()  # Get all campaigns
        
        if not campaigns:
            st.info("No active campaigns yet. Create your first campaign above!")
            return

        # Create DataFrame for better table display
        df = pd.DataFrame([
            {
                'Campaign Name': c.get('campaign_name', c['short_code']),
                'Original URL': c['original_url'],
                'Short URL': f"{BASE_URL}?r={c['short_code']}",
                'Created': datetime.strptime(c['created_at'], '%Y-%m-%d %H:%M:%S').strftime('%Y-%m-%d'),
                'Total Clicks': c['total_clicks'],
                'Unique Clicks': self.db.get_unique_clicks_count(c['short_code']),
                'Last Click': self.db.get_last_click_date(c['short_code']).strftime('%Y-%m-%d') if self.db.get_last_click_date(c['short_code']) else "Never",
                'Status': 'Active',
                'Actions': c['short_code']  # We'll use this for action buttons
            } for c in campaigns
        ])

        # Add filters above the table
        col1, col2, col3 = st.columns([2,1,1])
        with col1:
            search = st.text_input("🔍 Search", placeholder="Search campaigns...")
        with col2:
            status_filter = st.selectbox("Status", ["All", "Active", "Inactive"])
        with col3:
            sort_by = st.selectbox("Sort by", ["Created", "Clicks", "Campaign Name"])

        # Apply filters
        if search:
            df = df[
                df['Campaign Name'].str.contains(search, case=False) |
                df['Original URL'].str.contains(search, case=False) |
                df['Short URL'].str.contains(search, case=False)
            ]

        # Sort DataFrame
        if sort_by == "Clicks":
            df = df.sort_values('Total Clicks', ascending=False)
        elif sort_by == "Campaign Name":
            df = df.sort_values('Campaign Name')
        else:  # Created
            df = df.sort_values('Created', ascending=False)

        # Display table with custom formatting
        st.markdown("### Your Campaign Links")
        
        # Use AgGrid or custom styled dataframe
        st.dataframe(
            df,
            column_config={
                "Campaign Name": st.column_config.TextColumn(
                    "Campaign Name",
                    width="medium",
                ),
                "Original URL": st.column_config.LinkColumn(
                    "Original URL",
                    width="medium",
                ),
                "Short URL": st.column_config.LinkColumn(
                    "Short URL",
                    width="medium",
                    help="Click to copy"
                ),
                "Total Clicks": st.column_config.NumberColumn(
                    "Clicks",
                    help="Total number of clicks"
                ),
                "Unique Clicks": st.column_config.NumberColumn(
                    "Unique",
                    help="Unique visitors"
                ),
                "Created": st.column_config.DateColumn(
                    "Created",
                    format="YYYY-MM-DD"
                ),
                "Last Click": st.column_config.DateColumn(
                    "Last Click",
                    format="YYYY-MM-DD"
                ),
                "Status": st.column_config.TextColumn(
                    "Status",
                    width="small"
                )
            },
            hide_index=True,
            use_container_width=True
        )

        # Action buttons below each row
        for _, row in df.iterrows():
            with st.expander(f"Actions for {row['Campaign Name']}", expanded=False):
                col1, col2, col3, col4 = st.columns(4)
                with col1:
                    if st.button("📊 Analytics", key=f"stats_{row['Actions']}"):
                        stats = self.db.get_campaign_stats(row['Actions'])
                        st.json(stats)
                with col2:
                    if st.button("✏️ Edit", key=f"edit_{row['Actions']}"):
                        st.session_state.editing_campaign = row['Actions']
                        campaign_details = self.db.get_campaign_details(row['Actions'])
                        if campaign_details:
                            self.render_campaign_editor(campaign_details)
                with col3:
                    if st.button("🔗 Copy URL", key=f"copy_{row['Actions']}"):
                        st.code(row['Short URL'])
                        st.toast("URL copied to clipboard!")
                with col4:
                    if st.button("🗑️ Delete", key=f"delete_{row['Actions']}"):
                        if st.button("Confirm Delete", key=f"confirm_delete_{row['Actions']}"):
                            if self.db.delete_campaign(row['Actions']):
                                st.success("Campaign deleted successfully!")
                                st.rerun()

        # Add export options
        st.markdown("### Export Data")
        col1, col2 = st.columns(2)
        with col1:
            if st.button("📥 Export to CSV"):
                csv = df.to_csv(index=False).encode('utf-8')
                st.download_button(
                    "Download CSV",
                    csv,
                    "campaign_data.csv",
                    "text/csv",
                    key='download-csv'
                )
        with col2:
            if st.button("📊 Export Analytics"):
                # Create detailed analytics export
                analytics_data = {
                    'campaign_data': df.to_dict('records'),
                    'export_date': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                    'total_campaigns': len(df),
                    'total_clicks': df['Total Clicks'].sum()
                }
                json_str = json.dumps(analytics_data, indent=2)
                st.download_button(
                    "Download Analytics JSON",
                    json_str,
                    "campaign_analytics.json",
                    "application/json",
                    key='download-json'
                )

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
        """Create a campaign URL with all parameters"""
        if not form_data.get('url'):
            st.error('Please enter a URL')
            return None

        try:
            # Clean and validate URL
            cleaned_url = form_data['url'].strip()
            if not cleaned_url.startswith(('http://', 'https://')):
                cleaned_url = 'https://' + cleaned_url

            if not validators.url(cleaned_url):
                st.error('Please enter a valid URL')
                return None

            # Build UTM parameters
            utm_params = {
                'utm_source': form_data.get('utm_source', ''),
                'utm_medium': form_data.get('utm_medium', ''),
                'utm_campaign': form_data.get('utm_campaign', ''),
                'utm_content': form_data.get('utm_content', ''),
                'utm_term': form_data.get('utm_term', '')
            }
            
            # Filter out empty UTM parameters
            utm_params = {k: v for k, v in utm_params.items() if v}
            
            # Add UTM parameters to URL if any exist
            if utm_params:
                parsed_url = urlparse(cleaned_url)
                existing_params = parse_qs(parsed_url.query)
                # Combine existing and new parameters
                all_params = {**existing_params, **utm_params}
                # Create new query string
                new_query = urlencode(all_params, doseq=True)
                # Reconstruct URL with UTM parameters
                cleaned_url = parsed_url._replace(query=new_query).geturl()

            # Generate or use custom short code
            short_code = form_data.get('custom_code') or self.generate_short_code()
            
            # Save to database with campaign info
            if self.db.save_campaign_url(
                url=cleaned_url,
                short_code=short_code,
                campaign_name=form_data.get('campaign_name', ''),
                campaign_type=form_data.get('campaign_type', ''),
                utm_params=utm_params,
                expiry_date=form_data.get('expiry_date'),
                enable_tracking=form_data.get('track_conversions', True)
            ):
                logger.info(f"Successfully created campaign URL: {short_code}")
                return short_code
            else:
                st.error("Failed to save campaign URL")
                return None

        except Exception as e:
            logger.error(f"Error creating campaign URL: {str(e)}")
            st.error("An error occurred while creating the campaign URL")
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
        unique_clicks = sum(self.db.get_unique_clicks_count(link['short_code']) for link in recent_links)
        
        metrics_col1, metrics_col2 = st.columns(2)
        with metrics_col1:
            st.metric("Total Clicks (Recent)", total_clicks)
        with metrics_col2:
            st.metric("Unique Visitors (Recent)", unique_clicks)
        
        # Display recent links in a modern table
        df = pd.DataFrame([
            {
                'Campaign': link.get('campaign_name', link['short_code']),
                'Short URL': f"{BASE_URL}?r={link['short_code']}",
                'Created': datetime.strptime(link['created_at'], '%Y-%m-%d %H:%M:%S').strftime('%Y-%m-%d %H:%M'),
                'Clicks': link['total_clicks'],
                'Unique': self.db.get_unique_clicks_count(link['short_code']),
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
                "Unique": st.column_config.NumberColumn("Unique Clicks", format="%d"),
                "Last Click": st.column_config.DatetimeColumn("Last Activity", format="D MMM, HH:mm")
            },
            hide_index=True,
            use_container_width=True
        )

def main():
    # Initialize shortener
    shortener = URLShortener()
    
    # Check for redirect parameter first - using st.query_params instead of experimental
    if 'r' in st.query_params:
        short_code = st.query_params['r']  # No need for [0] as it's not a list anymore
        shortener.handle_redirect(short_code)
        return

    # Main Header with Stats
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        active_links = len(shortener.db.get_all_urls())
        st.metric("Active Links", active_links, "↑12")
    with col2:
        total_clicks = sum(url['total_clicks'] for url in shortener.db.get_all_urls())
        st.metric("Total Clicks", f"{total_clicks:,}", "↑15%")
    with col3:
        st.metric("Conversion Rate", "4.2%", "↑0.8%")
    with col4:
        st.metric("Active Campaigns", "5", "↑2")

    # Main Content in Tabs
    tab1, tab2, tab3 = st.tabs(["🎯 Create & Manage", "📊 Analytics", "⚙️ Bulk Operations"])

    with tab1:
        # Split the tab into two sections
        create_col, recent_col = st.columns([2, 1])
        
        with create_col:
            # URL Creation Form
            with st.form("url_shortener_form", clear_on_submit=True):
                st.subheader("Create Campaign URL")
                
                # Basic URL Input
                url = st.text_input("Long URL", placeholder="https://example.com")
                
                # Campaign Details
                col1, col2, col3 = st.columns(3)
                with col1:
                    campaign_name = st.text_input("Campaign Name", placeholder="summer_sale_2024")
                with col2:
                    custom_code = st.text_input("Custom Short Code (optional)", placeholder="summer24")
                with col3:
                    campaign_type = st.selectbox("Campaign Type", 
                        ["Social Media", "Email", "Paid Ads", "Blog", "Affiliate"])

                # UTM Parameters
                st.markdown("### UTM Parameters")
                utm_col1, utm_col2, utm_col3 = st.columns(3)
                with utm_col1:
                    utm_source = st.text_input("Source", placeholder="facebook")
                    utm_medium = st.text_input("Medium", placeholder="social")
                with utm_col2:
                    utm_campaign = st.text_input("Campaign", placeholder="summer_sale")
                    utm_content = st.text_input("Content", placeholder="banner_1")
                with utm_col3:
                    utm_term = st.text_input("Term", placeholder="summer_fashion")
                    
                # Advanced Options in Expander
                with st.expander("Advanced Options"):
                    adv_col1, adv_col2 = st.columns(2)
                    with adv_col1:
                        st.checkbox("Generate QR Code")
                        st.checkbox("Enable Link Retargeting")
                        st.checkbox("Track Conversions")
                    with adv_col2:
                        st.selectbox("Link Expiry", ["Never", "24 hours", "7 days", "30 days"])
                        st.selectbox("Target Device", ["All", "Mobile Only", "Desktop Only"])
                        st.selectbox("Geo Targeting", ["Global", "US Only", "Europe", "Asia"])

                submitted = st.form_submit_button("Create Campaign URL", use_container_width=True)
        
        with recent_col:
            # Show recent links
            shortener.render_recent_links()

        # Active Campaigns Table
        st.markdown("### Active Campaign URLs")
        
        # Filter and Search
        col1, col2, col3 = st.columns([2,1,1])
        with col1:
            st.text_input("🔍 Search URLs", placeholder="Search by name, URL or tags...")
        with col2:
            st.multiselect("Campaign Type", ["Social", "Email", "Ads", "Blog"])
        with col3:
            st.selectbox("Sort by", ["Created Date ↓", "Clicks ↓", "Conversion Rate ↓"])

        # Campaign URLs Table
        for i in range(3):  # Example campaigns
            with st.container():
                col1, col2, col3, col4 = st.columns([3,2,2,1])
                with col1:
                    st.markdown(f"**Campaign {i+1}**")
                    st.markdown("Original: `https://example.com/very-long-url...`")
                    st.markdown("Short: `https://short.link/abc123`")
                with col2:
                    st.metric("Clicks", "1,234")
                    st.metric("Conversions", "123")
                with col3:
                    st.metric("CTR", "4.5%")
                    st.metric("ROI", "$123")
                with col4:
                    st.button("📊", key=f"stats_{i}")
                    st.button("✏️", key=f"edit_{i}")
                    st.button("📱", key=f"qr_{i}")
                st.divider()

        if submitted:
            form_data = {
                'url': url,
                'campaign_name': campaign_name,
                'custom_code': custom_code,
                'campaign_type': campaign_type,
                'utm_source': utm_source,
                'utm_medium': utm_medium,
                'utm_campaign': utm_campaign,
                'utm_content': utm_content,
                'utm_term': utm_term,
                'track_conversions': st.session_state.get('track_conversions', True),
                'expiry_date': st.session_state.get('expiry_date', None)
            }
            
            short_code = shortener.create_campaign_url(form_data)
            if short_code:
                shortened_url = f"{BASE_URL}?r={short_code}"
                st.success("✨ Campaign URL created successfully!")
                st.code(shortened_url, language=None)
                
                # Show QR code if enabled
                if st.session_state.get('generate_qr', False):
                    qr = shortener.generate_qr_code(shortened_url)
                    st.image(qr, caption="Scan this QR code")

    with tab2:
        # Analytics Overview
        st.subheader("Campaign Performance")
        
        # Date Range Selector
        col1, col2 = st.columns([3,1])
        with col1:
            st.date_input("Date Range", value=[datetime.now(), datetime.now()])
        with col2:
            st.selectbox("Quick Range", ["Last 7 days", "Last 30 days", "Custom"])

        # Performance Metrics
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Total Clicks", "12,345", "↑10%")
        with col2:
            st.metric("Unique Visitors", "8,234", "↑5%")
        with col3:
            st.metric("Conversion Rate", "3.2%", "↑0.5%")
        with col4:
            st.metric("Avg. Time on Site", "2m 34s", "↑15%")

        # Performance Charts
        chart_col1, chart_col2 = st.columns(2)
        with chart_col1:
            st.markdown("### Click Performance")
            st.line_chart({"Clicks": [10, 20, 30, 20, 15, 25, 35]})
        with chart_col2:
            st.markdown("### Traffic Sources")
            st.bar_chart({"Facebook": 40, "Twitter": 30, "LinkedIn": 20, "Email": 10})

    with tab3:
        # Bulk Operations
        st.subheader("Bulk URL Operations")
        
        # Bulk Creation
        with st.expander("Bulk URL Creation"):
            st.file_uploader("Upload CSV with URLs", type="csv")
            st.button("Process Bulk Creation")

        # Bulk Export
        with st.expander("Export Data"):
            col1, col2 = st.columns(2)
            with col1:
                st.selectbox("Export Format", ["CSV", "Excel", "JSON"])
            with col2:
                st.selectbox("Data Range", ["All Time", "Last 30 Days", "Custom"])
            st.button("Export Data")

        # Bulk Actions
        with st.expander("Bulk Actions"):
            st.multiselect("Select Campaigns", ["Campaign 1", "Campaign 2", "Campaign 3"])
            col1, col2, col3 = st.columns(3)
            with col1:
                st.button("Update UTM Parameters")
            with col2:
                st.button("Generate QR Codes")
            with col3:
                st.button("Archive Selected")

if __name__ == "__main__":
    main() 
