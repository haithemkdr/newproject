# AliExpress Telegram Bot for Algerian Shoppers

A comprehensive Telegram bot that processes AliExpress product links and provides detailed product information in Arabic, specifically designed for Algerian shoppers.

## Features

- 🔗 **URL Parsing**: Supports all AliExpress URL formats (desktop, mobile, short links)
- 🛍️ **Product Information**: Detailed product data including prices, images, and descriptions
<<<<<<< HEAD
- 💰 **Price Calculation**: Shows prices in USD with shipping costs to Algeria
- 📦 **Shipping Details**: Delivery time and shipping methods to Algeria
- ⭐ **Ratings & Reviews**: Customer ratings and review counts
- 🏪 **Seller Information**: Store and seller details
- 🎨 **Product Variants**: Available colors, sizes, and other options
- 🇩🇿 **Arabic Support**: All responses in Arabic with RTL support
- ⚡ **Async Processing**: Fast, non-blocking message handling


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
<<<<<<< HEAD
   - `ALIEXPRESS_ACCESS_TOKEN`: Your API access token (optional)


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
<<<<<<< HEAD
| `ALIEXPRESS_ACCESS_TOKEN` | API access token for authenticated requests | Optional |
| `TARGET_CURRENCY` | Currency for price display | USD |
| `TARGET_LANGUAGE` | Language for API responses | AR |
| `SHIP_TO_COUNTRY` | Shipping destination country code | DZ |
| `TAX_RATE` | Tax rate for price calculations | 0.1 |

### API Configuration

The bot uses the following AliExpress Affiliate API endpoints:
- `aliexpress.affiliate.productdetail.get` - Product details
- `aliexpress.affiliate.product.sku.detail.get` - SKU details
- `aliexpress.affiliate.product.shipping.get` - Shipping information


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
<<<<<<< HEAD
├── aliexpress_api.py    # AliExpress API client
=======

├── link_parser.py       # URL parsing and extraction
├── formatter.py         # Arabic text formatting
├── requirements.txt     # Python dependencies
├── .env.example        # Environment variables template
└── README.md           # Documentation
```

<<<<<<< HEAD
=======

## Error Handling

The bot includes comprehensive error handling for:
- Invalid or malformed URLs
- Network connectivity issues
- API rate limits and failures
- Missing or unavailable products
- Message length validation (Telegram 4096 character limit)

All error messages are displayed in Arabic for better user experience.

<<<<<<< HEAD
## API Rate Limits

The AliExpress API has rate limits. The bot includes:
- Request throttling
- Error retry mechanisms
- Graceful degradation when limits are reached

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
<<<<<<< HEAD
- Local regulations regarding e-commerce and affiliate marketing

