import string
import random
import validators
import logging
from typing import Optional, Dict, Any
from urllib.parse import urlparse, parse_qs, urlencode
from datetime import datetime
import qrcode
from io import BytesIO

logger = logging.getLogger(__name__)

class LinkService:
    def __init__(self, database):
        """Initialize LinkService with database connection"""
        self.db = database
        
    def generate_short_code(self, length=6) -> str:
        """Generate a unique short code"""
        characters = string.ascii_letters + string.digits
        while True:
            code = ''.join(random.choice(characters) for _ in range(length))
            if not self.db.get_url_info(code):
                return code

    def create_short_url(self, url: str, campaign_name: str, campaign_type: str = None, utm_params: dict = None) -> str:
        """Create a new short URL"""
        try:
            # Validate URL
            if not validators.url(url):
                raise ValueError("Invalid URL format")

            # Create short URL using database method
            short_code = self.db.create_short_url(
                url=url,
                campaign_name=campaign_name,
                campaign_type=campaign_type,
                utm_params=utm_params
            )
            
            logger.info(f"Created short URL for {url}: {short_code}")
            return short_code

        except Exception as e:
            logger.error(f"Error creating short URL: {str(e)}")
            raise

    def create_campaign_url(self, form_data: dict) -> Optional[str]:
        """Create a new campaign URL"""
        try:
            url = form_data['url']
            campaign_name = form_data['campaign_name']
            
            logger.info(f"Starting campaign creation process...")
            logger.info(f"URL: {url}")
            logger.info(f"Campaign Name: {campaign_name}")
            
            # Clean and validate URL
            if not url.startswith(('http://', 'https://')):
                url = 'https://' + url
                logger.info(f"Modified URL: {url}")

            # Generate short code
            short_code = form_data.get('custom_code') or self.generate_short_code()
            logger.info(f"Generated short code: {short_code}")
            
            # Prepare UTM parameters
            utm_params = {
                'utm_source': form_data.get('utm_source'),
                'utm_medium': form_data.get('utm_medium'),
                'utm_campaign': form_data.get('utm_campaign'),
                'utm_content': form_data.get('utm_content'),
                'utm_term': form_data.get('utm_term')
            }
            
            # Filter out empty UTM parameters
            utm_params = {k: v for k, v in utm_params.items() if v}
            logger.info(f"UTM parameters: {utm_params}")
            
            # Add UTM parameters to URL if any exist
            if utm_params:
                parsed_url = urlparse(url)
                existing_params = parse_qs(parsed_url.query)
                all_params = {**existing_params, **utm_params}
                new_query = urlencode(all_params, doseq=True)
                url = parsed_url._replace(query=new_query).geturl()
                logger.info(f"Final URL with UTM parameters: {url}")
            
            # Save to database
            logger.info("Attempting to save to database...")
            success = self.db.save_campaign_url(
                url=url,
                short_code=short_code,
                campaign_name=campaign_name,
                campaign_type=form_data.get('campaign_type'),
                utm_params=utm_params
            )
            
            if success:
                logger.info(f"Successfully created campaign '{campaign_name}' with short code: {short_code}")
                return short_code
            else:
                logger.error("Database save operation failed")
                return None
            
        except Exception as e:
            logger.error(f"Error creating campaign URL: {str(e)}", exc_info=True)
            return None

    def generate_qr_code(self, url: str) -> BytesIO:
        """Generate QR code for a URL"""
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=10,
            border=4,
        )
        qr.add_data(url)
        qr.make(fit=True)

        img = qr.make_image(fill_color="black", back_color="white")
        img_bytes = BytesIO()
        img.save(img_bytes, format='PNG')
        img_bytes.seek(0)
        return img_bytes 