import streamlit as st
import pandas as pd
from typing import Dict, Any
from datetime import datetime

BASE_URL = "https://shortlinksnandan.streamlit.app"

class UI:
    def __init__(self, url_shortener):
        self.url_shortener = url_shortener

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
        if not analytics_data:
            st.warning("No analytics data available yet")
            return
            
        st.subheader("Analytics Overview")
        
        # URL Info
        st.write("Original URL:", analytics_data['original_url'])
        
        # Key metrics in columns
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Total Clicks", analytics_data['total_clicks'])
        with col2:
            st.metric("Unique Sources", analytics_data.get('unique_sources', 0))
        with col3:
            if analytics_data.get('last_clicked'):
                st.metric("Last Click", analytics_data['last_clicked'])
            else:
                st.metric("Last Click", "No clicks yet")

        # Campaign Source breakdown
        if analytics_data['utm_sources']:
            st.subheader("Traffic Sources")
            utm_df = pd.DataFrame(
                analytics_data['utm_sources'].items(),
                columns=['Source', 'Clicks']
            )
            st.bar_chart(utm_df.set_index('Source'))
            st.dataframe(utm_df, hide_index=True)

        # Campaign Medium breakdown
        if analytics_data.get('utm_mediums'):
            st.subheader("Traffic Mediums")
            utm_medium_df = pd.DataFrame(
                analytics_data['utm_mediums'].items(),
                columns=['Medium', 'Clicks']
            )
            st.bar_chart(utm_medium_df.set_index('Medium'))
            st.dataframe(utm_medium_df, hide_index=True)

    def render_past_links(self, past_links: list):
        if not past_links:
            st.info("No links created yet. Create your first short link in the 'Create Short URL' tab!")
            return

        st.subheader("Your Short Links")
        
        for link in past_links:
            with st.expander(f"📎 {link['short_code']} ({link['total_clicks']} clicks)"):
                col1, col2 = st.columns([3, 1])
                with col1:
                    st.write("**Original URL:**", link['original_url'])
                    shortened_url = f"{BASE_URL}/?r={link['short_code']}"
                    st.code(shortened_url)
                    st.markdown(f"[Test link]({shortened_url})")
                with col2:
                    st.write("**Created:**", datetime.strptime(link['created_at'], 
                            '%Y-%m-%d %H:%M:%S').strftime('%Y-%m-%d'))
                    st.metric("Clicks", link['total_clicks'])
                
                # Show analytics button
                if st.button("View Analytics", key=f"analytics_{link['short_code']}"):
                    analytics_data = self.url_shortener.analytics.get_analytics(link['short_code'])
                    if analytics_data:
                        self.render_analytics(analytics_data)
                    else:
                        st.warning("No analytics data available yet")

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
