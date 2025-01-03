import streamlit as st
import pandas as pd
from typing import Dict, Any, List
from datetime import datetime
import io

BASE_URL = "https://shortlinksnandan.streamlit.app"

class UI:
    def __init__(self, url_shortener):
        self.url_shortener = url_shortener

    def render_url_form(self):
        with st.form("url_shortener_form"):
            url_input = st.text_input('Enter URL to shorten')
            
            # UTM Parameters
            with st.expander("Add Campaign Parameters (Optional)"):
                utm_source = st.text_input('Campaign Source (e.g., facebook, twitter)', '')
                utm_medium = st.text_input('Campaign Medium (e.g., social, email)', '')
                utm_campaign = st.text_input('Campaign Name', '')
            
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
        """Render analytics data for a URL"""
        st.subheader("📊 Link Analytics")
        
        # Basic Stats
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Total Clicks", analytics_data['total_clicks'])
        with col2:
            st.metric("Last Click", analytics_data.get('last_clicked', 'Never'))
        with col3:
            created_date = datetime.strptime(analytics_data['created_at'], '%Y-%m-%d %H:%M:%S')
            days_active = (datetime.now() - created_date).days
            if days_active > 0:
                clicks_per_day = analytics_data['total_clicks'] / days_active
                st.metric("Avg. Clicks/Day", f"{clicks_per_day:.1f}")
            else:
                st.metric("Avg. Clicks/Day", "0")

        # Traffic Sources
        if analytics_data.get('utm_sources'):
            st.subheader("🔍 Traffic Sources")
            source_df = pd.DataFrame(
                analytics_data['utm_sources'].items(),
                columns=['Source', 'Clicks']
            ).sort_values('Clicks', ascending=False)
            
            # Calculate percentages
            total = source_df['Clicks'].sum()
            source_df['Percentage'] = (source_df['Clicks'] / total * 100).round(1)
            source_df['Percentage'] = source_df['Percentage'].astype(str) + '%'
            
            st.dataframe(source_df, hide_index=True)

        # Traffic Mediums
        if analytics_data.get('utm_mediums'):
            st.subheader("📱 Traffic Mediums")
            medium_df = pd.DataFrame(
                analytics_data['utm_mediums'].items(),
                columns=['Medium', 'Clicks']
            ).sort_values('Clicks', ascending=False)
            
            total = medium_df['Clicks'].sum()
            medium_df['Percentage'] = (medium_df['Clicks'] / total * 100).round(1)
            medium_df['Percentage'] = medium_df['Percentage'].astype(str) + '%'
            
            st.dataframe(medium_df, hide_index=True)

        # Recent Clicks
        if analytics_data.get('recent_clicks'):
            st.subheader("🕒 Recent Activity")
            clicks_df = pd.DataFrame(analytics_data['recent_clicks'])
            if not clicks_df.empty:
                clicks_df['clicked_at'] = pd.to_datetime(clicks_df['clicked_at'])
                clicks_df = clicks_df.sort_values('clicked_at', ascending=False)
                
                for _, click in clicks_df.iterrows():
                    with st.expander(f"Click at {click['clicked_at'].strftime('%Y-%m-%d %H:%M:%S')}"):
                        st.write(f"Source: {click['utm_source']}")
                        st.write(f"Medium: {click['utm_medium']}")
                        st.write(f"Campaign: {click['utm_campaign']}")
                        if click['referrer']:
                            st.write(f"Referrer: {click['referrer']}")

        # Export Data
        st.subheader("📥 Export Data")
        if st.button("Download Analytics"):
            csv = self.generate_analytics_csv(analytics_data)
            st.download_button(
                label="Download CSV",
                data=csv,
                file_name=f"analytics_{analytics_data['short_code']}.csv",
                mime="text/csv"
            )

    def generate_analytics_csv(self, analytics_data: Dict[str, Any]) -> str:
        """Generate CSV data for analytics export"""
        # Create DataFrames for different sections
        basic_info = pd.DataFrame([{
            'Short Code': analytics_data['short_code'],
            'Original URL': analytics_data['original_url'],
            'Total Clicks': analytics_data['total_clicks'],
            'Created At': analytics_data['created_at'],
            'Last Click': analytics_data.get('last_clicked', 'Never')
        }])

        # Combine all data into CSV
        csv_parts = []
        csv_parts.append("Basic Information")
        csv_parts.append(basic_info.to_csv(index=False))
        
        if analytics_data.get('utm_sources'):
            csv_parts.append("\nTraffic Sources")
            sources_df = pd.DataFrame(analytics_data['utm_sources'].items(), 
                                    columns=['Source', 'Clicks'])
            csv_parts.append(sources_df.to_csv(index=False))

        if analytics_data.get('recent_clicks'):
            csv_parts.append("\nRecent Clicks")
            clicks_df = pd.DataFrame(analytics_data['recent_clicks'])
            csv_parts.append(clicks_df.to_csv(index=False))

        return '\n'.join(csv_parts)

    def render_past_links(self, past_links: list):
        if not past_links:
            st.info("No links created yet. Create your first short link in the 'Create Short URL' tab!")
            return

        st.subheader("Your Short Links")
        
        # Sort links by creation date
        past_links.sort(key=lambda x: datetime.strptime(x['created_at'], '%Y-%m-%d %H:%M:%S'), reverse=True)
        
        for link in past_links:
            with st.expander(f"📎 {link['short_code']} ({link['total_clicks']} clicks)"):
                col1, col2 = st.columns([3, 1])
                with col1:
                    st.write("**Original URL:**", link['original_url'])
                    shortened_url = f"{BASE_URL}/?r={link['short_code']}"
                    st.code(shortened_url)
                    st.markdown(f"[Test link]({shortened_url})")
                with col2:
                    created_date = datetime.strptime(link['created_at'], '%Y-%m-%d %H:%M:%S')
                    days_active = (datetime.now() - created_date).days + 1
                    clicks_per_day = link['total_clicks'] / days_active
                    
                    st.metric("Created", created_date.strftime('%Y-%m-%d'))
                    st.metric("Total Clicks", link['total_clicks'])
                    st.metric("Clicks/Day", f"{clicks_per_day:.1f}")
                
                # Show analytics button
                if st.button("View Detailed Analytics", key=f"analytics_{link['short_code']}"):
                    analytics_data = self.url_shortener.db.get_analytics_data(link['short_code'])
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
