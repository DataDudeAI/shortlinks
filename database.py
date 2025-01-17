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
import uuid
from geo_service import GeoService
from ip_tracker import IPTracker

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
            # Create organizations table
            c.execute('''
                CREATE TABLE IF NOT EXISTS organizations (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL,
                    domain TEXT NOT NULL UNIQUE,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # Create users table
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
            
            # Create URLs table with unique_visitors column
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
                    unique_visitors INTEGER DEFAULT 0,
                    is_active BOOLEAN DEFAULT 1,
                    UNIQUE(campaign_name)
                )
            ''')

            # Drop and recreate analytics tables
            c.execute("DROP TABLE IF EXISTS analytics")
            c.execute("DROP TABLE IF EXISTS engagement_metrics")
            
            # Create analytics table with all required fields
            c.execute('''
                CREATE TABLE IF NOT EXISTS analytics (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    short_code TEXT NOT NULL,
                    clicked_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    ip_address TEXT,
                    user_agent TEXT,
                    referrer TEXT,
                    state TEXT,
                    device_type TEXT,
                    browser TEXT,
                    os TEXT,
                    event_type TEXT,
                    event_data TEXT,
                    session_id TEXT,
                    time_on_page INTEGER DEFAULT 0,
                    is_bounce BOOLEAN DEFAULT 1,
                    is_conversion BOOLEAN DEFAULT 0,
                    engagement_score FLOAT DEFAULT 0,
                    FOREIGN KEY (short_code) REFERENCES urls(short_code)
                )
            ''')

            # Create engagement metrics table
            c.execute('''
                CREATE TABLE IF NOT EXISTS engagement_metrics (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    short_code TEXT NOT NULL,
                    session_id TEXT NOT NULL,
                    page_views INTEGER DEFAULT 1,
                    time_spent INTEGER DEFAULT 0,
                    actions_taken INTEGER DEFAULT 0,
                    last_interaction TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    is_converted BOOLEAN DEFAULT 0,
                    FOREIGN KEY (short_code) REFERENCES urls(short_code)
                )
            ''')

            # Insert default organization and users
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
            logger.info("Database initialized successfully with all tables")
            
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
        """Get URL info including click stats"""
        try:
            query = """
                SELECT 
                    original_url,
                    campaign_name,
                    campaign_type,
                    created_at,
                    last_clicked,
                    total_clicks,
                    is_active
                FROM urls 
                WHERE short_code = ?
            """
            result = self.execute_query(query, (short_code,), fetch_one=True)
            return result if result else None
        except Exception as e:
            logger.error(f"Error getting URL info: {str(e)}")
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
        try:
            stats = {}
            
            # Get basic stats with proper counting
            base_query = """
                WITH base_stats AS (
                    SELECT 
                        COUNT(DISTINCT a.id) as total_clicks,
                        COUNT(DISTINCT a.ip_address) as unique_visitors,
                        COUNT(DISTINCT u.short_code) as total_campaigns,
                        COUNT(DISTINCT CASE WHEN u.last_clicked >= date('now', '-30 day') THEN u.short_code END) as active_campaigns,
                        ROUND(AVG(CASE WHEN a.time_on_page > 0 THEN a.time_on_page ELSE NULL END), 2) as avg_time,
                        ROUND(SUM(CASE WHEN a.is_bounce = 1 THEN 1 ELSE 0 END) * 100.0 / NULLIF(COUNT(*), 0), 2) as bounce_rate,
                        COUNT(CASE WHEN a.is_conversion = 1 THEN 1 END) as conversions
                    FROM urls u
                    LEFT JOIN analytics a ON u.short_code = a.short_code
                    WHERE a.clicked_at >= date('now', '-30 day') OR a.clicked_at IS NULL
                )
                SELECT 
                    *,
                    ROUND(CAST(conversions AS FLOAT) * 100 / NULLIF(total_clicks, 0), 2) as conversion_rate
                FROM base_stats
            """
            
            base_stats = self.execute_query(base_query, fetch_one=True)
            if base_stats:
                stats.update({
                    'total_clicks': base_stats['total_clicks'] or 0,
                    'unique_visitors': base_stats['unique_visitors'] or 0,
                    'total_campaigns': base_stats['total_campaigns'] or 0,
                    'active_campaigns': base_stats['active_campaigns'] or 0,
                    'avg_time': base_stats['avg_time'] or 0,
                    'bounce_rate': base_stats['bounce_rate'] or 0,
                    'conversion_rate': base_stats['conversion_rate'] or 0
                })
            
            # Get device stats
            device_query = """
                SELECT 
                    device_type,
                    COUNT(*) as count
                FROM analytics
                WHERE clicked_at >= date('now', '-30 day')
                GROUP BY device_type
            """
            device_stats = self.execute_query(device_query)
            stats['device_stats'] = {row['device_type']: row['count'] for row in device_stats} if device_stats else {}
            
            # Get browser stats
            browser_query = """
                SELECT 
                    browser,
                    COUNT(*) as count
                FROM analytics
                WHERE clicked_at >= date('now', '-30 day')
                GROUP BY browser
            """
            browser_stats = self.execute_query(browser_query)
            stats['browser_stats'] = {row['browser']: row['count'] for row in browser_stats} if browser_stats else {}
            
            # Get recent activities
            stats['recent_activities'] = self.get_recent_activities(10)
            
            # Get traffic sources
            stats['traffic_sources'] = self.get_traffic_sources()
            
            # Get top campaigns
            campaign_query = """
                SELECT 
                    u.campaign_name,
                    COUNT(DISTINCT a.id) as clicks,
                    COUNT(DISTINCT a.ip_address) as unique_visitors,
                    ROUND(COUNT(CASE WHEN a.is_conversion = 1 THEN 1 END) * 100.0 / NULLIF(COUNT(*), 0), 2) as conversion_rate
                FROM urls u
                LEFT JOIN analytics a ON u.short_code = a.short_code
                GROUP BY u.campaign_name
                ORDER BY clicks DESC
                LIMIT 5
            """
            stats['top_campaigns'] = self.execute_query(campaign_query) or []
            
            return stats
            
        except Exception as e:
            logger.error(f"Error getting dashboard stats: {str(e)}")
            return {
                'total_clicks': 0,
                'unique_visitors': 0,
                'total_campaigns': 0,
                'active_campaigns': 0,
                'avg_time': 0,
                'bounce_rate': 0,
                'conversion_rate': 0,
                'device_stats': {},
                'browser_stats': {},
                'recent_activities': [],
                'traffic_sources': {},
                'top_campaigns': []
            }

    def record_click(self, short_code: str, client_info: Dict[str, Any]):
        """Record click analytics with engagement metrics"""
        try:
            # Get IP and click data
            ip_tracker = IPTracker()
            click_data = ip_tracker.get_click_data(client_info)
            
            # Enrich client info with geo data
            geo_service = GeoService()
            enriched_info = geo_service.enrich_client_info(click_data)
            
            # Generate session ID if not exists
            session_id = enriched_info.get('session_id', str(uuid.uuid4()))
            current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

            # Insert analytics record
            insert_query = """
                INSERT INTO analytics (
                    short_code, clicked_at, ip_address, user_agent,
                    referrer, state, device_type, browser, os,
                    event_type, session_id, is_bounce, time_on_page,
                    is_conversion
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """
            
            self.execute_query(insert_query, (
                short_code,
                current_time,
                enriched_info.get('ip_address'),
                enriched_info.get('user_agent'),
                enriched_info.get('referrer'),
                enriched_info.get('state'),
                enriched_info.get('device_type', 'Desktop'),
                enriched_info.get('browser', 'Chrome'),
                enriched_info.get('os', 'Unknown'),
                'click',
                session_id,
                1,  # is_bounce
                0,  # initial time_on_page
                0   # is_conversion
            ))

            # Update URL stats with proper unique visitor counting
            update_query = """
                UPDATE urls 
                SET 
                    total_clicks = total_clicks + 1,
                    last_clicked = CURRENT_TIMESTAMP,
                    unique_visitors = (
                        SELECT COUNT(DISTINCT ip_address) 
                        FROM analytics 
                        WHERE short_code = ? 
                        AND ip_address IS NOT NULL
                        AND ip_address != ''
                    )
                WHERE short_code = ?
            """
            self.execute_query(update_query, (short_code, short_code))
            
            logger.info(f"Recorded click with enhanced metrics for {short_code}")
            return True

        except Exception as e:
            logger.error(f"Error recording click: {str(e)}")
            return False

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
        """Handle URL redirect and record analytics"""
        try:
            # Get URL info
            url_info = self.get_url_info(short_code)
            if not url_info or not url_info.get('is_active', False):
                return None

            # Get client info from session state
            client_info = st.session_state.get('client_info', {})
            
            # Record the click
            self.record_click(short_code, client_info)
            
            # Return original URL for redirect
            return url_info.get('original_url')
            
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

    def get_total_visitors(self) -> int:
        """Get total number of visitors"""
        try:
            query = "SELECT COUNT(DISTINCT ip_address) FROM analytics"
            result = self.execute_query(query, fetch_one=True)
            return result['COUNT(DISTINCT ip_address)'] if result else 0
        except Exception as e:
            logger.error(f"Error getting total visitors: {str(e)}")
            return 0

    def get_unique_visitors(self) -> int:
        """Get number of unique visitors"""
        try:
            query = """
                SELECT COUNT(DISTINCT ip_address) as unique_visitors
                FROM analytics
                WHERE clicked_at >= date('now', '-30 day')
            """
            result = self.execute_query(query, fetch_one=True)
            return result['unique_visitors'] if result else 0
        except Exception as e:
            logger.error(f"Error getting unique visitors: {str(e)}")
            return 0

    def get_total_conversions(self) -> int:
        """Get total number of conversions"""
        try:
            query = """
                SELECT COUNT(*) as conversions
                FROM analytics
                WHERE event_type = 'conversion'
            """
            result = self.execute_query(query, fetch_one=True)
            return result['conversions'] if result else 0
        except Exception as e:
            logger.error(f"Error getting total conversions: {str(e)}")
            return 0

    def get_device_stats(self) -> Dict[str, int]:
        """Get device type distribution"""
        try:
            query = """
                SELECT device_type, COUNT(*) as count
                FROM analytics
                GROUP BY device_type
            """
            results = self.execute_query(query)
            return {row['device_type']: row['count'] for row in results}
        except Exception as e:
            logger.error(f"Error getting device stats: {str(e)}")
            return {}

    def get_browser_stats(self) -> Dict[str, int]:
        """Get browser distribution"""
        try:
            query = """
                SELECT browser, COUNT(*) as count
                FROM analytics
                GROUP BY browser
            """
            results = self.execute_query(query)
            return {row['browser']: row['count'] for row in results}
        except Exception as e:
            logger.error(f"Error getting browser stats: {str(e)}")
            return {}

    def get_os_stats(self) -> Dict[str, int]:
        """Get OS distribution"""
        try:
            query = """
                SELECT os, COUNT(*) as count
                FROM analytics
                GROUP BY os
            """
            results = self.execute_query(query)
            return {row['os']: row['count'] for row in results}
        except Exception as e:
            logger.error(f"Error getting OS stats: {str(e)}")
            return {}

    def get_geo_stats(self) -> Dict[str, int]:
        """Get geographical distribution"""
        try:
            query = """
                SELECT state, COUNT(*) as count
                FROM analytics
                WHERE state IS NOT NULL
                GROUP BY state
            """
            results = self.execute_query(query)
            return {row['state']: row['count'] for row in results}
        except Exception as e:
            logger.error(f"Error getting geo stats: {str(e)}")
            return {}

    def save_analytics_event(self, event_type: str, event_data: Dict[str, Any]):
        """Save analytics event to database"""
        try:
            query = """
                INSERT INTO analytics (
                    short_code, clicked_at, ip_address, user_agent,
                    referrer, state, device_type, browser, os,
                    event_type, event_data
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """
            self.execute_query(query, (
                event_data.get('short_code'),
                datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                event_data.get('ip_address'),
                event_data.get('user_agent'),
                event_data.get('referrer'),
                event_data.get('state'),
                event_data.get('device_type'),
                event_data.get('browser'),
                event_data.get('os'),
                event_type,
                json.dumps(event_data)
            ))
            logger.info(f"Saved analytics event: {event_type}")
        except Exception as e:
            logger.error(f"Error saving analytics event: {str(e)}")

    def get_recent_events(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Get recent analytics events"""
        try:
            query = """
                SELECT * FROM analytics
                ORDER BY clicked_at DESC
                LIMIT ?
            """
            return self.execute_query(query, (limit,))
        except Exception as e:
            logger.error(f"Error getting recent events: {str(e)}")
            return []

    def get_recent_activities(self, limit=10) -> List[Dict]:
        """Get recent activities with enhanced details"""
        try:
            query = """
                SELECT 
                    a.id,
                    u.campaign_name,
                    u.campaign_type,
                    a.clicked_at,
                    a.device_type,
                    a.browser,
                    a.os,
                    a.state,
                    a.ip_address,
                    a.referrer,
                    a.time_on_page,
                    a.is_bounce,
                    a.is_conversion
                FROM analytics a
                JOIN urls u ON a.short_code = u.short_code
                ORDER BY a.clicked_at DESC
                LIMIT ?
            """
            activities = self.execute_query(query, (limit,))
            
            # Process and enhance each activity
            for activity in activities:
                # Clean up device type
                if not activity['device_type'] or activity['device_type'] == 'Unknown':
                    activity['device_type'] = 'Desktop'
                
                # Clean up browser info
                if not activity['browser'] or activity['browser'] == 'Unknown':
                    activity['browser'] = self._detect_browser(activity.get('user_agent', ''))
                
                # Clean up state info
                if not activity['state'] or activity['state'] == 'Unknown':
                    activity['state'] = 'Maharashtra'  # Default if unknown
                    
            return activities
            
        except Exception as e:
            logger.error(f"Error getting recent activities: {str(e)}")
            return []

    def get_traffic_sources(self) -> Dict[str, int]:
        """Get traffic source distribution"""
        try:
            query = """
                SELECT 
                    CASE
                        WHEN referrer IS NULL OR referrer = '' THEN 'Direct'
                        WHEN referrer LIKE '%google%' THEN 'Google'
                        WHEN referrer LIKE '%facebook%' THEN 'Facebook'
                        WHEN referrer LIKE '%twitter%' THEN 'Twitter'
                        WHEN referrer LIKE '%linkedin%' THEN 'LinkedIn'
                        WHEN referrer LIKE '%instagram%' THEN 'Instagram'
                        ELSE 'Other'
                    END as source,
                    COUNT(*) as count
                FROM analytics
                GROUP BY source
                ORDER BY count DESC
            """
            results = self.execute_query(query)
            return {row['source']: row['count'] for row in results}
            
        except Exception as e:
            logger.error(f"Error getting traffic sources: {str(e)}")
            return {
                'Direct': 0,
                'Google': 0,
                'Facebook': 0,
                'Twitter': 0,
                'LinkedIn': 0,
                'Instagram': 0,
                'Other': 0
            }

    def _detect_browser(self, user_agent: str) -> str:
        """Helper method to detect browser from user agent"""
        browsers = {
            'chrome': 'Chrome',
            'firefox': 'Firefox',
            'safari': 'Safari',
            'edge': 'Edge',
            'opera': 'Opera',
            'msie': 'Internet Explorer'
        }
        
        user_agent = user_agent.lower()
        for key, value in browsers.items():
            if key in user_agent:
                return value
        return 'Chrome'  # Default to Chrome if unknown