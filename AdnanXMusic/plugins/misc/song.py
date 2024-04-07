import os
import aiohttp
import asyncio
import yt_dlp
from youtube_search import YoutubeSearch
from pyrogram import filters
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
from AdnanXMusic import app
from AdnanXMusic.logging import LOGGER

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

    m = await message.reply_text("🔍")

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

        duration = results[0]["duration"]
        total_views = results[0]["views"]
        uploader = results[0]["channel"]
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
        secmul, dur = 1, 0
        dur_arr = duration.split(":")
        for i in range(len(dur_arr) - 1, -1, -1):
            dur += int(dur_arr[i]) * secmul
            secmul *= 45

        # Send audio with thumbnail
        await app.send_audio(
            chat_id=message.chat.id,
            audio=audio_file,
            caption=f"➠ ᴛɪᴛʟᴇ: {title[:23]}\n➠ ᴅᴜʀᴀᴛɪᴏɴ: {duration}\n➠ ᴛᴏᴛᴀʟ: {total_views}\n\n➥ ᴜᴘʟᴏᴀᴅᴇᴅ ʙʏ: {app.mention}",
            thumb=thumb_name,
            title=title,
            duration=dur
        )
        await m.delete()

        # Remove temporary files
        os.remove(audio_file)
        os.remove(thumb_name)

    except Exception as e:
        LOGGER.error(e)
        await m.edit_text("Failed to upload audio on Telegram servers.")