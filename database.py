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
        """Get comprehensive dashboard statistics"""
        conn = self.get_connection()
        c = conn.cursor()
        try:
            # Initialize empty stats
            stats = {
                'total_clicks': None,
                'unique_visitors': None,
                'total_campaigns': None,
                'active_campaigns': None,
                'recent_activities': [],
                'top_campaigns': [],
                'state_stats': {},
                'device_stats': {},
                'daily_stats': {}
            }
            
            # Check if any data exists
            c.execute("SELECT COUNT(*) FROM urls")
            if c.fetchone()[0] == 0:
                # Return empty stats if no data
                return stats
            
            # Get basic metrics
            c.execute("""
                SELECT 
                    COUNT(DISTINCT a.id) as total_clicks,
                    COUNT(DISTINCT a.ip_address) as unique_visitors,
                    COUNT(DISTINCT u.id) as total_campaigns,
                    COUNT(DISTINCT CASE WHEN u.is_active = 1 THEN u.id END) as active_campaigns
                FROM urls u
                LEFT JOIN analytics a ON u.short_code = a.short_code
            """)
            row = c.fetchone()
            if row:
                stats.update({
                    'total_clicks': row[0] or 0,
                    'unique_visitors': row[1] or 0,
                    'total_campaigns': row[2] or 0,
                    'active_campaigns': row[3] or 0
                })

            # Only fetch other stats if we have campaigns
            if stats['total_campaigns']:
                # Get recent activities
                c.execute("""
                    SELECT 
                        u.campaign_name,
                        a.clicked_at,
                        a.state,
                        a.device_type,
                        a.browser,
                        u.campaign_type
                    FROM analytics a
                    JOIN urls u ON a.short_code = u.short_code
                    ORDER BY a.clicked_at DESC
                    LIMIT 10
                """)
                stats['recent_activities'] = [{
                    'campaign_name': row[0],
                    'clicked_at': row[1],
                    'state': row[2],
                    'device_type': row[3],
                    'browser': row[4],
                    'campaign_type': row[5]
                } for row in c.fetchall()]

                # Get top performing campaigns
                c.execute("""
                    SELECT 
                        u.campaign_name,
                        COUNT(a.id) as clicks,
                        COUNT(DISTINCT a.ip_address) as unique_visitors,
                        u.campaign_type,
                        MAX(a.clicked_at) as last_click
                    FROM urls u
                    LEFT JOIN analytics a ON u.short_code = a.short_code
                    GROUP BY u.id
                    ORDER BY clicks DESC
                    LIMIT 5
                """)
                stats['top_campaigns'] = [{
                    'campaign_name': row[0],
                    'clicks': row[1],
                    'unique_visitors': row[2],
                    'campaign_type': row[3],
                    'last_click': row[4]
                } for row in c.fetchall()]

                # Get state distribution
                c.execute("""
                    SELECT state, COUNT(*) as count
                    FROM analytics
                    WHERE state IS NOT NULL
                    GROUP BY state
                    ORDER BY count DESC
                """)
                stats['state_stats'] = dict(c.fetchall())

                # Get device distribution
                c.execute("""
                    SELECT device_type, COUNT(*) as count
                    FROM analytics
                    WHERE device_type IS NOT NULL
                    GROUP BY device_type
                """)
                stats['device_stats'] = dict(c.fetchall())

                # Get daily clicks for the last 30 days
                c.execute("""
                    SELECT 
                        date(clicked_at) as click_date,
                        COUNT(*) as clicks
                    FROM analytics
                    WHERE clicked_at >= date('now', '-30 days')
                    GROUP BY click_date
                    ORDER BY click_date
                """)
                stats['daily_stats'] = dict(c.fetchall())

            return stats

        except Exception as e:
            logger.error(f"Error getting dashboard stats: {str(e)}")
            return {
                'total_clicks': None,
                'unique_visitors': None,
                'total_campaigns': None,
                'active_campaigns': None,
                'recent_activities': [],
                'top_campaigns': [],
                'state_stats': {},
                'device_stats': {},
                'daily_stats': {}
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
                SET total_clicks = total_clicks + 1,
                    last_clicked = datetime('now')
                WHERE short_code = ?
            ''', (short_code,))
            
            # Then insert click data
            c.execute('''
                INSERT INTO analytics (
                    short_code, clicked_at, ip_address, user_agent,
                    referrer, state, device_type, browser, os,
                    time_on_page
                ) VALUES (?, datetime('now'), ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                short_code,
                kwargs.get('ip_address'),
                kwargs.get('user_agent'),
                kwargs.get('referrer'),
                kwargs.get('state'),
                kwargs.get('device_type'),
                kwargs.get('browser'),
                kwargs.get('os'),
                kwargs.get('time_on_page', 0)  # Default to 0 if not provided
            ))
            
            conn.commit()
            logger.info(f"Click recorded successfully for {short_code}")
            return True
            
        except Exception as e:
            logger.error(f"Error recording click: {str(e)}")
            conn.rollback()
            return False
            
        finally:
            conn.close()

    def handle_redirect(self, short_code: str) -> Optional[str]:
        """Handle URL redirect and record click analytics"""
        try:
            # Get URL info
            url_info = self.get_url_info(short_code)
            
            if url_info and url_info.get('original_url'):
                # Record the click first
                click_recorded = self.record_click(
                    short_code=short_code,
                    ip_address=st.session_state.get('client_ip', '127.0.0.1'),
                    user_agent=st.session_state.get('user_agent', 'Unknown'),
                    referrer=st.session_state.get('referrer', 'Direct'),
                    state=st.session_state.get('state', 'Unknown'),
                    device_type=st.session_state.get('device_type', 'Unknown'),
                    browser=st.session_state.get('browser', 'Unknown'),
                    os=st.session_state.get('os', 'Unknown')
                )
                
                if click_recorded:
                    logger.info(f"Click recorded for {short_code}")
                    # Force a cache clear to update stats
                    st.cache_data.clear()
                    return url_info['original_url']
                else:
                    logger.error(f"Failed to record click for {short_code}")
                    
            return None
            
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
                    return cursor.fetchone()
                return cursor.fetchall()
            
        except Exception as e:
            logger.error(f"Database query error: {str(e)}")
            if query.strip().upper().startswith(('INSERT', 'UPDATE', 'DELETE')):
                conn.rollback()
            raise
        finally:
            conn.close()
