import os
import requests
import yt_dlp
from pyrogram import filters
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup, Message
from youtube_search import YoutubeSearch
from AdnanXMusic import app
import logging

# Initialize the LOGGER object
LOGGER = logging.getLogger(__name__)

# Configure the LOGGER object
logging.basicConfig(level=logging.ERROR)  # Set the logging level to ERROR or any level you prefer

BOT_MENTION = "AdnanXMusic"

def shorten_views(views):
    try:
        views = int(views)
    except ValueError:
        return views  # Return as it is if not convertible to int

    if views < 1000:
        return str(views)  # If less than 1000, return as it is

    for unit in ["", "K", "M", "B"]:
        if views < 1000.0:
            return f"{views:.1f}{unit}" if unit else f"{views:.0f}"
        views /= 1000.0
    return f"{views:.1f}T"

@app.on_message(filters.command(["song", "music"]))
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
        duration_formatted = shorten_views(duration)
        singer = results[0]["channel"]
        # Fetch total views using yt_dlp
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info_dict = ydl.extract_info(link, download=False)
            total_views = info_dict.get("view_count", "N/A")
            total_views_short = shorten_views(total_views)
    except Exception as ex:
        LOGGER.error(ex)
        return await m.edit_text(
            f"<b>Failed to fetch track from YouTube.\n●ʀᴇᴀsᴏɴ:</b> `{ex}`"
        )

    await m.edit_text("»⏳ᴅᴏᴡɴʟᴏᴀᴅɪɴɢ sᴏɴɢ, ᴘʟᴇᴀsᴇ ᴡᴀɪᴛ...!")
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info_dict = ydl.extract_info(link, download=False)
            audio_file = ydl.prepare_filename(info_dict)
            ydl.process_info(info_dict)
        bot_username = (await app.get_me()).username
        rep = f"<b>➠ ᴛɪᴛʟᴇ:</b> {title[:20]}\n<b>➠ ᴅᴜʀᴀᴛɪᴏɴ:</b> {duration_formatted}\n<b>➠ ᴛᴏᴛᴀʟ ᴠɪᴇᴡs:</b> {total_views_short}\n\n<b>➥ ᴜᴘʟᴏᴀᴅᴇᴅ ʙʏ:</b> @{bot_username}"
        secmul, dur, dur_arr = 1, 0, duration.split(":")
        for i in range(len(dur_arr) - 1, -1, -1):
            dur += int(dur_arr[i]) * secmul
            secmul *= 60
        try:
            await app.send_audio(
                chat_id=message.chat.id,  # Send the song in the same chat where the command was called
                audio=audio_file,
                caption=rep,
                thumb=thumb_name,
                title=title,
                duration=dur,
            )
            await m.delete()  # Delete the message indicating that the song is being downloaded
        except Exception as e:
            LOGGER.error(e)
            return await m.edit_text("Failed to send audio.")
    except Exception as e:
        LOGGER.error(e)
        return await m.edit_text("Failed to upload audio on Telegram servers.")

    try:
        os.remove(audio_file)
        os.remove(thumb_name)
    except Exception as ex:
        LOGGER.error(ex)
