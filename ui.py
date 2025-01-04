import streamlit as st
import pandas as pd
from typing import Dict, Any, List
from datetime import datetime, timedelta
import io
import plotly.express as px
import qrcode
from PIL import Image
import json
import uuid
from io import BytesIO
import base64

BASE_URL = "https://shortlinksnandan.streamlit.app"

class UI:
    def __init__(self, url_shortener):
        self.url_shortener = url_shortener

    def render_url_form(self):
        with st.form("url_shortener_form"):
            url_input = st.text_input('Enter URL to shorten')
            
            # Advanced Options
            with st.expander("Advanced Options"):
                # Custom short code
                custom_code = st.text_input('Custom short code (optional)', '')
                
                # Link expiration
                col1, col2 = st.columns(2)
                with col1:
                    enable_expiry = st.checkbox('Enable link expiration')
                with col2:
                    if enable_expiry:
                        expiry_days = st.number_input('Expire after days', min_value=1, value=30)
                
                # A/B Testing
                enable_ab = st.checkbox('Enable A/B Testing')
                if enable_ab:
                    variant_b_url = st.text_input('Variant B URL')
                    split_ratio = st.slider('Traffic Split (A/B)', 0, 100, 50)
                
                # Link grouping/tagging
                tags = st.multiselect('Add tags', 
                    ['Personal', 'Business', 'Marketing', 'Social', 'Other'],
                    default=None)
                
                # QR Code customization
                enable_qr = st.checkbox('Generate QR Code')
                if enable_qr:
                    qr_color = st.color_picker('QR Code Color', '#000000')
                    qr_bg_color = st.color_picker('Background Color', '#FFFFFF')
            
            # UTM Parameters
            with st.expander("Campaign Parameters (UTM)"):
                utm_source = st.text_input('Campaign Source (e.g., facebook, twitter)', '')
                utm_medium = st.text_input('Campaign Medium (e.g., social, email)', '')
                utm_campaign = st.text_input('Campaign Name', '')
                utm_term = st.text_input('Campaign Term (for paid search)', '')
                utm_content = st.text_input('Campaign Content (for A/B testing)', '')
            
            submitted = st.form_submit_button("Create Short URL")
            
            if submitted:
                expiry_date = None
                if enable_expiry:
                    expiry_date = (datetime.now() + timedelta(days=expiry_days)).strftime('%Y-%m-%d %H:%M:%S')
                
                return {
                    'url': url_input,
                    'custom_code': custom_code if custom_code else None,
                    'expiry_date': expiry_date,
                    'ab_testing': {
                        'enabled': enable_ab,
                        'variant_b_url': variant_b_url if enable_ab else None,
                        'split_ratio': split_ratio if enable_ab else None
                    },
                    'tags': tags,
                    'qr_code': {
                        'enabled': enable_qr,
                        'color': qr_color if enable_qr else '#000000',
                        'bg_color': qr_bg_color if enable_qr else '#FFFFFF'
                    },
                    'utm_params': {
                        'utm_source': utm_source,
                        'utm_medium': utm_medium,
                        'utm_campaign': utm_campaign,
                        'utm_term': utm_term,
                        'utm_content': utm_content
                    }
                }
        return None

    def generate_qr_code(self, url: str, color: str = '#000000', bg_color: str = '#FFFFFF') -> Image:
        """Generate a customized QR code"""
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=10,
            border=4,
        )
        qr.add_data(url)
        qr.make(fit=True)

        # Convert hex colors to RGB
        fill_color = tuple(int(color.lstrip('#')[i:i+2], 16) for i in (0, 2, 4))
        back_color = tuple(int(bg_color.lstrip('#')[i:i+2], 16) for i in (0, 2, 4))
        
        return qr.make_image(fill_color=fill_color, back_color=back_color)

    def render_analytics_dashboard(self, analytics_data: Dict[str, Any]):
        """Enhanced analytics dashboard with A/B testing results"""
        st.subheader("📊 Enhanced Analytics")
        
        # Main metrics
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Total Clicks", analytics_data['total_clicks'])
        with col2:
            st.metric("Unique Visitors", analytics_data.get('unique_visitors', 0))
        with col3:
            conversion_rate = analytics_data.get('conversion_rate', 0)
            st.metric("Conversion Rate", f"{conversion_rate:.1f}%")
        with col4:
            bounce_rate = analytics_data.get('bounce_rate', 0)
            st.metric("Bounce Rate", f"{bounce_rate:.1f}%")

        # A/B Testing Results
        if analytics_data.get('ab_testing', {}).get('enabled'):
            st.subheader("🔄 A/B Testing Results")
            ab_data = analytics_data['ab_testing']
            
            col1, col2 = st.columns(2)
            with col1:
                st.metric("Variant A Conversions", 
                         f"{ab_data['variant_a_conversion']:.1f}%")
            with col2:
                st.metric("Variant B Conversions", 
                         f"{ab_data['variant_b_conversion']:.1f}%")
            
            # Statistical significance
            if ab_data.get('significant'):
                st.success(f"Winner: Variant {'A' if ab_data['winner'] == 'a' else 'B'}")
            else:
                st.info("Not enough data for statistical significance")

        # Time series analysis
        st.subheader("📈 Traffic Over Time")
        if analytics_data.get('daily_clicks'):
            df = pd.DataFrame(analytics_data['daily_clicks'])
            fig = px.line(df, x='date', y='clicks', title='Daily Clicks')
            st.plotly_chart(fig, use_container_width=True)

        # Device & Browser Analytics
        col1, col2 = st.columns(2)
        with col1:
            self.render_pie_chart(analytics_data.get('devices', {}), "Device Types")
        with col2:
            self.render_pie_chart(analytics_data.get('browsers', {}), "Browsers")

        # Geographic Data
        if analytics_data.get('geo_data'):
            st.subheader("🌍 Geographic Distribution")
            df = pd.DataFrame(analytics_data['geo_data'])
            fig = px.choropleth(df, 
                              locations='country_code',
                              color='clicks',
                              hover_name='country',
                              title='Global Click Distribution')
            st.plotly_chart(fig, use_container_width=True)

    def render_link_management(self, links: List[Dict[str, Any]]):
        """Enhanced link management interface"""
        st.subheader("🔗 Link Management")
        
        # Filter and sort options
        col1, col2, col3 = st.columns(3)
        with col1:
            sort_by = st.selectbox('Sort by', 
                ['Created Date', 'Clicks', 'Conversion Rate'])
        with col2:
            filter_tag = st.multiselect('Filter by tags', 
                ['Personal', 'Business', 'Marketing', 'Social', 'Other'])
        with col3:
            search = st.text_input('Search links', '')

        # Apply filters
        filtered_links = [
            link for link in links
            if (not filter_tag or any(tag in link.get('tags', []) for tag in filter_tag))
            and (not search or search.lower() in link['original_url'].lower())
        ]

        # Sort links
        if sort_by == 'Clicks':
            filtered_links.sort(key=lambda x: x['total_clicks'], reverse=True)
        elif sort_by == 'Conversion Rate':
            filtered_links.sort(key=lambda x: x.get('conversion_rate', 0), reverse=True)
        else:  # Created Date
            filtered_links.sort(key=lambda x: x['created_at'], reverse=True)

        # Display links
        for link in filtered_links:
            self.render_link_card(link)

    def render_link_card(self, link: Dict[str, Any]):
        """Render an individual link card"""
        with st.expander(f"🔗 {link['short_code']} ({link['total_clicks']} clicks)"):
            col1, col2 = st.columns([3, 1])
            
            with col1:
                st.markdown(f"**Original URL:** {link['original_url']}")
                shortened_url = f"{BASE_URL}/?r={link['short_code']}"
                st.code(shortened_url)
                
                # Tags
                if link.get('tags'):
                    st.markdown("**Tags:** " + ", ".join(link['tags']))
                
                # Expiration
                if link.get('expiry_date'):
                    expiry = datetime.strptime(link['expiry_date'], '%Y-%m-%d %H:%M:%S')
                    if expiry > datetime.now():
                        days_left = (expiry - datetime.now()).days
                        st.info(f"Expires in {days_left} days")
                    else:
                        st.error("Link expired")
            
            with col2:
                if st.button("📋 Copy", key=f"copy_{link['short_code']}"):
                    st.toast("Copied to clipboard!")
                if st.button("🔄 Reset Stats", key=f"reset_{link['short_code']}"):
                    if st.confirm("Are you sure? This will reset all analytics data."):
                        self.url_shortener.reset_analytics(link['short_code'])
                        st.success("Analytics reset successfully!")

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

    def generate_qr_code(self, url: str) -> str:
        """Generate QR code for URL"""
        qr = qrcode.QRCode(version=1, box_size=10, border=5)
        qr.add_data(url)
        qr.make(fit=True)
        
        img = qr.make_image(fill_color="black", back_color="white")
        buffered = BytesIO()
        img.save(buffered, format="PNG")
        return buffered.getvalue() 
