import sys
import os
# Add the parent directory to sys.path to allow importing config and wdk
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import json
import logging
import asyncio
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes
import config
from wdk.trac_parser import TracParser

# Configure logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

SUBSCRIPTIONS_FILE = os.path.join(os.path.dirname(__file__), 'subscriptions.json')

# Global variable to hold telegram app application
tg_app = None

def load_subscriptions():
    if not os.path.exists(SUBSCRIPTIONS_FILE):
        return {}
    try:
        with open(SUBSCRIPTIONS_FILE, 'r') as f:
            return json.load(f)
    except Exception as e:
        logger.error(f"Error loading subscriptions: {e}")
        return {}

def save_subscriptions(subs):
    try:
        with open(SUBSCRIPTIONS_FILE, 'w') as f:
            json.dump(subs, f, indent=4)
    except Exception as e:
        logger.error(f"Error saving subscriptions: {e}")

subscriptions = load_subscriptions()

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_id = str(update.effective_user.id)
    if user_id not in subscriptions:
        subscriptions[user_id] = {"wallets": [], "tokens": []}
        save_subscriptions(subscriptions)
        
    await update.message.reply_text(
        "Welcome to TracAlphaBot!\n\n"
        "Commands:\n"
        "/watch_wallet <address> - Subscribe to a wallet\n"
        "/watch_token <address> - Subscribe to a token\n"
        "/my_subscriptions - List your subscriptions"
    )

async def watch_wallet(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_id = str(update.effective_user.id)
    if not context.args:
        await update.message.reply_text("Usage: /watch_wallet <wallet_address>")
        return
        
    address = context.args[0]
    if user_id not in subscriptions:
        subscriptions[user_id] = {"wallets": [], "tokens": []}
        
    if address not in subscriptions[user_id]["wallets"]:
        subscriptions[user_id]["wallets"].append(address)
        save_subscriptions(subscriptions)
        await update.message.reply_text(f"Subscribed to wallet: {address}")
    else:
        await update.message.reply_text("You are already watching this wallet.")

async def watch_token(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_id = str(update.effective_user.id)
    if not context.args:
        await update.message.reply_text("Usage: /watch_token <token_address>")
        return
        
    address = context.args[0]
    if user_id not in subscriptions:
        subscriptions[user_id] = {"wallets": [], "tokens": []}
        
    if address not in subscriptions[user_id]["tokens"]:
        subscriptions[user_id]["tokens"].append(address)
        save_subscriptions(subscriptions)
        await update.message.reply_text(f"Subscribed to token: {address}")
    else:
        await update.message.reply_text("You are already watching this token.")

async def my_subscriptions(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_id = str(update.effective_user.id)
    if user_id not in subscriptions:
        await update.message.reply_text("You have no subscriptions.")
        return
        
    user_subs = subscriptions[user_id]
    wallets = "\n".join(user_subs.get("wallets", [])) or "None"
    tokens = "\n".join(user_subs.get("tokens", [])) or "None"
    
    await update.message.reply_text(
        f"Your Subscriptions:\n\n"
        f"Wallets:\n{wallets}\n\n"
        f"Tokens:\n{tokens}"
    )

def handle_trac_event(event):
    """
    Called by TracParser when an event is received from the blockchain.
    """
    logger.info(f"Received event: {event}")
    
    amount = event.get("amount", 0)
    # Check whale alert threshold
    if amount < config.WHALE_ALERT_USD:
        return
        
    wallet = event.get("wallet")
    token = event.get("token")
    
    # Check subscriptions and send alerts
    for user_id, subs in subscriptions.items():
        is_subscribed = False
        if wallet and wallet in subs.get("wallets", []):
            is_subscribed = True
        if token and token in subs.get("tokens", []):
            is_subscribed = True
            
        if is_subscribed:
            message = (
                f"🚨 *WHALE ALERT* 🚨\n"
                f"Type: {event.get('type')}\n"
                f"Amount: ${amount:,.2f}\n"
                f"Wallet: {wallet}\n"
                f"Token: {token}"
            )
            # Use asyncio to schedule the message sending in the main event loop
            if tg_app:
                asyncio.run_coroutine_threadsafe(
                    tg_app.bot.send_message(chat_id=user_id, text=message, parse_mode='Markdown'),
                    tg_app.loop
                )

def main():
    global tg_app
    
    if not config.TELEGRAM_TOKEN:
        logger.error("TELEGRAM_TOKEN is not set in environment or config.py")
        return

    # Initialize Trac parser
    parser = TracParser(config.TRAC_RPC_URL, handle_trac_event)
    parser.start()
    
    # Initialize Telegram Bot
    application = Application.builder().token(config.TELEGRAM_TOKEN).build()
    tg_app = application
    
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("watch_wallet", watch_wallet))
    application.add_handler(CommandHandler("watch_token", watch_token))
    application.add_handler(CommandHandler("my_subscriptions", my_subscriptions))
    
    logger.info("Bot started and listening for commands...")
    # Run the bot until the user presses Ctrl-C
    application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == "__main__":
    main()
