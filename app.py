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

# Must be the first Streamlit command
st.set_page_config(page_title="URL Shortener", layout="wide")

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

    def add_utm_parameters(self, url: str, utm_params: dict) -> str:
        parsed_url = urlparse(url)
        query_dict = parse_qs(parsed_url.query)
        
        # Add UTM parameters if they exist
        for key, value in utm_params.items():
            if value:
                query_dict[key] = [value]
        
        # Rebuild query string
        new_query = urlencode(query_dict, doseq=True)
        
        # Rebuild URL
        return parsed_url._replace(query=new_query).geturl()

    def create_short_url(self, url_data: dict) -> Optional[str]:
        if not validators.url(url_data['url']):
            st.error('Please enter a valid URL')
            return None

        try:
            # Add UTM parameters if provided
            final_url = self.add_utm_parameters(url_data['url'], url_data['utm_params'])
            
            # Generate short code
            short_code = self.generate_short_code()
            
            # Save URL
            url_data = {
                'original_url': final_url,
                'short_code': short_code
            }
            
            self.db.save_url(url_data)
            return short_code

        except Exception as e:
            st.error(f"Error creating short URL: {str(e)}")
            return None

def main():
    shortener = URLShortener()
    
    # Check if this is a redirect request using new query_params
    path = st.query_params.get('r')
    if path:
        redirect_url = shortener.analytics.get_redirect_url(path)
        if redirect_url:
            # Track the click
            shortener.analytics.track_click(path, {
                'referrer': st.query_params.get('ref', '')
            })
            st.markdown(f'<meta http-equiv="refresh" content="0;url={redirect_url}">', unsafe_allow_html=True)
            st.write(f"Redirecting to {redirect_url}...")
            return

    st.title('URL Shortener')
    
    # Create tabs
    tab1, tab2 = st.tabs(["Create Short URL", "Your Links"])

    with tab1:
        form_data = shortener.ui.render_url_form()
        if form_data:
            short_code = shortener.create_short_url(form_data)
            if short_code:
                shortened_url = f"http://localhost:8501/?r={short_code}"
                st.success('URL shortened successfully!')
                st.code(shortened_url)
                st.markdown(f"[Test your link]({shortened_url})")

    with tab2:
        # Get all URLs from database
        past_links = shortener.db.get_all_urls()
        if past_links:
            for link in past_links:
                with st.expander(f"📎 {link['short_code']} ({link['total_clicks']} clicks)"):
                    col1, col2 = st.columns([3, 1])
                    with col1:
                        st.write("**Original URL:**", link['original_url'])
                        shortened_url = f"http://localhost:8501/?r={link['short_code']}"
                        st.code(shortened_url)
                        st.markdown(f"[Test link]({shortened_url})")
                    with col2:
                        st.write("**Created:**", datetime.strptime(link['created_at'], 
                                '%Y-%m-%d %H:%M:%S').strftime('%Y-%m-%d'))
                        st.write("**Clicks:**", link['total_clicks'])
                    
                    # Show analytics button
                    if st.button("View Analytics", key=f"analytics_{link['short_code']}"):
                        analytics_data = shortener.db.get_analytics_data(link['short_code'])
                        if analytics_data:
                            shortener.ui.render_analytics(analytics_data)
        else:
            st.info("No links created yet. Create your first short link in the 'Create Short URL' tab!")

if __name__ == "__main__":
    main() 