from AdnanXMusic import Update, Bot
from AdnanXMusic import Updater, CommandHandler, MessageHandler, Filters, CallbackContext

# Bot token
TOKEN = "YOUR_BOT_TOKEN"

# Counter for the number of groups
bot_count = 0

def start(update: Update, context: CallbackContext) -> None:
    update.message.reply_text('Bot is running. Use /info to get info about the group.')

def info(update: Update, context: CallbackContext) -> None:
    chat = update.message.chat
    message = f"» ʙᴏᴛ ᴀᴅᴅᴇᴅ ᴛᴏ ɴᴇᴡ ɢʀᴏᴜᴘ! 🥳\n\n"
    message += f"ᴄʜᴀᴛ : {chat.title}\n"
    message += f"ᴄʜᴀᴛ ɪᴅ : {chat.id}\n"
    message += f"ᴄʜᴀᴛ ᴜɴᴀᴍᴇ : @{chat.username}\n"
    message += f"ᴛᴏᴛᴀʟ ᴄʜᴀᴛ : {chat.get_members_count()}\n"
    message += f"ᴀᴅᴅᴇᴅ ʙʏ : {update.message.from_user.first_name}"
    update.message.reply_text(message)

    # Increase bot_count when added to a new group
    global bot_count
    bot_count += 1

def main() -> None:
    updater = Updater(TOKEN)
    dispatcher = updater.dispatcher

    dispatcher.add_handler(CommandHandler("start", start))
    dispatcher.add_handler(CommandHandler("info", info))

    updater.start_polling()
    updater.idle()

if __name__ == '__main__':
    main()