"""
AliExpress API Client
Handles all interactions with the AliExpress Affiliate API using only App Key and App Secret
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
        self.base_url = 'https://gw.api.taobao.com/router/rest'
        
        # API Configuration
        self.target_currency = os.getenv('TARGET_CURRENCY', 'USD')
        self.target_language = os.getenv('TARGET_LANGUAGE', 'EN')
        self.ship_to_country = os.getenv('SHIP_TO_COUNTRY', 'DZ')
        
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
    
    async def search_products_by_keywords(self, keywords: str, page_size: int = 1) -> Optional[Dict[str, Any]]:
        """Search for products using keywords (public API)"""
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
                result = response['aliexpress_affiliate_product_query_response']['result']
                return result
            
            return None
            
        except Exception as e:
            logger.error(f"Error searching products: {e}")
            return None
    
    async def get_product_by_id(self, product_id: str) -> Optional[Dict[str, Any]]:
        """Get product information by searching with product ID"""
        try:
            # Use the product ID as keywords to find the specific product
            search_result = await self.search_products_by_keywords(product_id, page_size=20)
            
            if not search_result or not search_result.get('products'):
                return None
            
            # Look for exact product ID match
            products = search_result['products']
            for product in products:
                if str(product.get('product_id')) == str(product_id):
                    return product
            
            # If no exact match, return the first result (might be related)
            return products[0] if products else None
            
        except Exception as e:
            logger.error(f"Error getting product by ID: {e}")
            return None
    
    async def get_hot_products(self, category_ids: str = None, page_size: int = 10) -> Optional[Dict[str, Any]]:
        """Get hot products (public API)"""
        try:
            params = {
                'page_size': page_size,
                'target_currency': self.target_currency,
                'target_language': self.target_language,
                'ship_to_country': self.ship_to_country
            }
            
            if category_ids:
                params['category_ids'] = category_ids
            
            response = await self._make_api_request(
                'aliexpress.affiliate.hotproduct.query',
                params
            )
            
            if response and 'aliexpress_affiliate_hotproduct_query_response' in response:
                result = response['aliexpress_affiliate_hotproduct_query_response']['result']
                return result
            
            return None
            
        except Exception as e:
            logger.error(f"Error getting hot products: {e}")
            return None
    
    async def get_product_details(self, product_id: str, sku_id: str = None) -> Optional[Dict[str, Any]]:
        """Get detailed product information using public APIs"""
        try:
            # First try to get product by direct search
            product_data = await self.get_product_by_id(product_id)
            
            if not product_data:
                # If direct search fails, try searching with partial ID or related terms
                # Extract last 8 digits of product ID for search
                search_term = product_id[-8:] if len(product_id) > 8 else product_id
                search_result = await self.search_products_by_keywords(search_term, page_size=5)
                
                if search_result and search_result.get('products'):
                    # Return the first result as a fallback
                    product_data = search_result['products'][0]
                else:
                    return None
            
            return product_data
            
        except Exception as e:
            logger.error(f"Error getting product details: {e}")
            return None
    
    async def get_shipping_info(self, product_id: str) -> Optional[Dict[str, Any]]:
        """Get shipping information (simplified)"""
        try:
            # Since we can't access detailed shipping APIs without auth,
            # we'll return basic shipping info based on the product data
            return {
                'estimated_delivery': '15-30 days',
                'shipping_method': 'Standard Shipping',
                'destination': self.ship_to_country,
                'note': 'Shipping times may vary'
            }
            
        except Exception as e:
            logger.error(f"Error getting shipping info: {e}")
            return None
    
    def calculate_total_price(self, base_price: float, shipping_cost: float = 0) -> Dict[str, float]:
        """Calculate total price including shipping and estimated taxes"""
        # Estimated shipping cost for Algeria (if not provided)
        if shipping_cost == 0:
            if base_price < 10:
                shipping_cost = 2.99
            elif base_price < 50:
                shipping_cost = 5.99
            else:
                shipping_cost = 9.99
        
        subtotal = base_price + shipping_cost
        # Estimated tax rate for Algeria
        tax_rate = 0.19  # 19% VAT
        tax_amount = subtotal * tax_rate
        total = subtotal + tax_amount
        
        return {
            'base_price': base_price,
            'shipping_cost': shipping_cost,
            'subtotal': subtotal,
            'tax_amount': tax_amount,
            'total': total
        }