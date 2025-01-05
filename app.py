import streamlit as st
from database import Database
from ui import UI
import validators
import string
import random
from urllib.parse import urlparse, parse_qs
import logging
from typing import Optional

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
            original_url = url_info['original_url']
            st.markdown(f'<meta http-equiv="refresh" content="0;URL=\'{original_url}\'">', unsafe_allow_html=True)
            return
        else:
            st.error("Invalid or expired link")
            return

    st.title("URL Shortener")
    
    # Create URL Form
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

if __name__ == "__main__":
    main() 
