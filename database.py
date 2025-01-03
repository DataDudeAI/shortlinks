import sqlite3
from datetime import datetime
from typing import Optional, Dict, Any
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
                utm_source TEXT,
                utm_medium TEXT,
                utm_campaign TEXT,
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
                    short_code, utm_source, utm_medium, utm_campaign
                ) VALUES (?, ?, ?, ?)
            ''', (
                analytics_data['short_code'],
                analytics_data.get('utm_source'),
                analytics_data.get('utm_medium'),
                analytics_data.get('utm_campaign')
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
            # Get URL info
            url_info = self.get_url_info(short_code)
            if not url_info:
                return None

            # Get click analytics
            c.execute('''
                SELECT 
                    COUNT(*) as total_clicks,
                    MAX(clicked_at) as last_clicked,
                    COUNT(DISTINCT utm_source) as unique_sources,
                    COUNT(DISTINCT utm_medium) as unique_mediums
                FROM analytics
                WHERE short_code = ?
            ''', (short_code,))
            
            analytics = c.fetchone()
            
            # Get UTM breakdowns
            c.execute('''
                SELECT utm_source, COUNT(*) as count
                FROM analytics
                WHERE short_code = ? AND utm_source IS NOT NULL
                GROUP BY utm_source
            ''', (short_code,))
            
            utm_sources = dict(c.fetchall() or [])
            
            c.execute('''
                SELECT utm_medium, COUNT(*) as count
                FROM analytics
                WHERE short_code = ? AND utm_medium IS NOT NULL
                GROUP BY utm_medium
            ''', (short_code,))
            
            utm_mediums = dict(c.fetchall() or [])
            
            return {
                **url_info,
                'total_clicks': analytics[0],
                'last_clicked': analytics[1],
                'unique_sources': analytics[2],
                'unique_mediums': analytics[3],
                'utm_sources': utm_sources,
                'utm_mediums': utm_mediums
            }
        finally:
            conn.close() 
