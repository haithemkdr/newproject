"""
Arabic Formatter
Handles formatting of product information in Arabic for Telegram messages
"""

import logging
from typing import Dict, Any, List
import re

logger = logging.getLogger(__name__)

class ArabicFormatter:
    def __init__(self):
        self.max_message_length = 4096  # Telegram message limit
        
        # Arabic text templates
        self.templates = {
            'product_header': "🛍️ **{title}**\n\n",
            'price_section': "💰 **الأسعار:**\n",
            'shipping_section': "🚚 **معلومات الشحن:**\n",
            'rating_section': "⭐ **التقييمات:**\n",
            'seller_section': "🏪 **معلومات البائع:**\n",
            'variants_section': "🎨 **المتغيرات المتاحة:**\n",
            'description_section': "📋 **وصف المنتج:**\n"
        }
    
    def format_product_info(self, product_data: Dict[str, Any], shipping_data: Dict[str, Any] = None) -> str:
        """Format complete product information in Arabic"""
        try:
            formatted_parts = []
            
            # Product header with title and image
            title = self._get_product_title(product_data)
            formatted_parts.append(self.templates['product_header'].format(title=title))
            
            # Product image
            image_url = self._get_product_image(product_data)
            if image_url:
                formatted_parts.append(f"[📸 صورة المنتج]({image_url})\n\n")
            
            # Price information
            price_info = self._format_price_section(product_data, shipping_data)
            if price_info:
                formatted_parts.append(price_info)
            
            # Rating and reviews
            rating_info = self._format_rating_section(product_data)
            if rating_info:
                formatted_parts.append(rating_info)
            
            # Seller information
            seller_info = self._format_seller_section(product_data)
            if seller_info:
                formatted_parts.append(seller_info)
            
            # Shipping information
            shipping_info = self._format_shipping_section(shipping_data)
            if shipping_info:
                formatted_parts.append(shipping_info)
            
            # Product variants
            variants_info = self._format_variants_section(product_data)
            if variants_info:
                formatted_parts.append(variants_info)
            
            # Product description (truncated if too long)
            description = self._format_description_section(product_data)
            if description:
                formatted_parts.append(description)
            
            # Join all parts
            formatted_message = "".join(formatted_parts)
            
            # Add footer
            formatted_message += "\n📱 **تم إنشاؤه بواسطة بوت معلومات علي إكسبريس**"
            
            return formatted_message.strip()
            
        except Exception as e:
            logger.error(f"Error formatting product info: {e}")
            return "❌ حدث خطأ في تنسيق معلومات المنتج"
    
    def _get_product_title(self, product_data: Dict[str, Any]) -> str:
        """Extract and clean product title"""
        try:
            title = product_data.get('product_title', 'غير متاح')
            
            # Clean title - remove excessive special characters
            title = re.sub(r'[^\w\s\-\(\)\[\]،؛\.!؟]', '', title)
            
            # Truncate if too long
            if len(title) > 100:
                title = title[:97] + "..."
            
            return title
        except:
            return "غير متاح"
    
    def _get_product_image(self, product_data: Dict[str, Any]) -> str:
        """Extract product main image URL"""
        try:
            return product_data.get('product_main_image_url', '')
        except:
            return ''
    
    def _format_price_section(self, product_data: Dict[str, Any], shipping_data: Dict[str, Any] = None) -> str:
        """Format price information section"""
        try:
            price_section = self.templates['price_section']
            
            # Get base price info
            base_info = product_data.get('ae_item_base_info_dto', {})
            
            if 'original_price' in base_info:
                original_price = float(base_info['original_price'])
                price_section += f"• السعر الأصلي: ${original_price:.2f}\n"
            
            if 'sale_price' in base_info:
                sale_price = float(base_info['sale_price'])
                price_section += f"• سعر البيع: **${sale_price:.2f}**\n"
                
                # Calculate discount if both prices available
                if 'original_price' in base_info and original_price > sale_price:
                    discount = ((original_price - sale_price) / original_price) * 100
                    price_section += f"• الخصم: {discount:.0f}%\n"
            
            # Add shipping cost
            shipping_cost = self._get_shipping_cost(shipping_data)
            if shipping_cost > 0:
                price_section += f"• تكلفة الشحن: ${shipping_cost:.2f}\n"
            
            # Calculate total
            base_price = float(base_info.get('sale_price', base_info.get('original_price', 0)))
            if base_price > 0:
                total = base_price + shipping_cost
                price_section += f"• **المجموع الكلي: ${total:.2f}**\n"
            
            price_section += "\n"
            return price_section
            
        except Exception as e:
            logger.error(f"Error formatting price section: {e}")
            return ""
    
    def _get_shipping_cost(self, shipping_data: Dict[str, Any]) -> float:
        """Extract shipping cost from shipping data"""
        try:
            if not shipping_data:
                return 0.0
            
            shipping_info = shipping_data.get('aeop_freight_calculate_result_for_buyers_dto', {})
            
            if 'freight' in shipping_info:
                return float(shipping_info['freight'].get('cent', 0)) / 100
            
            return 0.0
        except:
            return 0.0
    
    def _format_rating_section(self, product_data: Dict[str, Any]) -> str:
        """Format rating and review information"""
        try:
            base_info = product_data.get('ae_item_base_info_dto', {})
            
            avg_rating = base_info.get('avg_evaluation_rating')
            review_count = base_info.get('evaluation_count')
            
            if not avg_rating and not review_count:
                return ""
            
            rating_section = self.templates['rating_section']
            
            if avg_rating:
                stars = "⭐" * int(float(avg_rating))
                rating_section += f"• التقييم: {stars} ({avg_rating}/5)\n"
            
            if review_count:
                rating_section += f"• عدد المراجعات: {review_count}\n"
            
            rating_section += "\n"
            return rating_section
            
        except Exception as e:
            logger.error(f"Error formatting rating section: {e}")
            return ""
    
    def _format_seller_section(self, product_data: Dict[str, Any]) -> str:
        """Format seller information"""
        try:
            base_info = product_data.get('ae_item_base_info_dto', {})
            
            seller_id = base_info.get('seller_id')
            shop_id = base_info.get('shop_id')
            
            if not seller_id and not shop_id:
                return ""
            
            seller_section = self.templates['seller_section']
            
            if seller_id:
                seller_section += f"• معرف البائع: {seller_id}\n"
            
            if shop_id:
                seller_section += f"• معرف المتجر: {shop_id}\n"
            
            seller_section += "\n"
            return seller_section
            
        except Exception as e:
            logger.error(f"Error formatting seller section: {e}")
            return ""
    
    def _format_shipping_section(self, shipping_data: Dict[str, Any]) -> str:
        """Format shipping information"""
        try:
            if not shipping_data:
                return ""
            
            shipping_section = self.templates['shipping_section']
            
            shipping_info = shipping_data.get('aeop_freight_calculate_result_for_buyers_dto', {})
            
            # Delivery time
            if 'delivery_day_max' in shipping_info and 'delivery_day_min' in shipping_info:
                min_days = shipping_info['delivery_day_min']
                max_days = shipping_info['delivery_day_max']
                shipping_section += f"• مدة التوصيل: {min_days}-{max_days} يوم\n"
            
            # Shipping method
            if 'service_name' in shipping_info:
                service_name = shipping_info['service_name']
                shipping_section += f"• طريقة الشحن: {service_name}\n"
            
            # Destination
            shipping_section += f"• الوجهة: الجزائر (DZ)\n"
            
            shipping_section += "\n"
            return shipping_section
            
        except Exception as e:
            logger.error(f"Error formatting shipping section: {e}")
            return ""
    
    def _format_variants_section(self, product_data: Dict[str, Any]) -> str:
        """Format product variants (colors, sizes, etc.)"""
        try:
            sku_info = product_data.get('ae_item_sku_info_dtos', [])
            
            if not sku_info:
                return ""
            
            variants_section = self.templates['variants_section']
            
            # Group variants by type
            variant_groups = {}
            
            for sku in sku_info:
                if 'ae_sku_property_dtos' in sku:
                    for prop in sku['ae_sku_property_dtos']:
                        prop_name = prop.get('sku_property_name', 'غير محدد')
                        prop_value = prop.get('property_value_definition_name', 'غير محدد')
                        
                        if prop_name not in variant_groups:
                            variant_groups[prop_name] = set()
                        
                        variant_groups[prop_name].add(prop_value)
            
            # Format variant groups
            for group_name, values in variant_groups.items():
                if len(values) > 0:
                    values_str = "، ".join(sorted(values))
                    variants_section += f"• {group_name}: {values_str}\n"
            
            if len(variant_groups) > 0:
                variants_section += "\n"
                return variants_section
            
            return ""
            
        except Exception as e:
            logger.error(f"Error formatting variants section: {e}")
            return ""
    
    def _format_description_section(self, product_data: Dict[str, Any]) -> str:
        """Format product description (truncated)"""
        try:
            # This would typically come from product details
            # For now, we'll use basic info
            base_info = product_data.get('ae_item_base_info_dto', {})
            
            # We could add more description formatting here
            # For now, just return empty as descriptions are usually too long
            return ""
            
        except Exception as e:
            logger.error(f"Error formatting description section: {e}")
            return ""
    
    def split_message(self, message: str) -> List[str]:
        """Split long message into multiple parts for Telegram"""
        if len(message) <= self.max_message_length:
            return [message]
        
        chunks = []
        current_chunk = ""
        
        lines = message.split('\n')
        
        for line in lines:
            # If adding this line would exceed the limit
            if len(current_chunk) + len(line) + 1 > self.max_message_length:
                if current_chunk:
                    chunks.append(current_chunk.strip())
                    current_chunk = line + '\n'
                else:
                    # Line itself is too long, force split
                    while len(line) > self.max_message_length:
                        chunks.append(line[:self.max_message_length])
                        line = line[self.max_message_length:]
                    current_chunk = line + '\n'
            else:
                current_chunk += line + '\n'
        
        if current_chunk.strip():
            chunks.append(current_chunk.strip())
        
        return chunks
    
    def format_error_message(self, error_type: str, details: str = "") -> str:
        """Format error messages in Arabic"""
        error_messages = {
            'invalid_url': "❌ **رابط غير صحيح**\nيرجى إرسال رابط صحيح من علي إكسبريس.",
            'product_not_found': "❌ **المنتج غير موجود**\nلم أتمكن من العثور على هذا المنتج. قد يكون غير متاح أو منتهي الصلاحية.",
            'api_error': "❌ **خطأ في الخدمة**\nحدث خطأ أثناء جلب معلومات المنتج. يرجى المحاولة مرة أخرى.",
            'network_error': "❌ **خطأ في الاتصال**\nتحقق من اتصالك بالإنترنت وحاول مرة أخرى.",
            'general_error': "❌ **خطأ عام**\nحدث خطأ غير متوقع. يرجى المحاولة مرة أخرى."
        }
        
        base_message = error_messages.get(error_type, error_messages['general_error'])
        
        if details:
            base_message += f"\n\n**تفاصيل الخطأ:** {details}"
        
        return base_message