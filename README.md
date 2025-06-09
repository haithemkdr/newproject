# AliExpress Telegram Bot for Algerian Shoppers

A comprehensive Telegram bot that processes AliExpress product links and provides detailed product information in Arabic, specifically designed for Algerian shoppers.

## Features

- 🔗 **URL Parsing**: Supports all AliExpress URL formats (desktop, mobile, short links)
- 🛍️ **Product Information**: Detailed product data including prices, images, and descriptions
- 💰 **Price Calculation**: Shows prices in USD with estimated shipping costs to Algeria
- 📦 **Shipping Details**: Estimated delivery time and shipping methods to Algeria
- ⭐ **Ratings & Reviews**: Customer ratings when available
- 🏪 **Seller Information**: Store and seller details
- 🇩🇿 **Arabic Support**: All responses in Arabic with RTL support
- ⚡ **Async Processing**: Fast, non-blocking message handling
- 🔓 **No OAuth Required**: Works with just App Key and App Secret

## Installation

1. **Clone the repository**:
   ```bash
   git clone <repository-url>
   cd aliexpress-telegram-bot
   ```

2. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Configure environment variables**:
   ```bash
   cp .env.example .env
   ```
   
   Edit `.env` and add your credentials:
   - `TELEGRAM_BOT_TOKEN`: Get from @BotFather on Telegram
   - `ALIEXPRESS_APP_KEY`: Your AliExpress API app key
   - `ALIEXPRESS_APP_SECRET`: Your AliExpress API app secret

4. **Run the bot**:
   ```bash
   python main.py
   ```

## Configuration

### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `TELEGRAM_BOT_TOKEN` | Telegram bot token from BotFather | Required |
| `ALIEXPRESS_APP_KEY` | AliExpress API application key | Required |
| `ALIEXPRESS_APP_SECRET` | AliExpress API application secret | Required |
| `TARGET_CURRENCY` | Currency for price display | USD |
| `TARGET_LANGUAGE` | Language for API responses | EN |
| `SHIP_TO_COUNTRY` | Shipping destination country code | DZ |

### API Configuration

The bot uses the following AliExpress Affiliate API endpoints (no OAuth required):
- `aliexpress.affiliate.product.query` - Product search
- `aliexpress.affiliate.hotproduct.query` - Hot products

**Note**: This bot uses public API endpoints that don't require user authorization. Some advanced features like detailed shipping calculations may have limited functionality compared to authenticated APIs.

## Usage

1. **Start the bot**: Send `/start` to get a welcome message
2. **Get help**: Send `/help` for usage instructions
3. **Send product links**: Simply paste any AliExpress product URL

### Supported URL Formats

- `https://www.aliexpress.com/item/...`
- `https://m.aliexpress.com/item/...`
- `https://a.aliexpress.com/_mNvN...`
- `https://aliexpress.com/store/product/...`

## Project Structure

```
├── main.py              # Application entry point
├── telegram_bot.py      # Telegram bot implementation
├── aliexpress_api.py    # AliExpress API client (no OAuth)
├── link_parser.py       # URL parsing and extraction
├── formatter.py         # Arabic text formatting
├── requirements.txt     # Python dependencies
├── .env.example        # Environment variables template
└── README.md           # Documentation
```

## API Limitations

Since this bot works without OAuth/user authorization:

- **Product Search**: Uses keyword-based search to find products by ID
- **Shipping Info**: Provides estimated shipping costs and delivery times
- **Limited Data**: Some detailed product information may not be available
- **Rate Limits**: Subject to public API rate limits

## Error Handling

The bot includes comprehensive error handling for:
- Invalid or malformed URLs
- Network connectivity issues
- API rate limits and failures
- Missing or unavailable products
- Message length validation (Telegram 4096 character limit)

All error messages are displayed in Arabic for better user experience.

## Getting AliExpress API Credentials

1. Visit the [AliExpress Open Platform](https://open.aliexpress.com/)
2. Register for a developer account
3. Create a new application
4. Get your App Key and App Secret
5. No OAuth setup required for this bot

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Support

For support or questions:
- Open an issue on GitHub
- Check the documentation
- Review the API documentation provided by AliExpress

## Disclaimer

This bot is for educational and personal use. Make sure to comply with:
- AliExpress API terms of service
- Telegram bot guidelines
- Local regulations regarding e-commerce and affiliate marketing

**Note**: This bot uses public APIs and provides estimated information. For the most accurate and up-to-date product details, users should visit the actual product pages on AliExpress.