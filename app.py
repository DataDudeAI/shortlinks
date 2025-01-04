import streamlit as st
from database import Database
from analytics import Analytics
from ui import UI
import validators
import string
import random
from urllib.parse import urlparse, parse_qs, urlencode
from typing import Optional
from datetime import datetime, timedelta
import webbrowser
import time
import logging
from logging.handlers import RotatingFileHandler
import plotly.express as px
import pandas as pd

# Setup logging
logging.basicConfig(
    handlers=[RotatingFileHandler('url_shortener.log', maxBytes=100000, backupCount=5)],
    level=logging.INFO,
    format='%(asctime)s %(levelname)s: %(message)s'
)
logger = logging.getLogger(__name__)

# Must be the first Streamlit command
st.set_page_config(
    page_title="Advanced URL Shortener",
    page_icon="🔗",
    layout="wide",
    initial_sidebar_state="expanded"
)

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
            
            # Prepare URL data
            url_data = {
                'original_url': cleaned_url,
                'short_code': short_code,
                'created_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                'utm_params': url_data.get('utm_params', {}),
                'tags': url_data.get('tags', []),
                'ab_testing': url_data.get('ab_testing', {})
            }
            
            # Save to database
            if self.db.save_url(url_data):
                return short_code
            return None

        except Exception as e:
            logger.error(f"Error creating short URL: {str(e)}")
            st.error(f"Error creating short URL: {str(e)}")
            return None

def render_analytics_dashboard(shortener):
    st.title("📊 Analytics Dashboard")
    
    # Get all URLs
    urls = shortener.db.get_all_urls()
    if not urls:
        st.info("No links created yet. Create your first short link in the 'Create Short URL' tab!")
        return

    # Sidebar filters
    st.sidebar.header("Filters")
    
    # Date range filter
    date_range = st.sidebar.date_input(
        "Date Range",
        value=(datetime.now() - timedelta(days=30), datetime.now())
    )
    
    # URL filter
    selected_urls = st.sidebar.multiselect(
        "Select URLs",
        options=[url['short_code'] for url in urls],
        default=[urls[0]['short_code']]
    )

    # Main content area
    col1, col2, col3 = st.columns(3)
    
    # Overall metrics
    total_clicks = sum(url['total_clicks'] for url in urls)
    with col1:
        st.metric("Total Links", len(urls))
    with col2:
        st.metric("Total Clicks", total_clicks)
    with col3:
        avg_clicks = total_clicks / len(urls) if urls else 0
        st.metric("Average Clicks/Link", f"{avg_clicks:.1f}")

    # Detailed analytics for selected URLs
    st.subheader("URL Performance")
    
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
                st.metric("Success Rate", f"{analytics['engagement']['success_rate']:.1f}%")
            with col4:
                st.metric("Countries Reached", len(analytics['geographic']))

            # Traffic Sources
            st.subheader("Traffic Sources")
            sources_df = pd.DataFrame(analytics['traffic_sources']['sources'])
            if not sources_df.empty:
                fig = px.pie(sources_df, values='clicks', names='source', title='Traffic Sources')
                st.plotly_chart(fig, use_container_width=True)

            # Geographic Distribution
            st.subheader("Geographic Distribution")
            geo_df = pd.DataFrame(analytics['geographic'])
            if not geo_df.empty:
                fig = px.choropleth(
                    geo_df,
                    locations='country',
                    locationmode='country names',
                    color='clicks',
                    hover_name='country',
                    color_continuous_scale='Viridis'
                )
                st.plotly_chart(fig, use_container_width=True)

            # Device Analysis
            st.subheader("Device Analysis")
            devices_df = pd.DataFrame(analytics['devices']['devices'])
            if not devices_df.empty:
                col1, col2 = st.columns(2)
                with col1:
                    fig = px.pie(devices_df, values='clicks', names='device_type', title='Device Types')
                    st.plotly_chart(fig, use_container_width=True)
                with col2:
                    browsers_df = pd.DataFrame(list(analytics['devices']['browsers'].items()), 
                                            columns=['Browser', 'Clicks'])
                    fig = px.pie(browsers_df, values='Clicks', names='Browser', title='Browsers')
                    st.plotly_chart(fig, use_container_width=True)

            # Time Analysis
            st.subheader("Time Analysis")
            time_data = analytics['time_analysis']
            hourly_df = pd.DataFrame(list(time_data['hourly'].items()), 
                                   columns=['Hour', 'Clicks'])
            fig = px.line(hourly_df, x='Hour', y='Clicks', title='Clicks by Hour')
            st.plotly_chart(fig, use_container_width=True)

            # Performance Alerts
            alerts = shortener.db.get_performance_alerts(short_code)
            if alerts:
                st.subheader("⚠️ Performance Alerts")
                for alert in alerts:
                    if alert['type'] == 'warning':
                        st.warning(alert['message'])
                    else:
                        st.error(alert['message'])

            # Export Data
            if st.button(f"Export Data for {short_code}"):
                export_data = shortener.db.export_analytics_data(
                    short_code,
                    start_date=date_range[0].strftime('%Y-%m-%d'),
                    end_date=date_range[1].strftime('%Y-%m-%d')
                )
                df = pd.DataFrame(export_data)
                st.download_button(
                    "Download CSV",
                    df.to_csv(index=False),
                    f"analytics_{short_code}.csv",
                    "text/csv"
                )

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

    # Sidebar navigation
    st.sidebar.title("URL Shortener")
    page = st.sidebar.radio("Navigation", ["Create URL", "Analytics Dashboard", "Real-time Monitor"])

    if page == "Create URL":
        st.title("Create Short URL")
        form_data = shortener.ui.render_url_form()
        if form_data:
            short_code = shortener.create_short_url(form_data)
            if short_code:
                shortened_url = f"{BASE_URL}/?r={short_code}"
                st.success('URL shortened successfully!')
                st.code(shortened_url)
                
                # Display QR Code if enabled
                if form_data.get('qr_code', {}).get('enabled'):
                    st.image(shortener.ui.generate_qr_code(shortened_url))

    elif page == "Analytics Dashboard":
        render_analytics_dashboard(shortener)

    else:  # Real-time Monitor
        st.title("🔴 Real-time Monitor")
        
        # Get all active URLs
        urls = shortener.db.get_all_urls()
        if not urls:
            st.info("No links to monitor. Create some links first!")
            return

        # Real-time metrics
        st.subheader("Last 5 Minutes Activity")
        for url in urls:
            stats = shortener.db.get_real_time_stats(url['short_code'])
            if stats['clicks'] > 0:
                with st.expander(f"Activity for {url['short_code']}", expanded=True):
                    col1, col2, col3 = st.columns(3)
                    with col1:
                        st.metric("Active Visitors", stats['active_visitors'])
                    with col2:
                        st.metric("Recent Clicks", stats['clicks'])
                    with col3:
                        st.metric("Success Rate", f"{stats['current_success_rate']:.1f}%")

        # Auto-refresh every 30 seconds
        time.sleep(30)
        st.experimental_rerun()

if __name__ == "__main__":
    main() 
