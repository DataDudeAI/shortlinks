Project Overview
The Campaign Dashboard is a Streamlit-based web application designed for URL shortening and campaign management. It includes features to help users create and manage campaigns with powerful analytics and insights.

Key Features
1. URL Shortening
Generate unique short URLs for campaigns.
Validate URLs to ensure proper format.
Manage short URLs with custom UTM parameters and QR code generation.
2. Campaign Management
Organize campaigns by name, type, and additional metadata.
Manage settings such as default UTM parameters and custom domains.
Provide options like link retargeting, A/B testing, and link expiry.
3. Dashboard Metrics
Display high-level metrics such as:
Active campaigns.
Total clicks.
Conversion rates.
ROI (Return on Investment).
Metrics are updated dynamically based on database queries.
4. Campaign Analytics
Filters for date ranges, campaign names, and traffic sources.
Visualizations using Plotly for:
Click distribution.
Traffic sources.
Key metrics such as average time on page and bounce rate.
5. User Interface
Modern, theme-aware UI (light/dark themes).
Tabs for Overview, Settings, and Analytics.
Tables to display campaigns with sorting, filtering, and search functionality.
6. Database Integration
Uses a database for persistent storage of:
Original URLs.
Short codes.
Click data and analytics.
Tracks metrics like total clicks and conversion rates.
7. Analytics Tracking
Captures user-agent, referrer, and screen resolution during redirection.
Adds these as query parameters to the redirected URL for advanced tracking.
Technologies Used
Programming Language: Python
Framework: Streamlit
Visualization: Plotly
Database: Custom Database module for data persistence.
UI Styling: load_ui_styles for dynamic themes.
Other Libraries:
validators for URL validation.
qrcode and PIL for QR code generation.
pandas for data manipulation.
random for short code generation.
Unique Selling Points
Comprehensive Campaign Management:
Combines URL shortening, analytics, and campaign management in one tool.
Ease of Use:
Streamlined interface with intuitive tabs for campaign creation, monitoring, and analysis.
Real-time Insights:
Interactive visualizations and metrics updates for informed decision-making.
Extensibility:
Modular design supports additional features like deep links, affiliate tracking, and retargeting.
Next Steps
