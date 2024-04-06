import os
import asyncio
from pyrogram import Client, filters
from pyrogram.types import Message
from AdnanXMusic import app
from AdnanXMusic.utils.database import get_served_chats

# Function to fetch the Logger ID
def get_logger_id():
    return os.environ.get("LOGGER_ID")  # Assuming LOGGER_ID is set as an environment variable

async def lul_message(chat_id: int, message: str):
    await app.send_message(chat_id=chat_id, text=message)

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
        lemda_text = f"ʙᴏᴛ ʀᴇᴍᴏᴠᴇᴅ ғʀᴏᴍ ɢʀᴏᴜᴘ..!😢\n\nᴄʜᴀᴛ ɴᴀᴍᴇ: {chatname}\nᴄʜᴀᴛ ɪᴅ: {chat_id}\nᴜsᴇʀɴᴀᴍᴇ: {chatusername}\nʀᴇᴍᴏᴠᴇᴅ ʙʏ:{removed_by}"
        logger_id = get_logger_id()  # Fetch the logger ID
        await lul_message(logger_id, lemda_text)

async def main():
    await app.start()
    await app.idle()

if __name__ == "__main__":
    asyncio.run(main())
