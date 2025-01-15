import logging
from datetime import datetime
from typing import Dict, Optional, List
import json
from dataclasses import dataclass
from enum import Enum
import uuid
from google.analytics.data_v1beta import BetaAnalyticsDataClient
from google.analytics.data_v1beta.types import RunReportRequest
import requests
from user_agents import parse
import os

# Setup logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class JourneyEventType(Enum):
    LINK_CLICK = "link_click"
    APP_OPEN = "app_open"
    APP_INSTALL = "app_install"
    PAGE_VIEW = "page_view"
    CONVERSION = "conversion"
    APP_ENGAGEMENT = "app_engagement"
    DEEP_LINK = "deep_link"
    ATTRIBUTION = "attribution"
    FUNNEL_PROGRESS = "funnel_progress"
    BUTTON_CLICK = "button_click"
    EXPORT = "export"
    REFRESH = "refresh"
    FEATURE_USE = "feature_use"
    VIEW = "view"
    ERROR = "error"
    FORM_SUBMIT = "form_submit"

@dataclass
class UserDevice:
    device_type: str
    os: str
    browser: str
    screen_resolution: str
    language: str
    user_agent: str

@dataclass
class UserLocation:
    country: str
    region: str
    city: str
    ip_address: str

@dataclass
class JourneyEvent:
    event_id: str
    event_type: JourneyEventType
    timestamp: datetime
    session_id: str
    device: UserDevice
    location: UserLocation
    campaign_data: Dict
    custom_parameters: Dict
    previous_event_id: Optional[str] = None

