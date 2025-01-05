import streamlit as st
from database import Database
from ui import UI
import validators
import string
import random
from urllib.parse import urlparse, parse_qs, urlencode
import logging
from typing import Optional
from datetime import datetime

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
            if not cleaned_url.startswith(('http://', 'https://', 'www.')):
                cleaned_url = 'https://' + cleaned_url.lstrip('www.')
            
            # Special handling for Facebook URLs
            if 'facebook.com' in cleaned_url or 'fb.com' in cleaned_url:
                # Ensure proper URL format for Facebook
                if not validators.url(cleaned_url):
                    st.error('Please enter a valid Facebook URL')
                    return None
                logger.info(f"Processing Facebook URL: {cleaned_url}")
            elif not validators.url(cleaned_url):
                st.error('Please enter a valid URL')
                return None

            # Add UTM parameters if provided
            if url_data.get('utm_params'):
                parsed_url = urlparse(cleaned_url)
                query_params = parse_qs(parsed_url.query)
                query_params.update(url_data['utm_params'])
                cleaned_url = f"{parsed_url.scheme}://{parsed_url.netloc}{parsed_url.path}"
                if query_params:
                    cleaned_url += f"?{urlencode(query_params, doseq=True)}"

            # Generate or use custom short code
            short_code = url_data.get('custom_code') or self.generate_short_code()
            
            # Save to database with updated parameter names
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
        url_info = self.db.get_url_info(short_code)
        if url_info:
            original_url = url_info['original_url']
            logger.info(f"Redirecting to: {original_url}")
            
            # Track click
            self.db.increment_clicks(short_code)
            
            # Clear any existing content
            st.set_page_config(page_title="Redirecting...", layout="centered")
            st.markdown("""
                <style>
                    #root > div:nth-child(1) > div > div > div > div > section > div {display: none}
                </style>
                """, unsafe_allow_html=True)
            
            # Show redirection page with JavaScript
            html_content = f"""
                <html>
                    <head>
                        <title>Redirecting...</title>
                        <script>
                            window.location.href = "{original_url}";
                        </script>
                    </head>
                    <body style="font-family: Arial, sans-serif; text-align: center; padding-top: 50px;">
                        <h3>Redirecting to your destination...</h3>
                        <p>If you are not redirected automatically, 
                           <a href="{original_url}">click here</a>
                        </p>
                    </body>
                </html>
            """
            st.markdown(html_content, unsafe_allow_html=True)
            
            # Fallback meta refresh
            st.markdown(f'<meta http-equiv="refresh" content="0;url={original_url}">', unsafe_allow_html=True)
        else:
            st.error("Invalid or expired link")

def main():
    # Initialize shortener
    shortener = URLShortener()

    # Check for redirect parameter first
    if 'r' in st.query_params:  # Updated from st.experimental_get_query_params()
        short_code = st.query_params['r']  # No need for [0] as it's not a list anymore
        logger.info(f"Redirect requested for code: {short_code}")
        shortener.handle_redirect(short_code)
        return

    # Sidebar navigation
    with st.sidebar:
        st.title("🔗 URL Shortener")
        st.markdown("---")
        page = st.radio(
            "Navigation",
            ["Create URL", "Analytics Dashboard"]
        )

    if page == "Create URL":
        st.title("Create Short URL")
        
        form_data = shortener.ui.render_url_form()
        if form_data:
            short_code = shortener.create_short_url(form_data)
            if short_code:
                shortened_url = f"{BASE_URL}/?r={short_code}"
                
                # Display success message and shortened URL
                shortener.ui.render_success_message(shortened_url)
                
                # Display QR code if enabled
                if form_data.get('qr_code', {}).get('enabled'):
                    shortener.ui.render_qr_code_section(
                        shortened_url, 
                        short_code,
                        form_data['qr_code']['color'],
                        form_data['qr_code']['bg_color']
                    )

    else:  # Analytics Dashboard
        st.title("Analytics Dashboard")
        urls = shortener.db.get_all_urls()
        if urls:
            for url in urls:
                with st.expander(f"Analytics for {url['short_code']}", expanded=False):
                    analytics = shortener.db.get_analytics_data(url['short_code'])
                    if analytics:
                        st.metric("Total Clicks", url['total_clicks'])
                        st.metric("Original URL", url['original_url'])
                        st.markdown(f"Short URL: `{BASE_URL}/?r={url['short_code']}`")
        else:
            st.info("No URLs found. Create some links first!")

if __name__ == "__main__":
    main() 
