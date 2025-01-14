# Google Analytics 4 Monitoring Guide

## Real-time Monitoring
1. Login to GA4: https://analytics.google.com
2. Select your property
3. Go to Reports > Realtime

## Key Metrics to Monitor
1. Active Users
   - Path: Reports > Realtime > Overview
   - Check: Current active users

2. Event Tracking
   - Path: Reports > Engagement > Events
   - Monitor:
     * page_view
     * campaign_created
     * link_click
     * conversion

3. User Journey
   - Path: Reports > User > User acquisition
   - Check: Traffic sources and user paths

4. Campaign Performance
   - Path: Reports > Acquisition > Traffic acquisition
   - Filter by campaign names

## Custom Reports
1. Create Campaign Dashboard
   - Go to: Customization > Custom Reports
   - Add metrics:
     * Campaign clicks
     * Unique visitors
     * Conversion rate
     * Engagement time

2. User Journey Analysis
   - Go to: Explore
   - Create funnel visualization
   - Add steps:
     1. Page view
     2. Campaign creation
     3. Link click
     4. Conversion

## Debugging
1. Enable Debug Mode
   - Go to: Admin > DebugView
   - Check real-time events

2. Error Tracking
   - Monitor server logs
   - Check GA4 Debug events
   - Verify event parameters

## Best Practices
1. Regular Monitoring
   - Check real-time data daily
   - Review full reports weekly
   - Analyze trends monthly

2. Data Quality
   - Verify event tracking
   - Check for missing data
   - Monitor bounce rates

3. Optimization
   - Analyze user paths
   - Identify drop-off points
   - Optimize conversion funnel 