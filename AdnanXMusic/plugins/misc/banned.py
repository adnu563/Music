import os
import asyncio
from pyrogram import Client, filters
from pyrogram.types import Chat, User, ChatMemberUpdated
from AdnanXMusic import app
from AdnanXMusic.utils.database import get_served_chats

# Function to fetch the Logger ID
def get_logger_id():
    return int(os.environ.get("LOGGER_ID"))  # Assuming LOGGER_ID is set as an environment variable

async def send_message_to_logger(chat_id: int, message: str):
    try:
        await app.send_message(chat_id=chat_id, text=message)
    except Exception as e:
        print(f"Failed to send message to logger: {e}")

@app.on_chat_member_updated()
async def on_bot_kicked_from_chat(client: Client, chat_member_updated: ChatMemberUpdated):
    if chat_member_updated.old_chat_member and chat_member_updated.old_chat_member.status != "left" and chat_member_updated.new_chat_member.status == "left" and chat_member_updated.new_chat_member.user.id == client.get_me().id:
        removed_by = chat_member_updated.from_user.first_name if chat_member_updated.from_user else "Unknown User"
        chatname = chat_member_updated.chat.title if chat_member_updated.chat.title else "Unnamed Chat"
        chat_id = chat_member_updated.chat.id
        if chat_member_updated.chat.username:
            chatusername = f"@{chat_member_updated.chat.username}"
        else:
            chatusername = "Private Chat"
        message_text = f"Bot banned from group\n\nChat Name: {chatname}\nChat ID: {chat_id}\nUsername: {chatusername}\nBanned by: {removed_by}"
        logger_id = get_logger_id()  # Fetch the logger ID
        await send_message_to_logger(logger_id, message_text)

async def main():
    await app.start()
    await app.idle()

if __name__ == "__main__":
    asyncio.run(main())
