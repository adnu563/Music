from telegram.ext import Updater, MessageHandler, Filters
import logging

# Set up logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

# Define a function to handle new members joining the group
def new_member(update, context):
    new_members = update.message.new_chat_members
    for member in new_members:
        logger.info(f"New member joined: {member.first_name} ({member.id})")

def main():
    # Set up the updater and dispatcher
    updater = Updater("YOUR_BOT_TOKEN", use_context=True)
    dp = updater.dispatcher

    # Add a message handler to handle new members joining the group
    dp.add_handler(MessageHandler(Filters.status_update.new_chat_members, new_member))

    # Start the bot
    updater.start_polling()
    logger.info("Bot started polling...")
    updater.idle()

if __name__ == '__main__':
    main()