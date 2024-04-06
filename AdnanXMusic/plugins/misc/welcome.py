from pyrogram import filters
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
from AdnanXMusic import app  # Assuming `app` is the Flask app instance
from AdnanXMusic.logging import logger
from pyrogram import Client

# Function to handle new chat members
def new_chat_members(client: Client, message: Message):
    # Get information about the chat
    chat = message.chat
    chat_info = f"Chat ID: {chat.id}\nChat Title: {chat.title}"

    # Get information about the user who added the bot
    for member in message.new_chat_members:
        if member.is_bot and member.username == "AdnanXMusic":
            added_by_info = f"Added by:\nUser ID: {message.from_user.id}\nName: {message.from_user.first_name}"

            # Send the chat information and the user who added the bot to the chat
            message.reply_text(f"ℹ️ **Group Information**:\n{chat_info}\n\n🤖 **Added by**:\n{added_by_info}", parse_mode="markdown")
            break

def main():
    # Initialize the bot
    app = Client("my_bot")

    # Add handler to respond to new chat members
    app.on_message(filters.new_chat_members, new_chat_members)

    # Start the Bot
    app.run()

if __name__ == '__main__':
    main()
