from telegram.ext import Updater, CommandHandler
import logging

# Define action for the /start command at home
def start(update, context):
    chat = update.effective_chat
    user = update.effective_user
    added_by = update.message.from_user.first_name

    # Create log message and print
    log_message = f"» ʙᴏᴛ ᴀᴅᴅᴇᴅ ᴛᴏ ɴᴇᴡ ɢʀᴏᴜᴘ! 🥳\n\nᴄʜᴀᴛ ɴᴀᴍᴇ: {chat.title}\nᴄʜᴀᴛ ɪᴅ: {chat.id}\nᴜsᴇʀɴᴀᴍᴇ: @{user.username}\nᴛᴏᴛᴀʟ ᴄʜᴀᴛ: {context.bot.get_chat_members_count(chat.id)}\nᴀᴅᴅᴇᴅ ʙʏ: {added_by}"
    print(log_message)

# Logging setup
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

# Create handler and add for /start command
dp = updater.dispatcher
dp.add_handler(CommandHandler("start", start))

# Start the bot
updater.start_polling()
updater.idle()