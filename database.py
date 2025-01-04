import sqlite3
from datetime import datetime
from typing import Dict, Any, List, Optional
import json
import logging

logger = logging.getLogger(__name__)

class Database:
    def __init__(self, db_path="shortlinks.db"):
        self.db_path = db_path
        self.init_db()

    def init_db(self):
        """Initialize database with enhanced schema"""
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        
        # Create URLs table with new fields
        c.execute('''
            CREATE TABLE IF NOT EXISTS urls (
                short_code TEXT PRIMARY KEY,
                original_url TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                expiry_date TIMESTAMP,
                total_clicks INTEGER DEFAULT 0,
                ab_testing TEXT,
                tags TEXT,
                qr_settings TEXT,
                utm_params TEXT
            )
        ''')
        
        # Create enhanced analytics table
        c.execute('''
            CREATE TABLE IF NOT EXISTS analytics (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                short_code TEXT NOT NULL,
                clicked_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                ip_address TEXT,
                user_agent TEXT,
                country TEXT,
                city TEXT,
                device_type TEXT,
                browser TEXT,
                os TEXT,
                utm_source TEXT,
                utm_medium TEXT,
                utm_campaign TEXT,
                utm_term TEXT,
                utm_content TEXT,
                variant TEXT,
                conversion BOOLEAN DEFAULT FALSE,
                FOREIGN KEY (short_code) REFERENCES urls (short_code)
            )
        ''')
        
        conn.commit()
        conn.close()

    def save_url(self, url_data: Dict[str, Any]) -> bool:
        """Save URL with enhanced data"""
        try:
            conn = sqlite3.connect(self.db_path)
            c = conn.cursor()
            
            c.execute('''
                INSERT INTO urls (
                    short_code, original_url, expiry_date, 
                    ab_testing, tags, qr_settings, utm_params
                ) VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (
                url_data['short_code'],
                url_data['url'],
                url_data.get('expiry_date'),
                json.dumps(url_data.get('ab_testing', {})),
                json.dumps(url_data.get('tags', [])),
                json.dumps(url_data.get('qr_code', {})),
                json.dumps(url_data.get('utm_params', {}))
            ))
            
            conn.commit()
            return True
        except Exception as e:
            logger.error(f"Error saving URL: {str(e)}")
            return False
        finally:
            conn.close()

    def get_analytics_data(self, short_code: str) -> Dict[str, Any]:
        """Get enhanced analytics data"""
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        
        try:
            # Get basic URL info
            c.execute('''
                SELECT original_url, created_at, total_clicks, 
                       ab_testing, tags, expiry_date
                FROM urls 
                WHERE short_code = ?
            ''', (short_code,))
            
            url_info = c.fetchone()
            if not url_info:
                return {}

            # Get analytics data
            analytics_data = {
                'short_code': short_code,
                'original_url': url_info[0],
                'created_at': url_info[1],
                'total_clicks': url_info[2],
                'ab_testing': json.loads(url_info[3]) if url_info[3] else {},
                'tags': json.loads(url_info[4]) if url_info[4] else [],
                'expiry_date': url_info[5]
            }

            # Add enhanced analytics
            self._add_enhanced_analytics(c, short_code, analytics_data)
            
            return analytics_data
            
        except Exception as e:
            logger.error(f"Error getting analytics: {str(e)}")
            return {}
        finally:
            conn.close()

    def _add_enhanced_analytics(self, cursor, short_code: str, data: Dict[str, Any]):
        """Add enhanced analytics data"""
        # Get unique visitors
        cursor.execute('''
            SELECT COUNT(DISTINCT ip_address) 
            FROM analytics 
            WHERE short_code = ?
        ''', (short_code,))
        data['unique_visitors'] = cursor.fetchone()[0]

        # Get device distribution
        cursor.execute('''
            SELECT device_type, COUNT(*) 
            FROM analytics 
            WHERE short_code = ? 
            GROUP BY device_type
        ''', (short_code,))
        data['devices'] = dict(cursor.fetchall())

        # Get browser distribution
        cursor.execute('''
            SELECT browser, COUNT(*) 
            FROM analytics 
            WHERE short_code = ? 
            GROUP BY browser
        ''', (short_code,))
        data['browsers'] = dict(cursor.fetchall())

        # Get daily clicks
        cursor.execute('''
            SELECT DATE(clicked_at) as date, COUNT(*) as clicks 
            FROM analytics 
            WHERE short_code = ? 
            GROUP BY DATE(clicked_at)
            ORDER BY date
        ''', (short_code,))
        data['daily_clicks'] = [
            {'date': row[0], 'clicks': row[1]} 
            for row in cursor.fetchall()
        ]

    def get_all_urls(self) -> List[Dict[str, Any]]:
        """Get all URLs with basic stats"""
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        
        try:
            c.execute('''
                SELECT short_code, original_url, created_at, 
                       total_clicks, tags, expiry_date 
                FROM urls
                ORDER BY created_at DESC
            ''')
            
            urls = []
            for row in c.fetchall():
                urls.append({
                    'short_code': row[0],
                    'original_url': row[1],
                    'created_at': row[2],
                    'total_clicks': row[3],
                    'tags': json.loads(row[4]) if row[4] else [],
                    'expiry_date': row[5]
                })
            
            return urls
            
        except Exception as e:
            logger.error(f"Error getting URLs: {str(e)}")
            return []
        finally:
            conn.close() 

    def update_url_info(self, short_code: str, data: Dict[str, Any]) -> bool:
        """Update URL information"""
        conn = self.get_connection()
        c = conn.cursor()
        try:
            c.execute('''
                UPDATE urls 
                SET original_url = ?,
                    total_clicks = ?
                WHERE short_code = ?
            ''', (data.get('original_url'), data.get('total_clicks', 0), short_code))
            conn.commit()
            return True
        except Exception as e:
            print(f"Error updating URL info: {e}")
            return False
        finally:
            conn.close()

    def get_url_stats(self, short_code: str) -> Dict[str, Any]:
        """Get detailed URL statistics"""
        conn = self.get_connection()
        c = conn.cursor()
        try:
            # Get basic stats
            stats = self.get_url_info(short_code)
            if not stats:
                return None

            # Get device types
            c.execute('''
                SELECT device_type, COUNT(*) as count
                FROM analytics
                WHERE short_code = ?
                GROUP BY device_type
            ''', (short_code,))
            stats['devices'] = dict(c.fetchall())

            # Get browsers
            c.execute('''
                SELECT browser, COUNT(*) as count
                FROM analytics
                WHERE short_code = ?
                GROUP BY browser
            ''', (short_code,))
            stats['browsers'] = dict(c.fetchall())

            # Get countries
            c.execute('''
                SELECT country, COUNT(*) as count
                FROM analytics
                WHERE short_code = ?
                GROUP BY country
            ''', (short_code,))
            stats['countries'] = dict(c.fetchall())

            # Get UTM sources
            c.execute('''
                SELECT utm_source, COUNT(*) as count
                FROM analytics
                WHERE short_code = ?
                GROUP BY utm_source
            ''', (short_code,))
            stats['utm_sources'] = dict(c.fetchall())

            return stats
        finally:
            conn.close()

    def get_daily_clicks(self, short_code: str, days: int = 30) -> List[Dict[str, Any]]:
        """Get daily click statistics"""
        conn = self.get_connection()
        c = conn.cursor()
        try:
            c.execute('''
                SELECT 
                    DATE(clicked_at) as date,
                    COUNT(*) as clicks,
                    COUNT(DISTINCT ip_address) as unique_clicks
                FROM analytics
                WHERE short_code = ?
                AND clicked_at >= date('now', ?)
                GROUP BY DATE(clicked_at)
                ORDER BY date DESC
            ''', (short_code, f'-{days} days'))
            
            return [{
                'date': row[0],
                'clicks': row[1],
                'unique_clicks': row[2]
            } for row in c.fetchall()]
        finally:
            conn.close()

    def delete_url(self, short_code: str) -> bool:
        """Delete a URL and its analytics"""
        conn = self.get_connection()
        c = conn.cursor()
        try:
            # Delete analytics first due to foreign key
            c.execute('DELETE FROM analytics WHERE short_code = ?', (short_code,))
            c.execute('DELETE FROM urls WHERE short_code = ?', (short_code,))
            conn.commit()
            return True
        except Exception as e:
            print(f"Error deleting URL: {e}")
            return False
        finally:
            conn.close()

    def clear_analytics(self, short_code: str) -> bool:
        """Clear analytics for a specific URL"""
        conn = self.get_connection()
        c = conn.cursor()
        try:
            c.execute('DELETE FROM analytics WHERE short_code = ?', (short_code,))
            c.execute('UPDATE urls SET total_clicks = 0 WHERE short_code = ?', (short_code,))
            conn.commit()
            return True
        except Exception as e:
            print(f"Error clearing analytics: {e}")
            return False
        finally:
            conn.close() 

    def get_top_performing_urls(self, limit: int = 5) -> List[Dict[str, Any]]:
        """Get top performing URLs based on clicks"""
        conn = self.get_connection()
        c = conn.cursor()
        try:
            c.execute('''
                SELECT 
                    urls.short_code,
                    urls.original_url,
                    urls.total_clicks,
                    urls.created_at,
                    COUNT(DISTINCT analytics.ip_address) as unique_visitors,
                    COUNT(DISTINCT analytics.country) as countries_reached
                FROM urls
                LEFT JOIN analytics ON urls.short_code = analytics.short_code
                GROUP BY urls.short_code
                ORDER BY urls.total_clicks DESC
                LIMIT ?
            ''', (limit,))
            
            return [{
                'short_code': row[0],
                'original_url': row[1],
                'total_clicks': row[2],
                'created_at': row[3],
                'unique_visitors': row[4],
                'countries_reached': row[5]
            } for row in c.fetchall()]
        finally:
            conn.close()

    def get_traffic_sources(self, short_code: str) -> Dict[str, Any]:
        """Get detailed traffic source analysis"""
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

            # Get referrer breakdown
            c.execute('''
                SELECT 
                    referrer,
                    COUNT(*) as clicks
                FROM analytics
                WHERE short_code = ? AND referrer IS NOT NULL
                GROUP BY referrer
                ORDER BY clicks DESC
            ''', (short_code,))
            
            referrers = dict(c.fetchall())

            return {
                'sources': sources,
                'referrers': referrers
            }
        finally:
            conn.close()

    def get_geographic_data(self, short_code: str) -> List[Dict[str, Any]]:
        """Get geographic distribution of clicks"""
        conn = self.get_connection()
        c = conn.cursor()
        try:
            c.execute('''
                SELECT 
                    country,
                    COUNT(*) as clicks,
                    COUNT(DISTINCT ip_address) as unique_visitors,
                    COUNT(DISTINCT device_type) as device_types,
                    COUNT(DISTINCT browser) as browsers
                FROM analytics
                WHERE short_code = ? AND country IS NOT NULL
                GROUP BY country
                ORDER BY clicks DESC
            ''', (short_code,))
            
            return [{
                'country': row[0],
                'clicks': row[1],
                'unique_visitors': row[2],
                'device_types': row[3],
                'browsers': row[4]
            } for row in c.fetchall()]
        finally:
            conn.close()

    def get_time_analysis(self, short_code: str) -> Dict[str, Any]:
        """Get time-based click analysis"""
        conn = self.get_connection()
        c = conn.cursor()
        try:
            # Get hourly distribution
            c.execute('''
                SELECT 
                    strftime('%H', clicked_at) as hour,
                    COUNT(*) as clicks
                FROM analytics
                WHERE short_code = ?
                GROUP BY hour
                ORDER BY hour
            ''', (short_code,))
            hourly = dict(c.fetchall())

            # Get daily distribution
            c.execute('''
                SELECT 
                    strftime('%w', clicked_at) as day,
                    COUNT(*) as clicks
                FROM analytics
                WHERE short_code = ?
                GROUP BY day
                ORDER BY day
            ''', (short_code,))
            daily = dict(c.fetchall())

            # Get monthly distribution
            c.execute('''
                SELECT 
                    strftime('%m', clicked_at) as month,
                    COUNT(*) as clicks
                FROM analytics
                WHERE short_code = ?
                GROUP BY month
                ORDER BY month
            ''', (short_code,))
            monthly = dict(c.fetchall())

            return {
                'hourly': hourly,
                'daily': daily,
                'monthly': monthly
            }
        finally:
            conn.close()

    def get_device_analysis(self, short_code: str) -> Dict[str, Any]:
        """Get detailed device and browser analysis"""
        conn = self.get_connection()
        c = conn.cursor()
        try:
            # Get device types
            c.execute('''
                SELECT 
                    device_type,
                    COUNT(*) as clicks,
                    COUNT(DISTINCT ip_address) as unique_visitors
                FROM analytics
                WHERE short_code = ?
                GROUP BY device_type
            ''', (short_code,))
            
            devices = [{
                'device_type': row[0],
                'clicks': row[1],
                'unique_visitors': row[2]
            } for row in c.fetchall()]

            # Get OS distribution
            c.execute('''
                SELECT 
                    os,
                    COUNT(*) as clicks
                FROM analytics
                WHERE short_code = ?
                GROUP BY os
            ''', (short_code,))
            os_data = dict(c.fetchall())

            # Get browser versions
            c.execute('''
                SELECT 
                    browser,
                    COUNT(*) as clicks
                FROM analytics
                WHERE short_code = ?
                GROUP BY browser
            ''', (short_code,))
            browsers = dict(c.fetchall())

            return {
                'devices': devices,
                'operating_systems': os_data,
                'browsers': browsers
            }
        finally:
            conn.close()

    def search_urls(self, query: str) -> List[Dict[str, Any]]:
        """Search URLs by original URL or short code"""
        conn = self.get_connection()
        c = conn.cursor()
        try:
            c.execute('''
                SELECT 
                    short_code,
                    original_url,
                    created_at,
                    total_clicks
                FROM urls
                WHERE original_url LIKE ? OR short_code LIKE ?
                ORDER BY created_at DESC
            ''', (f'%{query}%', f'%{query}%'))
            
            return [{
                'short_code': row[0],
                'original_url': row[1],
                'created_at': row[2],
                'total_clicks': row[3]
            } for row in c.fetchall()]
        finally:
            conn.close() 

    def get_conversion_tracking(self, short_code: str) -> Dict[str, Any]:
        """Track conversion rates and user behavior"""
        conn = self.get_connection()
        c = conn.cursor()
        try:
            # Get total clicks and unique visitors
            c.execute('''
                SELECT 
                    COUNT(*) as total_clicks,
                    COUNT(DISTINCT ip_address) as unique_visitors,
                    COUNT(DISTINCT CASE WHEN successful = TRUE THEN ip_address END) as converted_visitors
                FROM analytics
                WHERE short_code = ?
            ''', (short_code,))
            
            row = c.fetchone()
            total_clicks = row[0]
            unique_visitors = row[1]
            converted_visitors = row[2]

            # Get conversion rate by source
            c.execute('''
                SELECT 
                    utm_source,
                    COUNT(*) as total,
                    COUNT(DISTINCT ip_address) as unique_visitors,
                    COUNT(DISTINCT CASE WHEN successful = TRUE THEN ip_address END) as conversions
                FROM analytics
                WHERE short_code = ?
                GROUP BY utm_source
                ORDER BY total DESC
            ''', (short_code,))
            
            sources = [{
                'source': row[0],
                'total_clicks': row[1],
                'unique_visitors': row[2],
                'conversions': row[3],
                'conversion_rate': (row[3] / row[2] * 100) if row[2] > 0 else 0
            } for row in c.fetchall()]

            return {
                'total_clicks': total_clicks,
                'unique_visitors': unique_visitors,
                'converted_visitors': converted_visitors,
                'conversion_rate': (converted_visitors / unique_visitors * 100) if unique_visitors > 0 else 0,
                'sources': sources
            }
        finally:
            conn.close()

    def get_engagement_metrics(self, short_code: str) -> Dict[str, Any]:
        """Get detailed engagement metrics"""
        conn = self.get_connection()
        c = conn.cursor()
        try:
            # Get time-based engagement
            c.execute('''
                SELECT 
                    AVG(CASE WHEN successful = TRUE THEN 1 ELSE 0 END) as success_rate,
                    COUNT(DISTINCT DATE(clicked_at)) as active_days,
                    MAX(clicked_at) as last_click,
                    MIN(clicked_at) as first_click
                FROM analytics
                WHERE short_code = ?
            ''', (short_code,))
            
            row = c.fetchone()
            success_rate = row[0] * 100 if row[0] is not None else 0
            active_days = row[1]
            last_click = row[2]
            first_click = row[3]

            # Get peak hours
            c.execute('''
                SELECT 
                    strftime('%H', clicked_at) as hour,
                    COUNT(*) as clicks
                FROM analytics
                WHERE short_code = ?
                GROUP BY hour
                ORDER BY clicks DESC
                LIMIT 5
            ''', (short_code,))
            
            peak_hours = dict(c.fetchall())

            return {
                'success_rate': success_rate,
                'active_days': active_days,
                'last_click': last_click,
                'first_click': first_click,
                'peak_hours': peak_hours,
                'avg_daily_clicks': total_clicks / active_days if active_days > 0 else 0
            }
        finally:
            conn.close()

    def get_retention_analysis(self, short_code: str) -> Dict[str, Any]:
        """Analyze user retention and return visits"""
        conn = self.get_connection()
        c = conn.cursor()
        try:
            # Get return visitor stats
            c.execute('''
                SELECT 
                    ip_address,
                    COUNT(*) as visits
                FROM analytics
                WHERE short_code = ?
                GROUP BY ip_address
                HAVING COUNT(*) > 1
            ''', (short_code,))
            
            return_visitors = c.fetchall()
            
            # Calculate retention metrics
            total_returns = len(return_visitors)
            visits_distribution = {}
            for _, visits in return_visitors:
                visits_distribution[visits] = visits_distribution.get(visits, 0) + 1

            return {
                'return_visitors': total_returns,
                'visits_distribution': visits_distribution,
                'avg_visits_per_returner': sum(visits * count for visits, count in visits_distribution.items()) / total_returns if total_returns > 0 else 0
            }
        finally:
            conn.close()

    def get_comparative_analysis(self, short_codes: List[str]) -> Dict[str, Any]:
        """Compare performance of multiple URLs"""
        conn = self.get_connection()
        c = conn.cursor()
        try:
            results = {}
            for short_code in short_codes:
                # Get basic metrics
                c.execute('''
                    SELECT 
                        urls.total_clicks,
                        COUNT(DISTINCT analytics.ip_address) as unique_visitors,
                        COUNT(DISTINCT analytics.country) as countries_reached,
                        AVG(CASE WHEN analytics.successful = TRUE THEN 1 ELSE 0 END) as success_rate
                    FROM urls
                    LEFT JOIN analytics ON urls.short_code = analytics.short_code
                    WHERE urls.short_code = ?
                    GROUP BY urls.short_code
                ''', (short_code,))
                
                row = c.fetchone()
                if row:
                    results[short_code] = {
                        'total_clicks': row[0],
                        'unique_visitors': row[1],
                        'countries_reached': row[2],
                        'success_rate': row[3] * 100 if row[3] is not None else 0
                    }

            return results
        finally:
            conn.close()

    def generate_report(self, short_code: str) -> Dict[str, Any]:
        """Generate a comprehensive performance report"""
        return {
            'basic_stats': self.get_url_info(short_code),
            'conversion_data': self.get_conversion_tracking(short_code),
            'engagement': self.get_engagement_metrics(short_code),
            'retention': self.get_retention_analysis(short_code),
            'geographic': self.get_geographic_data(short_code),
            'devices': self.get_device_analysis(short_code),
            'traffic_sources': self.get_traffic_sources(short_code),
            'time_analysis': self.get_time_analysis(short_code)
        } 

    def get_campaign_performance(self, short_code: str) -> Dict[str, Any]:
        """Analyze campaign performance with detailed metrics"""
        conn = self.get_connection()
        c = conn.cursor()
        try:
            # Get campaign metrics
            c.execute('''
                SELECT 
                    utm_campaign,
                    utm_source,
                    utm_medium,
                    COUNT(*) as clicks,
                    COUNT(DISTINCT ip_address) as unique_visitors,
                    COUNT(DISTINCT CASE WHEN successful = TRUE THEN ip_address END) as conversions,
                    COUNT(DISTINCT country) as countries,
                    COUNT(DISTINCT device_type) as devices
                FROM analytics
                WHERE short_code = ? AND utm_campaign != 'no campaign'
                GROUP BY utm_campaign, utm_source, utm_medium
                ORDER BY clicks DESC
            ''', (short_code,))
            
            campaigns = [{
                'campaign': row[0],
                'source': row[1],
                'medium': row[2],
                'clicks': row[3],
                'unique_visitors': row[4],
                'conversions': row[5],
                'countries_reached': row[6],
                'device_types': row[7],
                'conversion_rate': (row[5] / row[4] * 100) if row[4] > 0 else 0
            } for row in c.fetchall()]

            return {
                'campaigns': campaigns,
                'total_campaigns': len(campaigns),
                'best_performing': campaigns[0] if campaigns else None
            }
        finally:
            conn.close()

    def get_ab_test_results(self, short_code_a: str, short_code_b: str) -> Dict[str, Any]:
        """Compare two URLs for A/B testing analysis"""
        def get_metrics(c, short_code):
            c.execute('''
                SELECT 
                    COUNT(*) as total_clicks,
                    COUNT(DISTINCT ip_address) as unique_visitors,
                    COUNT(DISTINCT CASE WHEN successful = TRUE THEN ip_address END) as conversions,
                    AVG(CASE WHEN successful = TRUE THEN 1 ELSE 0 END) as success_rate
                FROM analytics
                WHERE short_code = ?
            ''', (short_code,))
            return c.fetchone()

        conn = self.get_connection()
        c = conn.cursor()
        try:
            metrics_a = get_metrics(c, short_code_a)
            metrics_b = get_metrics(c, short_code_b)

            if not metrics_a or not metrics_b:
                return None

            return {
                'variant_a': {
                    'clicks': metrics_a[0],
                    'unique_visitors': metrics_a[1],
                    'conversions': metrics_a[2],
                    'conversion_rate': (metrics_a[2] / metrics_a[1] * 100) if metrics_a[1] > 0 else 0,
                    'success_rate': metrics_a[3] * 100 if metrics_a[3] is not None else 0
                },
                'variant_b': {
                    'clicks': metrics_b[0],
                    'unique_visitors': metrics_b[1],
                    'conversions': metrics_b[2],
                    'conversion_rate': (metrics_b[2] / metrics_b[1] * 100) if metrics_b[1] > 0 else 0,
                    'success_rate': metrics_b[3] * 100 if metrics_b[3] is not None else 0
                }
            }
        finally:
            conn.close()

    def get_performance_alerts(self, short_code: str) -> List[Dict[str, Any]]:
        """Generate performance alerts and insights"""
        conn = self.get_connection()
        c = conn.cursor()
        try:
            alerts = []
            
            # Check for significant drop in clicks
            c.execute('''
                SELECT 
                    COUNT(*) as today_clicks,
                    (
                        SELECT COUNT(*)
                        FROM analytics
                        WHERE short_code = ?
                        AND clicked_at >= date('now', '-2 days')
                        AND clicked_at < date('now', '-1 days')
                    ) as yesterday_clicks
                FROM analytics
                WHERE short_code = ?
                AND clicked_at >= date('now', '-1 days')
            ''', (short_code, short_code))
            
            today, yesterday = c.fetchone()
            if yesterday > 0 and today < yesterday * 0.5:
                alerts.append({
                    'type': 'warning',
                    'message': f'Click volume dropped by {((yesterday-today)/yesterday*100):.1f}% compared to yesterday',
                    'metric': 'clicks'
                })

            # Check for unusual success rate changes
            c.execute('''
                SELECT 
                    AVG(CASE WHEN successful = TRUE THEN 1 ELSE 0 END) as today_rate,
                    (
                        SELECT AVG(CASE WHEN successful = TRUE THEN 1 ELSE 0 END)
                        FROM analytics
                        WHERE short_code = ?
                        AND clicked_at >= date('now', '-7 days')
                        AND clicked_at < date('now', '-1 days')
                    ) as week_rate
                FROM analytics
                WHERE short_code = ?
                AND clicked_at >= date('now', '-1 days')
            ''', (short_code, short_code))
            
            today_rate, week_rate = c.fetchone()
            if week_rate and today_rate and abs(today_rate - week_rate) > 0.2:
                alerts.append({
                    'type': 'alert',
                    'message': f'Success rate changed significantly from {week_rate*100:.1f}% to {today_rate*100:.1f}%',
                    'metric': 'success_rate'
                })

            return alerts
        finally:
            conn.close()

    def export_analytics_data(self, short_code: str, start_date: str = None, end_date: str = None) -> List[Dict[str, Any]]:
        """Export detailed analytics data for the specified period"""
        conn = self.get_connection()
        c = conn.cursor()
        try:
            query = '''
                SELECT 
                    clicked_at,
                    ip_address,
                    country,
                    device_type,
                    browser,
                    os,
                    utm_source,
                    utm_medium,
                    utm_campaign,
                    referrer,
                    successful
                FROM analytics
                WHERE short_code = ?
            '''
            params = [short_code]

            if start_date:
                query += ' AND clicked_at >= ?'
                params.append(start_date)
            if end_date:
                query += ' AND clicked_at <= ?'
                params.append(end_date)

            query += ' ORDER BY clicked_at DESC'
            
            c.execute(query, params)
            
            return [{
                'timestamp': row[0],
                'ip_address': row[1],
                'country': row[2],
                'device_type': row[3],
                'browser': row[4],
                'os': row[5],
                'utm_source': row[6],
                'utm_medium': row[7],
                'utm_campaign': row[8],
                'referrer': row[9],
                'successful': row[10]
            } for row in c.fetchall()]
        finally:
            conn.close()

    def get_real_time_stats(self, short_code: str, minutes: int = 5) -> Dict[str, Any]:
        """Get real-time statistics for the last few minutes"""
        conn = self.get_connection()
        c = conn.cursor()
        try:
            c.execute('''
                SELECT 
                    COUNT(*) as clicks,
                    COUNT(DISTINCT ip_address) as visitors,
                    COUNT(DISTINCT country) as countries,
                    COUNT(DISTINCT device_type) as devices,
                    AVG(CASE WHEN successful = TRUE THEN 1 ELSE 0 END) as success_rate
                FROM analytics
                WHERE short_code = ?
                AND clicked_at >= datetime('now', ?)
            ''', (short_code, f'-{minutes} minutes'))
            
            row = c.fetchone()
            
            return {
                'clicks': row[0],
                'active_visitors': row[1],
                'active_countries': row[2],
                'active_devices': row[3],
                'current_success_rate': row[4] * 100 if row[4] is not None else 0,
                'time_window': f'{minutes} minutes'
            }
        finally:
            conn.close() 
