from telegram.ext import Updater, CommandHandler
from telegram import Update
from telegram.ext import CallbackContext

# Define your welcome message function
def print_welcome_message(update: Update, context: CallbackContext):
    chat_name = update.message.chat.title
    chat_id = update.message.chat_id
    username = update.message.from_user.username
    total_chat = context.bot.get_chat_members_count(chat_id)
    added_by = update.message.from_user.name

    welcome_message = (
        "» ʙᴏᴛ ᴀᴅᴅᴇᴅ ᴛᴏ ɴᴇᴡ ɢʀᴏᴜᴘ! 🥳\n\n"
        f"ᴄʜᴀᴛ ɴᴀᴍᴇ: {chat_name}\n"
        f"ᴄʜᴀᴛ ɪᴅ: {chat_id}\n"
        f"ᴜsᴇʀɴᴀᴍᴇ: {username}\n"
        f"ᴛᴏᴛᴀʟ ᴄʜᴀᴛ: {total_chat}\n"
        f"ᴀᴅᴅᴇᴅ ʙʏ: {added_by}\n"
    )

    update.message.reply_text(welcome_message)

# Define the command handler for when the bot is added to a new group
def start(update: Update, context: CallbackContext):
    print_welcome_message(update, context)

# Set up the bot
def main():
    updater = Updater("YOUR_BOT_TOKEN", use_context=True)
    dp = updater.dispatcher

    dp.add_handler(CommandHandler("start", start))

    updater.start_polling()
    updater.idle()

if __name__ == "__main__":
    main()