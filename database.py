import sqlite3
from datetime import datetime
from typing import Optional, Dict, Any, List
import os
import logging
import pandas as pd

logger = logging.getLogger(__name__)

class Database:
    """Database handler for URL shortener with analytics"""
    
    def __init__(self):
        """Initialize database connection and create tables if they don't exist"""
        self.db_path = "urls.db"
        
        # Check if database exists
        db_exists = os.path.exists(self.db_path)
        
        # Create tables only if database doesn't exist
        if not db_exists:
            logger.info("Creating new database...")
            self.create_tables()
        else:
            logger.info("Using existing database")

    def get_connection(self):
        """Get database connection"""
        return sqlite3.connect(self.db_path)

    # === Database Initialization ===
    
    def create_tables(self):
        """Create necessary database tables if they don't exist"""
        conn = self.get_connection()
        c = conn.cursor()
        try:
            # Check if tables exist first
            c.execute("""
                SELECT name FROM sqlite_master 
                WHERE type='table' AND name='urls'
            """)
            table_exists = c.fetchone() is not None

            if not table_exists:
                # Create URLs table
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
                        total_clicks INTEGER DEFAULT 0,
                        is_active BOOLEAN DEFAULT 1,
                        UNIQUE(campaign_name)
                    )
                ''')
                
                # Create analytics table
                c.execute('''
                    CREATE TABLE IF NOT EXISTS analytics (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        short_code TEXT NOT NULL,
                        clicked_at DATETIME NOT NULL,
                        FOREIGN KEY (short_code) REFERENCES urls (short_code)
                    )
                ''')
                
                conn.commit()
                logger.info("Database tables created successfully")
            else:
                logger.info("Database tables already exist")

        except Exception as e:
            logger.error(f"Error creating tables: {str(e)}")
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
            logger.info(f"Fetching URL info for short code: {short_code}")
            
            c.execute('''
                SELECT 
                    original_url, 
                    campaign_name,
                    total_clicks,
                    created_at
                FROM urls 
                WHERE short_code = ?
            ''', (short_code,))
            
            result = c.fetchone()
            if not result:
                logger.error(f"No URL found for short code: {short_code}")
                return None
            
            url_info = {
                'original_url': result[0],
                'campaign_name': result[1],
                'total_clicks': result[2],
                'created_at': result[3],
                'short_code': short_code
            }
            
            logger.info(f"Found URL info: {url_info}")
            return url_info
            
        except Exception as e:
            logger.error(f"Error getting URL info for {short_code}: {str(e)}")
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
                    campaign_name,
                    campaign_type,
                    created_at,
                    total_clicks,
                    utm_source,
                    utm_medium,
                    utm_campaign,
                    utm_content,
                    utm_term
                FROM urls 
                ORDER BY created_at DESC
            ''')
            
            results = []
            for row in c.fetchall():
                results.append({
                    'original_url': row[0],
                    'short_code': row[1],
                    'campaign_name': row[2],
                    'campaign_type': row[3],
                    'created_at': row[4],
                    'total_clicks': row[5],
                    'utm_source': row[6],
                    'utm_medium': row[7],
                    'utm_campaign': row[8],
                    'utm_content': row[9],
                    'utm_term': row[10]
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
            
            # Get current click count
            c.execute('SELECT total_clicks FROM urls WHERE short_code = ?', (short_code,))
            result = c.fetchone()
            if not result:
                logger.error(f"No URL found for short code: {short_code}")
                return False
            
            current_clicks = result[0]
            
            # Update click count in urls table
            c.execute('''
                UPDATE urls 
                SET total_clicks = total_clicks + 1,
                    last_clicked = datetime('now')
                WHERE short_code = ?
            ''', (short_code,))
            
            # Add analytics entry
            c.execute('''
                INSERT INTO analytics (
                    short_code,
                    clicked_at
                ) VALUES (?, ?)
            ''', (short_code, now))
            
            conn.commit()
            logger.info(f"Click tracked for {short_code}: Total clicks now {current_clicks + 1}")
            return True
        except Exception as e:
            logger.error(f"Error tracking click for {short_code}: {str(e)}")
            conn.rollback()
            return False
        finally:
            conn.close()

    def get_recent_links(self, limit: int = 5) -> List[Dict[str, Any]]:
        """Get the most recent shortened URLs with full details"""
        conn = self.get_connection()
        c = conn.cursor()
        try:
            c.execute('''
                SELECT 
                    original_url,
                    short_code,
                    campaign_name,
                    campaign_type,
                    created_at,
                    total_clicks,
                    utm_source,
                    utm_medium,
                    utm_campaign
                FROM urls 
                ORDER BY created_at DESC 
                LIMIT ?
            ''', (limit,))
            
            results = []
            for row in c.fetchall():
                results.append({
                    'original_url': row[0],
                    'short_code': row[1],
                    'campaign_name': row[2],
                    'campaign_type': row[3],
                    'created_at': row[4],
                    'total_clicks': row[5],
                    'utm_source': row[6],
                    'utm_medium': row[7],
                    'utm_campaign': row[8]
                })
            return results
        except Exception as e:
            logger.error(f"Error getting recent links: {str(e)}")
            return []
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
            # Just count total clicks since we don't track IP addresses yet
            c.execute('''
                SELECT COUNT(*) as click_count
                FROM analytics
                WHERE short_code = ?
            ''', (short_code,))
            
            result = c.fetchone()
            return result[0] if result else 0
        except Exception as e:
            logger.error(f"Error getting unique clicks count: {str(e)}")
            return 0
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

    def save_campaign_url(self, url: str, short_code: str, campaign_name: str, 
                         campaign_type: str = None, utm_params: dict = None) -> bool:
        """Save a campaign URL with required campaign name"""
        if not campaign_name:
            logger.error("Campaign name is required")
            return False
        
        conn = self.get_connection()
        c = conn.cursor()
        try:
            # Check if campaign name already exists
            c.execute('SELECT id FROM urls WHERE campaign_name = ?', (campaign_name,))
            if c.fetchone():
                logger.error(f"Campaign name already exists: {campaign_name}")
                return False
            
            # Insert URL with campaign details
            c.execute('''
                INSERT INTO urls (
                    original_url,
                    short_code,
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
            ''', (
                url,
                short_code,
                campaign_name,
                campaign_type,
                utm_params.get('utm_source') if utm_params else None,
                utm_params.get('utm_medium') if utm_params else None,
                utm_params.get('utm_campaign') if utm_params else None,
                utm_params.get('utm_content') if utm_params else None,
                utm_params.get('utm_term') if utm_params else None
            ))
            
            conn.commit()
            logger.info(f"Successfully saved campaign URL: {campaign_name} -> {url}")
            return True
        except Exception as e:
            logger.error(f"Error saving campaign URL: {str(e)}")
            conn.rollback()
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

    def get_click_timeline(self, short_code: str) -> pd.DataFrame:
        """Get timeline of clicks for visualization"""
        conn = self.get_connection()
        c = conn.cursor()
        try:
            # Get clicks grouped by date
            c.execute('''
                SELECT 
                    DATE(clicked_at) as click_date,
                    COUNT(*) as click_count
                FROM analytics 
                WHERE short_code = ?
                GROUP BY DATE(clicked_at)
                ORDER BY click_date
            ''', (short_code,))
            
            results = c.fetchall()
            
            # Create DataFrame with continuous date range
            if results:
                df = pd.DataFrame(results, columns=['date', 'clicks'])
                df['date'] = pd.to_datetime(df['date'])
                
                # Create continuous date range
                date_range = pd.date_range(
                    start=df['date'].min(),
                    end=df['date'].max()
                )
                
                # Reindex with full date range, fill missing values with 0
                df = df.set_index('date').reindex(date_range, fill_value=0)
                
                return df
            else:
                # Return empty DataFrame with current date if no clicks
                today = datetime.now().date()
                return pd.DataFrame(
                    {'clicks': [0]},
                    index=pd.date_range(today, today)
                )
                
        except Exception as e:
            logger.error(f"Error getting click timeline for {short_code}: {str(e)}")
            # Return empty DataFrame on error
            today = datetime.now().date()
            return pd.DataFrame(
                {'clicks': [0]},
                index=pd.date_range(today, today)
            )
        finally:
            conn.close()

    def get_total_clicks(self) -> int:
        """Get total clicks across all campaigns"""
        conn = self.get_connection()
        c = conn.cursor()
        try:
            c.execute('SELECT SUM(total_clicks) FROM urls WHERE is_active = 1')
            result = c.fetchone()
            total = result[0] if result[0] is not None else 0
            logger.info(f"Total clicks across all campaigns: {total}")
            return total
        except Exception as e:
            logger.error(f"Error getting total clicks: {str(e)}")
            return 0
        finally:
            conn.close()

    def get_recent_clicks_count(self, hours: int = 24) -> int:
        """Get click count for the last X hours"""
        conn = self.get_connection()
        c = conn.cursor()
        try:
            c.execute('''
                SELECT COUNT(*) 
                FROM analytics 
                WHERE clicked_at >= datetime('now', ?)
            ''', (f'-{hours} hours',))
            result = c.fetchone()
            count = result[0] if result[0] is not None else 0
            logger.info(f"Recent clicks (last {hours} hours): {count}")
            return count
        except Exception as e:
            logger.error(f"Error getting recent clicks: {str(e)}")
            return 0
        finally:
            conn.close()
