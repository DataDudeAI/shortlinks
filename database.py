import sqlite3
from datetime import datetime
from typing import Optional, Dict, Any, List
import os
import logging

logger = logging.getLogger(__name__)

class Database:
    """Database handler for URL shortener with analytics"""
    
    def __init__(self):
        """Initialize database connection and create tables if they don't exist"""
        self.db_path = "urls.db"
        self.create_tables()

    def get_connection(self):
        """Get database connection"""
        return sqlite3.connect(self.db_path)

    # === Database Initialization ===
    
    def create_tables(self):
        """Create necessary database tables if they don't exist"""
        conn = self.get_connection()
        c = conn.cursor()
        try:
            # Create URLs table without dropping existing one
            c.execute('''
                CREATE TABLE IF NOT EXISTS urls (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    original_url TEXT NOT NULL,
                    short_code TEXT UNIQUE NOT NULL,
                    campaign_name TEXT,
                    campaign_type TEXT,
                    created_at DATETIME NOT NULL,
                    total_clicks INTEGER DEFAULT 0,
                    enable_tracking BOOLEAN DEFAULT 1,
                    utm_source TEXT,
                    utm_medium TEXT,
                    utm_campaign TEXT,
                    utm_content TEXT,
                    utm_term TEXT,
                    expiry_date DATETIME,
                    status TEXT DEFAULT 'active',
                    tags TEXT,
                    notes TEXT,
                    last_updated DATETIME
                )
            ''')
            
            # Create analytics table without dropping existing one
            c.execute('''
                CREATE TABLE IF NOT EXISTS analytics (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    short_code TEXT NOT NULL,
                    clicked_at DATETIME NOT NULL,
                    country TEXT,
                    city TEXT,
                    device_type TEXT,
                    browser TEXT,
                    os TEXT,
                    screen_size TEXT,
                    language TEXT,
                    referrer TEXT,
                    ip_address TEXT,
                    user_agent TEXT,
                    utm_data TEXT,
                    conversion_data TEXT,
                    FOREIGN KEY (short_code) REFERENCES urls (short_code)
                )
            ''')
            
            conn.commit()
            logger.info("Database tables checked/created successfully")
        except Exception as e:
            logger.error(f"Error checking/creating tables: {str(e)}")
            raise
        finally:
            conn.close()

    # === URL Management Methods ===

    def save_url(self, url: str, short_code: str, enable_tracking: bool = True) -> bool:
        """Save a shortened URL to the database"""
        conn = self.get_connection()
        c = conn.cursor()
        try:
            now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            
            # Check if enable_tracking column exists
            c.execute("PRAGMA table_info(urls)")
            columns = [column[1] for column in c.fetchall()]
            
            if 'enable_tracking' in columns:
                c.execute('''
                    INSERT INTO urls (
                        original_url,
                        short_code,
                        created_at,
                        enable_tracking,
                        total_clicks
                    ) VALUES (?, ?, ?, ?, ?)
                ''', (url, short_code, now, 1 if enable_tracking else 0, 0))
            else:
                # Fall back to old schema if column doesn't exist
                c.execute('''
                    INSERT INTO urls (
                        original_url,
                        short_code,
                        created_at,
                        total_clicks
                    ) VALUES (?, ?, ?, ?)
                ''', (url, short_code, now, 0))
            
            conn.commit()
            return True
        except Exception as e:
            logger.error(f"Error saving URL: {str(e)}")
            return False
        finally:
            conn.close()

    def get_url_info(self, short_code: str) -> Optional[Dict[str, Any]]:
        """Get URL information for a given short code"""
        conn = self.get_connection()
        c = conn.cursor()
        try:
            c.execute('''
                SELECT 
                    original_url, 
                    created_at, 
                    total_clicks,
                    campaign_name,
                    campaign_type,
                    utm_source,
                    utm_medium,
                    utm_campaign,
                    utm_content,
                    utm_term,
                    expiry_date,
                    enable_tracking
                FROM urls 
                WHERE short_code = ?
            ''', (short_code,))
            
            result = c.fetchone()
            if not result:
                logger.error(f"No URL found for short code: {short_code}")
                return None
            
            # Check if URL has expired
            if result[10]:  # expiry_date
                expiry = datetime.strptime(result[10], '%Y-%m-%d')
                if expiry < datetime.now():
                    logger.error(f"URL has expired: {short_code}")
                    return None
            
            return {
                'original_url': result[0],
                'created_at': result[1],
                'total_clicks': result[2],
                'campaign_name': result[3],
                'campaign_type': result[4],
                'utm_source': result[5],
                'utm_medium': result[6],
                'utm_campaign': result[7],
                'utm_content': result[8],
                'utm_term': result[9],
                'expiry_date': result[10],
                'enable_tracking': bool(result[11]),
                'short_code': short_code
            }
        except Exception as e:
            logger.error(f"Error getting URL info: {str(e)}")
            return None
        finally:
            conn.close()

    def get_all_urls(self) -> List[Dict[str, Any]]:
        """Get all URLs from the database"""
        conn = self.get_connection()
        c = conn.cursor()
        try:
            c.execute('''
                SELECT 
                    original_url,
                    short_code,
                    created_at,
                    total_clicks 
                FROM urls 
                ORDER BY created_at DESC
            ''')
            
            # Convert tuples to dictionaries explicitly
            results = []
            for row in c.fetchall():
                results.append({
                    'original_url': row[0],
                    'short_code': row[1],
                    'created_at': row[2],
                    'total_clicks': row[3]
                })
            return results
        finally:
            conn.close()

    # === Analytics Methods ===

    def save_analytics(self, analytics_data: Dict[str, Any]) -> bool:
        """Save click analytics data"""
        conn = self.get_connection()
        c = conn.cursor()
        try:
            # Insert analytics data
            c.execute('''
                INSERT INTO analytics (
                    short_code, ip_address, user_agent, referrer,
                    utm_source, utm_medium, utm_campaign,
                    country, device_type, browser, os
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                analytics_data['short_code'],
                analytics_data['ip_address'],
                analytics_data['user_agent'],
                analytics_data['referrer'],
                analytics_data['utm_source'],
                analytics_data['utm_medium'],
                analytics_data['utm_campaign'],
                analytics_data['country'],
                analytics_data['device_type'],
                analytics_data['browser'],
                analytics_data['os']
            ))
            
            # Update total clicks
            c.execute('''
                UPDATE urls 
                SET total_clicks = total_clicks + 1 
                WHERE short_code = ?
            ''', (analytics_data['short_code'],))
            
            conn.commit()
            return True
        except Exception as e:
            logger.error(f"Error saving analytics: {str(e)}")
            return False
        finally:
            conn.close()

    def get_analytics_data(self, short_code: str) -> Dict[str, Any]:
        """Get analytics data for a URL"""
        conn = self.get_connection()
        c = conn.cursor()
        try:
            # Get basic URL info
            c.execute('''
                SELECT original_url, created_at, total_clicks 
                FROM urls 
                WHERE short_code = ?
            ''', (short_code,))
            
            result = c.fetchone()
            if not result:
                return None
            
            # Get unique clicks
            unique_clicks = self.get_unique_clicks_count(short_code)
            
            return {
                'original_url': result[0],
                'created_at': result[1],
                'total_clicks': result[2],
                'unique_clicks': unique_clicks,
                'short_code': short_code
            }
        finally:
            conn.close()

    def get_clicks(self, short_code: str) -> List[Dict[str, Any]]:
        """Get all clicks for a URL"""
        conn = self.get_connection()
        c = conn.cursor()
        try:
            c.execute('''
                SELECT 
                    clicked_at,
                    utm_source,
                    utm_medium,
                    utm_campaign,
                    referrer
                FROM analytics
                WHERE short_code = ?
                ORDER BY clicked_at DESC
            ''', (short_code,))
            
            return [{
                'clicked_at': row[0],
                'utm_source': row[1],
                'utm_medium': row[2],
                'utm_campaign': row[3],
                'referrer': row[4]
            } for row in c.fetchall()]
        finally:
            conn.close()

    def get_recent_clicks(self, short_code: str, limit: int = 10) -> List[Dict[str, Any]]:
        """Get recent clicks with detailed info"""
        conn = self.get_connection()
        c = conn.cursor()
        try:
            c.execute('''
                SELECT 
                    clicked_at,
                    country,
                    device_type,
                    browser,
                    os,
                    utm_source,
                    utm_medium,
                    utm_campaign,
                    referrer
                FROM analytics
                WHERE short_code = ?
                ORDER BY clicked_at DESC
                LIMIT ?
            ''', (short_code, limit))
            
            return [{
                'clicked_at': row[0],
                'country': row[1],
                'device_type': row[2],
                'browser': row[3],
                'os': row[4],
                'utm_source': row[5],
                'utm_medium': row[6],
                'utm_campaign': row[7],
                'referrer': row[8]
            } for row in c.fetchall()]
        finally:
            conn.close() 

    def get_geographic_data(self, short_code: str) -> Dict[str, Any]:
        """Get geographic analytics data"""
        conn = self.get_connection()
        c = conn.cursor()
        try:
            # Get country breakdown
            c.execute('''
                SELECT 
                    country,
                    COUNT(*) as clicks
                FROM analytics
                WHERE short_code = ?
                GROUP BY country
            ''', (short_code,))
            
            return dict(c.fetchall())
        finally:
            conn.close()

    def get_traffic_sources(self, short_code: str) -> Dict[str, Any]:
        """Get traffic source analysis"""
        conn = self.get_connection()
        c = conn.cursor()
        try:
            # Get UTM source breakdown
            c.execute('''
                SELECT 
                    utm_source,
                    utm_medium,
                    utm_campaign,
                    COUNT(*) as clicks,
                    COUNT(DISTINCT ip_address) as unique_visitors
                FROM analytics
                WHERE short_code = ?
                GROUP BY utm_source, utm_medium, utm_campaign
                ORDER BY clicks DESC
            ''', (short_code,))
            
            sources = [{
                'source': row[0],
                'medium': row[1],
                'campaign': row[2],
                'clicks': row[3],
                'unique_visitors': row[4]
            } for row in c.fetchall()]

            return {
                'sources': sources,
                'total_sources': len(sources)
            }
        finally:
            conn.close()

    def get_device_analysis(self, short_code: str) -> Dict[str, Any]:
        """Get device and browser analytics"""
        conn = self.get_connection()
        c = conn.cursor()
        try:
            # Get device breakdown
            c.execute('''
                SELECT device_type, COUNT(*) 
                FROM analytics 
                WHERE short_code = ? 
                GROUP BY device_type
            ''', (short_code,))
            devices = dict(c.fetchall())

            # Get browser breakdown
            c.execute('''
                SELECT browser, COUNT(*) 
                FROM analytics 
                WHERE short_code = ? 
                GROUP BY browser
            ''', (short_code,))
            browsers = dict(c.fetchall())

            # Get OS breakdown
            c.execute('''
                SELECT os, COUNT(*) 
                FROM analytics 
                WHERE short_code = ? 
                GROUP BY os
            ''', (short_code,))
            os_data = dict(c.fetchall())

            return {
                'devices': devices or {},
                'browsers': browsers or {},
                'operating_systems': os_data or {}
            }
        finally:
            conn.close()

    def generate_report(self, short_code: str) -> Dict[str, Any]:
        """Generate a comprehensive report for a URL"""
        try:
            # Get basic stats
            basic_stats = self.get_url_info(short_code)
            if not basic_stats:
                return None

            # Get analytics data
            analytics_data = self.get_analytics_data(short_code)
            
            # Get recent clicks
            recent_clicks = self.get_recent_clicks(short_code)

            # Get geographic data
            geographic_data = self.get_geographic_data(short_code)

            # Get traffic sources
            traffic_sources = self.get_traffic_sources(short_code)

            # Get device analysis
            device_data = self.get_device_analysis(short_code)

            return {
                'basic_stats': basic_stats,
                'analytics_data': analytics_data,
                'recent_clicks': recent_clicks,
                'geographic': geographic_data or {},
                'traffic_sources': traffic_sources or {'sources': [], 'total_sources': 0},
                'devices': device_data,
                'conversion_data': {
                    'total_clicks': basic_stats['total_clicks'],
                    'unique_visitors': analytics_data.get('unique_visitors', 0) if analytics_data else 0
                },
                'engagement': {
                    'success_rate': 100.0,
                    'total_clicks': basic_stats['total_clicks']
                }
            }
        except Exception as e:
            logger.error(f"Error generating report: {str(e)}")
            return {
                'basic_stats': {},
                'analytics_data': {},
                'recent_clicks': [],
                'geographic': {},
                'traffic_sources': {'sources': [], 'total_sources': 0},
                'devices': {'devices': {}, 'browsers': {}, 'operating_systems': {}},
                'conversion_data': {'total_clicks': 0, 'unique_visitors': 0},
                'engagement': {'success_rate': 0, 'total_clicks': 0}
            }

    def get_real_time_stats(self, short_code: str, minutes: int = 5) -> Dict[str, Any]:
        """Get real-time statistics for the last few minutes"""
        conn = self.get_connection()
        c = conn.cursor()
        try:
            # Get recent activity
            c.execute('''
                SELECT COUNT(*) as clicks,
                       COUNT(DISTINCT ip_address) as visitors
                FROM analytics
                WHERE short_code = ?
                AND clicked_at >= datetime('now', ?)
            ''', (short_code, f'-{minutes} minutes'))
            
            row = c.fetchone()
            clicks = row[0] if row else 0
            visitors = row[1] if row else 0

            return {
                'clicks': clicks,
                'active_visitors': visitors,
                'current_success_rate': 100.0,  # Default success rate
                'time_window': f'{minutes} minutes'
            }
        except Exception as e:
            logger.error(f"Error getting real-time stats: {str(e)}")
            return {'clicks': 0, 'active_visitors': 0, 'current_success_rate': 0, 'time_window': f'{minutes} minutes'}
        finally:
            conn.close() 

    def increment_clicks(self, short_code: str) -> bool:
        """Track click with basic analytics"""
        conn = self.get_connection()
        c = conn.cursor()
        try:
            now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            
            # Update click count
            c.execute('''
                UPDATE urls 
                SET total_clicks = total_clicks + 1 
                WHERE short_code = ?
            ''', (short_code,))
            
            # Add analytics entry
            c.execute('''
                INSERT INTO analytics (short_code, clicked_at) 
                VALUES (?, ?)
            ''', (short_code, now))
            
            conn.commit()
            return True
        except Exception as e:
            logger.error(f"Error tracking click: {str(e)}")
            return False
        finally:
            conn.close() 

    def get_recent_links(self, limit: int = 3) -> List[Dict[str, Any]]:
        """Get the most recent shortened URLs"""
        conn = self.get_connection()
        c = conn.cursor()
        try:
            c.execute('''
                SELECT original_url, short_code, created_at, total_clicks 
                FROM urls 
                ORDER BY created_at DESC 
                LIMIT ?
            ''', (limit,))
            
            results = []
            for row in c.fetchall():
                results.append({
                    'original_url': row[0],
                    'short_code': row[1],
                    'created_at': row[2],
                    'total_clicks': row[3]
                })
            return results
        finally:
            conn.close()

    def get_last_click_date(self, short_code: str) -> Optional[datetime]:
        """Get the date of the last click for a URL"""
        conn = self.get_connection()
        c = conn.cursor()
        try:
            c.execute('''
                SELECT clicked_at 
                FROM analytics 
                WHERE short_code = ? 
                ORDER BY clicked_at DESC 
                LIMIT 1
            ''', (short_code,))
            result = c.fetchone()
            if result:
                return datetime.strptime(result[0], '%Y-%m-%d %H:%M:%S')
            return None
        finally:
            conn.close()

    def get_unique_clicks_count(self, short_code: str) -> int:
        """Get count of unique clicks for a URL"""
        conn = self.get_connection()
        c = conn.cursor()
        try:
            c.execute('''
                SELECT COUNT(DISTINCT ip_address) as unique_clicks
                FROM analytics 
                WHERE short_code = ?
            ''', (short_code,))
            result = c.fetchone()
            return result[0] if result else 0
        finally:
            conn.close() 

    def track_click(self, short_code: str, ip_address: str = None, user_agent: str = None, referrer: str = None):
        """Track click analytics"""
        conn = self.get_connection()
        c = conn.cursor()
        try:
            now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            c.execute('''
                INSERT INTO analytics (
                    short_code,
                    clicked_at,
                    ip_address,
                    user_agent,
                    referrer
                ) VALUES (?, ?, ?, ?, ?)
            ''', (short_code, now, ip_address, user_agent, referrer))
            conn.commit()
            return True
        except Exception as e:
            logger.error(f"Error tracking click: {str(e)}")
            return False
        finally:
            conn.close() 

    def save_campaign_url(self, url: str, short_code: str, campaign_name: str = None, 
                         campaign_type: str = None, utm_params: dict = None, 
                         expiry_date: str = None, enable_tracking: bool = True) -> bool:
        """Save a campaign URL with all associated parameters"""
        conn = self.get_connection()
        c = conn.cursor()
        try:
            now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            
            # Check if short_code already exists
            c.execute('SELECT id FROM urls WHERE short_code = ?', (short_code,))
            if c.fetchone():
                logger.error(f"Short code already exists: {short_code}")
                return False
            
            # Insert URL with campaign details
            c.execute('''
                INSERT INTO urls (
                    original_url,
                    short_code,
                    campaign_name,
                    campaign_type,
                    created_at,
                    enable_tracking,
                    total_clicks,
                    utm_source,
                    utm_medium,
                    utm_campaign,
                    utm_content,
                    utm_term,
                    expiry_date
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                url,
                short_code,
                campaign_name,
                campaign_type,
                now,
                1 if enable_tracking else 0,
                0,  # Initial click count
                utm_params.get('utm_source') if utm_params else None,
                utm_params.get('utm_medium') if utm_params else None,
                utm_params.get('utm_campaign') if utm_params else None,
                utm_params.get('utm_content') if utm_params else None,
                utm_params.get('utm_term') if utm_params else None,
                expiry_date
            ))
            
            conn.commit()
            logger.info(f"Successfully saved campaign URL: {short_code} -> {url}")
            return True
        except Exception as e:
            logger.error(f"Error saving campaign URL: {str(e)}")
            return False
        finally:
            conn.close() 

    def update_campaign(self, short_code: str, update_data: dict) -> bool:
        """Update campaign details"""
        conn = self.get_connection()
        c = conn.cursor()
        try:
            # Build update query dynamically based on provided fields
            update_fields = []
            values = []
            for key, value in update_data.items():
                if key in ['campaign_name', 'campaign_type', 'utm_source', 'utm_medium', 
                          'utm_campaign', 'utm_content', 'utm_term', 'status', 'tags', 
                          'notes', 'expiry_date']:
                    update_fields.append(f"{key} = ?")
                    values.append(value)
            
            if not update_fields:
                return False
            
            # Add last_updated timestamp
            update_fields.append("last_updated = ?")
            values.append(datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
            
            # Add short_code to values
            values.append(short_code)
            
            # Execute update
            query = f'''
                UPDATE urls 
                SET {", ".join(update_fields)}
                WHERE short_code = ?
            '''
            c.execute(query, values)
            
            conn.commit()
            return True
        except Exception as e:
            logger.error(f"Error updating campaign: {str(e)}")
            return False
        finally:
            conn.close()

    def delete_campaign(self, short_code: str) -> bool:
        """Delete a campaign and its analytics"""
        conn = self.get_connection()
        c = conn.cursor()
        try:
            # Begin transaction
            c.execute("BEGIN TRANSACTION")
            
            # Delete analytics data
            c.execute("DELETE FROM analytics WHERE short_code = ?", (short_code,))
            
            # Delete URL record
            c.execute("DELETE FROM urls WHERE short_code = ?", (short_code,))
            
            conn.commit()
            return True
        except Exception as e:
            conn.rollback()
            logger.error(f"Error deleting campaign: {str(e)}")
            return False
        finally:
            conn.close()

    def get_campaign_details(self, short_code: str) -> Optional[Dict[str, Any]]:
        """Get detailed campaign information"""
        conn = self.get_connection()
        c = conn.cursor()
        try:
            c.execute('''
                SELECT 
                    original_url,
                    campaign_name,
                    campaign_type,
                    created_at,
                    total_clicks,
                    enable_tracking,
                    utm_source,
                    utm_medium,
                    utm_campaign,
                    utm_content,
                    utm_term,
                    expiry_date,
                    status,
                    tags,
                    notes,
                    last_updated
                FROM urls 
                WHERE short_code = ?
            ''', (short_code,))
            
            result = c.fetchone()
            if not result:
                return None
            
            return {
                'original_url': result[0],
                'campaign_name': result[1],
                'campaign_type': result[2],
                'created_at': result[3],
                'total_clicks': result[4],
                'enable_tracking': bool(result[5]),
                'utm_source': result[6],
                'utm_medium': result[7],
                'utm_campaign': result[8],
                'utm_content': result[9],
                'utm_term': result[10],
                'expiry_date': result[11],
                'status': result[12],
                'tags': result[13].split(',') if result[13] else [],
                'notes': result[14],
                'last_updated': result[15],
                'short_code': short_code
            }
        finally:
            conn.close()

    def get_campaign_stats(self, short_code: str) -> Dict[str, Any]:
        """Get comprehensive campaign statistics"""
        conn = self.get_connection()
        c = conn.cursor()
        try:
            stats = {
                'total_clicks': 0,
                'unique_visitors': 0,
                'devices': {},
                'browsers': {},
                'countries': {},
                'utm_sources': {},
                'conversions': 0,
                'last_click': None
            }
            
            # Get basic stats
            c.execute('''
                SELECT total_clicks, last_updated
                FROM urls 
                WHERE short_code = ?
            ''', (short_code,))
            basic = c.fetchone()
            if basic:
                stats['total_clicks'] = basic[0]
                stats['last_updated'] = basic[1]
            
            # Get detailed analytics
            c.execute('''
                SELECT 
                    COUNT(DISTINCT ip_address) as unique_visitors,
                    COUNT(CASE WHEN conversion_data IS NOT NULL THEN 1 END) as conversions,
                    MAX(clicked_at) as last_click
                FROM analytics 
                WHERE short_code = ?
            ''', (short_code,))
            
            analytics = c.fetchone()
            if analytics:
                stats['unique_visitors'] = analytics[0]
                stats['conversions'] = analytics[1]
                stats['last_click'] = analytics[2]
            
            return stats
        finally:
            conn.close()
