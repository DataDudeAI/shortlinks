import streamlit as st
from database import Database
from ui import UI
import validators
import string
import random
from urllib.parse import urlparse, parse_qs
import logging
from typing import Optional
import pandas as pd
from datetime import datetime, timedelta

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Must be the first Streamlit command
st.set_page_config(
    page_title="URL Shortener",
    page_icon="🔗",
    layout="wide"
)

BASE_URL = "https://shortlinksnandan.streamlit.app"

def render_analytics_dashboard(shortener):
    st.title("Analytics Dashboard")
    
    # Get all URLs
    urls = shortener.db.get_all_urls()
    if not urls:
        st.info("No URLs found. Create some links first!")
        return
    
    # URL Selection
    selected_urls = st.multiselect(
        "Select URLs to analyze",
        options=[url['short_code'] for url in urls],
        default=[urls[0]['short_code']] if urls else None
    )
    
    if not selected_urls:
        st.warning("Please select at least one URL to analyze")
        return
    
    # Analytics for each selected URL
    for short_code in selected_urls:
        with st.expander(f"Analytics for {short_code}", expanded=True):
            # Get comprehensive analytics
            analytics = shortener.db.generate_report(short_code)
            
            # Display metrics in columns
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.metric("Total Clicks", analytics['basic_stats']['total_clicks'])
            with col2:
                st.metric("Unique Visitors", analytics['conversion_data']['unique_visitors'])
            with col3:
                st.metric("Success Rate", f"{analytics['engagement']['success_rate']}%")
            with col4:
                st.metric("Countries Reached", len(analytics['geographic']))
            
            # Traffic Sources
            st.subheader("Traffic Sources")
            sources_df = pd.DataFrame(analytics['traffic_sources']['sources'])
            if not sources_df.empty:
                st.dataframe(sources_df)
                
                # Download CSV
                csv = sources_df.to_csv(index=False)
                st.download_button(
                    "Download Traffic Sources CSV",
                    csv,
                    f"traffic_sources_{short_code}.csv",
                    "text/csv"
                )
            
            # Geographic Data
            st.subheader("Geographic Distribution")
            geo_df = pd.DataFrame(list(analytics['geographic'].items()), columns=['Country', 'Clicks'])
            if not geo_df.empty:
                st.bar_chart(geo_df.set_index('Country'))
            
            # Device Analysis
            st.subheader("Device Analysis")
            devices_df = pd.DataFrame(analytics['devices']['devices'].items(), columns=['Device', 'Count'])
            if not devices_df.empty:
                col1, col2 = st.columns(2)
                with col1:
                    st.pie_chart(devices_df.set_index('Device'))
                with col2:
                    st.dataframe(devices_df)
            
            # Recent Clicks
            st.subheader("Recent Activity")
            recent_clicks = pd.DataFrame(analytics['recent_clicks'])
            if not recent_clicks.empty:
                st.dataframe(recent_clicks)
                
                # Download CSV
                csv = recent_clicks.to_csv(index=False)
                st.download_button(
                    "Download Recent Activity CSV",
                    csv,
                    f"recent_clicks_{short_code}.csv",
                    "text/csv"
                )

class URLShortener:
    def __init__(self):
        self.db = Database()
        self.ui = UI(self)

    def generate_short_code(self, length=6):
        characters = string.ascii_letters + string.digits
        while True:
            code = ''.join(random.choice(characters) for _ in range(length))
            if not self.db.get_url_info(code):
                return code

    def create_short_url(self, url_data: dict) -> Optional[str]:
        if not url_data.get('url'):
            st.error('Please enter a URL')
            return None

        try:
            # Clean and validate URL
            cleaned_url = url_data['url'].strip()
            if not cleaned_url.startswith(('http://', 'https://')):
                cleaned_url = 'https://' + cleaned_url
            
            if not validators.url(cleaned_url):
                st.error('Please enter a valid URL')
                return None
            
            # Generate or use custom short code
            short_code = url_data.get('custom_code') or self.generate_short_code()
            
            # Save URL
            data = {
                'url': cleaned_url,
                'short_code': short_code
            }
            
            if self.db.save_url(data):
                return short_code
            else:
                st.error('Error creating short URL')
                return None
                
        except Exception as e:
            logger.error(f"Error creating URL: {str(e)}")
            st.error('Error creating short URL')
            return None

def main():
    shortener = URLShortener()
    
    # Check if this is a redirect request
    params = st.query_params
    if 'r' in params:
        short_code = params['r']
        url_info = shortener.db.get_url_info(short_code)
        if url_info:
            # Save analytics data
            analytics_data = {
                'short_code': short_code,
                'ip_address': st.get_client_ip(),
                'user_agent': st.get_user_agent(),
                'referrer': st.get_referrer() if hasattr(st, 'get_referrer') else None,
                'utm_source': params.get('utm_source', 'direct'),
                'utm_medium': params.get('utm_medium', 'none'),
                'utm_campaign': params.get('utm_campaign', 'no campaign'),
                'country': 'Unknown',  # You can add IP-based geolocation if needed
                'device_type': 'desktop' if 'desktop' in st.get_user_agent().lower() else 'mobile',
                'browser': st.get_user_agent().split('/')[0],
                'os': 'Unknown'
            }
            
            # Save the click
            shortener.db.save_analytics(analytics_data)
            
            # Redirect to original URL
            original_url = url_info['original_url']
            st.markdown(f'<meta http-equiv="refresh" content="0;URL=\'{original_url}\'">', unsafe_allow_html=True)
            return
        else:
            st.error("Invalid or expired link")
            return

    # Sidebar navigation
    st.sidebar.title("URL Shortener")
    page = st.sidebar.radio("Navigation", ["Create URL", "Analytics Dashboard"])

    if page == "Create URL":
        st.title("Create Short URL")
        form_data = shortener.ui.render_url_form()
        if form_data:
            short_code = shortener.create_short_url(form_data)
            if short_code:
                shortened_url = f"{BASE_URL}/?r={short_code}"
                st.success('URL shortened successfully!')
                
                # Make the shortened URL clickable
                st.markdown(f"""
                ### Your shortened URL:
                #### 🔗 [Click here to visit]({shortened_url})
                """)
                
                # Display the URL as text for copying
                st.code(shortened_url)
                
                # Add copy button
                st.button("Copy URL", on_click=lambda: st.write(f"```{shortened_url}```"))
                
                # Display QR Code if enabled
                if form_data.get('qr_code', {}).get('enabled'):
                    st.image(shortener.ui.generate_qr_code(shortened_url))

    else:  # Analytics Dashboard
        render_analytics_dashboard(shortener)

if __name__ == "__main__":
    main() 
