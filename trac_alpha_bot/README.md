# TracAlphaBot

A Telegram bot that monitors the Trac blockchain in real-time and sends alerts about wallet or token activity.

## Features
- Real-time monitoring using a WebSocket-based WDK-style parser.
- Subscription management via Telegram commands.
- Whale alerts based on a configurable USD threshold.

## Telegram Commands
- `/start` - Welcome message
- `/watch_wallet <wallet_address>` - Subscribe to a wallet
- `/watch_token <token_address>` - Subscribe to a token
- `/my_subscriptions` - Show your current subscriptions

## Local Installation

1. Clone the repository and navigate to the project root:
   ```bash
   cd trac_alpha_bot
   ```
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Set environment variables (e.g., in a `.env` file or exported to your shell):
   ```bash
   export TELEGRAM_TOKEN="your-bot-token"
   export TRAC_RPC_URL="wss://your-trac-rpc-url"
   export WHALE_ALERT_USD="10000"
   ```
4. Run the bot:
   ```bash
   python bot/bot.py
   ```

## Deployment on Railway

1. Connect your GitHub repository to Railway.
2. Railway will automatically detect the `Dockerfile` and build the container.
3. In the Railway dashboard, navigate to the **Variables** section of your service and add the following:
   - `TELEGRAM_TOKEN`
   - `TRAC_RPC_URL`
   - `WHALE_ALERT_USD`
4. Deploy the service.
