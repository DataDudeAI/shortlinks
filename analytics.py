from typing import Dict, Any, List
from urllib.parse import urlparse, parse_qs
from datetime import datetime

class Analytics:
    def __init__(self, database):
        self.db = database

    def parse_utm_parameters(self, url: str) -> Dict[str, str]:
        try:
            parsed_url = urlparse(url)
            query_params = parse_qs(parsed_url.query)
            
            utm_params = {
                'utm_source': query_params.get('utm_source', [None])[0],
                'utm_medium': query_params.get('utm_medium', [None])[0],
                'utm_campaign': query_params.get('utm_campaign', [None])[0]
            }
            
            # Set default values if parameters are missing
            if not utm_params['utm_source']:
                utm_params['utm_source'] = 'direct'
            if not utm_params['utm_medium']:
                utm_params['utm_medium'] = 'none'
            if not utm_params['utm_campaign']:
                utm_params['utm_campaign'] = 'no campaign'
                
            return utm_params
        except Exception:
            return {
                'utm_source': 'direct',
                'utm_medium': 'none',
                'utm_campaign': 'no campaign'
            }

    def track_click(self, short_code: str, request_data: Dict[str, Any]):
        try:
            # Get referrer or use direct if none
            referrer = request_data.get('referrer', '')
            
            # Parse UTM parameters from the original URL
            url_info = self.db.get_url_info(short_code)
            if url_info:
                utm_params = self.parse_utm_parameters(url_info['original_url'])
            else:
                utm_params = {
                    'utm_source': 'direct',
                    'utm_medium': 'none',
                    'utm_campaign': 'no campaign'
                }

            # Combine with referrer data
            analytics_data = {
                'short_code': short_code,
                'clicked_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                'utm_source': utm_params['utm_source'],
                'utm_medium': utm_params['utm_medium'],
                'utm_campaign': utm_params['utm_campaign'],
                'referrer': referrer
            }
            
            self.db.save_analytics(analytics_data)
            
        except Exception as e:
            print(f"Error tracking click: {str(e)}")

    def get_analytics(self, short_code: str) -> Dict[str, Any]:
        try:
            analytics_data = self.db.get_analytics_data(short_code)
            if not analytics_data:
                return None

            # Ensure we have default values for all fields
            analytics_data.setdefault('utm_sources', {'direct': 0})
            analytics_data.setdefault('utm_mediums', {'none': 0})
            analytics_data.setdefault('campaigns', {'no campaign': 0})
            analytics_data.setdefault('clicks_over_time', {})

            return analytics_data
            
        except Exception as e:
            print(f"Error getting analytics: {str(e)}")
            return None

    def get_redirect_url(self, short_code: str) -> str:
        url_info = self.db.get_url_info(short_code)
        if url_info:
            return url_info['original_url']
        return None

    def get_past_links(self) -> List[Dict[str, Any]]:
        try:
            return self.db.get_all_urls()
        except Exception as e:
            print(f"Error getting past links: {str(e)}")
            return [] 
