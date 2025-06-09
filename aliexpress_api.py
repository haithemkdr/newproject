"""
AliExpress API Client
<<<<<<< HEAD
Handles all interactions with the AliExpress Affiliate API
=======

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

        self.access_token = os.getenv('ALIEXPRESS_ACCESS_TOKEN')
        self.base_url = os.getenv('ALIEXPRESS_API_BASE_URL', 'https://api.aliexpress.com/sync')
        self.sandbox = os.getenv('ALIEXPRESS_SANDBOX', 'false').lower() == 'true'
        
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
        

        if self.access_token:
            params['session'] = self.access_token
        


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
            # Prepare parameters for product detail API
            params = {
                'product_ids': product_id,
                'fields': 'product_id,product_title,product_main_image_url,product_video_url,ae_item_base_info_dto,ae_item_sku_info_dtos,ae_item_properties,logistics_info_dto,ae_multimedia_info_dto'
            }
            
            # Call product detail API
            response = await self._make_api_request(
                'aliexpress.affiliate.productdetail.get',
                params
            )
            
            if not response:
                return None
            
            # Parse response
            if 'aliexpress_affiliate_productdetail_get_response' in response:
                result = response['aliexpress_affiliate_productdetail_get_response']['result']
                
                if result.get('products'):
                    product_data = result['products'][0]
                    
                    # Get additional SKU details if SKU ID is provided
                    if sku_id:
                        sku_details = await self.get_sku_details(product_id, sku_id)
                        if sku_details:
                            product_data['sku_details'] = sku_details
                    
                    return product_data
            
            return None
            
        except Exception as e:
            logger.error(f"Error getting product details: {e}")
            return None
    
    async def get_sku_details(self, product_id: str, sku_id: str) -> Optional[Dict[str, Any]]:
        """Get SKU-specific details"""
        try:
            params = {
                'product_id': product_id,
                'sku_id': sku_id,
                'target_currency': self.target_currency,
                'target_language': self.target_language,
                'ship_to_country': self.ship_to_country
            }
            
            response = await self._make_api_request(
                'aliexpress.affiliate.product.sku.detail.get',
                params
            )
            
            if response and 'aliexpress_affiliate_product_sku_detail_get_response' in response:
                return response['aliexpress_affiliate_product_sku_detail_get_response']['result']
            
            return None
            
        except Exception as e:
            logger.error(f"Error getting SKU details: {e}")
            return None
    
    async def get_shipping_info(self, product_id: str) -> Optional[Dict[str, Any]]:
        """Get shipping information for the product"""
        try:
            params = {
                'product_id': product_id,
                'send_goods_country_code': 'CN',  # Most AliExpress products ship from China
                'target_country_code': self.ship_to_country,
                'target_currency': self.target_currency
            }
            
            response = await self._make_api_request(
                'aliexpress.affiliate.product.shipping.get',
                params
            )
            
            if response and 'aliexpress_affiliate_product_shipping_get_response' in response:
                return response['aliexpress_affiliate_product_shipping_get_response']['result']
            
            return None
            
        except Exception as e:
            logger.error(f"Error getting shipping info: {e}")
            return None
    
    async def search_products(self, keywords: str, page_size: int = 10) -> Optional[Dict[str, Any]]:
        """Search for products (optional method for future use)"""

        try:
            params = {
                'keywords': keywords,
                'page_size': page_size,
                'sort': 'default',
                'target_currency': self.target_currency,
                'target_language': self.target_language,
                'ship_to_country': self.ship_to_country
            }
            
            response = await self._make_api_request(
                'aliexpress.affiliate.product.query',
                params
            )
            
            if response and 'aliexpress_affiliate_product_query_response' in response:

                return response['aliexpress_affiliate_product_query_response']['result']

            
            return None
            
        except Exception as e:
            logger.error(f"Error searching products: {e}")
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