from google.analytics.data_v1beta import BetaAnalyticsDataClient
from google.analytics.data_v1beta.types import RunReportRequest
import streamlit as st
import os
import logging

logger = logging.getLogger(__name__)

class GoogleAnalytics:
    def __init__(self):
        """Initialize Google Analytics client"""
        try:
            self.measurement_id = os.getenv('GA_MEASUREMENT_ID')
            self.api_secret = os.getenv('GA_API_SECRET')
            
            if self.measurement_id:
                # Add GA4 tracking code to Streamlit
                ga_script = f"""
                    <!-- Global site tag (gtag.js) - Google Analytics -->
                    <script async src="https://www.googletagmanager.com/gtag/js?id={self.measurement_id}"></script>
                    <script>
                        window.dataLayer = window.dataLayer || [];
                        function gtag(){{dataLayer.push(arguments);}}
                        gtag('js', new Date());
                        gtag('config', '{self.measurement_id}');
                    </script>
                """
                st.markdown(ga_script, unsafe_allow_html=True)
            else:
                logger.warning("GA4 measurement ID not found in environment variables")
            
        except Exception as e:
            logger.error(f"Error initializing Google Analytics: {str(e)}")
            
    def track_event(self, event_category: str, event_action: str, event_label: str = None):
        """Track an event in GA4"""
        try:
            if self.measurement_id:
                event_params = {
                    'event_category': event_category,
                    'event_action': event_action
                }
                if event_label:
                    event_params['event_label'] = event_label
                    
                gtag_script = f"""
                    <script>
                        gtag('event', '{event_action}', {event_params});
                    </script>
                """
                st.markdown(gtag_script, unsafe_allow_html=True)
        except Exception as e:
            logger.error(f"Error tracking event: {str(e)}") 

    def track_page_view(self, page_name: str):
        """Track page view in GA4"""
        try:
            if self.measurement_id:
                gtag_script = f"""
                    <script>
                        gtag('event', 'page_view', {{
                            'page_title': '{page_name}',
                            'page_location': window.location.href
                        }});
                    </script>
                """
                st.markdown(gtag_script, unsafe_allow_html=True)
        except Exception as e:
            logger.error(f"Error tracking page view: {str(e)}") 