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
            'category_section': "📂 **الفئة:**\n",
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
            price_info = self._format_price_section(product_data)
            if price_info:
                formatted_parts.append(price_info)
            
            # Rating and reviews
            rating_info = self._format_rating_section(product_data)
            if rating_info:
                formatted_parts.append(rating_info)
            
            # Category information
            category_info = self._format_category_section(product_data)
            if category_info:
                formatted_parts.append(category_info)
            
            # Seller information
            seller_info = self._format_seller_section(product_data)
            if seller_info:
                formatted_parts.append(seller_info)
            
            # Shipping information
            shipping_info = self._format_shipping_section(shipping_data)
            if shipping_info:
                formatted_parts.append(shipping_info)
            
            # Product URL
            product_url = self._get_product_url(product_data)
            if product_url:
                formatted_parts.append(f"🔗 **رابط المنتج:** [اضغط هنا للشراء]({product_url})\n\n")
            
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
    
    def _get_product_url(self, product_data: Dict[str, Any]) -> str:
        """Extract product URL"""
        try:
            return product_data.get('product_detail_url', '')
        except:
            return ''
    
    def _format_price_section(self, product_data: Dict[str, Any]) -> str:
        """Format price information section"""
        try:
            price_section = self.templates['price_section']
            
            # Get price info
            original_price = product_data.get('original_price')
            sale_price = product_data.get('sale_price')
            
            if original_price:
                price_section += f"• السعر الأصلي: ${original_price}\n"
            
            if sale_price:
                price_section += f"• سعر البيع: **${sale_price}**\n"
                
                # Calculate discount if both prices available
                if original_price and float(original_price) > float(sale_price):
                    discount = ((float(original_price) - float(sale_price)) / float(original_price)) * 100
                    price_section += f"• الخصم: {discount:.0f}%\n"
            
            # Add estimated shipping and total
            base_price = float(sale_price or original_price or 0)
            if base_price > 0:
                if base_price < 10:
                    shipping = 2.99
                elif base_price < 50:
                    shipping = 5.99
                else:
                    shipping = 9.99
                
                price_section += f"• تكلفة الشحن المقدرة: ${shipping:.2f}\n"
                
                subtotal = base_price + shipping
                tax = subtotal * 0.19  # 19% VAT estimate
                total = subtotal + tax
                
                price_section += f"• الضرائب المقدرة (19%): ${tax:.2f}\n"
                price_section += f"• **المجموع الكلي المقدر: ${total:.2f}**\n"
            
            price_section += "\n"
            return price_section
            
        except Exception as e:
            logger.error(f"Error formatting price section: {e}")
            return ""
    
    def _format_rating_section(self, product_data: Dict[str, Any]) -> str:
        """Format rating and review information"""
        try:
            evaluate_rate = product_data.get('evaluate_rate')
            
            if not evaluate_rate:
                return ""
            
            rating_section = self.templates['rating_section']
            
            try:
                rating_value = float(evaluate_rate.rstrip('%'))
                stars = "⭐" * min(5, max(1, int(rating_value / 20)))  # Convert percentage to 5-star scale
                rating_section += f"• التقييم: {stars} ({evaluate_rate})\n"
            except:
                rating_section += f"• التقييم: {evaluate_rate}\n"
            
            rating_section += "\n"
            return rating_section
            
        except Exception as e:
            logger.error(f"Error formatting rating section: {e}")
            return ""
    
    def _format_category_section(self, product_data: Dict[str, Any]) -> str:
        """Format category information"""
        try:
            first_level_category_name = product_data.get('first_level_category_name')
            second_level_category_name = product_data.get('second_level_category_name')
            
            if not first_level_category_name and not second_level_category_name:
                return ""
            
            category_section = self.templates['category_section']
            
            if first_level_category_name:
                category_section += f"• الفئة الرئيسية: {first_level_category_name}\n"
            
            if second_level_category_name:
                category_section += f"• الفئة الفرعية: {second_level_category_name}\n"
            
            category_section += "\n"
            return category_section
            
        except Exception as e:
            logger.error(f"Error formatting category section: {e}")
            return ""
    
    def _format_seller_section(self, product_data: Dict[str, Any]) -> str:
        """Format seller information"""
        try:
            shop_id = product_data.get('shop_id')
            shop_url = product_data.get('shop_url')
            
            if not shop_id and not shop_url:
                return ""
            
            seller_section = self.templates['seller_section']
            
            if shop_id:
                seller_section += f"• معرف المتجر: {shop_id}\n"
            
            if shop_url:
                seller_section += f"• [زيارة المتجر]({shop_url})\n"
            
            seller_section += "\n"
            return seller_section
            
        except Exception as e:
            logger.error(f"Error formatting seller section: {e}")
            return ""
    
    def _format_shipping_section(self, shipping_data: Dict[str, Any]) -> str:
        """Format shipping information"""
        try:
            if not shipping_data:
                shipping_data = {
                    'estimated_delivery': '15-30 يوم',
                    'shipping_method': 'الشحن العادي',
                    'destination': 'الجزائر'
                }
            
            shipping_section = self.templates['shipping_section']
            
            if 'estimated_delivery' in shipping_data:
                shipping_section += f"• مدة التوصيل المقدرة: {shipping_data['estimated_delivery']}\n"
            
            if 'shipping_method' in shipping_data:
                shipping_section += f"• طريقة الشحن: {shipping_data['shipping_method']}\n"
            
            if 'destination' in shipping_data:
                shipping_section += f"• الوجهة: {shipping_data['destination']}\n"
            
            shipping_section += "• ملاحظة: أوقات الشحن قد تختلف حسب الموقع والظروف\n"
            shipping_section += "\n"
            return shipping_section
            
        except Exception as e:
            logger.error(f"Error formatting shipping section: {e}")
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