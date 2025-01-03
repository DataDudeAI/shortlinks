import streamlit as st
from database import Database
from analytics import Analytics
from ui import UI
import validators
import string
import random
from urllib.parse import urlparse, parse_qs, urlencode
from typing import Optional
import pandas as pd
from datetime import datetime

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
        # Remove leading/trailing whitespace
        url = url.strip()
        
        # Ensure URL has proper protocol
        if not url.startswith(('http://', 'https://')):
            url = 'https://' + url
            
        # Remove any quotes that might cause issues
        url = url.replace('"', '').replace("'", '')
        
        return url

    def add_utm_parameters(self, url: str, utm_params: dict) -> str:
        """Add UTM parameters to URL"""
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
        if not url_data.get('url'):
            st.error('Please enter a URL')
            return None

        try:
            # Clean and format the URL
            cleaned_url = self.clean_url(url_data['url'])
            
            # Validate the cleaned URL
            if not validators.url(cleaned_url):
                st.error('Please enter a valid URL')
                return None
            
            # Add UTM parameters if provided
            final_url = cleaned_url
            if url_data.get('utm_params'):
                final_url = self.add_utm_parameters(cleaned_url, url_data['utm_params'])
            
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
    
    # Check if this is a redirect request
    path = st.query_params.get('r')
    if path:
        redirect_url = shortener.analytics.get_redirect_url(path)
        if redirect_url:
            # Track the click before redirecting
            shortener.analytics.track_click(path, {
                'referrer': st.query_params.get('ref', ''),
                'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            })
            
            # Ensure the URL is properly formatted
            redirect_url = shortener.clean_url(redirect_url)
            
            # Create a frame-breaking redirect
            st.markdown(
                f"""
                <html>
                <head>
                <title>Redirecting...</title>
                </head>
                <body>
                <a href="{redirect_url}" id="redirectLink" target="_parent">Click here if not automatically redirected</a>
                <script>
                    // Break out of frames
                    if (window !== window.top) {{
                        window.top.location.href = "{redirect_url}";
                    }} else {{
                        window.location.href = "{redirect_url}";
                    }}
                    // Fallback
                    document.getElementById('redirectLink').click();
                </script>
                </body>
                </html>
                """,
                unsafe_allow_html=True
            )
            return
        else:
            st.error("Invalid or expired short URL")
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
                
                # Display the shortened URL with copy functionality
                col1, col2 = st.columns([3, 1])
                with col1:
                    st.code(shortened_url)
                with col2:
                    st.markdown(
                        f"""
                        <div style="margin-top: 10px;">
                            <input type="text" value="{shortened_url}" id="shortUrl" 
                                style="position: absolute; left: -9999px;">
                            <button onclick="copyToClipboard()" 
                                style="background-color: #4CAF50; color: white; 
                                padding: 8px 16px; border: none; border-radius: 4px; 
                                cursor: pointer; width: 100%;">
                                Copy URL
                            </button>
                        </div>
                        <script>
                            function copyToClipboard() {{
                                var copyText = document.getElementById("shortUrl");
                                copyText.select();
                                document.execCommand("copy");
                                alert("URL copied to clipboard!");
                            }}
                        </script>
                        """,
                        unsafe_allow_html=True
                    )
                
                # Add direct link
                st.markdown(
                    f"""
                    <a href="{shortened_url}" target="_blank" rel="noopener noreferrer"
                    style="display: inline-block; padding: 10px 20px; 
                    background-color: #1E88E5; color: white; 
                    text-decoration: none; border-radius: 5px; 
                    margin-top: 20px;">
                    Open Link ↗
                    </a>
                    """,
                    unsafe_allow_html=True
                )

    with tab2:
        # Display analytics for all URLs
        urls = shortener.db.get_all_urls()
        if urls:
            for url in urls:
                with st.expander(f"📊 {url['short_code']} - {url['total_clicks']} clicks"):
                    analytics_data = shortener.analytics.get_analytics(url['short_code'])
                    if analytics_data:
                        # Display analytics
                        col1, col2, col3 = st.columns(3)
                        with col1:
                            st.metric("Total Clicks", analytics_data['total_clicks'])
                        with col2:
                            st.metric("Unique Sources", analytics_data.get('unique_sources', 0))
                        with col3:
                            st.metric("Last Click", analytics_data.get('last_clicked', 'Never'))
                        
                        # Show original URL
                        st.write("**Original URL:**")
                        st.write(analytics_data['original_url'])
                        
                        # Show traffic sources if available
                        if analytics_data.get('utm_sources'):
                            st.write("**Traffic Sources:**")
                            source_df = pd.DataFrame(
                                analytics_data['utm_sources'].items(),
                                columns=['Source', 'Clicks']
                            )
                            st.dataframe(source_df)
                        
                        # Show recent clicks
                        if analytics_data.get('recent_clicks'):
                            st.write("**Recent Clicks:**")
                            clicks_df = pd.DataFrame(analytics_data['recent_clicks'])
                            st.dataframe(clicks_df)
        else:
            st.info("No links created yet. Create your first short link in the 'Create Short URL' tab!")

if __name__ == "__main__":
    main() 
