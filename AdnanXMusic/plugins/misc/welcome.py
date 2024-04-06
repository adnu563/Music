import os
import asyncio
from pyrogram import Client, filters
from pyrogram.types import Message
from AdnanXMusic import app
from AdnanXMusic.utils.database import get_served_chats

async def lul_message(chat_id: int, message: str):
    await app.send_message(chat_id=chat_id, text=message)

@app.on_message(filters.new_chat_members)
async def on_new_chat_members(client: Client, message: Message):
    if (await client.get_me()).id in [user.id for user in message.new_chat_members]:
        added_by = message.from_user.first_name if message.from_user else "ᴜɴᴋɴᴏᴡɴ ᴜsᴇʀ"
        matlabi_jhanto = message.chat.title
        served_chats = len(await get_served_chats())
        chat_id = message.chat.id
        if message.chat.username:
            chatusername = f"@{message.chat.username}"
        else:
            chatusername = "ᴩʀɪᴠᴀᴛᴇ ᴄʜᴀᴛ"
        lemda_text = f"ʙᴏᴛ ᴀᴅᴅᴇᴅ ᴛᴏ ɴᴇᴡ ɢʀᴏᴜᴘ..🥳\n\nᴄʜᴀᴛ ɴᴀᴍᴇ: {matlabi_jhanto}\nᴄʜᴀᴛ ɪᴅ: {chat_id}\nᴜsᴇʀɴᴀᴍᴇ: {chatusername}\nᴛᴏᴛᴀʟ ᴄʜᴀᴛ: {served_chats}\nᴀᴅᴅᴇᴅ ʙʏ:{added_by}"
        await lul_message("-1001728024036", lemda_text)  # Replace 123456789 with the desired group ID

async def main():
    await app.start()
    await app.idle()

if __name__ == "__main__":
    asyncio.run(main())
