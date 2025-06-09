"""
Telegram Bot Implementation
Handles all Telegram bot interactions and message processing
"""

import logging
import asyncio
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
from telegram.constants import ParseMode
import os

from link_parser import AliExpressLinkParser
from aliexpress_api import AliExpressAPI
from formatter import ArabicFormatter

logger = logging.getLogger(__name__)

class TelegramBot:
    def __init__(self):
        self.token = os.getenv('TELEGRAM_BOT_TOKEN')
        self.link_parser = AliExpressLinkParser()
        self.api = AliExpressAPI()
        self.formatter = ArabicFormatter()
        self.application = None
        
    async def start(self):
        """Start the Telegram bot"""
        # Create application
        self.application = Application.builder().token(self.token).build()
        
        # Add handlers
        self.application.add_handler(CommandHandler("start", self.start_command))
        self.application.add_handler(CommandHandler("help", self.help_command))
        self.application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, self.handle_message))
        
        # Start polling
        await self.application.initialize()
        await self.application.start()
        await self.application.updater.start_polling()
        
        logger.info("Bot started successfully!")
        
        # Keep the bot running
        await asyncio.Event().wait()
    
    async def start_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /start command"""
        welcome_text = """
🛍️ **مرحباً بك في بوت معلومات منتجات علي إكسبريس!**

أرسل لي رابط أي منتج من علي إكسبريس وسأقوم بإرسال معلومات مفصلة عن المنتج باللغة العربية.

**الميزات:**
• معلومات المنتج مع الصور
• الأسعار بالدولار الأمريكي
• تكلفة الشحن إلى الجزائر
• تقييمات العملاء
• معلومات البائع
• المتغيرات المتاحة (الألوان، الأحجام)

ما عليك سوى إرسال رابط المنتج وسأتولى الباقي! 📦
        """
        
        await update.message.reply_text(
            welcome_text, 
            parse_mode=ParseMode.MARKDOWN
        )
    
    async def help_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /help command"""
        help_text = """
🔗 **كيفية استخدام البوت:**

1. انسخ رابط أي منتج من علي إكسبريس
2. ألصق الرابط في المحادثة
3. انتظر حتى أحضر لك المعلومات

**أمثلة على الروابط المدعومة:**
• https://www.aliexpress.com/item/...
• https://a.aliexpress.com/_mNvN...
• https://m.aliexpress.com/item/...

**ملاحظة:** 📋
• يتم عرض الأسعار بالدولار الأمريكي
• تكلفة الشحن محسوبة للجزائر
• المعلومات محدثة في الوقت الفعلي

إذا واجهت أي مشاكل، تأكد من أن الرابط صحيح ومن علي إكسبريس.
        """
        
        await update.message.reply_text(
            help_text,
            parse_mode=ParseMode.MARKDOWN
        )
    
    async def handle_message(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle incoming messages"""
        message_text = update.message.text.strip()
        
        # Check if message contains AliExpress URL
        if not self.link_parser.is_aliexpress_url(message_text):
            error_message = """
❌ **رابط غير صحيح**

يرجى إرسال رابط صحيح من علي إكسبريس.

**أمثلة على الروابط الصحيحة:**
• https://www.aliexpress.com/item/...
• https://a.aliexpress.com/_mNvN...
• https://m.aliexpress.com/item/...
            """
            await update.message.reply_text(
                error_message,
                parse_mode=ParseMode.MARKDOWN
            )
            return
        
        # Send processing message
        processing_message = await update.message.reply_text(
            "🔄 **جاري تحليل الرابط وجلب معلومات المنتج...**\nيرجى الانتظار قليلاً..."
        )
        
        try:
            # Parse the URL to extract product information
            product_info = self.link_parser.parse_url(message_text)
            
            if not product_info:
                await processing_message.edit_text(
                    "❌ **خطأ في تحليل الرابط**\nلم أتمكن من استخراج معرف المنتج من الرابط المرسل."
                )
                return
            
            # Fetch product details from AliExpress API
            product_data = await self.api.get_product_details(
                product_info['product_id'],
                product_info.get('sku_id')
            )
            
            if not product_data:
                await processing_message.edit_text(
                    "❌ **خطأ في جلب البيانات**\nلم أتمكن من الحصول على معلومات هذا المنتج. قد يكون المنتج غير متاح أو الرابط منتهي الصلاحية."
                )
                return
            
            # Get shipping information
            shipping_data = await self.api.get_shipping_info(
                product_info['product_id']
            )
            
            # Format the response in Arabic
            formatted_response = self.formatter.format_product_info(
                product_data, 
                shipping_data
            )
            
            # Check if message is too long for Telegram
            if len(formatted_response) > 4096:
                # Split message into chunks
                chunks = self.formatter.split_message(formatted_response)
                
                await processing_message.delete()
                
                for i, chunk in enumerate(chunks):
                    if i == 0:
                        await update.message.reply_text(
                            chunk,
                            parse_mode=ParseMode.MARKDOWN,
                            disable_web_page_preview=False
                        )
                    else:
                        await update.message.reply_text(
                            chunk,
                            parse_mode=ParseMode.MARKDOWN,
                            disable_web_page_preview=True
                        )
            else:
                await processing_message.edit_text(
                    formatted_response,
                    parse_mode=ParseMode.MARKDOWN,
                    disable_web_page_preview=False
                )
                
        except Exception as e:
            logger.error(f"Error processing message: {e}")
            await processing_message.edit_text(
                f"❌ **خطأ في المعالجة**\nحدث خطأ أثناء معالجة طلبك: {str(e)}\n\nيرجى المحاولة مرة أخرى أو التحقق من صحة الرابط."
            )
    
    async def stop(self):
        """Stop the bot gracefully"""
        if self.application:
            await self.application.stop()
            await self.application.shutdown()
            logger.info("Bot stopped successfully!")