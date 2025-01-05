import sqlite3
from datetime import datetime
from typing import Optional, Dict, Any, List
import os
import logging

logger = logging.getLogger(__name__)

class Database:
    """Database handler for URL shortener with analytics"""
    
    def __init__(self, db_path: str = 'urls.db'):
        # Ensure we're using an absolute path for Streamlit Cloud
        self.db_path = os.path.abspath(db_path)
        self.init_db()

    def get_connection(self):
        """Get database connection"""
        return sqlite3.connect(self.db_path)

    # === Database Initialization ===
    
    def init_db(self):
        """Initialize database with success tracking"""
        conn = self.get_connection()
        c = conn.cursor()
        try:
            # Create tables if they don't exist
            c.execute('''
                CREATE TABLE IF NOT EXISTS urls (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    original_url TEXT NOT NULL,
                    short_code TEXT NOT NULL UNIQUE,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    total_clicks INTEGER DEFAULT 0
                )
            ''')
            
            # Drop existing analytics table to update schema
            c.execute('DROP TABLE IF EXISTS analytics')
            
            # Create new analytics table with all fields
            c.execute('''
                CREATE TABLE IF NOT EXISTS analytics (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    short_code TEXT NOT NULL,
                    clicked_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    utm_source TEXT DEFAULT 'direct',
                    utm_medium TEXT DEFAULT 'none',
                    utm_campaign TEXT DEFAULT 'no campaign',
                    referrer TEXT,
                    user_agent TEXT,
                    ip_address TEXT,
                    country TEXT,
                    device_type TEXT,
                    browser TEXT,
                    os TEXT,
                    successful BOOLEAN DEFAULT TRUE,
                    FOREIGN KEY (short_code) REFERENCES urls (short_code)
                )
            ''')
            
            # Create indexes after table creation
            c.execute('''CREATE INDEX IF NOT EXISTS idx_short_code ON urls (short_code)''')
            c.execute('''CREATE INDEX IF NOT EXISTS idx_analytics_short_code ON analytics (short_code)''')
            c.execute('''CREATE INDEX IF NOT EXISTS idx_clicked_at ON analytics (clicked_at)''')
            c.execute('''CREATE INDEX IF NOT EXISTS idx_country ON analytics (country)''')
            c.execute('''CREATE INDEX IF NOT EXISTS idx_device_type ON analytics (device_type)''')
            c.execute('''CREATE INDEX IF NOT EXISTS idx_successful ON analytics (successful)''')
            
            conn.commit()
        except Exception as e:
            logger.error(f"Error initializing database: {str(e)}")
            conn.rollback()
        finally:
            conn.close()

    # === URL Management Methods ===

    def save_url(self, data: Dict[str, Any]) -> Optional[str]:
        """Save a new URL"""
        conn = self.get_connection()
        c = conn.cursor()
        try:
            # Validate required data
            if not data.get('url') or not data.get('short_code'):
                logger.error("Missing required URL data")
                return None

            # Insert the URL
            c.execute('''
                INSERT INTO urls (original_url, short_code, total_clicks)
                VALUES (?, ?, 0)
            ''', (data['url'], data['short_code']))
            
            conn.commit()
            logger.info(f"Successfully created short URL: {data['short_code']}")
            return data['short_code']
        except sqlite3.IntegrityError as e:
            logger.error(f"URL creation failed - duplicate short code: {str(e)}")
            return None
        except Exception as e:
            logger.error(f"URL creation failed: {str(e)}")
            return None
        finally:
            conn.close()

    def get_url_info(self, short_code: str) -> Optional[Dict[str, Any]]:
        """Get URL information for a given short code"""
        conn = self.get_connection()
        c = conn.cursor()
        try:
            c.execute('''
                SELECT original_url, created_at, total_clicks 
                FROM urls 
                WHERE short_code = ?
            ''', (short_code,))
            
            result = c.fetchone()
            if not result:
                return None
                
            return {
                'original_url': result[0],
                'created_at': result[1],
                'total_clicks': result[2],
                'short_code': short_code
            }
        finally:
            conn.close()

    def get_all_urls(self) -> List[Dict[str, Any]]:
        """Get all URLs with their basic info"""
        conn = self.get_connection()
        c = conn.cursor()
        try:
            c.execute('''
                SELECT short_code, original_url, created_at, total_clicks
                FROM urls
                ORDER BY created_at DESC
            ''')
            
            return [{
                'short_code': row[0],
                'original_url': row[1],
                'created_at': row[2],
                'total_clicks': row[3]
            } for row in c.fetchall()]
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
        """Get comprehensive analytics data"""
        conn = self.get_connection()
        c = conn.cursor()
        try:
            # Get basic URL info
            url_info = self.get_url_info(short_code)
            if not url_info:
                return None

            # Get unique visitors
            c.execute('''
                SELECT COUNT(DISTINCT ip_address) 
                FROM analytics 
                WHERE short_code = ?
            ''', (short_code,))
            unique_visitors = c.fetchone()[0]

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

            # Get country breakdown
            c.execute('''
                SELECT country, COUNT(*) 
                FROM analytics 
                WHERE short_code = ? 
                GROUP BY country
            ''', (short_code,))
            countries = dict(c.fetchall())

            return {
                **url_info,
                'unique_visitors': unique_visitors,
                'devices': devices,
                'browsers': browsers,
                'countries': countries
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
        """Increment the click count for a URL"""
        conn = self.get_connection()
        c = conn.cursor()
        try:
            c.execute('''
                UPDATE urls 
                SET total_clicks = total_clicks + 1 
                WHERE short_code = ?
            ''', (short_code,))
            conn.commit()
            return True
        except Exception as e:
            logger.error(f"Error incrementing clicks: {str(e)}")
            return False
        finally:
            conn.close() 
