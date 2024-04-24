import os
import requests
from pyrogram import filters
from pyrogram.types import Message
from AdnanXMusic import app
import logging

# Initialize the LOGGER object
LOGGER = logging.getLogger(__name__)

# Configure the LOGGER object
logging.basicConfig(level=logging.ERROR)  # Set the logging level to ERROR or any level you prefer

@app.on_message(filters.command("download"))
async def download_and_upload_video(_, message: Message):
    try:
        await message.delete()
    except:
        pass

    m = await message.reply_text("🔎 Downloading This File, please wait...")

    link = message.text.split(" ", 1)[1]

    try:
        if link.endswith(".mkv") or link.endswith(".m3u8"):
            # If it's an MKV or M3U8 file link
            await download_and_upload_video_file(message.chat.id, link, m)

        else:
            raise ValueError("Unsupported file format")

        await m.delete()  # Delete the message indicating downloading
    except Exception as e:
        LOGGER.error(f"Error: {e}")
        await m.edit_text("Failed to download and upload video.")

async def download_and_upload_video_file(chat_id, link, m):
    try:
        # Download the video file
        video_file_name = link.split("/")[-1]
        with requests.get(link, stream=True) as r:
            r.raise_for_status()
            with open(video_file_name, 'wb') as f:
                for chunk in r.iter_content(chunk_size=8192):
                    f.write(chunk)

        # Upload the video file
        async with app.send_document(chat_id, video_file_name) as msg:
            await app.send_chat_action(chat_id, "upload_document")
            with open(video_file_name, 'rb') as file:
                while True:
                    chunk = file.read(2097152)  # Read 2 MB at a time
                    if not chunk:
                        break
                    await msg.upload_chunk(chunk)

        # Delete the temporary video file
        os.remove(video_file_name)

    except Exception as e:
        LOGGER.error(f"Error downloading and uploading video file: {e}")
        await m.edit_text("Failed to download and upload video.")