import streamlit as st
import pandas as pd
from typing import Dict, Any, List
from datetime import datetime
import io
import plotly.express as px

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
        """Enhanced analytics visualization with real-time data"""
        st.subheader("📊 Link Analytics")
        
        # Summary metrics in columns
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Total Clicks", analytics_data['total_clicks'])
        with col2:
            st.metric("Unique Visitors", analytics_data.get('unique_visitors', 0))
        with col3:
            success_rate = (analytics_data.get('successful_redirects', 0) / analytics_data['total_clicks'] * 100) if analytics_data['total_clicks'] > 0 else 0
            st.metric("Success Rate", f"{success_rate:.1f}%")
        with col4:
            bounce_rate = (analytics_data.get('bounces', 0) / analytics_data['unique_visitors'] * 100) if analytics_data.get('unique_visitors', 0) > 0 else 0
            st.metric("Bounce Rate", f"{bounce_rate:.1f}%")

        # Recent Clicks Table
        st.subheader("🕒 Recent Clicks")
        if analytics_data.get('recent_clicks'):
            recent_clicks = analytics_data['recent_clicks']
            for click in recent_clicks:
                with st.container():
                    col1, col2, col3 = st.columns([2,2,1])
                    with col1:
                        time_ago = (datetime.now() - datetime.strptime(click['clicked_at'], '%Y-%m-%d %H:%M:%S'))
                        if time_ago.total_seconds() < 60:
                            time_str = f"{int(time_ago.total_seconds())} seconds ago"
                        elif time_ago.total_seconds() < 3600:
                            time_str = f"{int(time_ago.total_seconds()/60)} minutes ago"
                        else:
                            time_str = f"{int(time_ago.total_seconds()/3600)} hours ago"
                        
                        st.text(f"🕒 {time_str}")
                        st.text(f"🌍 {click['country']}")
                    with col2:
                        st.text(f"📱 {click['device_type']}")
                        st.text(f"🌐 {click['browser']} ({click['os']})")
                    with col3:
                        status = "✅" if click['successful'] else "❌"
                        st.text(f"{status} {click['utm_source']}")
                    st.divider()
        else:
            st.info("No clicks recorded yet")

        # Link Details
        st.subheader("🔗 Link Details")
        cols = st.columns([3, 2])
        with cols[0]:
            st.markdown("**Original URL:**")
            st.write(analytics_data['original_url'])
            
            shortened_url = f"{BASE_URL}/?r={analytics_data['short_code']}"
            st.markdown("**Short URL:**")
            st.code(shortened_url)
            
            col1, col2 = st.columns([1, 2])
            with col1:
                if st.button("📋 Copy", key=f"copy_{analytics_data['short_code']}"):
                    st.write("Copied to clipboard!")
            with col2:
                st.markdown(f"[🔗 Test Link]({shortened_url})")

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

    def render_recent_clicks(self, short_code: str):
        """Display recent clicks for a URL"""
        st.subheader("🕒 Recent Clicks")
        
        recent_clicks = self.url_shortener.analytics.get_recent_clicks(short_code)
        
        if not recent_clicks:
            st.info("No clicks recorded yet")
            return
        
        # Create a DataFrame for better display
        df = pd.DataFrame(recent_clicks)
        
        # Format the timestamp
        df['clicked_at'] = pd.to_datetime(df['clicked_at'])
        df['time_ago'] = (datetime.now() - df['clicked_at']).apply(
            lambda x: f"{int(x.total_seconds())} seconds ago" if x.total_seconds() < 60
            else f"{int(x.total_seconds()/60)} minutes ago" if x.total_seconds() < 3600
            else f"{int(x.total_seconds()/3600)} hours ago"
        )
        
        # Display in an expandable container
        with st.expander("View Recent Clicks", expanded=True):
            for _, click in df.iterrows():
                with st.container():
                    col1, col2, col3 = st.columns([2,2,1])
                    with col1:
                        st.text(f"🕒 {click['time_ago']}")
                        st.text(f"🌍 {click['country']}")
                    with col2:
                        st.text(f"📱 {click['device_type']}")
                        st.text(f"🌐 {click['browser']} ({click['os']})")
                    with col3:
                        if click['utm_source'] != 'direct':
                            st.text(f"📢 {click['utm_source']}")
                    st.divider() 

    def render_analytics_tab(self, urls: list):
        """Enhanced analytics tab with clickable links and detailed stats"""
        st.header("📊 Analytics Dashboard")
        
        if not urls:
            st.info("No links created yet. Create your first short link in the 'Create Short URL' tab!")
            return
        
        # Sort URLs by total clicks
        urls.sort(key=lambda x: x['total_clicks'], reverse=True)
        
        # Summary metrics
        total_clicks = sum(url['total_clicks'] for url in urls)
        total_links = len(urls)
        avg_clicks = total_clicks / total_links if total_links > 0 else 0
        
        # Display overall metrics
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Total Links", total_links)
        with col2:
            st.metric("Total Clicks", total_clicks)
        with col3:
            st.metric("Average Clicks/Link", f"{avg_clicks:.1f}")
        
        # Links table with analytics
        st.subheader("Your Short Links")
        for url in urls:
            with st.expander(f"🔗 {url['short_code']} ({url['total_clicks']} clicks)", expanded=False):
                cols = st.columns([3, 2])
                
                with cols[0]:
                    st.markdown("**Original URL:**")
                    st.write(url['original_url'])
                    
                    shortened_url = f"{BASE_URL}/?r={url['short_code']}"
                    st.markdown("**Short URL:**")
                    st.code(shortened_url)
                    
                    # Clickable buttons
                    col1, col2 = st.columns([1, 2])
                    with col1:
                        if st.button("📋 Copy", key=f"copy_{url['short_code']}"):
                            st.write("Copied to clipboard!")
                    with col2:
                        st.markdown(f"[🔗 Open Link]({shortened_url})")
                
                with cols[1]:
                    created_date = datetime.strptime(url['created_at'], '%Y-%m-%d %H:%M:%S')
                    days_active = (datetime.now() - created_date).days + 1
                    clicks_per_day = url['total_clicks'] / days_active
                    
                    st.metric("Created", created_date.strftime('%Y-%m-%d'))
                    st.metric("Days Active", days_active)
                    st.metric("Clicks/Day", f"{clicks_per_day:.1f}")
                
                # Get detailed analytics
                analytics_data = self.url_shortener.db.get_analytics_data(url['short_code'])
                if analytics_data:
                    # Traffic Sources
                    st.subheader("📈 Traffic Analysis")
                    source_cols = st.columns(3)
                    
                    with source_cols[0]:
                        self.render_pie_chart(
                            analytics_data.get('utm_sources', {}),
                            "Traffic Sources"
                        )
                    
                    with source_cols[1]:
                        self.render_pie_chart(
                            analytics_data.get('devices', {}),
                            "Devices"
                        )
                    
                    with source_cols[2]:
                        self.render_pie_chart(
                            analytics_data.get('browsers', {}),
                            "Browsers"
                        )
                    
                    # Recent Activity
                    st.subheader("🕒 Recent Activity")
                    self.render_recent_clicks(url['short_code'])
                    
                    # Success Rate
                    successful_redirects = analytics_data.get('successful_redirects', 0)
                    total_attempts = analytics_data.get('total_attempts', 0)
                    if total_attempts > 0:
                        success_rate = (successful_redirects / total_attempts) * 100
                        st.metric("Redirect Success Rate", f"{success_rate:.1f}%")
                    
                    # Export Analytics
                    if st.button("📊 Export Analytics", key=f"export_{url['short_code']}"):
                        csv_data = self.generate_analytics_csv(analytics_data)
                        st.download_button(
                            "Download CSV",
                            csv_data,
                            file_name=f"analytics_{url['short_code']}.csv",
                            mime="text/csv"
                        )

    def render_pie_chart(self, data: Dict[str, int], title: str):
        """Helper method to render pie charts"""
        if data:
            df = pd.DataFrame(list(data.items()), columns=['Label', 'Value'])
            fig = px.pie(df, values='Value', names='Label', title=title)
            fig.update_layout(showlegend=True, height=300)
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info(f"No {title.lower()} data available") 
