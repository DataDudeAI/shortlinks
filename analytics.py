import logging
from datetime import datetime
from typing import Dict, Any, Optional, List
from user_agents import parse
from ip2geotools.databases.noncommercial import DbIpCity
import os

# Setup logging
logger = logging.getLogger(__name__)

class Analytics:
    def __init__(self, db):
        self.db = db

    def get_geo_data(self, ip_address: str) -> Dict[str, str]:
        """Get geolocation data from IP address using free IP database"""
        try:
            if ip_address and ip_address not in ('127.0.0.1', 'localhost', ''):
                response = DbIpCity.get(ip_address, api_key='free')
                if response and response.country:
                    return {
                        'country': response.country,
                        'city': response.city or 'Unknown'
                    }
        except Exception as e:
            logger.warning(f"Error getting geo data for IP {ip_address}: {str(e)}")
        
        # Default response for any failure case
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
