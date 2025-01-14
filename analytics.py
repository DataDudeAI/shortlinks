import logging
from datetime import datetime
from typing import Dict, Any, Optional, List
from user_agents import parse
import requests
import os
import streamlit as st
from user_journey_tracker import JourneyEventType

# Setup logging
logger = logging.getLogger(__name__)

class Analytics:
    def __init__(self, db):
        self.db = db
        self.ip_api_url = "http://ip-api.com/json/"  # Free IP geolocation API

    def get_geo_data(self, ip_address: str) -> Dict[str, str]:
        """Get geolocation data from IP address using free IP API"""
        try:
            if ip_address and ip_address not in ('127.0.0.1', 'localhost', ''):
                response = requests.get(f"{self.ip_api_url}{ip_address}")
                if response.status_code == 200:
                    data = response.json()
                    if data.get('status') == 'success':
                        return {
                            'country': data.get('country', 'Unknown'),
                            'city': data.get('city', 'Unknown')
                        }
        except Exception as e:
            logger.warning(f"Error getting geo data for IP {ip_address}: {str(e)}")
        
        return {
            'country': 'Unknown',
            'city': 'Unknown'
        }

    def track_click(self, short_code: str, request_data: Dict[str, Any]) -> Dict[str, Any]:
        """Enhanced click tracking with success tracking"""
        try:
            # Get the original URL first
            original_url = self.get_redirect_url(short_code)
            is_successful = bool(original_url)
            
            # Extract user agent info
            user_agent = request_data.get('User-Agent', '')
            ua_parser = parse(user_agent) if user_agent else None
            
            # Get geolocation data
            ip_address = request_data.get('ip', '')
            geo_data = self.get_geo_data(ip_address)
            
            # Prepare analytics data with safe defaults
            analytics_data = {
                'short_code': short_code,
                'clicked_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                'utm_source': request_data.get('utm_source', 'direct'),
                'utm_medium': request_data.get('utm_medium', 'none'),
                'utm_campaign': request_data.get('utm_campaign', 'no campaign'),
                'referrer': request_data.get('referrer', ''),
                'user_agent': user_agent,
                'ip_address': ip_address,
                'country': geo_data.get('country', 'Unknown'),
                'device_type': ua_parser.device.family if ua_parser else 'Unknown',
                'browser': ua_parser.browser.family if ua_parser else 'Unknown',
                'os': ua_parser.os.family if ua_parser else 'Unknown',
                'successful': is_successful
            }
            
            # Save to database
            self.db.save_analytics(analytics_data)
            logger.info(f"Tracked click for {short_code}: {analytics_data['successful']}")
            
            return analytics_data
            
        except Exception as e:
            logger.error(f"Error tracking click for {short_code}: {str(e)}")
            return {
                'short_code': short_code,
                'clicked_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                'successful': False
            }

    def get_recent_clicks(self, short_code: str, limit: int = 10) -> List[Dict[str, Any]]:
        """Get most recent clicks for a URL"""
        try:
            return self.db.get_recent_clicks(short_code, limit)
        except Exception as e:
            logger.error(f"Error getting recent clicks for {short_code}: {str(e)}")
            return []

    def get_analytics(self, short_code: str) -> Dict[str, Any]:
        """Get analytics data for a specific short code"""
        try:
            return self.db.get_analytics_data(short_code)
        except Exception as e:
            logger.error(f"Error getting analytics for {short_code}: {str(e)}")
            return None

    def get_redirect_url(self, short_code: str) -> Optional[str]:
        """Get the original URL for redirection"""
        try:
            url_info = self.db.get_url_info(short_code)
            return url_info['original_url'] if url_info else None
        except Exception as e:
            logger.error(f"Error getting redirect URL for {short_code}: {str(e)}")
            return None 

    def capture_client_info(self) -> Dict[str, Any]:
        """Capture detailed client information"""
        try:
            user_agent = st.request_headers.get('User-Agent', '')
            ua_parser = parse(user_agent) if user_agent else None
            
            client_info = {
                'ip_address': st.request_headers.get('X-Forwarded-For', '').split(',')[0],
                'user_agent': user_agent,
                'referrer': st.request_headers.get('Referer', ''),
                'device_type': ua_parser.device.family if ua_parser else 'Unknown',
                'browser': ua_parser.browser.family if ua_parser else 'Unknown',
                'browser_version': ua_parser.browser.version_string if ua_parser else 'Unknown',
                'os': ua_parser.os.family if ua_parser else 'Unknown',
                'os_version': ua_parser.os.version_string if ua_parser else 'Unknown',
                'is_mobile': ua_parser.is_mobile if ua_parser else False,
                'is_tablet': ua_parser.is_tablet if ua_parser else False,
                'is_pc': ua_parser.is_pc if ua_parser else False,
                'timestamp': datetime.now().isoformat()
            }

            # Get geolocation data
            if client_info['ip_address'] and client_info['ip_address'] not in ('127.0.0.1', 'localhost'):
                geo_data = self.get_geo_data(client_info['ip_address'])
                client_info.update(geo_data)

            return client_info

        except Exception as e:
            logger.error(f"Error capturing client info: {str(e)}")
            return {}

    def track_event(self, event_type: str, event_data: Dict[str, Any] = None):
        """Track analytics event with client data"""
        try:
            client_info = self.capture_client_info()
            event_data = event_data or {}
            event_data.update(client_info)

            # Store in database
            self.db.save_analytics_event(
                event_type=event_type,
                event_data=event_data
            )

            # Track in journey if available
            if hasattr(st.session_state, 'journey_tracker') and st.session_state.journey_tracker:
                st.session_state.journey_tracker.track_event(
                    event_type=JourneyEventType.CUSTOM_EVENT,
                    event_name=event_type,
                    event_data=event_data
                )

            logger.info(f"Tracked event {event_type}: {event_data}")

        except Exception as e:
            logger.error(f"Error tracking event: {str(e)}")

    def get_analytics_summary(self) -> Dict[str, Any]:
        """Get comprehensive analytics summary"""
        try:
            summary = {
                'total_visitors': self.db.get_total_visitors(),
                'unique_visitors': self.db.get_unique_visitors(),
                'conversion_rate': self.calculate_conversion_rate(),
                'device_stats': self.get_device_stats(),
                'browser_stats': self.get_browser_stats(),
                'os_stats': self.get_os_stats(),
                'geo_stats': self.get_geo_stats(),
                'recent_events': self.get_recent_events(limit=10)
            }
            return summary
        except Exception as e:
            logger.error(f"Error getting analytics summary: {str(e)}")
            return {}

    def calculate_conversion_rate(self) -> float:
        """Calculate conversion rate"""
        try:
            total_visitors = self.db.get_total_visitors()
            conversions = self.db.get_total_conversions()
            if total_visitors > 0:
                return (conversions / total_visitors) * 100
            return 0.0
        except Exception as e:
            logger.error(f"Error calculating conversion rate: {str(e)}")
            return 0.0

    def get_device_stats(self) -> Dict[str, int]:
        """Get device type distribution"""
        try:
            return self.db.get_device_stats()
        except Exception as e:
            logger.error(f"Error getting device stats: {str(e)}")
            return {}

    def get_browser_stats(self) -> Dict[str, int]:
        """Get browser distribution"""
        try:
            return self.db.get_browser_stats()
        except Exception as e:
            logger.error(f"Error getting browser stats: {str(e)}")
            return {}

    def get_os_stats(self) -> Dict[str, int]:
        """Get operating system distribution"""
        try:
            return self.db.get_os_stats()
        except Exception as e:
            logger.error(f"Error getting OS stats: {str(e)}")
            return {}

    def get_geo_stats(self) -> Dict[str, int]:
        """Get geographical distribution"""
        try:
            return self.db.get_geo_stats()
        except Exception as e:
            logger.error(f"Error getting geo stats: {str(e)}")
            return {}

    def get_recent_events(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Get recent analytics events"""
        try:
            return self.db.get_recent_events(limit)
        except Exception as e:
            logger.error(f"Error getting recent events: {str(e)}")
            return [] 
