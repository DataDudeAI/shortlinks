from typing import Dict, Any, List
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

class Organization:
    def __init__(self, db):
        self.db = db

    def create_organization(self, data: Dict[str, Any]) -> bool:
        """Create a new organization with social media and ad network credentials"""
        try:
            org_data = {
                'org_id': data.get('org_id'),
                'name': data.get('name'),
                'website': data.get('website'),
                'industry': data.get('industry'),
                'created_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                'social_media': {
                    'facebook': {
                        'app_id': data.get('fb_app_id'),
                        'app_secret': data.get('fb_app_secret'),
                        'access_token': data.get('fb_access_token'),
                        'page_id': data.get('fb_page_id')
                    },
                    'twitter': {
                        'api_key': data.get('twitter_api_key'),
                        'api_secret': data.get('twitter_api_secret'),
                        'access_token': data.get('twitter_access_token'),
                        'access_secret': data.get('twitter_access_secret')
                    },
                    'linkedin': {
                        'client_id': data.get('linkedin_client_id'),
                        'client_secret': data.get('linkedin_client_secret'),
                        'access_token': data.get('linkedin_access_token')
                    },
                    'instagram': {
                        'client_id': data.get('instagram_client_id'),
                        'client_secret': data.get('instagram_client_secret'),
                        'access_token': data.get('instagram_access_token')
                    }
                },
                'ad_networks': {
                    'google_ads': {
                        'client_id': data.get('google_client_id'),
                        'client_secret': data.get('google_client_secret'),
                        'developer_token': data.get('google_developer_token'),
                        'refresh_token': data.get('google_refresh_token'),
                        'customer_id': data.get('google_customer_id')
                    },
                    'facebook_ads': {
                        'ad_account_id': data.get('fb_ad_account_id'),
                        'access_token': data.get('fb_ads_access_token')
                    },
                    'linkedin_ads': {
                        'organization_id': data.get('linkedin_org_id'),
                        'access_token': data.get('linkedin_ads_access_token')
                    }
                },
                'settings': {
                    'auto_posting': data.get('auto_posting', False),
                    'default_platforms': data.get('default_platforms', []),
                    'post_approval': data.get('post_approval', True),
                    'scheduling_enabled': data.get('scheduling_enabled', False)
                }
            }
            return self.db.save_organization(org_data)
        except Exception as e:
            logger.error(f"Error creating organization: {str(e)}")
            return False

    def update_organization(self, org_id: str, data: Dict[str, Any]) -> bool:
        """Update organization settings and credentials"""
        try:
            return self.db.update_organization(org_id, data)
        except Exception as e:
            logger.error(f"Error updating organization: {str(e)}")
            return False 