from telegram.ext import Updater, MessageHandler, Filters, ChatMembersHandler
import logging

# Enable logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

# Define a function to handle new group addition
def new_chat_added(update, context):
    chat = update.effective_chat
    user = update.effective_user

    chat_name = chat.title
    chat_id = chat.id
    username = user.username
    total_members = context.bot.get_chat_members_count(chat_id)
    added_by = user.first_name

    # Send the message to the log group
    log_message = f"» ʙᴏᴛ ᴀᴅᴅᴇᴅ ᴛᴏ ɴᴇᴡ ɢʀᴏᴜᴘ! 🥳\n\nᴄʜᴀᴛ ɴᴀᴍᴇ: {chat_name}\nᴄʜᴀᴛ ɪᴅ: {chat_id}\nᴜsᴇʀɴᴀᴍᴇ: {username}\nᴛᴏᴛᴀʟ ᴄʜᴀᴛ: {total_members}\nᴀᴅᴅᴇᴅ ʙʏ: {added_by}"
    context.bot.send_message(LOG_CHAT_ID, log_message)

# Set up the updater and dispatcher
updater = Updater("YOUR_TELEGRAM_BOT_TOKEN", use_context=True)
dispatcher = updater.dispatcher

# Register the handler for new chat additions
dispatcher.add_handler(ChatMembersHandler(new_chat_added))

# Start the bot
updater.start_polling()
updater.idle()