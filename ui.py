import streamlit as st
import pandas as pd
import plotly.express as px
from typing import Dict, Any
from datetime import datetime

class UI:
    def __init__(self, url_shortener):
        self.url_shortener = url_shortener
        
    def render_header(self):
        st.set_page_config(page_title="URL Shortener", layout="wide")
        st.title('URL Shortener')

    def render_url_form(self):
        with st.form("url_shortener_form"):
            url_input = st.text_input('Enter URL to shorten')
            
            # UTM Parameters
            st.subheader("Campaign Parameters")
            utm_source = st.text_input('Campaign Source (e.g., google, facebook, newsletter)')
            utm_medium = st.text_input('Campaign Medium (e.g., cpc, email, social)')
            utm_campaign = st.text_input('Campaign Name')
            
            submitted = st.form_submit_button("Create Short URL")
            
            if submitted:
                return {
                    'url': url_input,
                    'utm_params': {
                        'utm_source': utm_source,
                        'utm_medium': utm_medium,
                        'utm_campaign': utm_campaign
                    }
                }
        return None

    def render_analytics(self, analytics_data: Dict[str, Any]):
        st.subheader("Analytics Overview")
        
        # URL Info
        st.write("Original URL:", analytics_data['original_url'])
        created_at = datetime.strptime(analytics_data['created_at'], '%Y-%m-%d %H:%M:%S')
        
        # Key metrics in columns
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Total Clicks", analytics_data['total_clicks'])
        with col2:
            st.metric("Created Date", created_at.strftime('%Y-%m-%d'))
        with col3:
            if analytics_data['last_clicked']:
                last_click = datetime.strptime(analytics_data['last_clicked'], '%Y-%m-%d %H:%M:%S')
                st.metric("Last Click", last_click.strftime('%Y-%m-%d %H:%M'))
            else:
                st.metric("Last Click", "No clicks yet")

        # Campaign Source breakdown
        if analytics_data['utm_sources']:
            st.subheader("Traffic Sources")
            utm_df = pd.DataFrame(
                analytics_data['utm_sources'].items(),
                columns=['Source', 'Clicks']
            )
            col1, col2 = st.columns(2)
            with col1:
                fig = px.pie(utm_df, values='Clicks', names='Source', title='Traffic by Source')
                st.plotly_chart(fig)
            with col2:
                st.dataframe(utm_df, hide_index=True)

        # Campaign Medium breakdown
        if analytics_data.get('utm_mediums'):
            st.subheader("Traffic Mediums")
            utm_medium_df = pd.DataFrame(
                analytics_data['utm_mediums'].items(),
                columns=['Medium', 'Clicks']
            )
            col1, col2 = st.columns(2)
            with col1:
                fig = px.bar(utm_medium_df, x='Medium', y='Clicks', title='Traffic by Medium')
                st.plotly_chart(fig)
            with col2:
                st.dataframe(utm_medium_df, hide_index=True)

    def render_past_links(self, past_links: list):
        st.subheader("Your Short Links")
        
        if not past_links:
            st.info("No links created yet")
            return

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
                    analytics_data = self.url_shortener.analytics.get_analytics(link['short_code'])
                    self.render_analytics(analytics_data)

    def render_documentation(self):
        st.header("How to Use")
        st.markdown("""
        1. **Create Short URL**
           - Enter your long URL
           - Add UTM parameters for better tracking
           - Set custom short code (optional)
           - Set expiration if needed

        2. **Analytics**
           - Track clicks and unique visitors
           - Monitor traffic sources
           - Analyze device types
           - View daily averages

        3. **UTM Parameters**
           - Source: Where the traffic comes from
           - Medium: The marketing medium
           - Campaign: Specific campaign name
           - Term: Paid search keywords
           - Content: A/B testing content
        """) 