import os
import requests
import yt_dlp
import logging
from PIL import Image
from pyrogram import filters
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
from youtube_search import YoutubeSearch
from AdnanXMusic import app
from AdnanXMusic.logging import LOGGER  # Assuming LOGGER is defined correctly in AdnanXMusic.logging

@app.on_message(filters.command(["song", "vsong", "video", "music"]))
async def song(_, message: Message):
    try:
        await message.delete()
    except:
        pass
    m = await message.reply_text("🔎")

    query = "".join(" " + str(i) for i in message.command[1:])
    ydl_opts = {"format": "bestaudio[ext=m4a]"}
    try:
        results = YoutubeSearch(query, max_results=5).to_dict()
        link = f"https://youtube.com{results[0]['url_suffix']}"
        title = results[0]["title"][:40]
        thumbnail = results[0]["thumbnails"][0]
        thumb_name = f"thumb{title}.jpg"
        thumb = requests.get(thumbnail, allow_redirects=True)
        open(thumb_name, "wb").write(thumb.content)
        duration = results[0]["duration"]
        total_views = results[0]["views"]
        uploader = results[0]["channel"]
    except Exception as ex:
        LOGGER.error(ex)
        return await m.edit_text(
            f"Failed to fetch track from YT-DL.\n\nReason: `{ex}`"
        )

    await m.edit_text("⏳Downloading Song, Please Wait..!")
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info_dict = ydl.extract_info(link, download=False)
            audio_file = ydl.prepare_filename(info_dict)
            ydl.process_info(info_dict)
        rep = f"➻ ᴛɪᴛʟᴇ: {title[:20]}\n➻ ᴅᴜʀᴀᴛɪᴏɴ: {duration}\n➻ ᴛᴏᴛᴀʟ: {total_views}\n\n➻ ᴜᴘʟᴏᴀᴅᴇᴅ ʙʏ: {app.mention}"
        secmul, dur, dur_arr = 0.5, 0, duration.split(":")
        for i in range(len(dur_arr) - 1, -1, -1):
            dur += int(dur_arr[i]) * secmul
            secmul *= 40
        try:
            await app.send_audio(
                chat_id=message.chat.id,
                audio=audio_file,
                caption=rep,
                thumb=thumb_name,
                title=title,
                duration=dur,
            )
        except Exception as e:
            LOGGER.error(e)
            return await m.edit_text(
                text="Failed to upload audio on Telegram servers."
            )
        await m.delete()
    except Exception as e:
        LOGGER.error(ex)
        return await m.edit_text("Failed to upload audio on Telegram servers.")

    try:
        os.remove(audio_file)
        os.remove(thumb_name)
    except Exception as ex:
        LOGGER.error(ex)
