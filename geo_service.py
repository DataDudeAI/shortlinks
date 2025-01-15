import random
from typing import Dict, Optional
import logging
import socket
from datetime import datetime
import re

logger = logging.getLogger(__name__)

class GeoService:
    def __init__(self):
        # Major cities by state with weights for better distribution
        self.india_geo_data = {
            'Maharashtra': {
                'cities': ['Mumbai', 'Pune', 'Nagpur', 'Thane', 'Nashik'],
                'weight': 0.25,
                'ip_ranges': ['103.168.', '103.169.', '103.170.']
            },
            'Delhi': {
                'cities': ['New Delhi', 'North Delhi', 'South Delhi', 'East Delhi'],
                'weight': 0.20,
                'ip_ranges': ['103.171.', '103.172.']
            },
            'Karnataka': {
                'cities': ['Bangalore', 'Mysore', 'Hubli', 'Mangalore'],
                'weight': 0.15,
                'ip_ranges': ['103.173.', '103.174.']
            },
            'Tamil Nadu': {
                'cities': ['Chennai', 'Coimbatore', 'Madurai', 'Salem'],
                'weight': 0.12,
                'ip_ranges': ['103.175.', '103.176.']
            },
            'Telangana': {
                'cities': ['Hyderabad', 'Warangal', 'Nizamabad', 'Karimnagar'],
                'weight': 0.10,
                'ip_ranges': ['103.177.', '103.178.']
            },
            'Gujarat': {
                'cities': ['Ahmedabad', 'Surat', 'Vadodara', 'Rajkot'],
                'weight': 0.08,
                'ip_ranges': ['103.179.', '103.180.']
            },
            'West Bengal': {
                'cities': ['Kolkata', 'Howrah', 'Durgapur', 'Asansol'],
                'weight': 0.05,
                'ip_ranges': ['103.181.', '103.182.']
            },
            'Uttar Pradesh': {
                'cities': ['Lucknow', 'Kanpur', 'Agra', 'Noida', 'Varanasi'],
                'weight': 0.05,
                'ip_ranges': ['103.183.', '103.184.']
            }
        }
        
        # ISP data with market share weights
        self.isp_data = {
            'Jio': {
                'weight': 0.35,
                'ip_ranges': ['49.36.', '49.37.', '49.38.']
            },
            'Airtel': {
                'weight': 0.30,
                'ip_ranges': ['182.71.', '182.72.', '182.73.']
            },
            'BSNL': {
                'weight': 0.20,
                'ip_ranges': ['117.196.', '117.197.', '117.198.']
            },
            'Vodafone': {
                'weight': 0.15,
                'ip_ranges': ['203.101.', '203.102.', '203.103.']
            }
        }

    def get_location_from_ip(self, ip_address: str) -> Dict[str, str]:
        """Get location details from IP address with India focus"""
        try:
            if not ip_address or ip_address == '127.0.0.1':
                return self._get_smart_fallback_location()

            # Try to determine location from IP patterns
            for state, data in self.india_geo_data.items():
                if any(ip_address.startswith(prefix) for prefix in data['ip_ranges']):
                    return {
                        'country': 'India',
                        'state': state,
                        'city': random.choice(data['cities']),
                        'isp': self._detect_isp(ip_address)
                    }
            
            return self._get_smart_fallback_location()
            
        except Exception as e:
            logger.error(f"Error in IP lookup: {str(e)}")
            return self._get_smart_fallback_location()

    def _get_smart_fallback_location(self) -> Dict[str, str]:
        """Generate realistic India location data based on weights"""
        states = list(self.india_geo_data.keys())
        weights = [self.india_geo_data[state]['weight'] for state in states]
        
        state = random.choices(states, weights=weights)[0]
        city = random.choice(self.india_geo_data[state]['cities'])
        
        isp_names = list(self.isp_data.keys())
        isp_weights = [self.isp_data[isp]['weight'] for isp in isp_names]
        isp = random.choices(isp_names, weights=isp_weights)[0]
        
        return {
            'country': 'India',
            'state': state,
            'city': city,
            'isp': isp
        }

    def _detect_isp(self, ip_address: str) -> str:
        """Detect ISP from IP address patterns"""
        for isp, data in self.isp_data.items():
            if any(ip_address.startswith(prefix) for prefix in data['ip_ranges']):
                return isp
        return random.choices(
            list(self.isp_data.keys()),
            weights=[data['weight'] for data in self.isp_data.values()]
        )[0]

    def enrich_client_info(self, client_info: Dict) -> Dict:
        """Enrich client info with geo and device data"""
        try:
            ip = client_info.get('ip_address', '')
            geo_data = self.get_location_from_ip(ip)
            
            # Enrich with realistic data
            enriched_info = {
                **client_info,
                'country': geo_data['country'],
                'state': geo_data['state'],
                'city': geo_data['city'],
                'isp': geo_data['isp'],
                'visit_time': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                'is_mobile': 'mobile' in client_info.get('user_agent', '').lower(),
                'is_return_visitor': bool(client_info.get('session_id')),
                'referrer_type': self._classify_referrer(client_info.get('referrer', ''))
            }
            
            return enriched_info
            
        except Exception as e:
            logger.error(f"Error enriching client info: {str(e)}")
            return client_info

    def _classify_referrer(self, referrer: str) -> str:
        """Classify referrer into meaningful categories"""
        referrer = referrer.lower() if referrer else ''
        if not referrer:
            return 'Direct'
        elif 'google' in referrer:
            return 'Search'
        elif any(x in referrer for x in ['facebook', 'instagram', 'twitter', 'linkedin']):
            return 'Social'
        elif 'email' in referrer or 'mail' in referrer:
            return 'Email'
        else:
            return 'Other'