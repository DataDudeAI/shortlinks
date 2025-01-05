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
    layout="wide",
    initial_sidebar_state="expanded"
)

BASE_URL = "https://shortlinksnandan.streamlit.app"

def render_analytics_dashboard(shortener):
    st.title("📊 Analytics Dashboard")
    
    # Get all URLs
    urls = shortener.db.get_all_urls()
    if not urls:
        st.info("🔍 No URLs found. Create some links first!")
        return
    
    # URL Selection
    selected_urls = st.multiselect(
        "Select URLs to analyze",
        options=[url['short_code'] for url in urls],
        default=[urls[0]['short_code']] if urls else None
    )
    
    if not selected_urls:
        st.warning("⚠️ Please select at least one URL to analyze")
        return
    
    # Analytics for each selected URL
    for short_code in selected_urls:
        analytics = shortener.db.generate_report(short_code)
        if analytics:
            shortener.ui.render_analytics_dashboard({
                'total_clicks': analytics['basic_stats']['total_clicks'],
                'unique_visitors': analytics['conversion_data']['unique_visitors'],
                'success_rate': analytics['engagement']['success_rate'],
                'countries_count': len(analytics['geographic']),
                'traffic_sources': analytics['traffic_sources']['sources'],
                'geographic_data': analytics['geographic'],
                'device_data': analytics['devices']['devices']
            })

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
            st.error('⚠️ Please enter a URL')
            return None

        try:
            # Clean and validate URL
            cleaned_url = url_data['url'].strip()
            if not cleaned_url.startswith(('http://', 'https://')):
                cleaned_url = 'https://' + cleaned_url
            
            if not validators.url(cleaned_url):
                st.error('⚠️ Please enter a valid URL')
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
                st.error('❌ Error creating short URL')
                return None
                
        except Exception as e:
            logger.error(f"Error creating URL: {str(e)}")
            st.error('❌ Error creating short URL')
            return None

def main():
    shortener = URLShortener()
    
    # Check if this is a redirect request
    params = st.query_params
    if 'r' in params:
        short_code = params['r']
        url_info = shortener.db.get_url_info(short_code)
        if url_info:
            # Save basic analytics data
            analytics_data = {
                'short_code': short_code,
                'ip_address': 'Unknown',
                'user_agent': 'Unknown',
                'referrer': None,
                'utm_source': params.get('utm_source', 'direct'),
                'utm_medium': params.get('utm_medium', 'none'),
                'utm_campaign': params.get('utm_campaign', 'no campaign'),
                'country': 'Unknown',
                'device_type': 'unknown',
                'browser': 'unknown',
                'os': 'Unknown'
            }
            
            # Save the click
            shortener.db.save_analytics(analytics_data)
            
            # Increment click count
            shortener.db.increment_clicks(short_code)
            
            # Redirect to original URL
            original_url = url_info['original_url']
            st.markdown(f'<meta http-equiv="refresh" content="0;URL=\'{original_url}\'">', unsafe_allow_html=True)
            return
        else:
            st.error("❌ Invalid or expired link")
            return

    # Sidebar navigation
    with st.sidebar:
        st.title("🔗 URL Shortener")
        st.markdown("---")
        page = st.radio(
            "Navigation",
            ["🎯 Create URL", "📊 Analytics Dashboard"]
        )
        st.markdown("---")
        st.markdown("### About")
        st.markdown("Create short, trackable links with comprehensive analytics.")

    if page == "🎯 Create URL":
        st.title("Create Short URL")
        st.markdown("### Create your shortened URL below")
        
        form_data = shortener.ui.render_url_form()
        if form_data:
            short_code = shortener.create_short_url(form_data)
            if short_code:
                shortened_url = f"{BASE_URL}/?r={short_code}"
                
                # Display success message and shortened URL
                shortener.ui.render_success_message(shortened_url)
                
                # Display QR code if enabled
                if form_data.get('qr_code', {}).get('enabled'):
                    shortener.ui.render_qr_code_section(shortened_url, short_code)

    else:  # Analytics Dashboard
        render_analytics_dashboard(shortener)

if __name__ == "__main__":
    main() 
