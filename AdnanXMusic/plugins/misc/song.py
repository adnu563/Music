import os
import requests
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
            video_data = requests.get(link)
            open(video_file, "wb").write(video_data.content)

            bot_username = (await app.get_me()).username
            rep = f"➠ Title: {title[:23]}\n\n➥ Uploaded by: @{bot_username}"
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
