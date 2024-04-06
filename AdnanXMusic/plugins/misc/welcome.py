from AdnanXMusic import app  # Assuming `app` is the Flask app instance
from AdnanXMusic.logging import logger

# Function to handle new chat members
def new_chat_members(update, context):
    # Get information about the chat
    chat = update.effective_chat
    chat_info = f"Chat ID: {chat.id}\nChat Title: {chat.title}"

    # Get information about the user who added the bot
    for member in update.message.new_chat_members:
        if member.is_bot and member.username == "AdnanXMusic":
            added_by_info = f"Added by:\nUser ID: {update.message.from_user.id}\nName: {update.message.from_user.first_name}"

            # Send the chat information and the user who added the bot to the chat
            update.message.reply_text(f"ℹ️ **Group Information**:\n{chat_info}\n\n🤖 **Added by**:\n{added_by_info}", parse_mode=ParseMode.MARKDOWN)
            break

def main():
    # Initialize the bot
    updater = Updater("YOUR_BOT_TOKEN", use_context=True)
    dp = updater.dispatcher

    # Add handler to respond to new chat members
    dp.add_handler(MessageHandler(Filters.status_update.new_chat_members, new_chat_members))

    # Start the Bot
    updater.start_polling()
    updater.idle()

if __name__ == '__main__':
    main()
