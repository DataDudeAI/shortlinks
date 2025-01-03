from typing import Dict, Any
from datetime import datetime
import pandas as pd
from user_agents import parse

class Analytics:
    def __init__(self, database):
        self.db = database

    def track_click(self, short_code: str, request_data: Dict[str, Any]):
        """Enhanced click tracking with detailed analytics"""
        try:
            # Extract user agent info
            user_agent = request_data.get('User-Agent', '')
            user_agent_parser = parse(user_agent)
            
            # Get geolocation data from IP
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
                'device_type': user_agent_parser.device.family,
                'browser': user_agent_parser.browser.family,
                'os': user_agent_parser.os.family
            }
            
            # Save to database
            self.db.save_analytics(analytics_data)
            
            # Update cache for real-time analytics
            self.update_realtime_cache(short_code, analytics_data)
            
        except Exception as e:
            logger.error(f"Error tracking click: {str(e)}")

    def get_analytics(self, short_code: str) -> Dict[str, Any]:
        """Get analytics data for a specific short code"""
        try:
            # Get basic URL info
            url_info = self.db.get_url_info(short_code)
            if not url_info:
                return None
            
            # Get click data
            clicks = self.db.get_clicks(short_code)
            
            # Calculate statistics
            total_clicks = len(clicks)
            last_clicked = clicks[-1]['clicked_at'] if clicks else 'Never'
            
            # Count unique sources
            sources = {}
            mediums = {}
            campaigns = {}
            
            for click in clicks:
                # Count sources
                source = click.get('utm_source', 'direct')
                sources[source] = sources.get(source, 0) + 1
                
                # Count mediums
                medium = click.get('utm_medium', 'none')
                mediums[medium] = mediums.get(medium, 0) + 1
                
                # Count campaigns
                campaign = click.get('utm_campaign', 'none')
                campaigns[campaign] = campaigns.get(campaign, 0) + 1
            
            return {
                'original_url': url_info['original_url'],
                'short_code': short_code,
                'created_at': url_info['created_at'],
                'total_clicks': total_clicks,
                'last_clicked': last_clicked,
                'utm_sources': sources,
                'utm_mediums': mediums,
                'utm_campaigns': campaigns,
                'recent_clicks': clicks[-10:] if clicks else []  # Last 10 clicks
            }
            
        except Exception as e:
            print(f"Error getting analytics: {str(e)}")
            return None

    def get_redirect_url(self, short_code: str) -> str:
        """Get the redirect URL"""
        url_info = self.db.get_url_info(short_code)
        if url_info:
            return url_info['original_url']
        return None

    def parse_utm_parameters(self, url: str) -> Dict[str, str]:
        """Parse UTM parameters from URL"""
        try:
            parsed_url = urlparse(url)
            query_params = parse_qs(parsed_url.query)
            
            return {
                'utm_source': query_params.get('utm_source', ['direct'])[0],
                'utm_medium': query_params.get('utm_medium', ['none'])[0],
                'utm_campaign': query_params.get('utm_campaign', ['none'])[0]
            }
        except:
            return {
                'utm_source': 'direct',
                'utm_medium': 'none',
                'utm_campaign': 'none'
            } 
