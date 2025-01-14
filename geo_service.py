import csv
import ipaddress
from typing import Optional, Dict
import requests
import os
from datetime import datetime, timedelta

class GeoIPService:
    def __init__(self):
        self.ip_ranges = {
            'IN': [],  # India
            'PK': [],  # Pakistan
            'BD': []   # Bangladesh
        }
        self.load_ip_ranges()
        
    def load_ip_ranges(self):
        """Load IP ranges from CSV files"""
        countries = {
            'IN': 'india_ip_ranges.csv',
            'PK': 'pakistan_ip_ranges.csv',
            'BD': 'bangladesh_ip_ranges.csv'
        }
        
        for country_code, filename in countries.items():
            if os.path.exists(filename):
                with open(filename, 'r') as f:
                    reader = csv.DictReader(f)
                    for row in reader:
                        self.ip_ranges[country_code].append({
                            'start_ip': ipaddress.ip_address(row['start_ip']),
                            'end_ip': ipaddress.ip_address(row['end_ip']),
                            'state': row.get('state', 'Unknown')
                        })

    def update_database(self):
        """Update IP ranges database from APNIC"""
        url = "https://ftp.apnic.net/apnic/stats/apnic/delegated-apnic-latest"
        
        try:
            response = requests.get(url)
            data = response.text.split('\n')
            
            # Process for each country
            for country_code in ['IN', 'PK', 'BD']:
                ranges = []
                
                for line in data:
                    if f"|{country_code}|ipv4|" in line:
                        parts = line.split('|')
                        if len(parts) >= 5:
                            start_ip = parts[3]
                            num_ips = int(parts[4])
                            
                            # Calculate end IP
                            start = ipaddress.ip_address(start_ip)
                            end = ipaddress.ip_address(int(start) + num_ips - 1)
                            
                            ranges.append({
                                'start_ip': start_ip,
                                'end_ip': str(end)
                            })
                
                # Save to CSV
                filename = f"{country_code.lower()}_ip_ranges.csv"
                with open(filename, 'w', newline='') as f:
                    writer = csv.DictWriter(f, fieldnames=['start_ip', 'end_ip'])
                    writer.writeheader()
                    writer.writerows(ranges)
                
            return True
            
        except Exception as e:
            print(f"Error updating database: {str(e)}")
            return False

    def get_location(self, ip: str) -> Dict[str, str]:
        """Get location information for an IP address"""
        try:
            ip_obj = ipaddress.ip_address(ip)
            
            # Check local addresses
            if ip_obj.is_private:
                return {
                    'country_code': 'LOCAL',
                    'country': 'Local Network',
                    'state': 'Local'
                }
            
            # Check each country's IP ranges
            for country_code, ranges in self.ip_ranges.items():
                for ip_range in ranges:
                    if ip_range['start_ip'] <= ip_obj <= ip_range['end_ip']:
                        return {
                            'country_code': country_code,
                            'country': self.get_country_name(country_code),
                            'state': ip_range['state']
                        }
            
            # If not found in our database, use a fallback service
            return self.get_location_fallback(ip)
            
        except Exception as e:
            print(f"Error getting location: {str(e)}")
            return {
                'country_code': 'XX',
                'country': 'Unknown',
                'state': 'Unknown'
            }

    def get_country_name(self, country_code: str) -> str:
        """Get country name from country code"""
        countries = {
            'IN': 'India',
            'PK': 'Pakistan',
            'BD': 'Bangladesh'
        }
        return countries.get(country_code, 'Unknown')

    def get_location_fallback(self, ip: str) -> Dict[str, str]:
        """Fallback to a free IP geolocation API"""
        try:
            response = requests.get(f"https://ipapi.co/{ip}/json/")
            data = response.json()
            
            return {
                'country_code': data.get('country_code', 'XX'),
                'country': data.get('country_name', 'Unknown'),
                'state': data.get('region', 'Unknown')
            }
        except:
            return {
                'country_code': 'XX',
                'country': 'Unknown',
                'state': 'Unknown'
            }