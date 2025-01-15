import requests
import json
from datetime import datetime
import logging
from typing import Dict, Optional
import os

logger = logging.getLogger(__name__)

class IPTracker:
    def __init__(self):
        self.log_file = "click_data.txt"
        self.api_endpoints = [
            "http://ip-api.com/json/",  # Free API, no key needed
            "https://ipapi.co/json/",    # Backup API
            "https://ipinfo.io/json"     # Another backup
        ]

    def get_ip_details(self, ip_address: str) -> Dict:
        """Get detailed information about an IP address"""
        try:
            # Try multiple APIs in case of failure
            for endpoint in self.api_endpoints:
                try:
                    response = requests.get(f"{endpoint}{ip_address}" if ip_address != "127.0.0.1" else endpoint)
                    if response.status_code == 200:
                        data = response.json()
                        ip_data = {
                            'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                            'ip_address': ip_address,
                            'country': data.get('country', 'Unknown'),
                            'region': data.get('region', 'Unknown'),
                            'city': data.get('city', 'Unknown'),
                            'isp': data.get('isp', 'Unknown'),
                            'org': data.get('org', 'Unknown'),
                            'latitude': data.get('lat', 0),
                            'longitude': data.get('lon', 0),
                            'timezone': data.get('timezone', 'Unknown'),
                            'asn': data.get('as', 'Unknown')
                        }
                        self._log_ip_data(ip_data)
                        return ip_data
                except Exception as e:
                    logger.error(f"Error with API endpoint {endpoint}: {str(e)}")
                    continue

            # If all APIs fail, return default India-based data
            return self._get_default_india_data(ip_address)

        except Exception as e:
            logger.error(f"Error getting IP details: {str(e)}")
            return self._get_default_india_data(ip_address)

    def _get_default_india_data(self, ip_address: str) -> Dict:
        """Return default India-based data when APIs fail"""
        return {
            'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'ip_address': ip_address,
            'country': 'India',
            'region': 'Maharashtra',
            'city': 'Mumbai',
            'isp': 'Unknown',
            'org': 'Unknown',
            'latitude': 19.0760,
            'longitude': 72.8777,
            'timezone': 'Asia/Kolkata',
            'asn': 'Unknown'
        }

    def _log_ip_data(self, data: Dict):
        """Log IP data to file with formatted output"""
        try:
            with open(self.log_file, 'a', encoding='utf-8') as f:
                f.write("\n" + "="*50 + "\n")
                f.write(f"Timestamp: {data['timestamp']}\n")
                f.write(f"IP Address: {data['ip_address']}\n")
                f.write(f"Location: {data['city']}, {data['region']}, {data['country']}\n")
                f.write(f"ISP: {data['isp']}\n")
                f.write(f"Organization: {data['org']}\n")
                f.write(f"Coordinates: {data['latitude']}, {data['longitude']}\n")
                f.write(f"Timezone: {data['timezone']}\n")
                f.write(f"ASN: {data['asn']}\n")
                f.write("="*50 + "\n")
        except Exception as e:
            logger.error(f"Error logging IP data: {str(e)}")

    def get_click_data(self, client_info: Dict) -> Dict:
        """Get comprehensive click data including IP details"""
        try:
            ip_address = client_info.get('ip_address', '')
            ip_details = self.get_ip_details(ip_address)
            
            click_data = {
                **ip_details,
                'user_agent': client_info.get('user_agent', 'Unknown'),
                'referrer': client_info.get('referrer', 'Direct'),
                'device_type': client_info.get('device_type', 'Desktop'),
                'browser': client_info.get('browser', 'Unknown'),
                'os': client_info.get('os', 'Unknown'),
                'session_id': client_info.get('session_id', 'Unknown'),
                'campaign': client_info.get('campaign_name', 'Unknown')
            }
            
            self._log_click_data(click_data)
            return click_data
            
        except Exception as e:
            logger.error(f"Error getting click data: {str(e)}")
            return client_info

    def _log_click_data(self, data: Dict):
        """Log comprehensive click data"""
        try:
            with open("click_data.txt", 'a', encoding='utf-8') as f:
                f.write("\n" + "*"*50 + "\n")
                f.write("CLICK EVENT DATA\n")
                f.write("*"*50 + "\n")
                f.write(json.dumps(data, indent=2))
                f.write("\n" + "*"*50 + "\n")
        except Exception as e:
            logger.error(f"Error logging click data: {str(e)}") 