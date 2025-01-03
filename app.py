import streamlit as st
from database import Database
from analytics import Analytics
from ui import UI
import validators
import string
import random
from urllib.parse import urlparse, parse_qs, urlencode
from typing import Optional
from datetime import datetime
import webbrowser
import time
import logging
from logging.handlers import RotatingFileHandler

# Setup logging
logging.basicConfig(
    handlers=[RotatingFileHandler('url_shortener.log', maxBytes=100000, backupCount=5)],
    level=logging.INFO,
    format='%(asctime)s %(levelname)s: %(message)s'
)
logger = logging.getLogger(__name__)

# Add error handling middleware
@st.cache_resource
def handle_error(func):
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            logger.error(f"Error in {func.__name__}: {str(e)}")
            st.error("An unexpected error occurred. Please try again later.")
            if st.session_state.get('debug_mode'):
                st.exception(e)
    return wrapper

# Must be the first Streamlit command
st.set_page_config(page_title="URL Shortener", layout="wide")

# Set the base URL for the deployed app
BASE_URL = "https://shortlinksnandan.streamlit.app"

class URLShortener:
    def __init__(self):
        self.db = Database()
        self.analytics = Analytics(self.db)
        self.ui = UI(self)

    def generate_short_code(self, length=6):
        characters = string.ascii_letters + string.digits
        while True:
            code = ''.join(random.choice(characters) for _ in range(length))
            if not self.db.get_url_info(code):
                return code

    def clean_url(self, url: str) -> str:
        """Clean and format the URL properly"""
        url = url.strip()
        if not url.startswith(('http://', 'https://')):
            url = 'https://' + url
        return url

    def create_short_url(self, url_data: dict) -> Optional[str]:
        if not url_data.get('url'):
            st.error('Please enter a URL')
            return None

        try:
            cleaned_url = self.clean_url(url_data['url'])
            if not validators.url(cleaned_url):
                st.error('Please enter a valid URL')
                return None
            
            short_code = self.generate_short_code()
            url_data = {
                'original_url': cleaned_url,
                'short_code': short_code,
                'created_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            }
            
            self.db.save_url(url_data)
            return short_code

        except Exception as e:
            st.error(f"Error creating short URL: {str(e)}")
            return None

def main():
    shortener = URLShortener()
    
    # Check if this is a redirect request
    path = st.query_params.get('r')
    if path:
        redirect_url = shortener.analytics.get_redirect_url(path)
        if redirect_url:
            # Track the click
            shortener.analytics.track_click(path, {
                'referrer': st.query_params.get('ref', ''),
                'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            })
            
            # Create a redirect page
            st.markdown(
                """
                <style>
                .redirect-container {
                    text-align: center;
                    padding: 20px;
                    margin-top: 50px;
                }
                .redirect-button {
                    display: inline-block;
                    padding: 12px 24px;
                    background-color: #1E88E5;
                    color: white;
                    text-decoration: none;
                    border-radius: 5px;
                    margin: 10px;
                    font-size: 16px;
                }
                </style>
                """,
                unsafe_allow_html=True
            )
            
            st.title("🔄 Redirect Page")
            st.write("You are being redirected to:")
            st.code(redirect_url)
            
            col1, col2 = st.columns(2)
            with col1:
                st.markdown(
                    f"""
                    <div class="redirect-container">
                        <a href="{redirect_url}" class="redirect-button" target="_blank">
                            Click to Continue ↗
                        </a>
                    </div>
                    """,
                    unsafe_allow_html=True
                )
            with col2:
                if st.button("Go Back"):
                    st.switch_page("app.py")
            
            return

        else:
            st.error("Invalid or expired short URL")
            if st.button("Go Back"):
                st.switch_page("app.py")
            return

    st.title('URL Shortener')
    
    # Create tabs
    tab1, tab2 = st.tabs(["Create Short URL", "Analytics"])

    with tab1:
        form_data = shortener.ui.render_url_form()
        if form_data:
            short_code = shortener.create_short_url(form_data)
            if short_code:
                shortened_url = f"{BASE_URL}/?r={short_code}"
                st.success('URL shortened successfully!')
                
                col1, col2 = st.columns([3, 1])
                with col1:
                    st.code(shortened_url)
                with col2:
                    if st.button("Copy URL"):
                        st.write("URL copied!")
                        st.code(shortened_url, language="")
                
                st.markdown(
                    f"""
                    <div style="margin-top: 20px;">
                        <a href="{shortened_url}" target="_blank" 
                        style="display: inline-block; padding: 12px 24px; 
                        background-color: #1E88E5; color: white; 
                        text-decoration: none; border-radius: 5px;">
                        Test Link ↗
                        </a>
                    </div>
                    """,
                    unsafe_allow_html=True
                )

    with tab2:
        st.subheader("📊 Analytics Dashboard")
        urls = shortener.db.get_all_urls()
        if urls:
            # Sort URLs by total clicks
            urls.sort(key=lambda x: x['total_clicks'], reverse=True)
            
            for url in urls:
                with st.expander(f"🔗 {url['short_code']} - {url['total_clicks']} clicks"):
                    analytics_data = shortener.analytics.get_analytics(url['short_code'])
                    if analytics_data:
                        shortener.ui.render_analytics(analytics_data)
                    else:
                        st.info("No analytics data available for this link yet.")
        else:
            st.info("No links created yet. Create your first short link in the 'Create Short URL' tab!")

if __name__ == "__main__":
    main() 
