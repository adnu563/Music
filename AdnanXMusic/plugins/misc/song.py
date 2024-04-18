import os
import aiohttp
import asyncio
import yt_dlp
from youtube_search import YoutubeSearch
from pyrogram import filters
from pyrogram.types import Message
from AdnanXMusic import app
import logging

# Initialize logger
LOGGER = logging.getLogger(__name__)
LOGGER.setLevel(logging.ERROR)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
stream_handler = logging.StreamHandler()
stream_handler.setFormatter(formatter)
LOGGER.addHandler(stream_handler)

async def download_file(url, filename):
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            if response.status == 200:
                with open(filename, 'wb') as f:
                    while True:
                        chunk = await response.content.read(1024)
                        if not chunk:
                            break
                        f.write(chunk)

@app.on_message(filters.command(["song", "vsong", "video", "music"]))
async def song(_, message: Message):
    try:
        await message.delete()
    except Exception as e:
        LOGGER.error(e)

    m = await message.reply_text("🔎")

    query = " ".join(message.command[1:])
    ydl_opts = {"format": "bestaudio[ext=m4a]"}

    try:
        results = YoutubeSearch(query, max_results=5).to_dict()
        link = f"https://youtube.com{results[0]['url_suffix']}"
        title = results[0]["title"][:40]
        thumbnail = results[0]["thumbnails"][0]
        thumb_name = f"thumb{title}.jpg"

        # Download thumbnail asynchronously
        await download_file(thumbnail, thumb_name)

    except Exception as ex:
        LOGGER.error(ex)
        return await m.edit_text(
            f"Failed to fetch track from YT-DL.\n\nReason: {ex}"
        )

    await m.edit_text("⏳ᴅᴏᴡɴʟᴏᴀᴅɪɴɢ sᴏɴɢ, ᴘʟᴇᴀsᴇ ᴡᴀɪᴛ...!")

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info_dict = ydl.extract_info(link, download=False)
            audio_file = ydl.prepare_filename(info_dict)
            ydl.process_info(info_dict)

        # Calculate duration
        duration = results[0]["duration"]
        duration_parts = duration.split(":")
        if len(duration_parts) == 3:
            hours, minutes, seconds = map(int, duration_parts)
            total_seconds = hours * 3600 + minutes * 60 + seconds
        else:
            minutes, seconds = map(int, duration_parts)
            total_seconds = minutes * 60 + seconds

        # Send audio with the thumbnail as the play thumbnail
        await app.send_audio(
            chat_id=message.chat.id,
            audio=audio_file,
            caption=f"➠ ᴛɪᴛʟᴇ: {title[:23]}\n➠ ᴅᴜʀᴀᴛɪᴏɴ: {duration}\n\n➥ ᴜᴘʟᴏᴀᴅᴇᴅ ʙʏ: {app.mention}",
            title=title,
            duration=total_seconds,
            thumb=thumb_name,
            reply_to_message_id=message.message_id
        )
        await m.delete()

        # Remove tempor
