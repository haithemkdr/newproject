"""
AliExpress Link Parser
Handles parsing and extraction of product information from AliExpress URLs
"""

import re
import logging
from urllib.parse import urlparse, parse_qs
from typing import Optional, Dict

logger = logging.getLogger(__name__)

class AliExpressLinkParser:
    def __init__(self):
        # Regex patterns for different AliExpress URL formats
        self.patterns = {
            # Standard desktop URLs
            'desktop': re.compile(r'(?:https?://)?(?:www\.)?aliexpress\.com/item/([^/]+)/(\d+)\.html'),
            'desktop_alt': re.compile(r'(?:https?://)?(?:www\.)?aliexpress\.com/item/(\d+)\.html'),
            
            # Mobile URLs
            'mobile': re.compile(r'(?:https?://)?(?:m\.)?aliexpress\.com/item/(\d+)\.html'),
            
            # Short URLs
            'short': re.compile(r'(?:https?://)?a\.aliexpress\.com/_([a-zA-Z0-9]+)'),
            
            # App URLs
            'app': re.compile(r'(?:https?://)?(?:www\.)?aliexpress\.com/item/([^/\?]+)'),
            
            # Store item URLs
            'store': re.compile(r'(?:https?://)?(?:www\.)?aliexpress\.com/store/product/[^/]+/(\d+)_(\d+)\.html'),
        }
        
        self.aliexpress_domains = [
            'aliexpress.com',
            'www.aliexpress.com',
            'm.aliexpress.com',
            'a.aliexpress.com'
        ]
    
    def is_aliexpress_url(self, url: str) -> bool:
        """Check if the URL is from AliExpress"""
        try:
            parsed = urlparse(url)
            domain = parsed.netloc.lower()
            
            # Remove 'www.' prefix if present
            if domain.startswith('www.'):
                domain = domain[4:]
            
            return domain in ['aliexpress.com', 'm.aliexpress.com', 'a.aliexpress.com']
        except Exception as e:
            logger.error(f"Error checking URL domain: {e}")
            return False
    
    def parse_url(self, url: str) -> Optional[Dict[str, str]]:
        """
        Parse AliExpress URL and extract product information
        Returns dict with product_id and optionally sku_id
        """
        if not self.is_aliexpress_url(url):
            return None
        
        try:
            # Normalize URL
            if not url.startswith(('http://', 'https://')):
                url = 'https://' + url
            
            # Try different patterns
            product_info = None
            
            # Desktop pattern with product name and ID
            match = self.patterns['desktop'].search(url)
            if match:
                product_info = {
                    'product_id': match.group(2),
                    'product_name_slug': match.group(1)
                }
            
            # Desktop alternative pattern
            if not product_info:
                match = self.patterns['desktop_alt'].search(url)
                if match:
                    product_info = {
                        'product_id': match.group(1)
                    }
            
            # Mobile pattern
            if not product_info:
                match = self.patterns['mobile'].search(url)
                if match:
                    product_info = {
                        'product_id': match.group(1)
                    }
            
            # Store pattern
            if not product_info:
                match = self.patterns['store'].search(url)
                if match:
                    product_info = {
                        'product_id': match.group(2),
                        'store_id': match.group(1)
                    }
            
            # Short URL pattern (requires expansion)
            if not product_info:
                match = self.patterns['short'].search(url)
                if match:
                    # For short URLs, we'll need to follow redirects
                    # This is a simplified approach
                    product_info = {
                        'short_code': match.group(1),
                        'needs_expansion': True
                    }
            
            # Extract SKU ID from query parameters if present
            if product_info:
                parsed_url = urlparse(url)
                query_params = parse_qs(parsed_url.query)
                
                # Common SKU parameter names
                sku_params = ['sku', 'skuId', 'sku_id', 'variation']
                for param in sku_params:
                    if param in query_params:
                        product_info['sku_id'] = query_params[param][0]
                        break
                
                # Extract other useful parameters
                if 'spm' in query_params:
                    product_info['spm'] = query_params['spm'][0]
                
                if 'scm' in query_params:
                    product_info['scm'] = query_params['scm'][0]
            
            if product_info:
                logger.info(f"Successfully parsed URL: {product_info}")
                return product_info
            else:
                logger.warning(f"Could not parse AliExpress URL: {url}")
                return None
                
        except Exception as e:
            logger.error(f"Error parsing URL {url}: {e}")
            return None
    
    def extract_product_id_from_redirect(self, url: str) -> Optional[str]:
        """
        Extract product ID by following redirects for short URLs
        This is a placeholder - in production, you'd use aiohttp to follow redirects
        """
        # This would require making HTTP requests to follow redirects
        # For now, return None and let the calling code handle it
        logger.warning(f"Redirect following not implemented for URL: {url}")
        return None
    
    def validate_product_id(self, product_id: str) -> bool:
        """Validate that the product ID is in the correct format"""
        try:
            # AliExpress product IDs are typically numeric and quite long
            return product_id.isdigit() and len(product_id) >= 8
        except:
            return False
    
    def clean_url(self, url: str) -> str:
        """Clean and normalize AliExpress URL"""
        try:
            # Remove tracking parameters
            tracking_params = [
                'spm', 'scm', '_t', 'algo_pvid', 'algo_expid', 'btsid',
                'ws_ab_test', 'pvid', 'ptl', 'utm_source', 'utm_medium',
                'utm_campaign', 'utm_content', 'utm_term'
            ]
            
            parsed = urlparse(url)
            query_params = parse_qs(parsed.query)
            
            # Remove tracking parameters
            cleaned_params = {k: v for k, v in query_params.items() 
                            if k not in tracking_params}
            
            # Reconstruct URL
            if cleaned_params:
                query_string = '&'.join([f"{k}={v[0]}" for k, v in cleaned_params.items()])
                cleaned_url = f"{parsed.scheme}://{parsed.netloc}{parsed.path}?{query_string}"
            else:
                cleaned_url = f"{parsed.scheme}://{parsed.netloc}{parsed.path}"
            
            return cleaned_url
            
        except Exception as e:
            logger.error(f"Error cleaning URL: {e}")
            return url