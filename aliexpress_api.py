"""
AliExpress API Client
Handles all interactions with the AliExpress Affiliate API
"""

import os
import logging
import hashlib
import time
import json
from typing import Optional, Dict, Any
import aiohttp
import asyncio

logger = logging.getLogger(__name__)

class AliExpressAPI:
    def __init__(self):
        self.app_key = os.getenv('ALIEXPRESS_APP_KEY')
        self.app_secret = os.getenv('ALIEXPRESS_APP_SECRET')
        self.base_url = os.getenv('ALIEXPRESS_API_BASE_URL', 'https://api.aliexpress.com/sync')
        
        # API Configuration
        self.target_currency = os.getenv('TARGET_CURRENCY', 'USD')
        self.target_language = os.getenv('TARGET_LANGUAGE', 'AR')
        self.ship_to_country = os.getenv('SHIP_TO_COUNTRY', 'DZ')
        self.tax_rate = float(os.getenv('TAX_RATE', '0.1'))
        
        self.session = None
    
    async def _get_session(self):
        """Get or create aiohttp session"""
        if self.session is None or self.session.closed:
            timeout = aiohttp.ClientTimeout(total=30)
            self.session = aiohttp.ClientSession(timeout=timeout)
        return self.session
    
    async def close(self):
        """Close the aiohttp session"""
        if self.session and not self.session.closed:
            await self.session.close()
    
    def _generate_signature(self, params: Dict[str, Any]) -> str:
        """Generate API signature for AliExpress API"""
        # Sort parameters by key
        sorted_params = sorted(params.items())
        
        # Create parameter string
        param_string = ''.join([f"{k}{v}" for k, v in sorted_params])
        
        # Add app secret at the beginning and end
        sign_string = f"{self.app_secret}{param_string}{self.app_secret}"
        
        # Generate MD5 hash
        signature = hashlib.md5(sign_string.encode('utf-8')).hexdigest().upper()
        
        return signature
    
    def _prepare_common_params(self, method: str) -> Dict[str, Any]:
        """Prepare common API parameters"""
        timestamp = str(int(time.time() * 1000))
        
        params = {
            'app_key': self.app_key,
            'method': method,
            'timestamp': timestamp,
            'format': 'json',
            'v': '2.0',
            'sign_method': 'md5',
            'target_currency': self.target_currency,
            'target_language': self.target_language,
            'ship_to_country': self.ship_to_country
        }
        
        return params
    
    async def _make_api_request(self, method: str, additional_params: Dict[str, Any] = None) -> Optional[Dict[str, Any]]:
        """Make API request to AliExpress"""
        try:
            # Prepare parameters
            params = self._prepare_common_params(method)
            
            if additional_params:
                params.update(additional_params)
            
            # Generate signature
            params['sign'] = self._generate_signature(params)
            
            # Make request
            session = await self._get_session()
            
            async with session.post(self.base_url, data=params) as response:
                if response.status == 200:
                    response_data = await response.json()
                    logger.info(f"API request successful: {method}")
                    return response_data
                else:
                    logger.error(f"API request failed with status {response.status}")
                    error_text = await response.text()
                    logger.error(f"Error response: {error_text}")
                    return None
                    
        except Exception as e:
            logger.error(f"Error making API request: {e}")
            return None
    
    async def get_product_details(self, product_id: str, sku_id: str = None) -> Optional[Dict[str, Any]]:
        """Get detailed product information"""
        try:
            # Prepare parameters for product query API
            params = {
                'fields': ','.join([
                    'title',
                    'sale_price', 
                    'discount_rate',
                    'evaluate_rate',
                    'target_sale_price',
                    'target_original_price',
                    'shop_info',
                    'promotion_link',
                    'images',
                    'product_id',
                    'commission_rate'
                ]),
                'keywords': product_id  # Search by product ID
            }
            
            # Call affiliate product query API
            response = await self._make_api_request(
                'aliexpress.affiliate.product.query',
                params
            )
            
            if response and 'aliexpress_affiliate_product_query_response' in response:
                result = response['aliexpress_affiliate_product_query_response']['result']
                if result and 'products' and len(result['products']) > 0:
                    return result['products'][0]  # Return first matching product
            
            return None
            
        except Exception as e:
            logger.error(f"Error getting product details: {e}")
            return None
    
    async def get_shipping_info(self, product_id: str) -> Optional[Dict[str, Any]]:
        """Get shipping information for the product"""
        try:
            params = {
                'product_id': product_id,
                'target_currency': self.target_currency,
                'country': self.ship_to_country,
                'fields': 'logistics'
            }
            
            response = await self._make_api_request(
                'aliexpress.affiliate.logistics.get',
                params
            )
            
            if response and 'aliexpress_affiliate_logistics_get_response' in response:
                return response['aliexpress_affiliate_logistics_get_response']['result']
            
            return None
            
        except Exception as e:
            logger.error(f"Error getting shipping info: {e}")
            return None
    
    def calculate_total_price(self, base_price: float, shipping_cost: float = 0) -> Dict[str, float]:
        """Calculate total price including shipping and taxes"""
        subtotal = base_price + shipping_cost
        tax_amount = subtotal * self.tax_rate
        total = subtotal + tax_amount
        
        return {
            'base_price': base_price,
            'shipping_cost': shipping_cost,
            'subtotal': subtotal,
            'tax_amount': tax_amount,
            'total': total
        }