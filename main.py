#!/usr/bin/env python3
"""
AliExpress Telegram Bot for Algerian Shoppers
Main entry point for the application
"""

import asyncio
import logging
import os
from dotenv import load_dotenv
from telegram_bot import TelegramBot

# Configure logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

async def main():
    """Main function to start the Telegram bot"""
    
    # Load environment variables
    load_dotenv()
    
    # Validate required environment variables
    required_vars = [
        'TELEGRAM_BOT_TOKEN',
        'ALIEXPRESS_APP_KEY',
        'ALIEXPRESS_APP_SECRET'
    ]
    
    missing_vars = [var for var in required_vars if not os.getenv(var)]
    if missing_vars:
        logger.error(f"Missing required environment variables: {', '.join(missing_vars)}")
        logger.error("Please check your .env file and ensure all required variables are set.")
        logger.info("Required variables:")
        logger.info("- TELEGRAM_BOT_TOKEN: Get from @BotFather on Telegram")
        logger.info("- ALIEXPRESS_APP_KEY: Your AliExpress API app key")
        logger.info("- ALIEXPRESS_APP_SECRET: Your AliExpress API app secret")
        return
    
    # Initialize and start the bot
    try:
        bot = TelegramBot()
        logger.info("Starting Telegram Bot for AliExpress Product Information...")
        logger.info("Bot is configured to work without OAuth - using public API endpoints only")
        await bot.start()
    except Exception as e:
        logger.error(f"Failed to start bot: {e}")
        raise

if __name__ == '__main__':
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Bot stopped by user")
    except Exception as e:
        logger.error(f"Bot crashed with error: {e}")