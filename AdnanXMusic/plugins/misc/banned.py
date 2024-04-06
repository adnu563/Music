import os
import asyncio
from pyrogram import Client, filters
from AdnanXMusic import app
from AdnanXMusic.utils.database import get_served_chats

# Function to fetch the Logger ID
def get_logger_id():
    return os.environ.get("LOGGER_ID")  # Assuming LOGGER_ID is set as an environment variable

async def lul_message(chat_id: int, message: str):
    await app.send_message(chat_id=chat_id, text=message)

@app.on_chat_member_updated()
async def on_chat_member_updated(client, message):
    if message.old_chat_member and message.old_chat_member.user.id == (await client.get_me()).id:
        chatname = message.chat.title
        served_chats = len(await get_served_chats())
        chat_id = message.chat.id
        if message.chat.username:
            chatusername = f"@{message.chat.username}"
        else:
            chatusername = "ᴩʀɪᴠᴀᴛᴇ ᴄʜᴀᴛ"
        
        lemda_text = f"➻ ʙᴏᴛ ʀᴇᴍᴏᴠᴇᴅ ꜰʀᴏᴍ ᴛʜɪs ɢʀᴏᴜᴘ! 😢\n\n‣ ᴄʜᴀᴛ ɴᴀᴍᴇ: {chatname}\n‣ ᴄʜᴀᴛ ɪᴅ: {chat_id}\n‣ ᴜsᴇʀɴᴀᴍᴇ: {chatusername}\n‣ ᴛᴏᴛᴀʟ ᴄʜᴀᴛ: {served_chats}\n‣ ʀᴇᴍᴏᴠᴇᴅ ʙʏ: {message.from_user.mention}"
        
        logger_id = get_logger_id()  # Fetch the logger ID
        await lul_message(logger_id, lemda_text)

async def main():
    await app.start()
    await app.idle()

if name == "main":
    asyncio.run(main())