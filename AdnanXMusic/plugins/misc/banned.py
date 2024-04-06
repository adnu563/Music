import os
import asyncio
from pyrogram import Client, filters
from pyrogram.types import Message
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

@app.on_message(filters.left_chat_member)
async def on_left_chat_member(client: Client, message: Message):
    if message.left_chat_member.id == (await client.get_me()).id:
        removed_by = message.from_user.first_name if message.from_user else "ᴜɴᴋɴᴏᴡɴ ᴜsᴇʀ"
        chatname = message.chat.title  # Changed matlabi_jhanto to chatname
        chat_id = message.chat.id
        if message.chat.username:
            chatusername = f"@{message.chat.username}"
        else:
            chatusername = "ᴩʀɪᴠᴀᴛᴇ ᴄʜᴀᴛ"
        message_text = f"Bot removed from group\n\nChat Name: {chatname}\nChat ID: {chat_id}\nUsername: {chatusername}\nRemoved by: {removed_by}"
        logger_id = get_logger_id()  # Fetch the logger ID
        await send_message_to_logger(logger_id, message_text)

async def main():
    await app.start()
    await app.idle()

if __name__ == "__main__":
    asyncio.run(main())
