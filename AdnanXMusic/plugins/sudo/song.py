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

@app.on_message(filters.command(["song", "vsong", "video", "music"]))
async def song(_, message: Message):
    try:
        await message.delete()
    except:
        pass
    m = await message.reply_text("🔎")

    command = message.command[0].lower()

    if command == "video":
        try:
            query = " ".join(message.command[1:])
            results = YoutubeSearch(query, max_results=5).to_dict()
            link = f"https://youtube.com{results[0]['url_suffix']}"
            title = results[0]["title"][:40]
            thumbnail = results[0]["thumbnails"][0]
            thumb_name = f"thumb{title}.jpg"
            video_file = f"{title}.mp4"
            thumb_data = requests.get(thumbnail, allow_redirects=True)
            open(thumb_name, "wb").write(thumb_data.content)
        except Exception as ex:
            LOGGER.error(ex)
            return await m.edit_text(
                f"Failed to fetch video from YouTube.\n\n**Reason:** `{ex}`"
            )

        await m.edit_text("»⏳ᴅᴏᴡɴʟᴏᴀᴅɪɴɢ ᴠɪᴅᴇᴏ, ᴘʟᴇᴀsᴇ ᴡᴀɪᴛ...!")
        try:
            ydl_opts = {"format": "best"}
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info_dict = ydl.extract_info(link, download=True)
                video_file = ydl.prepare_filename(info_dict)
                duration = info_dict.get('duration', '')

            total_views = info_dict.get('view_count', '')
            total_views_short = shorten_views(total_views)

            bot_username = (await app.get_me()).username
            rep = f"➠  ᴛɪᴛʟᴇ: {title[:23]}\n➠ ᴅᴜʀᴀᴛɪᴏɴ: {duration}\n➠ ᴛᴏᴛᴀʟ: {total_views_short}\n\n➥ ᴜᴘʟᴏᴀᴅᴇᴅ ʙʏ: @{bot_username}"
            secmul, dur, dur_arr = 1, 0, duration.split(":")
        for i in range(len(dur_arr) - 1, -1, -1):
            dur += int(dur_arr[i]) * secmul
            secmul *= 60
            try:
                await app.send_video(
                    chat_id=message.chat.id,
                    video=video_file,
                    caption=rep,
                    thumb=thumb_name
                )
                await m.delete()  # Delete the message indicating that the video is being downloaded
            except Exception as e:
                LOGGER.error(e)
                return await m.edit_text("Failed to send video.")
        except Exception as e:
            LOGGER.error(e)
            return await m.edit_text("Failed to download and upload video.")

        try:
            if os.path.exists(video_file):
                os.remove(video_file)
            if os.path.exists(thumb_name):
                os.remove(thumb_name)
        except Exception as ex:
            LOGGER.error(ex)
