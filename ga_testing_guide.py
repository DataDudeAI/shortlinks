"""
Google Analytics Testing Guide

1. Local Development Testing:
   - Run: streamlit run app.py
   - Check browser console for GA initialization
   - Verify events in GA4 DebugView
   
2. Event Verification:
   - Dashboard View: page_view
   - Campaign Creation: conversion
   - Link Clicks: link_click
   - User Journey: funnel_progress

3. GA4 Dashboard Setup:
   1. Login to Google Analytics
   2. Go to: Admin > Property > Data Streams
   3. Select your web stream
   4. Copy measurement ID (G-XXXXXXXX)
   5. Enable DebugView for testing

4. Custom Reports:
   - Realtime > Events
   - Engagement > Events
   - Monetization > E-commerce purchases
   - User > Demographics

5. Debugging:
   - Check .env file configuration
   - Verify GA initialization in console
   - Monitor server logs for errors
   - Use GA4 DebugView mode
"""

# Test GA4 connection
def test_ga_connection():
    import os
    from dotenv import load_dotenv
    from google.analytics.data_v1beta import BetaAnalyticsDataClient
    
    load_dotenv()
    
    try:
        client = BetaAnalyticsDataClient()
        property_id = os.getenv('GA_PROPERTY_ID')
        print(f"✅ GA4 Client initialized")
        print(f"✅ Property ID: {property_id}")
        return True
    except Exception as e:
        print(f"❌ GA4 Error: {str(e)}")
        return False

if __name__ == "__main__":
    test_ga_connection() 