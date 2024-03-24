from telegram.ext import Updater, MessageHandler, Filters
from telegram import Update

# Telegram bot token
TOKEN = 'YOUR_BOT_TOKEN'

# Function to handle new members joining a group
def new_member(update: Update, context):
    # Extract relevant information
    new_member = update.message.new_chat_members[0]
    group_name = update.message.chat.title
    group_id = update.message.chat_id
    
    # Send the information to yourself (you can replace with your desired logic)
    context.bot.send_message(
        chat_id=YOUR_USER_ID,  # Replace YOUR_USER_ID with your user ID
        text=f"New member {new_member.username} ({new_member.id}) joined group {group_name} ({group_id})"
    )

def main():
    # Create the Updater and pass it your bot's token
    updater = Updater(TOKEN, use_context=True)

    # Get the dispatcher to register handlers
    dp = updater.dispatcher

    # Add a message handler for new members joining the group
    dp.add_handler(MessageHandler(Filters.status_update.new_chat_members, new_member))

    # Start the Bot
    updater.start_polling()
    updater.idle()

if __name__ == '__main__':
    main()
