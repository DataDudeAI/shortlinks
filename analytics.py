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
            if ip_address and ip_address != '127.0.0.1':  # Skip localhost
                response = DbIpCity.get(ip_address, api_key='free')
                return {
                    'country': response.country or 'Unknown',
                    'city': response.city or 'Unknown',
                }
        except Exception as e:
            logger.warning(f"Error getting geo data: {str(e)}")
        
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
            ua_parser = parse(user_agent)
            
            # Get geolocation data
            ip_address = request_data.get('ip', '')
            geo_data = self.get_geo_data(ip_address)
            
            # Prepare analytics data
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
                'device_type': ua_parser.device.family,
                'browser': ua_parser.browser.family,
                'os': ua_parser.os.family,
                'successful': is_successful
            }
            
            # Save to database
            self.db.save_analytics(analytics_data)
            
            return analytics_data
            
        except Exception as e:
            logger.error(f"Error tracking click: {str(e)}")
            return {}

    def get_recent_clicks(self, short_code: str, limit: int = 10) -> List[Dict[str, Any]]:
        """Get most recent clicks for a URL"""
        return self.db.get_recent_clicks(short_code, limit)

    def get_analytics(self, short_code: str) -> Dict[str, Any]:
        """Get analytics data for a specific short code"""
        return self.db.get_analytics_data(short_code)

    def get_redirect_url(self, short_code: str) -> Optional[str]:
        """Get the original URL for redirection"""
        url_info = self.db.get_url_info(short_code)
        if url_info:
            return url_info['original_url']
        return None 
