import sqlite3
from datetime import datetime, timedelta
from typing import Optional, Dict, Any, List
import os
import logging
import pandas as pd
import json
import random
import string
from urllib.parse import urlparse, parse_qs, urlencode
import streamlit as st

# Setup logging
logger = logging.getLogger(__name__)

class Database:
    """Database handler for URL shortener with analytics"""
    
    def __init__(self):
        """Initialize database connection and create tables if they don't exist"""
        self.db_path = "urls.db"
        
        try:
            # Always initialize fresh database when reset flag exists
            if os.path.exists(".db_reset"):
                if os.path.exists(self.db_path):
                    os.remove(self.db_path)
                logger.info("Creating fresh database after reset...")
                self.initialize_database()
                os.remove(".db_reset")  # Remove reset flag
                return

            # Normal initialization
            if not os.path.exists(self.db_path):
                logger.info("Creating new database...")
                self.initialize_database()
            
        except Exception as e:
            logger.error(f"Database initialization error: {str(e)}")
            raise

    def get_connection(self):
        """Get database connection"""
        return sqlite3.connect(self.db_path)

    def initialize_database(self):
        """Create necessary database tables"""
        conn = self.get_connection()
        c = conn.cursor()
        try:
            # Drop existing tables if they exist
            c.execute("DROP TABLE IF EXISTS analytics")
            c.execute("DROP TABLE IF EXISTS urls")
            
            # Create URLs table without UNIQUE constraint on campaign_name
            c.execute('''
                CREATE TABLE IF NOT EXISTS urls (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    short_code TEXT UNIQUE NOT NULL,
                    original_url TEXT NOT NULL,
                    campaign_name TEXT NOT NULL,
                    campaign_type TEXT,
                    utm_source TEXT,
                    utm_medium TEXT,
                    utm_campaign TEXT,
                    utm_content TEXT,
                    utm_term TEXT,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    last_clicked DATETIME,
                    total_clicks INTEGER DEFAULT 0,
                    is_active BOOLEAN DEFAULT 1
                )
            ''')
            
            # Create analytics table with proper date handling
            c.execute('''
                CREATE TABLE IF NOT EXISTS analytics (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    short_code TEXT NOT NULL,
                    clicked_at DATE NOT NULL,
                    ip_address TEXT,
                    user_agent TEXT,
                    referrer TEXT,
                    state TEXT,
                    device_type TEXT,
                    browser TEXT,
                    os TEXT,
                    FOREIGN KEY (short_code) REFERENCES urls(short_code)
                )
            ''')

            # After creating tables
            c.execute('''
                CREATE INDEX IF NOT EXISTS idx_analytics_date 
                ON analytics(clicked_at)
            ''')

            conn.commit()
            logger.info("Database tables initialized successfully")
            
        except Exception as e:
            logger.error(f"Error initializing database: {str(e)}")
            conn.rollback()
            raise
        finally:
            conn.close()

    def get_analytics_summary(self, start_date=None, end_date=None, campaign_types=None, 
                             device_types=None, states=None, sources=None) -> Dict[str, Any]:
        """Get analytics summary with filters"""
        conn = self.get_connection()
        c = conn.cursor()
        
        try:
            # Set default date range to last 7 days if not provided
            if not start_date:
                start_date = datetime.now() - timedelta(days=7)
            if not end_date:
                end_date = datetime.now()

            # Base date parameters
            date_params = [start_date.strftime('%Y-%m-%d'), end_date.strftime('%Y-%m-%d')]
            
            # Build base WHERE clause
            where_conditions = ["date(a.clicked_at) BETWEEN ? AND ?"]
            query_params = list(date_params)  # Create a copy of date_params

            # Add optional filters
            if campaign_types:
                where_conditions.append(f"u.campaign_type IN ({','.join(['?' for _ in campaign_types])})")
                query_params.extend(campaign_types)
            
            if device_types:
                where_conditions.append(f"a.device_type IN ({','.join(['?' for _ in device_types])})")
                query_params.extend(device_types)
            
            if states:
                where_conditions.append(f"a.state IN ({','.join(['?' for _ in states])})")
                query_params.extend(states)
            
            if sources:
                where_conditions.append(f"a.referrer IN ({','.join(['?' for _ in sources])})")
                query_params.extend(sources)

            where_clause = " AND ".join(where_conditions)

            stats = {
                'total_clicks': 0,
                'unique_visitors': 0,
                'active_days': 0,
                'engagement_rate': 0,
                'total_campaigns': 0,
                'active_campaigns': 0,
                'daily_stats': {},
                'state_stats': {},
                'device_stats': {},
                'top_campaigns': [],
                'recent_activities': []
            }

            # Basic metrics query
            basic_query = f"""
                SELECT 
                    COUNT(DISTINCT a.id) as total_clicks,
                    COUNT(DISTINCT a.ip_address) as unique_visitors,
                    COUNT(DISTINCT date(a.clicked_at)) as active_days,
                    (SELECT COUNT(*) FROM urls) as total_campaigns
                FROM analytics a
                JOIN urls u ON a.short_code = u.short_code
                WHERE {where_clause}
            """
            c.execute(basic_query, query_params)
            row = c.fetchone()
            if row:
                stats['total_clicks'] = row[0] or 0
                stats['unique_visitors'] = row[1] or 0
                stats['active_days'] = row[2] or 0
                stats['total_campaigns'] = row[3] or 0
                stats['engagement_rate'] = (row[1] / row[0] * 100) if row[0] and row[1] else 0

            # Daily stats with date range
            daily_query = f"""
                WITH RECURSIVE dates(date) AS (
                    SELECT date(?) as date
                    UNION ALL
                    SELECT date(date, '+1 day')
                    FROM dates
                    WHERE date < date(?)
                )
                SELECT 
                    dates.date,
                    COALESCE(COUNT(DISTINCT a.id), 0) as clicks
                FROM dates
                LEFT JOIN analytics a ON date(a.clicked_at) = dates.date
                LEFT JOIN urls u ON a.short_code = u.short_code
                AND {where_clause}
                GROUP BY dates.date
                ORDER BY dates.date
            """
            c.execute(daily_query, date_params + query_params)
            stats['daily_stats'] = dict(c.fetchall())

            # Get recent activities
            query = f"""
                SELECT 
                    u.campaign_name,
                    date(a.clicked_at) as clicked_at,
                    a.state,
                    a.device_type,
                    u.campaign_type,
                    COUNT(*) as daily_clicks
                FROM analytics a
                JOIN urls u ON a.short_code = u.short_code
                WHERE {where_clause}
                GROUP BY date(a.clicked_at), u.campaign_name
                ORDER BY clicked_at DESC
                LIMIT 10
            """
            c.execute(query, query_params)
            stats['recent_activities'] = [
                {
                    'campaign_name': row[0],
                    'clicked_at': row[1],
                    'state': row[2] or "Unknown",
                    'device_type': row[3] or "Unknown",
                    'campaign_type': row[4] or "Other",
                    'daily_clicks': row[5]
                }
                for row in c.fetchall()
            ]

            # Get state distribution
            query = f"""
                SELECT a.state, COUNT(*) as visits
                FROM analytics a
                JOIN urls u ON a.short_code = u.short_code
                WHERE a.state IS NOT NULL AND {where_clause}
                GROUP BY a.state
                ORDER BY visits DESC
            """
            c.execute(query, query_params)
            stats['state_stats'] = dict(c.fetchall())

            # Get device distribution
            query = f"""
                SELECT a.device_type, COUNT(*) as count
                FROM analytics a
                JOIN urls u ON a.short_code = u.short_code
                WHERE a.device_type IS NOT NULL AND {where_clause}
                GROUP BY a.device_type
            """
            c.execute(query, query_params)
            stats['device_stats'] = dict(c.fetchall())

            # Get top campaigns
            query = f"""
                SELECT 
                    u.campaign_name,
                    COUNT(*) as clicks,
                    COUNT(DISTINCT a.ip_address) as unique_visitors,
                    u.campaign_type,
                    MAX(date(a.clicked_at)) as last_click
                FROM urls u
                JOIN analytics a ON u.short_code = a.short_code
                WHERE {where_clause}
                GROUP BY u.id
                ORDER BY clicks DESC
                LIMIT 5
            """
            c.execute(query, query_params)
            stats['top_campaigns'] = [
                {
                    'campaign_name': row[0],
                    'clicks': row[1],
                    'unique_visitors': row[2],
                    'campaign_type': row[3],
                    'last_click': row[4]
                }
                for row in c.fetchall()
            ]

            return stats

        except Exception as e:
            logger.error(f"Error getting analytics summary: {str(e)}")
            return {
                'total_clicks': 0,
                'unique_visitors': 0,
                'active_days': 0,
                'engagement_rate': 0,
                'total_campaigns': 0,
                'active_campaigns': 0,
                'daily_stats': {},
                'state_stats': {},
                'device_stats': {},
                'top_campaigns': [],
                'recent_activities': []
            }
        finally:
            conn.close()

    def get_recent_activity(self, limit: int = 5) -> List[Dict[str, Any]]:
        """Get recent activity"""
        conn = self.get_connection()
        c = conn.cursor()
        try:
            c.execute('''
                WITH RankedClicks AS (
                    SELECT 
                        u.campaign_name,
                        u.short_code,
                        a.clicked_at,
                        a.state,
                        a.device_type,
                        ROW_NUMBER() OVER (PARTITION BY u.short_code ORDER BY a.clicked_at DESC) as rn
                    FROM analytics a
                    JOIN urls u ON a.short_code = u.short_code
                    WHERE a.clicked_at IS NOT NULL
                )
                SELECT 
                    campaign_name,
                    short_code,
                    datetime(clicked_at) as clicked_at,
                    state,
                    device_type
                FROM RankedClicks
                WHERE rn = 1
                ORDER BY clicked_at DESC
                LIMIT ?
            ''', (limit,))
            
            activities = []
            for row in c.fetchall():
                activities.append({
                    "campaign_name": row[0],
                    "short_code": row[1],
                    "clicked_at": row[2],
                    "state": row[3] or "Unknown",
                    "device_type": row[4] or "Unknown"
                })
            return activities
        finally:
            conn.close()

    def get_all_urls(self) -> List[Dict[str, Any]]:
        """Get all URLs with their details"""
        conn = self.get_connection()
        c = conn.cursor()
        try:
            c.execute('''
                SELECT 
                    short_code,
                    original_url,
                    campaign_name,
                    campaign_type,
                    datetime(created_at) as created_at,
                    datetime(last_clicked) as last_clicked,
                    total_clicks,
                    utm_source,
                    utm_medium,
                    utm_campaign,
                    utm_content,
                    is_active
                FROM urls
                ORDER BY created_at DESC
            ''')
            
            urls = []
            for row in c.fetchall():
                urls.append({
                    'short_code': row[0],
                    'original_url': row[1],
                    'campaign_name': row[2],
                    'campaign_type': row[3],
                    'created_at': row[4],
                    'last_clicked': row[5] if row[5] else None,
                    'total_clicks': row[6],
                    'utm_source': row[7],
                    'utm_medium': row[8],
                    'utm_campaign': row[9],
                    'utm_content': row[10],
                    'is_active': bool(row[11])
                })
            return urls
        except Exception as e:
            logger.error(f"Error getting all URLs: {str(e)}")
            return []
        finally:
            conn.close()

    def get_url_info(self, short_code: str) -> Optional[Dict[str, Any]]:
        """Get URL information for redirection"""
        conn = self.get_connection()
        c = conn.cursor()
        try:
            c.execute("""
                SELECT 
                    original_url,
                    campaign_name,
                    campaign_type,
                    utm_source,
                    utm_medium,
                    utm_campaign,
                    utm_content,
                    utm_term
                FROM urls 
                WHERE short_code = ? AND is_active = 1
            """, (short_code,))
            
            row = c.fetchone()
            if row:
                return {
                    'original_url': row[0],
                    'campaign_name': row[1],
                    'campaign_type': row[2],
                    'utm_params': {
                        'source': row[3],
                        'medium': row[4],
                        'campaign': row[5],
                        'content': row[6],
                        'term': row[7]
                    }
                }
            return None
            
        except Exception as e:
            logger.error(f"Error getting URL info: {str(e)}")
            return None
        finally:
            conn.close()

    def build_redirect_url(self, url_info: Dict[str, Any]) -> str:
        """Build redirect URL with UTM parameters"""
        try:
            # Parse original URL
            parsed_url = urlparse(url_info['original_url'])
            
            # Get existing query parameters
            query_params = parse_qs(parsed_url.query)
            
            # Add/update UTM parameters if they exist
            utm_params = url_info.get('utm_params', {})
            for key, value in utm_params.items():
                if value:
                    query_params[f'utm_{key}'] = [value]
            
            # Build new query string
            new_query = urlencode(query_params, doseq=True)
            
            # Reconstruct URL
            redirect_url = parsed_url._replace(query=new_query).geturl()
            
            return redirect_url
            
        except Exception as e:
            logger.error(f"Error building redirect URL: {str(e)}")
            return url_info['original_url']

    def handle_redirect(self, short_code: str, **kwargs) -> Optional[str]:
        """Handle URL redirection and record analytics"""
        try:
            # Get URL information
            url_info = self.get_url_info(short_code)
            if not url_info:
                logger.error(f"No URL found for short code: {short_code}")
                return None
            
            # Record the click first
            click_recorded = self.record_click(
                short_code=short_code,
                ip_address=kwargs.get('ip_address', '127.0.0.1'),
                user_agent=kwargs.get('user_agent', 'Unknown'),
                referrer=kwargs.get('referrer', 'Direct'),
                state=kwargs.get('state', 'Unknown'),
                device_type=kwargs.get('device_type', 'Unknown'),
                browser=kwargs.get('browser', 'Unknown'),
                os=kwargs.get('os', 'Unknown')
            )
            
            if click_recorded:
                logger.info(f"Click recorded successfully for {short_code}")
            else:
                logger.warning(f"Failed to record click for {short_code}")
            
            # Build and return redirect URL
            redirect_url = self.build_redirect_url(url_info)
            logger.info(f"Redirecting to: {redirect_url}")
            return redirect_url
            
        except Exception as e:
            logger.error(f"Error handling redirect: {str(e)}")
            return None

    def get_campaign_performance(self) -> pd.DataFrame:
        """Get detailed campaign performance metrics"""
        conn = self.get_connection()
        try:
            query = '''
                WITH ClickStats AS (
                    SELECT 
                        u.short_code,
                        u.campaign_name,
                        u.campaign_type,
                        u.total_clicks,
                        COUNT(DISTINCT a.ip_address) as unique_visitors,
                        COUNT(DISTINCT a.state) as states_reached,
                        COUNT(DISTINCT date(a.clicked_at)) as active_days,
                        u.created_at,
                        MAX(a.clicked_at) as last_activity
                    FROM urls u
                    LEFT JOIN analytics a ON u.short_code = a.short_code
                    GROUP BY u.short_code
                )
                SELECT 
                    campaign_name,
                    campaign_type,
                    total_clicks,
                    unique_visitors,
                    states_reached,
                    active_days,
                    created_at,
                    last_activity,
                    ROUND(CAST(unique_visitors AS FLOAT) / 
                          CASE WHEN total_clicks = 0 THEN 1 
                               ELSE total_clicks END * 100, 2) as engagement_rate
                FROM ClickStats
                ORDER BY total_clicks DESC
            '''
            
            df = pd.read_sql_query(query, conn)
            return df
        except Exception as e:
            logger.error(f"Error getting campaign performance: {str(e)}")
            return pd.DataFrame()
        finally:
            conn.close()

    def generate_short_code(self, length=6) -> str:
        """Generate a unique short code"""
        characters = string.ascii_letters + string.digits
        while True:
            code = ''.join(random.choice(characters) for _ in range(length))
            # Check if code exists
            c = self.get_connection()
            cursor = c.cursor()
            try:
                cursor.execute("SELECT COUNT(*) FROM urls WHERE short_code = ?", (code,))
                if cursor.fetchone()[0] == 0:
                    return code
            finally:
                c.close()

    def create_short_url(self, url: str, campaign_name: str, campaign_type: str = None, utm_params: dict = None) -> Optional[str]:
        """Create a new short URL"""
        conn = self.get_connection()
        c = conn.cursor()
        try:
            # Generate unique short code
            short_code = ''.join(random.choices(string.ascii_letters + string.digits, k=6))
            
            # Check if short_code exists
            while True:
                c.execute("SELECT 1 FROM urls WHERE short_code = ?", (short_code,))
                if not c.fetchone():
                    break
                short_code = ''.join(random.choices(string.ascii_letters + string.digits, k=6))

            # Insert new URL
            c.execute("""
                INSERT INTO urls (
                    short_code, 
                    original_url, 
                    campaign_name, 
                    campaign_type,
                    utm_source,
                    utm_medium,
                    utm_campaign,
                    utm_content,
                    utm_term,
                    created_at,
                    total_clicks,
                    is_active
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, datetime('now'), 0, 1)
            """, (
                short_code,
                url,
                campaign_name,
                campaign_type,
                utm_params.get('source') if utm_params else None,
                utm_params.get('medium') if utm_params else None,
                utm_params.get('campaign') if utm_params else None,
                utm_params.get('content') if utm_params else None,
                utm_params.get('term') if utm_params else None
            ))
            
            conn.commit()
            logger.info(f"Campaign created successfully: {campaign_name} ({short_code})")
            return short_code
            
        except Exception as e:
            logger.error(f"Error creating short URL: {str(e)}")
            conn.rollback()
            return None
            
        finally:
            conn.close()

    def get_dashboard_stats(self) -> Dict[str, Any]:
        """Get comprehensive dashboard statistics"""
        conn = self.get_connection()
        c = conn.cursor()
        try:
            # Get basic metrics
            c.execute("""
                SELECT 
                    COUNT(*) as total_campaigns,
                    SUM(CASE WHEN is_active = 1 THEN 1 ELSE 0 END) as active_campaigns,
                    SUM(total_clicks) as total_clicks,
                    COUNT(DISTINCT a.ip_address) as unique_visitors
                FROM urls u
                LEFT JOIN analytics a ON u.short_code = a.short_code
                WHERE u.is_active = 1
            """)
            
            row = c.fetchone()
            stats = {
                'total_campaigns': row[0] or 0,
                'active_campaigns': row[1] or 0,
                'total_clicks': row[2] or 0,
                'unique_visitors': row[3] or 0
            }

            # Get top performing campaigns
            c.execute("""
                SELECT 
                    u.campaign_name,
                    u.campaign_type,
                    u.total_clicks as clicks,
                    COUNT(DISTINCT a.ip_address) as unique_visitors,
                    MAX(a.clicked_at) as last_click
                FROM urls u
                LEFT JOIN analytics a ON u.short_code = a.short_code
                WHERE u.is_active = 1
                GROUP BY u.id
                ORDER BY u.total_clicks DESC
                LIMIT 5
            """)
            
            stats['top_campaigns'] = [
                {
                    'campaign_name': row[0],
                    'campaign_type': row[1],
                    'clicks': row[2] or 0,
                    'unique_visitors': row[3] or 0,
                    'last_click': row[4]
                }
                for row in c.fetchall()
            ]

            # Get recent activities
            c.execute("""
                SELECT 
                    u.campaign_name,
                    u.campaign_type,
                    a.clicked_at,
                    a.state,
                    a.device_type,
                    a.browser,
                    a.referrer
                FROM analytics a
                JOIN urls u ON a.short_code = u.short_code
                WHERE u.is_active = 1
                ORDER BY a.clicked_at DESC
                LIMIT 10
            """)
            
            stats['recent_activities'] = [
                {
                    'campaign_name': row[0],
                    'campaign_type': row[1],
                    'clicked_at': row[2],
                    'state': row[3] or 'Unknown',
                    'device_type': row[4] or 'Unknown',
                    'browser': row[5] or 'Unknown',
                    'referrer': row[6] or 'Direct'
                }
                for row in c.fetchall()
            ]

            # Get daily stats
            c.execute("""
                WITH RECURSIVE dates(date) AS (
                    SELECT date('now', '-6 days')
                    UNION ALL
                    SELECT date(date, '+1 day')
                    FROM dates
                    WHERE date < date('now')
                )
                SELECT 
                    dates.date,
                    COUNT(DISTINCT a.id) as clicks
                FROM dates
                LEFT JOIN analytics a ON date(a.clicked_at) = dates.date
                GROUP BY dates.date
                ORDER BY dates.date
            """)
            stats['daily_stats'] = dict(c.fetchall())

            # Get device distribution
            c.execute("""
                SELECT 
                    COALESCE(device_type, 'Unknown') as device,
                    COUNT(*) as count
                FROM analytics
                GROUP BY device_type
                ORDER BY count DESC
            """)
            stats['device_stats'] = dict(c.fetchall())

            # Get geographic distribution
            c.execute("""
                SELECT 
                    COALESCE(state, 'Unknown') as state,
                    COUNT(*) as count
                FROM analytics
                GROUP BY state
                ORDER BY count DESC
            """)
            stats['state_stats'] = dict(c.fetchall())

            return stats
            
        except Exception as e:
            logger.error(f"Error getting dashboard stats: {str(e)}")
            return {
                'total_campaigns': 0,
                'active_campaigns': 0,
                'total_clicks': 0,
                'unique_visitors': 0,
                'daily_stats': {},
                'device_stats': {},
                'state_stats': {},
                'recent_activities': [],
                'top_campaigns': []
            }
        finally:
            conn.close()

    def record_click(self, short_code: str, **kwargs) -> bool:
        """Record a click for a short URL"""
        conn = self.get_connection()
        c = conn.cursor()
        try:
            # First update URL stats
            c.execute('''
                UPDATE urls 
                SET total_clicks = COALESCE(total_clicks, 0) + 1,
                    last_clicked = datetime('now')
                WHERE short_code = ?
            ''', (short_code,))
            
            if c.rowcount == 0:
                logger.error(f"No URL found for short code: {short_code}")
                return False

            # Then insert click data with all fields
            c.execute('''
                INSERT INTO analytics (
                    short_code, 
                    clicked_at, 
                    ip_address, 
                    user_agent,
                    referrer, 
                    state, 
                    device_type, 
                    browser, 
                    os
                ) VALUES (?, datetime('now'), ?, ?, ?, ?, ?, ?, ?)
            ''', (
                short_code,
                kwargs.get('ip_address', '127.0.0.1'),
                kwargs.get('user_agent', 'Unknown'),
                kwargs.get('referrer', 'Direct'),
                kwargs.get('state', 'Unknown'),
                kwargs.get('device_type', 'Unknown'),
                kwargs.get('browser', 'Unknown'),
                kwargs.get('os', 'Unknown')
            ))
            
            conn.commit()
            logger.info(f"Click recorded for {short_code} with data: {kwargs}")
            return True
            
        except Exception as e:
            logger.error(f"Error recording click: {str(e)}")
            conn.rollback()
            return False
            
        finally:
            conn.close()

    def update_campaign(self, short_code: str, **kwargs) -> bool:
        """Update campaign details"""
        conn = self.get_connection()
        c = conn.cursor()
        try:
            # Build update query dynamically based on provided fields
            update_fields = []
            values = []
            
            # Map incoming field names to database column names
            field_mapping = {
                'campaign_name': 'campaign_name',
                'campaign_type': 'campaign_type',
                'is_active': 'is_active'
            }
            
            for key, value in kwargs.items():
                if key in field_mapping and value is not None:
                    update_fields.append(f"{field_mapping[key]} = ?")
                    values.append(value)
            
            if not update_fields:
                return True
            
            # Add short_code to values
            values.append(short_code)
            
            # Execute update
            query = f"""
                UPDATE urls 
                SET {', '.join(update_fields)}
                WHERE short_code = ?
            """
            c.execute(query, values)
            
            if c.rowcount > 0:
                conn.commit()
                logger.info(f"Campaign {short_code} updated successfully")
                return True
            else:
                logger.error(f"No campaign found with short_code: {short_code}")
                return False
            
        except Exception as e:
            logger.error(f"Error updating campaign: {str(e)}")
            conn.rollback()
            return False
            
        finally:
            conn.close()

    def add_click(self, short_code: str, click_data: dict):
        """Add click data using existing record_click method"""
        try:
            return self.record_click(
                short_code=short_code,
                ip_address=click_data.get('ip'),
                user_agent=click_data.get('user_agent'),
                referrer=click_data.get('referrer'),
                state=click_data.get('state'),
                device_type=click_data.get('device_type'),
                browser=click_data.get('browser', 'Unknown'),
                os=click_data.get('os', 'Unknown'),
                clicked_at=click_data.get('clicked_at')
            )
        except Exception as e:
            logger.error(f"Error adding click: {e}")
            return False

    def get_clicks_by_date_range(self, start_date: datetime, end_date: datetime):
        """Get clicks within date range"""
        try:
            clicks = self.db.clicks.find({
                'clicked_at': {
                    '$gte': start_date.strftime('%Y-%m-%d %H:%M:%S'),
                    '$lte': end_date.strftime('%Y-%m-%d %H:%M:%S')
                }
            })
            return list(clicks)
        except Exception as e:
            logger.error(f"Error getting clicks: {e}")
            return []

    def get_campaign_stats(self, short_code: str) -> Dict[str, Any]:
        """Get campaign statistics"""
        conn = self.get_connection()
        c = conn.cursor()
        try:
            # Get basic stats
            c.execute("""
                SELECT 
                    COUNT(*) as total_clicks,
                    COUNT(DISTINCT ip_address) as unique_visitors
                FROM analytics
                WHERE short_code = ?
            """, (short_code,))
            
            row = c.fetchone()
            stats = {
                'total_clicks': row[0] or 0,
                'unique_visitors': row[1] or 0
            }
            
            # Get device stats
            c.execute("""
                SELECT 
                    device_type,
                    COUNT(*) as count
                FROM analytics
                WHERE short_code = ?
                GROUP BY device_type
            """, (short_code,))
            
            stats['device_stats'] = dict(c.fetchall())
            
            # Get daily clicks
            c.execute("""
                SELECT 
                    date(clicked_at) as click_date,
                    COUNT(*) as clicks
                FROM analytics
                WHERE short_code = ?
                GROUP BY date(clicked_at)
                ORDER BY click_date DESC
                LIMIT 30
            """, (short_code,))
            
            stats['daily_clicks'] = dict(c.fetchall())
            
            return stats
            
        except Exception as e:
            logger.error(f"Error getting campaign stats: {str(e)}")
            return {
                'total_clicks': 0,
                'unique_visitors': 0,
                'device_stats': {},
                'daily_clicks': {}
            }
        finally:
            conn.close()

    def create_campaign(self, name: str, campaign_type: str, url: str, short_code: str) -> bool:
        """Create a new campaign"""
        conn = self.get_connection()
        c = conn.cursor()
        try:
            # Check if short_code already exists
            c.execute("SELECT 1 FROM urls WHERE short_code = ?", (short_code,))
            if c.fetchone():
                logger.error(f"Short code {short_code} already exists")
                return False

            # Parse URL for UTM parameters
            parsed_url = urlparse(url)
            query_params = parse_qs(parsed_url.query)
            
            c.execute("""
                INSERT INTO urls (
                    short_code, 
                    original_url, 
                    campaign_name, 
                    campaign_type,
                    utm_source,
                    utm_medium,
                    utm_campaign,
                    utm_content,
                    utm_term,
                    created_at,
                    total_clicks,
                    is_active
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, datetime('now'), 0, 1)
            """, (
                short_code,
                url,
                name,
                campaign_type,
                query_params.get('utm_source', [None])[0],
                query_params.get('utm_medium', [None])[0],
                query_params.get('utm_campaign', [None])[0],
                query_params.get('utm_content', [None])[0],
                query_params.get('utm_term', [None])[0]
            ))
            
            conn.commit()
            logger.info(f"Campaign {name} created successfully")
            return True
            
        except Exception as e:
            logger.error(f"Error creating campaign: {str(e)}")
            conn.rollback()
            return False
            
        finally:
            conn.close()

    def get_all_campaigns(self) -> List[Dict[str, Any]]:
        """Get all campaigns with their stats"""
        conn = self.get_connection()
        c = conn.cursor()
        try:
            c.execute("""
                SELECT 
                    u.campaign_name,
                    u.campaign_type,
                    u.short_code,
                    u.original_url,
                    u.total_clicks,
                    datetime(u.created_at) as created_at,
                    datetime(COALESCE(u.last_clicked, u.created_at)) as last_clicked,
                    u.is_active,
                    COUNT(DISTINCT a.ip_address) as unique_visitors
                FROM urls u
                LEFT JOIN analytics a ON u.short_code = a.short_code
                GROUP BY 
                    u.id,
                    u.campaign_name,
                    u.campaign_type,
                    u.short_code,
                    u.original_url,
                    u.total_clicks,
                    u.created_at,
                    u.last_clicked,
                    u.is_active
                ORDER BY u.created_at DESC
            """)
            
            columns = [description[0] for description in c.description]
            campaigns = []
            for row in c.fetchall():
                campaign_dict = dict(zip(columns, row))
                # Ensure total_clicks is never None
                campaign_dict['total_clicks'] = campaign_dict['total_clicks'] or 0
                # Format dates properly
                campaign_dict['created_at'] = campaign_dict['created_at']
                campaign_dict['last_clicked'] = campaign_dict['last_clicked'] if campaign_dict['last_clicked'] != campaign_dict['created_at'] else None
                campaigns.append(campaign_dict)
            
            return campaigns
            
        except Exception as e:
            logger.error(f"Error getting campaigns: {str(e)}")
            return []
            
        finally:
            conn.close()

    def delete_campaign(self, short_code: str) -> bool:
        """Delete a campaign and its analytics"""
        conn = self.get_connection()
        c = conn.cursor()
        try:
            # Delete analytics first due to foreign key constraint
            c.execute("DELETE FROM analytics WHERE short_code = ?", (short_code,))
            # Then delete the campaign
            c.execute("DELETE FROM urls WHERE short_code = ?", (short_code,))
            conn.commit()
            return True
        except Exception as e:
            logger.error(f"Error deleting campaign: {str(e)}")
            conn.rollback()
            return False
        finally:
            conn.close()

    def save_campaign_url(self, url: str, short_code: str, campaign_name: str, 
                         campaign_type: str, utm_params: dict = None) -> bool:
        """Save campaign URL to database"""
        conn = self.get_connection()
        c = conn.cursor()
        try:
            # Check if short_code exists
            c.execute("SELECT 1 FROM urls WHERE short_code = ?", (short_code,))
            if c.fetchone():
                logger.error(f"Short code {short_code} already exists")
                return False

            # Insert new URL with all required fields
            c.execute("""
                INSERT INTO urls (
                    short_code, 
                    original_url, 
                    campaign_name, 
                    campaign_type,
                    utm_source,
                    utm_medium,
                    utm_campaign,
                    utm_content,
                    utm_term,
                    created_at,
                    total_clicks,
                    is_active
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, datetime('now'), 0, 1)
            """, (
                short_code,
                url,
                campaign_name,
                campaign_type,
                utm_params.get('source') if utm_params else None,
                utm_params.get('medium') if utm_params else None,
                utm_params.get('campaign') if utm_params else None,
                utm_params.get('content') if utm_params else None,
                utm_params.get('term') if utm_params else None  # Added utm_term
            ))
            
            conn.commit()
            logger.info(f"Campaign URL saved successfully: {short_code}")
            return True
            
        except Exception as e:
            logger.error(f"Error saving campaign URL: {str(e)}")
            conn.rollback()
            return False
        finally:
            conn.close()