class UserJourneyTracker:
    def __init__(self, db=None):  # Make database parameter optional
        """Initialize journey tracker"""
        self.db = db
        self.current_journey = {}

    def _send_ga4_event(self, event_name: str, event_params: Dict):
        """Send event to Google Analytics 4"""
        try:
            if not (self.measurement_id and self.api_secret):
                logger.warning("GA4 credentials not configured")
                return

            endpoint = f"https://www.google-analytics.com/mp/collect?measurement_id={self.measurement_id}&api_secret={self.api_secret}"
            
            payload = {
                "client_id": str(uuid.uuid4()),
                "events": [{
                    "name": event_name,
                    "params": event_params
                }]
            }

            response = requests.post(endpoint, json=payload)
            if response.status_code != 200:
                logger.error(f"Failed to send GA4 event: {response.text}")

        except Exception as e:
            logger.error(f"Error sending GA4 event: {e}")

    def start_journey(self, short_code: str, user_data: Dict) -> str:
        """Start tracking a new user journey"""
        try:
            if not user_data:
                raise ValueError("User data is required")

            session_id = str(uuid.uuid4())
            
            # Parse user agent using user-agents library
            user_agent_string = user_data.get('user_agent', '')
            user_agent = parse(user_agent_string)
            
            # Determine device type with more detailed logging
            device_type = 'Other'
            try:
                if user_agent.is_mobile:
                    device_type = 'Mobile'
                elif user_agent.is_tablet:
                    device_type = 'Tablet'
                elif user_agent.is_pc:
                    device_type = 'Desktop'
                logger.debug(f"Detected device type: {device_type} for user agent: {user_agent_string}")
            except Exception as e:
                logger.error(f"Error detecting device type: {e}")
            
            # Create device info
            device = UserDevice(
                device_type=device_type,
                os=f"{user_agent.os.family} {user_agent.os.version_string}",
                browser=f"{user_agent.browser.family} {user_agent.browser.version_string}",
                screen_resolution=user_data.get('screen_resolution', 'unknown'),
                language=user_data.get('language', 'unknown'),
                user_agent=user_agent_string
            )

            # Create location info
            location = UserLocation(
                country=user_data.get('country', 'unknown'),
                region=user_data.get('region', 'unknown'),
                city=user_data.get('city', 'unknown'),
                ip_address=user_data.get('ip_address', 'unknown')
            )

            # Get campaign data
            campaign_data = self.db.get_campaign_data(short_code)
            if not campaign_data:
                campaign_data = {}  # Provide default empty dict if no campaign data

            # Create initial event
            initial_event = JourneyEvent(
                event_id=str(uuid.uuid4()),
                event_type=JourneyEventType.LINK_CLICK,
                timestamp=datetime.now(),
                session_id=session_id,
                device=device,
                location=location,
                campaign_data=campaign_data,
                custom_parameters=user_data.get('custom_parameters', {})
            )

            # Store journey start
            self._store_journey_event(initial_event)
            
            # Send to GA4
            self._send_ga4_event('journey_start', {
                'session_id': session_id,
                'short_code': short_code,
                'device_type': device.device_type,
                'country': location.country,
                'campaign_name': campaign_data.get('campaign_name', '')
            })
            
            return session_id

        except Exception as e:
            logger.error(f"Error starting journey tracking: {e}")
            raise

    def track_event(self, event_type: JourneyEventType, event_name: str, custom_params: Dict = None) -> bool:
        """Track a user journey event"""
        try:
            # Create default device and location info
            device_info = {
                'device_type': 'Unknown',
                'os': 'Unknown',
                'browser': 'Unknown',
                'screen_resolution': 'Unknown',
                'language': 'Unknown',
                'user_agent': 'Unknown'
            }
            
            location_info = {
                'country': 'Unknown',
                'region': 'Unknown',
                'city': 'Unknown',
                'ip_address': 'Unknown'
            }
            
            # Get session ID or create new one
            session_id = str(uuid.uuid4())
            
            # Create event data
            event_data = {
                'event_id': str(uuid.uuid4()),
                'event_type': event_type,
                'timestamp': datetime.now(),
                'session_id': session_id,
                'device_info': device_info,
                'location_info': location_info,
                'campaign_data': {},
                'custom_parameters': custom_params or {}
            }
            
            # Get last event if exists
            last_event = self.db.get_last_journey_event(session_id)
            if last_event:
                event_data['previous_event_id'] = last_event.get('event_id')
            
            # Record event
            success = self.db.record_journey_event(event_data)
            
            if success:
                logger.info(f"Event tracked successfully: {event_type.value} - {event_name}")
            else:
                logger.error(f"Failed to track event: {event_type.value} - {event_name}")
            
            return success
            
        except Exception as e:
            logger.error(f"Error tracking event: {str(e)}")
            return False

    def _store_journey_event(self, event: JourneyEvent):
        """Store journey event in database"""
        try:
            event_data = {
                'event_id': event.event_id,
                'event_type': event.event_type.value,
                'timestamp': event.timestamp.isoformat(),
                'session_id': event.session_id,
                'device': {
                    'device_type': event.device.device_type,
                    'os': event.device.os,
                    'browser': event.device.browser,
                    'screen_resolution': event.device.screen_resolution,
                    'language': event.device.language,
                    'user_agent': event.device.user_agent
                },
                'location': {
                    'country': event.location.country,
                    'region': event.location.region,
                    'city': event.location.city,
                    'ip_address': event.location.ip_address
                },
                'campaign_data': event.campaign_data,
                'custom_parameters': event.custom_parameters,
                'previous_event_id': event.previous_event_id
            }

            self.db.insert_journey_event(event_data)

        except Exception as e:
            logger.error(f"Error storing journey event: {e}")
            raise

    def _track_analytics_event(self, event: JourneyEvent):
        """Track event in analytics platforms"""
        try:
            # Send to GA4
            self._send_ga4_event(event.event_type.value, {
                'session_id': event.session_id,
                'device_category': event.device.device_type,
                'country': event.location.country,
                'campaign_name': event.campaign_data.get('campaign_name', ''),
                'custom_params': json.dumps(event.custom_parameters)
            })

        except Exception as e:
            logger.error(f"Error tracking analytics event: {e}")

    def get_journey_summary(self, session_id: str) -> Dict:
        """Get summary of a user journey"""
        try:
            events = self.db.get_journey_events(session_id)
            
            # Calculate journey metrics
            journey_duration = None
            if len(events) > 1:
                first_event = events[0]
                last_event = events[-1]
                journey_duration = (
                    datetime.fromisoformat(last_event['timestamp']) -
                    datetime.fromisoformat(first_event['timestamp'])
                ).total_seconds()

            return {
                'session_id': session_id,
                'start_time': events[0]['timestamp'],
                'end_time': events[-1]['timestamp'] if len(events) > 1 else None,
                'duration_seconds': journey_duration,
                'total_events': len(events),
                'events': events,
                'conversion_achieved': any(
                    e['event_type'] == JourneyEventType.CONVERSION.value 
                    for e in events
                )
            }

        except Exception as e:
            logger.error(f"Error getting journey summary: {e}")
            raise

    def analyze_journeys(self, start_date: datetime, end_date: datetime) -> Dict:
        """Analyze user journeys for a given time period"""
        try:
            journeys = self.db.get_journeys_in_period(start_date, end_date)
            
            analysis = {
                'total_journeys': len(journeys),
                'conversion_rate': 0,
                'avg_journey_duration': 0,
                'popular_paths': [],
                'device_distribution': {},
                'location_distribution': {},
                'campaign_performance': {}
            }

            for journey in journeys:
                # Calculate metrics
                if journey.get('conversion_achieved'):
                    analysis['conversion_rate'] += 1
                
                if journey.get('duration_seconds'):
                    analysis['avg_journey_duration'] += journey['duration_seconds']

                # Track path
                path = self._get_journey_path(journey['events'])
                analysis['popular_paths'].append(path)

                # Device and location stats
                first_event = journey['events'][0]
                device = first_event['device']['device_type']
                country = first_event['location']['country']
                campaign = first_event['campaign_data'].get('campaign_name')

                analysis['device_distribution'][device] = \
                    analysis['device_distribution'].get(device, 0) + 1
                analysis['location_distribution'][country] = \
                    analysis['location_distribution'].get(country, 0) + 1
                analysis['campaign_performance'][campaign] = \
                    analysis['campaign_performance'].get(campaign, 0) + 1

            # Calculate averages
            total_journeys = len(journeys)
            if total_journeys > 0:
                analysis['conversion_rate'] = (analysis['conversion_rate'] / total_journeys) * 100
                analysis['avg_journey_duration'] = analysis['avg_journey_duration'] / total_journeys

            return analysis

        except Exception as e:
            logger.error(f"Error analyzing journeys: {e}")
            raise

    def _get_journey_path(self, events: List[Dict]) -> List[str]:
        """Convert events to a journey path"""
        return [event['event_type'] for event in events]

    def _get_last_event(self, session_id: str) -> Optional[JourneyEvent]:
        """Get the last event for a session"""
        try:
            event_data = self.db.get_last_journey_event(session_id)
            if not event_data:
                return None

            return JourneyEvent(
                event_id=event_data['event_id'],
                event_type=JourneyEventType(event_data['event_type']),
                timestamp=datetime.fromisoformat(event_data['timestamp']),
                session_id=event_data['session_id'],
                device=UserDevice(**event_data['device']),
                location=UserLocation(**event_data['location']),
                campaign_data=event_data['campaign_data'],
                custom_parameters=event_data['custom_parameters'],
                previous_event_id=event_data.get('previous_event_id')
            )

        except Exception as e:
            logger.error(f"Error getting last event: {e}")
            raise 

    def track_funnel_progression(self, session_id: str, funnel_name: str):
        """Track user progression through a defined funnel"""
        try:
            events = self.db.get_journey_events(session_id)
            funnel_stages = self.db.get_funnel_stages(funnel_name)
            
            current_stage = None
            for stage in funnel_stages:
                matching_events = [e for e in events if e['event_type'] == stage['event_type']]
                if not matching_events:
                    break
                current_stage = stage
            
            if current_stage:
                self.track_event(
                    session_id,
                    JourneyEventType.FUNNEL_PROGRESS,
                    {
                        'funnel_name': funnel_name,
                        'current_stage': current_stage['name'],
                        'stage_number': current_stage['order']
                    }
                )
                
            return current_stage

        except Exception as e:
            logger.error(f"Error tracking funnel progression: {e}")
            raise

    def detect_journey_anomalies(self, session_id: str) -> List[Dict]:
        """Detect anomalies in user journey"""
        try:
            events = self.db.get_journey_events(session_id)
            anomalies = []
            
            # Check for time gaps
            for i in range(1, len(events)):
                time_gap = (
                    datetime.fromisoformat(events[i]['timestamp']) -
                    datetime.fromisoformat(events[i-1]['timestamp'])
                ).total_seconds()
                
                if time_gap > 1800:  # 30 minutes
                    anomalies.append({
                        'type': 'time_gap',
                        'details': f'Large time gap ({time_gap}s) between events',
                        'events': [events[i-1]['event_id'], events[i]['event_id']]
                    })
            
            # Check for unusual patterns
            device_changes = len(set(e['device']['device_type'] for e in events))
            if device_changes > 1:
                anomalies.append({
                    'type': 'device_switch',
                    'details': 'Multiple devices used in single session'
                })
            
            return anomalies

        except Exception as e:
            logger.error(f"Error detecting journey anomalies: {e}")
            raise

    def generate_journey_recommendations(self, session_id: str) -> List[Dict]:
        """Generate recommendations based on user journey"""
        try:
            events = self.db.get_journey_events(session_id)
            recommendations = []
            
            # Analyze journey patterns
            event_types = [e['event_type'] for e in events]
            
            # Check for missing engagement events
            if JourneyEventType.APP_OPEN.value in event_types and \
               JourneyEventType.APP_ENGAGEMENT.value not in event_types:
                recommendations.append({
                    'type': 'engagement',
                    'priority': 'high',
                    'message': 'Consider adding in-app engagement features'
                })
            
            # Check conversion opportunity
            if len(events) > 3 and JourneyEventType.CONVERSION.value not in event_types:
                recommendations.append({
                    'type': 'conversion',
                    'priority': 'medium',
                    'message': 'User showing interest but no conversion'
                })
            
            return recommendations

        except Exception as e:
            logger.error(f"Error generating recommendations: {e}")
            raise

    def calculate_journey_metrics(self, session_id: str) -> Dict:
        """Calculate detailed metrics for a journey"""
        try:
            events = self.db.get_journey_events(session_id)
            
            metrics = {
                'total_duration': 0,
                'engagement_score': 0,
                'conversion_probability': 0,
                'stage_durations': {},
                'interaction_depth': len(events),
                'platform_switches': 0
            }
            
            if len(events) > 1:
                # Calculate total duration
                start_time = datetime.fromisoformat(events[0]['timestamp'])
                end_time = datetime.fromisoformat(events[-1]['timestamp'])
                metrics['total_duration'] = (end_time - start_time).total_seconds()
                
                # Calculate engagement score
                engagement_weights = {
                    JourneyEventType.PAGE_VIEW.value: 1,
                    JourneyEventType.APP_ENGAGEMENT.value: 2,
                    JourneyEventType.CONVERSION.value: 5
                }
                
                metrics['engagement_score'] = sum(
                    engagement_weights.get(e['event_type'], 0) for e in events
                )
                
                # Calculate conversion probability
                conversion_indicators = [
                    JourneyEventType.APP_ENGAGEMENT.value,
                    JourneyEventType.DEEP_LINK.value
                ]
                indicator_count = sum(
                    1 for e in events if e['event_type'] in conversion_indicators
                )
                metrics['conversion_probability'] = min(
                    indicator_count / len(events) * 100, 
                    100
                )
            
            return metrics

        except Exception as e:
            logger.error(f"Error calculating journey metrics: {e}")
            raise 