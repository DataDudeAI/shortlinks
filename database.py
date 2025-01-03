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
        """Initialize database if it doesn't exist"""
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
        
        c.execute('''
            CREATE TABLE IF NOT EXISTS analytics (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                short_code TEXT NOT NULL,
                clicked_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                utm_source TEXT DEFAULT 'direct',
                utm_medium TEXT DEFAULT 'none',
                utm_campaign TEXT DEFAULT 'no campaign',
                referrer TEXT,
                FOREIGN KEY (short_code) REFERENCES urls (short_code)
            )
        ''')
        
        # Create indexes if they don't exist
        c.execute('''CREATE INDEX IF NOT EXISTS idx_short_code ON urls (short_code)''')
        c.execute('''CREATE INDEX IF NOT EXISTS idx_analytics_short_code ON analytics (short_code)''')
        
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
        conn = self.get_connection()
        c = conn.cursor()
        try:
            # Get URL info first
            c.execute('''
                SELECT original_url, created_at, total_clicks, short_code
                FROM urls 
                WHERE short_code = ?
            ''', (short_code,))
            url_result = c.fetchone()
            
            if not url_result:
                return None

            # Get click analytics
            c.execute('''
                SELECT 
                    COUNT(*) as total_clicks,
                    MAX(clicked_at) as last_clicked,
                    COUNT(DISTINCT utm_source) as unique_sources,
                    COUNT(DISTINCT utm_medium) as unique_mediums,
                    COUNT(DISTINCT utm_campaign) as unique_campaigns
                FROM analytics
                WHERE short_code = ?
            ''', (short_code,))
            
            analytics = c.fetchone()
            
            # Get UTM source breakdown
            c.execute('''
                SELECT utm_source, COUNT(*) as count
                FROM analytics
                WHERE short_code = ? AND utm_source IS NOT NULL
                GROUP BY utm_source
            ''', (short_code,))
            
            utm_sources = dict(c.fetchall() or [])
            
            # Get UTM medium breakdown
            c.execute('''
                SELECT utm_medium, COUNT(*) as count
                FROM analytics
                WHERE short_code = ? AND utm_medium IS NOT NULL
                GROUP BY utm_medium
            ''', (short_code,))
            
            utm_mediums = dict(c.fetchall() or [])
            
            # Get campaign breakdown
            c.execute('''
                SELECT utm_campaign, COUNT(*) as count
                FROM analytics
                WHERE short_code = ? AND utm_campaign IS NOT NULL
                GROUP BY utm_campaign
            ''', (short_code,))
            
            campaigns = dict(c.fetchall() or [])
            
            # Get clicks over time
            c.execute('''
                SELECT 
                    date(clicked_at) as click_date,
                    COUNT(*) as clicks
                FROM analytics
                WHERE short_code = ?
                GROUP BY date(clicked_at)
                ORDER BY click_date
            ''', (short_code,))
            
            clicks_over_time = dict(c.fetchall() or [])
            
            return {
                'original_url': url_result[0],
                'created_at': url_result[1],
                'total_clicks': url_result[2],
                'short_code': url_result[3],
                'last_clicked': analytics[1],
                'unique_sources': analytics[2],
                'unique_mediums': analytics[3],
                'unique_campaigns': analytics[4],
                'utm_sources': utm_sources,
                'utm_mediums': utm_mediums,
                'campaigns': campaigns,
                'clicks_over_time': clicks_over_time
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
