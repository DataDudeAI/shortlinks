from typing import Dict, Any, List
from urllib.parse import urlparse, parse_qs

class Analytics:
    def __init__(self, database):
        self.db = database

    def parse_utm_parameters(self, url: str) -> Dict[str, str]:
        parsed_url = urlparse(url)
        query_params = parse_qs(parsed_url.query)
        
        utm_params = {
            'utm_source': query_params.get('utm_source', [None])[0],
            'utm_medium': query_params.get('utm_medium', [None])[0],
            'utm_campaign': query_params.get('utm_campaign', [None])[0]
        }
        
        return utm_params

    def track_click(self, short_code: str, request_data: Dict[str, Any]):
        analytics_data = {
            'short_code': short_code,
            **self.parse_utm_parameters(request_data.get('referrer', ''))
        }
        
        self.db.save_analytics(analytics_data)

    def get_analytics(self, short_code: str) -> Dict[str, Any]:
        conn = self.db.get_connection()
        c = conn.cursor()
        
        try:
            # Get URL info first
            url_info = self.db.get_url_info(short_code)
            if not url_info:
                return None

            # Get general statistics
            c.execute('''
                SELECT 
                    COUNT(*) as total_clicks,
                    MAX(clicked_at) as last_clicked
                FROM analytics
                WHERE short_code = ?
            ''', (short_code,))
            
            general_stats = c.fetchone()
            
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
            
            return {
                'total_clicks': url_info['total_clicks'],
                'last_clicked': general_stats[1] if general_stats else None,
                'utm_sources': utm_sources,
                'utm_mediums': utm_mediums,
                'original_url': url_info['original_url'],
                'created_at': url_info['created_at']
            }
        finally:
            conn.close()

    def get_redirect_url(self, short_code: str) -> str:
        url_info = self.db.get_url_info(short_code)
        if url_info:
            return url_info['original_url']
        return None

    def get_past_links(self) -> List[Dict[str, Any]]:
        conn = self.db.get_connection()
        c = conn.cursor()
        
        try:
            c.execute('''
                SELECT short_code, original_url, created_at, total_clicks
                FROM urls
                ORDER BY created_at DESC
            ''')
            
            links = []
            for row in c.fetchall():
                links.append({
                    'short_code': row[0],
                    'original_url': row[1],
                    'created_at': row[2],
                    'total_clicks': row[3]
                })
            
            return links
        finally:
            conn.close() 