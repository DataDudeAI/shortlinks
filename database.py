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
        
        # Create indexes for better performance
        c.execute('''CREATE INDEX IF NOT EXISTS idx_short_code ON urls (short_code)''')
        c.execute('''CREATE INDEX IF NOT EXISTS idx_analytics_short_code ON analytics (short_code)''')
        c.execute('''CREATE INDEX IF NOT EXISTS idx_clicked_at ON analytics (clicked_at)''')
        c.execute('''CREATE INDEX IF NOT EXISTS idx_country ON analytics (country)''')
        c.execute('''CREATE INDEX IF NOT EXISTS idx_device_type ON analytics (device_type)''')
        c.execute('''CREATE INDEX IF NOT EXISTS idx_successful ON analytics (successful)''')
        
        conn.commit()
        conn.close()

    # === URL Management Methods ===

    def save_url(self, data: Dict[str, Any]) -> str:
        """Save a new URL"""
        conn = self.get_connection()
        c = conn.cursor()
        try:
            c.execute('''
                INSERT INTO urls (original_url, short_code, total_clicks)
                VALUES (?, ?, 0)
            ''', (data['original_url'], data['short_code']))
            conn.commit()
            return data['short_code']
        except sqlite3.IntegrityError:
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

    def save_analytics(self, analytics_data: Dict[str, Any]):
        """Save click analytics data"""
        conn = self.get_connection()
        c = conn.cursor()
        try:
            # Insert analytics data
            c.execute('''
                INSERT INTO analytics (
                    short_code, clicked_at, utm_source, utm_medium, 
                    utm_campaign, referrer, user_agent, ip_address,
                    country, device_type, browser, os
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                analytics_data['short_code'],
                analytics_data.get('clicked_at', datetime.now().strftime('%Y-%m-%d %H:%M:%S')),
                analytics_data.get('utm_source', 'direct'),
                analytics_data.get('utm_medium', 'none'),
                analytics_data.get('utm_campaign', 'no campaign'),
                analytics_data.get('referrer', ''),
                analytics_data.get('user_agent', ''),
                analytics_data.get('ip_address', ''),
                analytics_data.get('country', ''),
                analytics_data.get('device_type', ''),
                analytics_data.get('browser', ''),
                analytics_data.get('os', '')
            ))
            
            # Update total clicks
            c.execute('''
                UPDATE urls 
                SET total_clicks = total_clicks + 1 
                WHERE short_code = ?
            ''', (analytics_data['short_code'],))
            
            conn.commit()
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
