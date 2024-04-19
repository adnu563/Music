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

@app.on_message(filters.command(["song", "vsong", "video", "music"]))
async def song(_, message: Message):
    try:
        await message.delete()
    except:
        pass
    m = await message.reply_text("🔎")

    command = message.command[0].lower()

    if command == "vsong":
        try:
            query = "".join(" " + str(i) for i in message.command[1:])
            ydl_opts = {"format": "best"}
            results = YoutubeSearch(query, max_results=5).to_dict()
            link = f"https://youtube.com{results[0]['url_suffix']}"
            title = results[0]["title"][:40]
            thumbnail = results[0]["thumbnails"][0]
            thumb_name = f"thumb{title}.jpg"
            thumb = requests.get(thumbnail, allow_redirects=True)
            open(thumb_name, "wb").write(thumb.content)
            duration = results[0]["duration"]

            # Fetch total views using yt_dlp
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info_dict = ydl.extract_info(link, download=False)
                total_views = info_dict.get("view_count", "N/A")
        except Exception as ex:
            LOGGER.error(ex)
            return await m.edit_text(
                f"Failed to fetch video from YouTube.\n\n**Reason:** `{ex}`"
            )

        await m.edit_text("»⏳ᴅᴏᴡɴʟᴏᴀᴅɪɴɢ ᴠɪᴅᴇᴏ, ᴘʟᴇᴀsᴇ ᴡᴀɪᴛ...!")
        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info_dict = ydl.extract_info(link, download=True)
                video_file = info_dict.get('filename')

                if not video_file:
                    raise Exception("Failed to download video: No video file found")

            bot_username = (await app.get_me()).username
            rep = f"➠ Title: {title[:23]}\n➠ Duration: {duration}\n➠ Total Views: {total_views}\n\n➥ Uploaded by: @{bot_username}"
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
                await app.send_video(
                    chat_id=message.chat.id,  # Send the video in the same chat where the command was called
                    video=video_file,
                    caption=rep,
                    thumb=thumb_name,
                    duration=int(info_dict.get('duration', 0)),
                    reply_markup=visit_butt,
                )
                await m.delete()  # Delete the message indicating that the video is being downloaded
            except Exception as e:
                LOGGER.error(e)
                return await m.edit_text("Failed to send video.")
        except Exception as e:
            LOGGER.error(e)
            return await m.edit_text("Failed to upload video on Telegram servers.")

        try:
            if video_file and os.path.exists(video_file):
                os.remove(video_file)
            if thumb_name and os.path.exists(thumb_name):
                os.remove(thumb_name)
        except Exception as ex:
            LOGGER.error(ex)
