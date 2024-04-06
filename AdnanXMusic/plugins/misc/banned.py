import os
import asyncio
from pyrogram import Client, filters
from pyrogram.types import Message
from AdnanXMusic import app
from AdnanXMusic.utils.database import get_served_chats

# Function to fetch the Logger ID
def get_logger_id():
    return os.environ.get("LOGGER_ID")  # Fetch the logger ID from environment variable

async def lul_message(chat_id: int, message: str):
    try:
        await app.send_message(chat_id=chat_id, text=message)
    except Exception as e:
        print(f"Error sending message to logger: {e}")

@app.on_message(filters.group & filters.left_chat_member)
async def on_bot_kicked(client: Client, message: Message):
    if message.left_chat_member and message.left_chat_member.id == (await client.get_me()).id:
        chatname = message.chat.title  # Get the name of the chat
        chat_id = message.chat.id
        logger_id = get_logger_id()  # Fetch the logger ID
        if logger_id:
            ban_message = f"ʙᴏᴛ ʙᴀɴɴᴇᴅ ғʀᴏᴍ ɢʀᴏᴜᴘ..!😔\n\nɢʀᴏᴜᴘ ɴᴀᴍᴇ: {chatname}\nɢʀᴏᴜᴘ ɪᴅ: {chat_id}"
            await lul_message(logger_id, ban_message)
        else:
            print("Logger ID not found. Please set the LOGGER_ID environment variable.")

async def main():
    await app.start()
    await app.idle()

if __name__ == "__main__":
    asyncio.run(main())
