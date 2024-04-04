import logging
from telegram.ext import Updater, CommandHandler
from telegram import Update

# Set up logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

# Function to handle /start command
def start(update: Update, context):
    chat = update.effective_chat
    user = update.effective_user
    logger.info("Bot added to new group!")
    logger.info(f"Chat name: {chat.title}")
    logger.info(f"Chat ID: {chat.id}")
    logger.info(f"Username: {user.username}")
    logger.info(f"Total chats: {len(context.bot.chat_data)}")
    logger.info(f"Added by: {user.full_name}")

# Function to count total groups
def total_chats(update: Update, context):
    update.message.reply_text(f"Total chats: {len(context.bot.chat_data)}")

def main():
    # Initialize the bot
    updater = Updater("YOUR_BOT_TOKEN", use_context=True)

    # Get the dispatcher to register handlers
    dp = updater.dispatcher

    # Register command handlers
    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CommandHandler("totalchats", total_chats))

    # Start the Bot
    updater.start_polling()
    updater.idle()

if __name__ == '__main__':
    main()