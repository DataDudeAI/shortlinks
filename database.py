import sqlite3
from datetime import datetime
from typing import Optional, Dict, Any, List
import os

class Database:
    def __init__(self, db_path: str = 'urls.db'):
        # Ensure we're using an absolute path for Streamlit Cloud
        self.db_path = os.path.abspath(db_path)
        self.init_db()
        
    def init_db(self):
        """Initialize database with success tracking"""
        conn = sqlite3.connect(self.db_path)
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
        
        # Drop existing analytics table if it exists
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
        
        # Create indexes for better performance
        c.execute('''CREATE INDEX IF NOT EXISTS idx_short_code ON urls (short_code)''')
        c.execute('''CREATE INDEX IF NOT EXISTS idx_analytics_short_code ON analytics (short_code)''')
        c.execute('''CREATE INDEX IF NOT EXISTS idx_clicked_at ON analytics (clicked_at)''')
        c.execute('''CREATE INDEX IF NOT EXISTS idx_country ON analytics (country)''')
        c.execute('''CREATE INDEX IF NOT EXISTS idx_device_type ON analytics (device_type)''')
        
        # Add index for successful field
        c.execute('''CREATE INDEX IF NOT EXISTS idx_successful ON analytics (successful)''')
        
        conn.commit()
        conn.close()

    def get_connection(self):
        return sqlite3.connect(self.db_path)

    def save_url(self, data: Dict[str, Any]) -> str:
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
            # If short_code already exists, generate a new one
            return None
        finally:
            conn.close()

    def get_url_info(self, short_code: str) -> Optional[Dict[str, Any]]:
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
                'total_clicks': result[2]
            }
        finally:
            conn.close()

    def save_analytics(self, analytics_data: Dict[str, Any]):
        conn = self.get_connection()
        c = conn.cursor()
        try:
            # Insert analytics data
            c.execute('''
                INSERT INTO analytics (
                    short_code, clicked_at, utm_source, utm_medium, utm_campaign, referrer
                ) VALUES (?, ?, ?, ?, ?, ?)
            ''', (
                analytics_data['short_code'],
                analytics_data.get('clicked_at', datetime.now().strftime('%Y-%m-%d %H:%M:%S')),
                analytics_data.get('utm_source', 'direct'),
                analytics_data.get('utm_medium', 'none'),
                analytics_data.get('utm_campaign', 'no campaign'),
                analytics_data.get('referrer', '')
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

    def get_all_urls(self) -> list:
        conn = self.get_connection()
        c = conn.cursor()
        try:
            c.execute('''
                SELECT short_code, original_url, created_at, total_clicks
                FROM urls
                ORDER BY created_at DESC
            ''')
            
            urls = []
            for row in c.fetchall():
                urls.append({
                    'short_code': row[0],
                    'original_url': row[1],
                    'created_at': row[2],
                    'total_clicks': row[3]
                })
            return urls
        finally:
            conn.close()

    def get_analytics_data(self, short_code: str) -> Dict[str, Any]:
        """Get enhanced analytics data for a specific short code"""
        conn = self.get_connection()
        c = conn.cursor()
        try:
            # Get basic URL info
            c.execute('''
                SELECT original_url, created_at, total_clicks
                FROM urls 
                WHERE short_code = ?
            ''', (short_code,))
            url_info = c.fetchone()
            
            if not url_info:
                return None

            # Get unique visitors count
            c.execute('''
                SELECT COUNT(DISTINCT ip_address) 
                FROM analytics 
                WHERE short_code = ?
            ''', (short_code,))
            unique_visitors = c.fetchone()[0]

            # Get successful redirections count
            c.execute('''
                SELECT COUNT(*) 
                FROM analytics 
                WHERE short_code = ? AND successful = TRUE
            ''', (short_code,))
            successful_redirects = c.fetchone()[0]

            # Get bounce rate (single page visits)
            c.execute('''
                SELECT COUNT(DISTINCT ip_address) 
                FROM analytics 
                WHERE short_code = ? 
                GROUP BY ip_address 
                HAVING COUNT(*) = 1
            ''', (short_code,))
            bounces = len(c.fetchall())

            # Get recent clicks with all details
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
                    successful
                FROM analytics
                WHERE short_code = ?
                ORDER BY clicked_at DESC
                LIMIT 10
            ''', (short_code,))
            
            recent_clicks = []
            for row in c.fetchall():
                recent_clicks.append({
                    'clicked_at': row[0],
                    'country': row[1],
                    'device_type': row[2],
                    'browser': row[3],
                    'os': row[4],
                    'utm_source': row[5],
                    'utm_medium': row[6],
                    'utm_campaign': row[7],
                    'successful': row[8]
                })

            return {
                'original_url': url_info[0],
                'created_at': url_info[1],
                'total_clicks': url_info[2],
                'unique_visitors': unique_visitors,
                'successful_redirects': successful_redirects,
                'bounces': bounces,
                'recent_clicks': recent_clicks,
                'short_code': short_code
            }
        finally:
            conn.close()

    def get_clicks(self, short_code: str) -> List[Dict[str, Any]]:
        """Get all clicks for a specific short code"""
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
            
            clicks = []
            for row in c.fetchall():
                clicks.append({
                    'clicked_at': row[0],
                    'utm_source': row[1],
                    'utm_medium': row[2],
                    'utm_campaign': row[3],
                    'referrer': row[4]
                })
            
            return clicks
            
        finally:
            conn.close() 

    def get_recent_clicks(self, short_code: str, limit: int = 10) -> List[Dict[str, Any]]:
        """Get recent clicks for a specific short code"""
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
            
            clicks = []
            for row in c.fetchall():
                clicks.append({
                    'clicked_at': row[0],
                    'country': row[1],
                    'device_type': row[2],
                    'browser': row[3],
                    'os': row[4],
                    'utm_source': row[5],
                    'utm_medium': row[6],
                    'utm_campaign': row[7],
                    'referrer': row[8]
                })
            
            return clicks
        finally:
            conn.close() 
