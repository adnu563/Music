from telegram.ext import Updater, CommandHandler
from telegram import Update
from telegram.ext import CallbackContext

# Your Telegram user ID
YOUR_TELEGRAM_USER_ID = "your_user_id"

# Define the function to send a notification to your Telegram account
def send_notification(bot, message):
    bot.send_message(chat_id=YOUR_TELEGRAM_USER_ID, text=message)

# Define the function to handle when the bot is added to a new group
def handle_new_chat(update: Update, context: CallbackContext):
    chat_id = update.message.chat_id
    chat_name = update.message.chat.title
    message = f"Bot added to new group!\nGroup Name: {chat_name}\nGroup ID: {chat_id}"
    send_notification(context.bot, message)

# Set up the bot
def main():
    # Replace "YOUR_BOT_TOKEN" with your actual bot token
    updater = Updater("YOUR_BOT_TOKEN", use_context=True)
    dp = updater.dispatcher

    # Register the handler for when the bot is added to a new group
    dp.add_handler(CommandHandler("new_chat", handle_new_chat))

    updater.start_polling()
    updater.idle()

if __name__ == "__main__":
    main()