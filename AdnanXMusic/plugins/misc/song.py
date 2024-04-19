import os
import requests
import yt_dlp
from pyrogram import filters
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup, Message
from youtube_search import YoutubeSearch
from AdnanXMusic import app
from AdnanXMusic.logging import LOGGER

BOT_MENTION = "AdnanXMusic"

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

    except Exception as ex:
        LOGGER.error(ex)
        return await m.edit_text(
            f"Failed to fetch track from YouTube.\n\n**Reason:** `{ex}`"
        )

    await m.edit_text("»⏳ᴅᴏᴡɴʟᴏᴀᴅɪɴɢ sᴏɴɢ, ᴘʟᴇᴀsᴇ ᴡᴀɪᴛ...!")
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info_dict = ydl.extract_info(link, download=False)
            audio_file = ydl.prepare_filename(info_dict)
            ydl.process_info(info_dict)
        rep = f"➠ Title: {title[:23]}\n➠ Duration: {duration}\n\n➥ Uploaded by: @{BOT_USERNAME}"
        secmul, dur, dur_arr = 1, 0, duration.split(":")
        for i in range(len(dur_arr) - 1, -1, -1):
            dur += int(dur_arr[i]) * secmul
            secmul *= 60
        try:
            visit_butt = InlineKeyboardMarkup(
                [
                    [
                        InlineKeyboardButton(
                            text="YouTube",
                            url=link,
                        )
                    ]
                ]
            )
            await app.send_audio(
                chat_id=message.chat.id,  # Send the song in the same chat where the command was called
                audio=audio_file,
                caption=rep,
                thumb=thumb_name,
                title=title,
                duration=dur,
                reply_markup=visit_butt,
            )
            await m.delete()  # Delete the message indicating that the song is being downloaded
        except Exception as e:
            LOGGER.error(e)
            return await m.edit_text("Failed to send audio.")
    except Exception as e:
        LOGGER.error(ex)
        return await m.edit_text("Failed to upload audio on Telegram servers.")

    try:
        os.remove(audio_file)
        os.remove(thumb_name)
    except Exception as ex:
        LOGGER.error(ex)
