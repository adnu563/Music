from telegram import Bot, Update
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext
import logging

# Set up logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

# Your bot's token
TOKEN = 'your_bot_token'

# Your user_id (you can get it by sending /id to the bot @userinfobot)
YOUR_USER_ID = 'your_user_id'

# Define a function to handle when the bot is removed from a group
def handle_removed(update: Update, context: CallbackContext):
    if update.message:
        chat_id = update.message.chat_id
        context.bot.send_message(chat_id=YOUR_USER_ID, text=f"Bot removed from group {chat_id}")

# Define a function to handle when the bot is banned from a group
def handle_banned(update: Update, context: CallbackContext):
    if update.message:
        chat_id = update.message.chat_id
        context.bot.send_message(chat_id=YOUR_USER_ID, text=f"Bot banned from group {chat_id}")

def main():
    updater = Updater(TOKEN, use_context=True)

    # Get the dispatcher to register handlers
    dp = updater.dispatcher

    # Register message handlers
    dp.add_handler(MessageHandler(Filters.status_update.new_chat_members, handle_removed))
    dp.add_handler(MessageHandler(Filters.status_update.left_chat_member, handle_banned))

    # Start the Bot
    updater.start_polling()
    logger.info("Bot started")
    updater.idle()

if __name__ == '__main__':
    main()
