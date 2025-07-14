#!/usr/bin/env python3
"""
Sassy Tanya Telegram Bot - Main Entry Point
Tech Stack: python-telegram-bot, aiohttp, asyncio
"""

import os
import sys
import asyncio
import logging
from typing import Optional
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
import aiohttp

# Configure logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Configuration
TELEGRAM_BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN', 'YOUR_BOT_TOKEN_HERE')
WEBHOOK_URL = os.getenv('WEBHOOK_URL', 'https://your-replit-app.replit.app/api/telegram/webhook')
PORT = int(os.getenv('PORT', 8080))

class SassyTanyaBot:
    def __init__(self):
        self.webhook_url = WEBHOOK_URL
        self.session: Optional[aiohttp.ClientSession] = None

    async def start_session(self):
        if not self.session:
            self.session = aiohttp.ClientSession()

    async def close_session(self):
        if self.session:
            await self.session.close()
            self.session = None

    async def send_to_webhook(self, update_data):
        try:
            await self.start_session()
            async with self.session.post(
                self.webhook_url,
                json=update_data,
                headers={'Content-Type': 'application/json'}
            ) as response:
                if response.status == 200:
                    result = await response.json()
                    return result.get('response', 'Sorry, I had trouble processing that!')
                else:
                    logger.error(f"Webhook error: {response.status}")
                    return "I'm having technical difficulties. Please try again later!"
        except Exception as e:
            logger.error(f"Error sending to webhook: {e}")
            return "Sorry, I'm having connection issues. Please try again!"

bot = SassyTanyaBot()

async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Hey there! I'm Tanya! Type /help to know more!")

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Here to help! Try sending /photo or /caption!")

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    update_data = {
        'message': {
            'message_id': update.message.message_id,
            'from': {
                'id': update.effective_user.id,
                'username': update.effective_user.username,
                'first_name': update.effective_user.first_name,
                'last_name': update.effective_user.last_name
            },
            'text': update.message.text,
            'chat': {
                'id': update.effective_chat.id,
                'type': update.effective_chat.type
            }
        }
    }
    response = await bot.send_to_webhook(update_data)
    await update.message.reply_text(response)

async def main():
    if TELEGRAM_BOT_TOKEN == 'YOUR_BOT_TOKEN_HERE':
        logger.error("Please set TELEGRAM_BOT_TOKEN environment variable")
        sys.exit(1)

    try:
        application = Application.builder().token(TELEGRAM_BOT_TOKEN).build()

        application.add_handler(CommandHandler("start", start_command))
        application.add_handler(CommandHandler("help", help_command))
        application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

        logger.info("Starting Sassy Tanya Bot...")
        await application.run_polling()
    except Exception as e:
        logger.error(f"Failed to start bot: {e}")
        sys.exit(1)
    finally:
        await bot.close_session()

if __name__ == '__main__':
    asyncio.run(main())
