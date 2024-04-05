import os
import requests
import yt_dlp
from pyrogram import filters
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup, Message
from youtube_search import YoutubeSearch
from AdnanXMusic import app
from AdnanXMusic.logging import LOGGER

BOT_MENTION = "AdnanXMusic"

# Define a command handler for the song command in public chats
@app.on_message(filters.command(["song", "vsong", "video", "music"]) & ~filters.private)
async def song(_, message: Message):
    try:
        await message.delete()
    except:
        pass
    # Reply to the user indicating that the bot is searching for the song
    m = await message.reply_text("🔎")

    # Get the query from the command
    query = " ".join(message.command[1:])
    # Define options for downloading the audio from YouTube
    ydl_opts = {"format": "bestaudio[ext=m4a]"}
    try:
        # Search YouTube for the query and get the results
        results = YoutubeSearch(query, max_results=5).to_dict()
        # Extract the title, thumbnail, link, and duration of the first result
        title = results[0]["title"][:80]
        thumbnail = results[0]["thumbnails"][0]
        thumb_name = f"thumb{title}.jpg"
        # Download and save the thumbnail
        thumb = requests.get(thumbnail, allow_redirects=True)
        open(thumb_name, "wb").write(thumb.content)
        link = f'https://www.youtube.com{results[0]["url_suffix"]}'
        duration = results[0]["duration"]

    except Exception as ex:
        # If there's an error fetching the song from YouTube, log the error and inform the user
        LOGGER.error(ex)
        return await m.edit_text(
            f"Failed to fetch track from YouTube.\n\n**Reason: `{ex}`"
        )

    # Inform the user that the song is being downloaded
    await m.edit_text("»⏳ Downloading Song, Please wait...!")
    try:
        # Download the audio from YouTube using youtube-dl
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info_dict = ydl.extract_info(link, download=False)
            audio_file = ydl.prepare_filename(info_dict)
            ydl.process_info(info_dict)
        # Construct a caption for the audio message
        rep = f"☁️ᴛɪᴛʟᴇ: [{title[:23]}]\n⏱ ᴅᴜʀᴀᴛᴏɴ: `{duration}` \n👀 ᴛᴏᴛᴀʟ: {total_views}\n\n⏳ ᴜᴘʟᴏᴀᴅᴇᴅ ʙʏ: {app.mention(BOT_MENTION)})"
        secmul, dur, dur_arr = 1, 0, duration.split(":")
        for i in range(len(dur_arr) - 1, -1, -1):
            dur += int(dur_arr[i]) * secmul
            secmul *= 60
        # Construct an inline keyboard button to link back to the YouTube video
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
        # Send the audio message to the chat where the command was received
        await app.send_audio(
            chat_id=message.chat.id,  # Send to the same chat where the command was received
            audio=audio_file,
            caption=rep,
            thumb=thumb_name,
            title=title,
            duration=dur,
            reply_markup=visit_butt,
        )
        # Inform the user that the song has been successfully downloaded
        await m.edit_text("» ✅SONG DOWNLOADED SUCCESSFULLY.")
        # Delete the search message
        await m.delete()
    except Exception as e:
        # If there's an error uploading the audio, inform the user
        LOGGER.error(e)
        return await m.edit_text("Failed to upload audio on Telegram servers.")

    # Clean up downloaded files
    try:
        os.remove(audio_file)
        os.remove(thumb_name)
    except Exception as ex:
        LOGGER.error(ex)
