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
            # Only initialize if database doesn't exist
            if not os.path.exists(self.db_path):
                logger.info("Creating new database...")
                self.initialize_database()
            else:
                # Check if tables exist
                conn = self.get_connection()
                c = conn.cursor()
                c.execute("SELECT name FROM sqlite_master WHERE type='table'")
                tables = [table[0] for table in c.fetchall()]
                conn.close()
                
                # Initialize only if required tables are missing
                required_tables = {'organizations', 'users', 'urls', 'analytics'}
                if not required_tables.issubset(set(tables)):
                    logger.info("Reinitializing database with missing tables...")
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
            # Create organizations table if not exists
            c.execute('''
                CREATE TABLE IF NOT EXISTS organizations (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL,
                    domain TEXT NOT NULL UNIQUE,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # Create users table if not exists
            c.execute('''
                CREATE TABLE IF NOT EXISTS users (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    username TEXT NOT NULL UNIQUE,
                    password TEXT NOT NULL,
                    organization_id INTEGER,
                    role TEXT NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (organization_id) REFERENCES organizations(id)
                )
            ''')
            
            # Create URLs table if not exists
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
                    is_active BOOLEAN DEFAULT 1,
                    UNIQUE(campaign_name)
                )
            ''')
            
            # Create analytics table if not exists
            c.execute('''
                CREATE TABLE IF NOT EXISTS analytics (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    short_code TEXT NOT NULL,
                    clicked_at DATETIME NOT NULL,
                    ip_address TEXT,
                    user_agent TEXT,
                    referrer TEXT,
                    state TEXT,
                    device_type TEXT,
                    browser TEXT,
                    os TEXT,
                    time_on_page INTEGER DEFAULT 0,
                    FOREIGN KEY (short_code) REFERENCES urls(short_code)
                )
            ''')

            # Insert default organization and users if they don't exist
            c.execute('''
                INSERT OR IGNORE INTO organizations (id, name, domain) 
                VALUES (1, 'VBG Game Studios', 'virtualbattleground.in')
            ''')

            c.execute('''
                INSERT OR IGNORE INTO users (username, password, organization_id, role) 
                VALUES ('admin', 'admin123', 1, 'admin')
            ''')
            
            c.execute('''
                INSERT OR IGNORE INTO users (username, password, organization_id, role)
                VALUES ('nandan', 'nandan123', 1, 'user')
            ''')

            conn.commit()
            logger.info("Database initialized with VBG Game Studios domain")
            
        except Exception as e:
            logger.error(f"Error initializing database: {str(e)}")
            conn.rollback()
            raise
        finally:
            conn.close()

    def get_analytics_summary(self, start_date=None, end_date=None, campaigns=None, states=None) -> Dict[str, Any]:
        """Get analytics summary with optional filters"""
        conn = self.get_connection()
        c = conn.cursor()
        try:
            # Build base query parts
            base_select = """
                SELECT 
                    COUNT(a.id) as total_clicks,
                    COUNT(DISTINCT a.ip_address) as unique_visitors,
                    COUNT(DISTINCT DATE(a.clicked_at)) as active_days
                FROM urls u
                LEFT JOIN analytics a ON u.short_code = a.short_code
            """
            
            # Build WHERE clause dynamically
            where_conditions = []
            params = []
            
            if start_date:
                where_conditions.append("DATE(a.clicked_at) >= DATE(?)")
                params.append(start_date)
            
            if end_date:
                where_conditions.append("DATE(a.clicked_at) <= DATE(?)")
                params.append(end_date)
            
            if campaigns:
                placeholders = ','.join(['?' for _ in campaigns])
                where_conditions.append(f"u.campaign_name IN ({placeholders})")
                params.extend(campaigns)
            
            if states:
                placeholders = ','.join(['?' for _ in states])
                where_conditions.append(f"a.state IN ({placeholders})")
                params.extend(states)
            
            where_clause = f"WHERE {' AND '.join(where_conditions)}" if where_conditions else ""
            
            # Execute main metrics query
            query = f"{base_select} {where_clause}"
            c.execute(query, params)
            row = c.fetchone()
            
            summary = {
                'total_clicks': row[0] or 0,
                'unique_visitors': row[1] or 0,
                'active_days': row[2] or 0,
                'engagement_rate': (row[1] / row[0] * 100) if row[0] and row[1] else 0
            }
            
            # Get daily stats
            daily_query = f"""
                SELECT 
                    DATE(COALESCE(a.clicked_at, u.created_at)) as date,
                    COUNT(a.id) as clicks
                FROM urls u
                LEFT JOIN analytics a ON u.short_code = a.short_code
                {where_clause}
                GROUP BY DATE(COALESCE(a.clicked_at, u.created_at))
                ORDER BY date
            """
            c.execute(daily_query, params)
            summary['daily_stats'] = {
                row[0]: row[1] for row in c.fetchall()
            }
            
            # Get state stats
            state_query = f"""
                SELECT 
                    COALESCE(a.state, 'Unknown') as state,
                    COUNT(a.id) as visits
                FROM urls u
                LEFT JOIN analytics a ON u.short_code = a.short_code
                {where_clause}
                GROUP BY COALESCE(a.state, 'Unknown')
                HAVING state IS NOT NULL
                ORDER BY visits DESC
            """
            c.execute(state_query, params)
            summary['state_stats'] = {
                row[0]: row[1] for row in c.fetchall()
            }
            
            # Get campaign stats
            campaign_query = f"""
                SELECT 
                    u.campaign_name,
                    COUNT(a.id) as total_clicks,
                    COUNT(DISTINCT a.ip_address) as unique_visitors,
                    0 as avg_time,
                    0 as bounce_rate
                FROM urls u
                LEFT JOIN analytics a ON u.short_code = a.short_code
                {where_clause}
                GROUP BY u.campaign_name
                ORDER BY total_clicks DESC
            """
            c.execute(campaign_query, params)
            summary['campaign_stats'] = [{
                'campaign_name': row[0],
                'total_clicks': row[1] or 0,
                'unique_visitors': row[2] or 0,
                'avg_time_on_page': "0s",  # Default value
                'bounce_rate': 0,  # Default value
                'conversion_rate': (row[2] / row[1] * 100) if row[1] and row[2] else 0
            } for row in c.fetchall()]
            
            return summary
            
        except Exception as e:
            logger.error(f"Error getting analytics summary: {str(e)}")
            return {
                'total_clicks': 0,
                'unique_visitors': 0,
                'active_days': 0,
                'engagement_rate': 0,
                'daily_stats': {},
                'state_stats': {},
                'campaign_stats': []
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
        """Get URL info by short code"""
        conn = self.get_connection()
        c = conn.cursor()
        try:
            c.execute('''
                SELECT 
                    original_url,
                    campaign_name,
                    campaign_type,
                    created_at,
                    last_clicked,
                    total_clicks,
                    utm_source,
                    utm_medium,
                    utm_campaign,
                    utm_content,
                    is_active
                FROM urls 
                WHERE short_code = ?
            ''', (short_code,))
            
            row = c.fetchone()
            if row:
                return {
                    'original_url': row[0],
                    'campaign_name': row[1],
                    'campaign_type': row[2],
                    'created_at': row[3],
                    'last_clicked': row[4],
                    'total_clicks': row[5],
                    'utm_source': row[6],
                    'utm_medium': row[7],
                    'utm_campaign': row[8],
                    'utm_content': row[9],
                    'is_active': bool(row[10])
                }
            return None
        except Exception as e:
            logger.error(f"Error getting URL info: {str(e)}")
            return None
        finally:
            conn.close()

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

    def create_short_url(self, url: str, campaign_name: str, campaign_type: str = None, utm_params: dict = None) -> str:
        """Create a new short URL"""
        conn = self.get_connection()
        c = conn.cursor()
        try:
            # Generate unique short code
            short_code = self.generate_short_code()
            
            # Add UTM parameters if provided
            if utm_params:
                parsed_url = urlparse(url)
                query_params = parse_qs(parsed_url.query)
                
                # Add UTM parameters
                if utm_params.get('source'): query_params['utm_source'] = [utm_params['source']]
                if utm_params.get('medium'): query_params['utm_medium'] = [utm_params['medium']]
                if utm_params.get('campaign'): query_params['utm_campaign'] = [utm_params['campaign']]
                if utm_params.get('content'): query_params['utm_content'] = [utm_params['content']]
                
                # Reconstruct URL with UTM parameters
                url = parsed_url._replace(query=urlencode(query_params, doseq=True)).geturl()
            
            # Insert new URL
            c.execute('''
                INSERT INTO urls (
                    short_code, original_url, campaign_name, campaign_type,
                    utm_source, utm_medium, utm_campaign, utm_content
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                short_code,
                url,
                campaign_name,
                campaign_type,
                utm_params.get('source') if utm_params else None,
                utm_params.get('medium') if utm_params else None,
                utm_params.get('campaign') if utm_params else None,
                utm_params.get('content') if utm_params else None
            ))
            
            conn.commit()
            logger.info(f"Created short URL: {short_code} for campaign: {campaign_name}")
            return short_code
            
        except sqlite3.IntegrityError as e:
            logger.error(f"Error creating short URL: {str(e)}")
            if "UNIQUE constraint failed: urls.campaign_name" in str(e):
                raise ValueError("Campaign name already exists")
            raise
        except Exception as e:
            logger.error(f"Error creating short URL: {str(e)}")
            conn.rollback()
            raise
        finally:
            conn.close()

    def get_dashboard_stats(self) -> Dict[str, Any]:
        """Get dashboard statistics"""
        try:
            stats = {
                'total_clicks': 0,
                'unique_visitors': 0,
                'total_campaigns': 0,
                'active_campaigns': 0,
                'recent_activities': [],
                'top_campaigns': [],
                'state_stats': {},
                'device_stats': {},
                'daily_stats': {},
                'previous_clicks': 0,
                'previous_unique': 0,
                'bounce_rate': 0,
                'avg_time': 0
            }
            
            # Get basic metrics with time comparison
            query = """
                WITH current_stats AS (
                    SELECT 
                        COUNT(*) as total_clicks,
                        COUNT(DISTINCT ip_address) as unique_visitors,
                        AVG(time_on_page) as avg_time,
                        (SELECT COUNT(*) FROM urls) as total_campaigns,
                        (SELECT COUNT(*) FROM urls WHERE is_active = 1) as active_campaigns
                    FROM analytics
                    WHERE clicked_at >= date('now', '-30 days')
                ),
                previous_stats AS (
                    SELECT 
                        COUNT(*) as prev_clicks,
                        COUNT(DISTINCT ip_address) as prev_unique
                    FROM analytics
                    WHERE clicked_at BETWEEN date('now', '-60 days') AND date('now', '-30 days')
                ),
                bounce_stats AS (
                    SELECT 
                        (COUNT(CASE WHEN time_on_page < 10 THEN 1 END) * 100.0 / COUNT(*)) as bounce_rate
                    FROM analytics
                    WHERE clicked_at >= date('now', '-30 days')
                )
                SELECT 
                    current_stats.*,
                    previous_stats.prev_clicks,
                    previous_stats.prev_unique,
                    bounce_stats.bounce_rate
                FROM current_stats, previous_stats, bounce_stats
            """
            
            result = self.execute_query(query, fetch_one=True)
            if result:
                stats.update({
                    'total_clicks': result['total_clicks'],
                    'unique_visitors': result['unique_visitors'],
                    'total_campaigns': result['total_campaigns'],
                    'active_campaigns': result['active_campaigns'],
                    'previous_clicks': result['prev_clicks'],
                    'previous_unique': result['prev_unique'],
                    'bounce_rate': round(result['bounce_rate'], 2) if result['bounce_rate'] else 0,
                    'avg_time': round(result['avg_time'], 2) if result['avg_time'] else 0
                })
            
            # Get device stats
            query = """
                SELECT 
                    device_type,
                    COUNT(*) as count
                FROM analytics
                WHERE clicked_at >= date('now', '-30 days')
                GROUP BY device_type
            """
            device_results = self.execute_query(query)
            stats['device_stats'] = {row['device_type']: row['count'] for row in device_results}
            
            # Get browser stats
            query = """
                SELECT 
                    browser,
                    COUNT(*) as count
                FROM analytics
                WHERE clicked_at >= date('now', '-30 days')
                GROUP BY browser
            """
            browser_results = self.execute_query(query)
            stats['browser_stats'] = {row['browser']: row['count'] for row in browser_results}
            
            # Get recent activities with enhanced details
            query = """
                SELECT 
                    a.clicked_at,
                    a.device_type,
                    a.browser,
                    a.state,
                    a.time_on_page,
                    u.campaign_name,
                    u.campaign_type
                FROM analytics a
                JOIN urls u ON a.short_code = u.short_code
                ORDER BY a.clicked_at DESC
                LIMIT 10
            """
            recent_activities = self.execute_query(query)
            stats['recent_activities'] = [dict(activity) for activity in recent_activities]
            
            # Get top campaigns with engagement metrics
            query = """
                SELECT 
                    u.campaign_name,
                    u.campaign_type,
                    COUNT(a.id) as clicks,
                    COUNT(DISTINCT a.ip_address) as unique_visitors,
                    AVG(a.time_on_page) as avg_time,
                    (COUNT(CASE WHEN a.time_on_page < 10 THEN 1 END) * 100.0 / COUNT(*)) as bounce_rate
                FROM urls u
                LEFT JOIN analytics a ON u.short_code = a.short_code
                GROUP BY u.campaign_name, u.campaign_type
                ORDER BY clicks DESC
                LIMIT 5
            """
            stats['top_campaigns'] = self.execute_query(query)
            
            return stats
            
        except Exception as e:
            logger.error(f"Error getting dashboard stats: {str(e)}")
            return {
                'total_clicks': 0,
                'unique_visitors': 0,
                'total_campaigns': 0,
                'active_campaigns': 0,
                'recent_activities': [],
                'top_campaigns': [],
                'state_stats': {},
                'device_stats': {},
                'daily_stats': {},
                'previous_clicks': 0,
                'previous_unique': 0,
                'bounce_rate': 0,
                'avg_time': 0
            }

    def record_click(self, short_code: str, **click_data):
        """Record click analytics"""
        try:
            query = """
                INSERT INTO analytics (
                    short_code, clicked_at, ip_address, user_agent,
                    referrer, state, device_type, browser, os
                ) VALUES (?, CURRENT_TIMESTAMP, ?, ?, ?, ?, ?, ?, ?)
            """
            params = (
                short_code,
                click_data.get('ip_address'),
                click_data.get('user_agent'),
                click_data.get('referrer'),
                click_data.get('state'),
                click_data.get('device_type', 'Unknown'),  # Default to Unknown
                click_data.get('browser', 'Unknown'),      # Default to Unknown
                click_data.get('os', 'Unknown')           # Default to Unknown
            )
            self.execute_query(query, params)
            logger.info(f"Recorded click with device data for {short_code}")
            
        except Exception as e:
            logger.error(f"Error recording click: {str(e)}")

    def update_url_stats(self, short_code: str):
        """Update URL statistics after click"""
        try:
            query = """
                UPDATE urls 
                SET total_clicks = total_clicks + 1,
                    last_clicked = CURRENT_TIMESTAMP
                WHERE short_code = ?
            """
            self.execute_query(query, (short_code,))
            logger.info(f"Updated stats for {short_code}")
            
        except Exception as e:
            logger.error(f"Error updating URL stats: {str(e)}")

    def handle_redirect(self, short_code: str) -> Optional[str]:
        """Handle URL redirect and record click data"""
        try:
            # Get URL info
            url_info = self.get_url_info(short_code)
            if not url_info:
                return None

            # Get client info from Streamlit session state
            client_info = st.session_state.get('client_info', {})
            
            # Record click with analytics
            self.record_click(
                short_code=short_code,
                ip_address=client_info.get('ip_address'),
                user_agent=client_info.get('user_agent'),
                referrer=client_info.get('referrer'),
                state=client_info.get('state'),
                device_type=client_info.get('device_type'),
                browser=client_info.get('browser'),
                os=client_info.get('os')
            )

            # Update URL stats
            self.update_url_stats(short_code)
            
            return url_info['original_url']
            
        except Exception as e:
            logger.error(f"Error handling redirect: {str(e)}")
            return None

    def update_campaign(self, short_code: str, **kwargs) -> bool:
        """Update campaign details"""
        conn = self.get_connection()
        c = conn.cursor()
        try:
            # Build update query dynamically based on provided fields
            update_fields = []
            values = []
            for key, value in kwargs.items():
                if value is not None:
                    update_fields.append(f"{key} = ?")
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
            
            conn.commit()
            logger.info(f"Campaign {short_code} updated successfully")
            return True
            
        except Exception as e:
            logger.error(f"Error updating campaign: {str(e)}")
            conn.rollback()
            return False
            
        finally:
            conn.close()

    def get_user(self, username: str) -> Optional[dict]:
        """Get user by username"""
        try:
            query = """
                SELECT u.*, o.name as organization, o.domain
                FROM users u
                JOIN organizations o ON u.organization_id = o.id
                WHERE u.username = ?
            """
            logger.info(f"Fetching user data for: {username}")
            result = self.execute_query(query, (username,), fetch_one=True)
            logger.info(f"Query result: {result}")
            return result if result else None
        except Exception as e:
            logger.error(f"Error getting user data: {str(e)}", exc_info=True)
            return None

    def get_organization_users(self, organization_id: int) -> List[dict]:
        """Get all users in an organization"""
        query = """
            SELECT username, role, created_at
            FROM users
            WHERE organization_id = ?
        """
        return self.execute_query(query, (organization_id,))

    def add_user(self, username: str, password: str, organization_id: int, role: str = 'user') -> bool:
        """Add a new user to an organization"""
        query = """
            INSERT INTO users (username, password, organization_id, role)
            VALUES (?, ?, ?, ?)
        """
        try:
            self.execute_query(query, (username, password, organization_id, role))
            return True
        except Exception as e:
            logger.error(f"Error adding user: {str(e)}")
            return False

    def remove_user(self, username: str, organization_id: int) -> bool:
        """Remove a user from an organization"""
        query = """
            DELETE FROM users
            WHERE username = ? AND organization_id = ?
        """
        try:
            self.execute_query(query, (username, organization_id))
            return True
        except Exception as e:
            logger.error(f"Error removing user: {str(e)}")
            return False

    def execute_query(self, query: str, params: tuple = (), fetch_one: bool = False):
        """Execute a database query with parameters"""
        conn = self.get_connection()
        try:
            conn.row_factory = sqlite3.Row  # This allows accessing columns by name
            cursor = conn.cursor()
            cursor.execute(query, params)
            
            if query.strip().upper().startswith(('INSERT', 'UPDATE', 'DELETE')):
                conn.commit()
                return cursor.lastrowid
            else:
                if fetch_one:
                    row = cursor.fetchone()
                    return dict(row) if row else None
                return [dict(row) for row in cursor.fetchall()]
            
        except Exception as e:
            logger.error(f"Database query error: {str(e)}")
            if query.strip().upper().startswith(('INSERT', 'UPDATE', 'DELETE')):
                conn.rollback()
            raise
        finally:
            conn.close()