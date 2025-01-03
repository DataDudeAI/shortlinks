import streamlit as st
import pandas as pd
from typing import Dict, Any
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

        # Create two columns for the layout
        col1, col2 = st.columns([2, 1])
        
        with col1:
            # URL Information Section
            st.subheader("📊 Link Details")
            url_info = pd.DataFrame({
                'Metric': [
                    'Original URL',
                    'Short Code',
                    'Created Date',
                    'Last Click',
                    'Total Clicks',
                    'Unique Sources',
                    'Unique Mediums'
                ],
                'Value': [
                    analytics_data['original_url'],
                    analytics_data.get('short_code', 'N/A'),
                    datetime.strptime(analytics_data['created_at'], '%Y-%m-%d %H:%M:%S').strftime('%Y-%m-%d %H:%M'),
                    analytics_data.get('last_clicked', 'No clicks yet'),
                    analytics_data['total_clicks'],
                    analytics_data.get('unique_sources', 0),
                    analytics_data.get('unique_mediums', 0)
                ]
            })
            st.dataframe(url_info, hide_index=True, use_container_width=True)

        with col2:
            # Quick Stats
            st.subheader("📈 Quick Stats")
            
            # Calculate click rate per day
            created_date = datetime.strptime(analytics_data['created_at'], '%Y-%m-%d %H:%M:%S')
            days_active = (datetime.now() - created_date).days + 1
            clicks_per_day = analytics_data['total_clicks'] / days_active

            metrics = {
                "Total Clicks": analytics_data['total_clicks'],
                "Days Active": days_active,
                "Avg. Clicks/Day": f"{clicks_per_day:.1f}"
            }
            
            for label, value in metrics.items():
                st.metric(label=label, value=value)

        # Traffic Sources Analysis
        st.subheader("🔍 Traffic Analysis")
        
        col1, col2 = st.columns(2)
        
        with col1:
            # Source Analysis
            st.subheader("Traffic Sources")
            if analytics_data['utm_sources']:
                utm_df = pd.DataFrame(
                    analytics_data['utm_sources'].items(),
                    columns=['Source', 'Clicks']
                )
                utm_df['Percentage'] = (utm_df['Clicks'] / utm_df['Clicks'].sum() * 100).round(1)
                utm_df['Percentage'] = utm_df['Percentage'].astype(str) + '%'
                
                st.bar_chart(utm_df.set_index('Source')['Clicks'])
                st.dataframe(utm_df, hide_index=True, use_container_width=True)
            else:
                st.info("No source data available yet")

        with col2:
            # Medium Analysis
            st.subheader("Traffic Mediums")
            if analytics_data.get('utm_mediums'):
                utm_medium_df = pd.DataFrame(
                    analytics_data['utm_mediums'].items(),
                    columns=['Medium', 'Clicks']
                )
                utm_medium_df['Percentage'] = (utm_medium_df['Clicks'] / utm_medium_df['Clicks'].sum() * 100).round(1)
                utm_medium_df['Percentage'] = utm_medium_df['Percentage'].astype(str) + '%'
                
                st.bar_chart(utm_medium_df.set_index('Medium')['Clicks'])
                st.dataframe(utm_medium_df, hide_index=True, use_container_width=True)
            else:
                st.info("No medium data available yet")

        # Time Analysis
        if analytics_data.get('clicks_over_time'):
            st.subheader("📅 Time Analysis")
            time_df = pd.DataFrame(
                analytics_data['clicks_over_time'].items(),
                columns=['Date', 'Clicks']
            )
            time_df['Date'] = pd.to_datetime(time_df['Date'])
            time_df = time_df.sort_values('Date')
            
            st.line_chart(time_df.set_index('Date'))
            st.dataframe(time_df, hide_index=True, use_container_width=True)

        # Campaign Performance
        if analytics_data.get('campaigns'):
            st.subheader("🎯 Campaign Performance")
            campaign_df = pd.DataFrame(
                analytics_data['campaigns'].items(),
                columns=['Campaign', 'Clicks']
            )
            campaign_df['Percentage'] = (campaign_df['Clicks'] / campaign_df['Clicks'].sum() * 100).round(1)
            campaign_df['Percentage'] = campaign_df['Percentage'].astype(str) + '%'
            
            st.bar_chart(campaign_df.set_index('Campaign')['Clicks'])
            st.dataframe(campaign_df, hide_index=True, use_container_width=True)

        # Export Options
        st.subheader("📤 Export Data")
        
        try:
            # Prepare data for CSV export
            export_dict = {
                'Link Details': {
                    'Original URL': analytics_data['original_url'],
                    'Short Code': analytics_data.get('short_code', 'N/A'),
                    'Created Date': analytics_data['created_at'],
                    'Total Clicks': analytics_data['total_clicks'],
                    'Last Click': analytics_data.get('last_clicked', 'No clicks yet'),
                    'Unique Sources': analytics_data.get('unique_sources', 0),
                    'Unique Mediums': analytics_data.get('unique_mediums', 0)
                }
            }

            # Add traffic sources
            if analytics_data.get('utm_sources'):
                export_dict['Traffic Sources'] = analytics_data['utm_sources']

            # Add traffic mediums
            if analytics_data.get('utm_mediums'):
                export_dict['Traffic Mediums'] = analytics_data['utm_mediums']

            # Convert to DataFrame
            df_details = pd.DataFrame([export_dict['Link Details']])
            
            # Create CSV data
            csv_data = io.StringIO()
            df_details.to_csv(csv_data, index=False)
            
            # Add traffic data if available
            if 'Traffic Sources' in export_dict:
                csv_data.write('\n\nTraffic Sources\n')
                pd.DataFrame(list(export_dict['Traffic Sources'].items()), 
                           columns=['Source', 'Clicks']).to_csv(csv_data, index=False)
            
            if 'Traffic Mediums' in export_dict:
                csv_data.write('\n\nTraffic Mediums\n')
                pd.DataFrame(list(export_dict['Traffic Mediums'].items()), 
                           columns=['Medium', 'Clicks']).to_csv(csv_data, index=False)

            # Offer download button
            st.download_button(
                label="📥 Download Analytics Report",
                data=csv_data.getvalue(),
                file_name=f"analytics_{analytics_data.get('short_code', 'data')}_{datetime.now().strftime('%Y%m%d')}.csv",
                mime="text/csv",
                key='download_analytics'
            )

        except Exception as e:
            st.error(f"Error generating export: {str(e)}")

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
