import logging
from telegram.ext import Updater, CommandHandler
from telegram import Update

# Set up logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

def start(update: Update, context):
    user_id = update.message.from_user.id
    chat_id = update.message.chat.id
    group_title = update.message.chat.title
    group_id = update.message.chat.id
    group_count = len(context.bot.get_chat_member(chat_id, user_id).user.joined_chat_ids)
    
    # Displaying information
    message = f"You've been added to the group '{group_title}' (Group ID: {group_id}, Chat ID: {chat_id}).\nTotal groups: {group_count}"
    context.bot.send_message(chat_id=user_id, text=message)

def main():
    updater = Updater("YOUR_BOT_TOKEN", use_context=True)  # Replace 'YOUR_BOT_TOKEN' with your actual bot token
    dp = updater.dispatcher

    dp.add_handler(CommandHandler("start", start))

    updater.start_polling()
    updater.idle()

if __name__ == '__main__':
    main()