#!/usr/bin/env python3
"""
AliExpress Telegram Bot for Algerian Shoppers
Main entry point for the application
"""

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

def main():
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
        return
    
    # Initialize and start the bot
    try:
        bot = TelegramBot()
        logger.info("Starting Telegram Bot for AliExpress Product Information...")
        bot.start()
    except KeyboardInterrupt:
        logger.info("Bot stopped by user")
    except Exception as e:
        logger.error(f"Failed to start bot: {e}")
        raise

if __name__ == '__main__':
    main()