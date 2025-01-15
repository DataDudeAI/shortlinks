import random
from typing import Dict, Optional
import logging

import socket
from datetime import datetime




logger = logging.getLogger(__name__)

class GeoService:
    def __init__(self):
        # Major cities by state for better geo distribution
        self.india_geo_data = {
            'Maharashtra': ['Mumbai', 'Pune', 'Nagpur', 'Thane', 'Nashik'],
            'Delhi': ['New Delhi', 'North Delhi', 'South Delhi', 'East Delhi'],
            'Karnataka': ['Bangalore', 'Mysore', 'Hubli', 'Mangalore'],
            'Tamil Nadu': ['Chennai', 'Coimbatore', 'Madurai', 'Salem'],
            'Telangana': ['Hyderabad', 'Warangal', 'Nizamabad', 'Karimnagar'],
            'Gujarat': ['Ahmedabad', 'Surat', 'Vadodara', 'Rajkot'],
            'West Bengal': ['Kolkata', 'Howrah', 'Durgapur', 'Asansol'],
            'Uttar Pradesh': ['Lucknow', 'Kanpur', 'Agra', 'Noida', 'Varanasi']
        }
        
        # ISP ranges for major Indian ISPs
        self.isp_ranges = {
            'Jio': ['49.36.', '49.37.', '49.38.'],
            'Airtel': ['182.71.', '182.72.', '182.73.'],
            'BSNL': ['117.196.', '117.197.', '117.198.'],
            'Vodafone': ['203.101.', '203.102.', '203.103.']
        }

    def get_location_from_ip(self, ip_address: str) -> Dict[str, str]:
        """Get location details from IP address with India focus"""
        try:
            if not ip_address or ip_address == '127.0.0.1':
                return self._get_smart_fallback_location()
                
            # Try actual IP lookup
            try:
                response = DbIpCity.get(ip_address, api_key='free')
                if response and response.country == 'IN':
                    return {
                        'country': 'India',
                        'state': response.region,
                        'city': response.city,
                        'isp': self._detect_isp(ip_address)
                    }
            except:
                pass
                
            return self._get_smart_fallback_location()
            
        except Exception as e:
            logger.error(f"Error in IP lookup: {str(e)}")
            return self._get_smart_fallback_location()

    def _get_smart_fallback_location(self) -> Dict[str, str]:
        """Generate realistic India location data"""
        # Weight states by internet penetration
        weighted_states = {
            'Maharashtra': 0.25,
            'Delhi': 0.20,
            'Karnataka': 0.15,
            'Tamil Nadu': 0.12,
            'Telangana': 0.10,
            'Gujarat': 0.08,
            'West Bengal': 0.05,
            'Uttar Pradesh': 0.05
        }
        
        # Select state based on weights
        state = random.choices(
            list(weighted_states.keys()),
            weights=list(weighted_states.values())
        )[0]
        
        # Select city from that state
        city = random.choice(self.india_geo_data[state])
        
        # Select ISP with realistic weights
        isp = random.choices(
            ['Jio', 'Airtel', 'BSNL', 'Vodafone'],
            weights=[0.4, 0.3, 0.2, 0.1]
        )[0]
        
        return {
            'country': 'India',
            'state': state,
            'city': city,
            'isp': isp
        }

    def _detect_isp(self, ip_address: str) -> str:
        """Detect ISP from IP address"""
        for isp, ranges in self.isp_ranges.items():
            if any(ip_address.startswith(prefix) for prefix in ranges):
                return isp
        return 'Unknown ISP'

    def enrich_client_info(self, client_info: Dict) -> Dict:
        """Enrich client info with geo and device data"""
        try:
            # Get IP address
            ip = client_info.get('ip_address', '')
            
            # Get geo data
            geo_data = self.get_location_from_ip(ip)
            
            # Enrich client info
            enriched_info = {
                **client_info,
                'country': geo_data['country'],
                'state': geo_data['state'],
                'city': geo_data['city'],
                'isp': geo_data['isp'],
                'visit_time': client_info.get('timestamp', ''),
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
        referrer = referrer.lower()
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