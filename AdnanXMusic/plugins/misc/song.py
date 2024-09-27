import os
import re
import requests
import yt_dlp
from pyrogram import filters
from pyrogram.types import Message
from youtube_search import YoutubeSearch
from AdnanXMusic import app

BOT_MENTION = "AdnanXMusic"

# Create a downloads directory if it doesn't exist
if not os.path.exists("downloads"):
    os.makedirs("downloads")

def sanitize_filename(filename):
    """Remove or replace problematic characters in the filename."""
    sanitized = re.sub(r'[\\/*?:"<>|]', "_", filename)  # Replace problematic characters with underscores
    return sanitized[:50]  # Limit the filename length to 50 characters to avoid long path issues

def shorten_views(views):
    try:
        views = int(views)
    except ValueError:
        return views

    if views < 1000:
        return str(views)

    for unit in ["", "K", "M", "B"]:
        if views < 1000.0:
            return f"{views:.1f}{unit}" if unit else f"{views:.0f}"
        views /= 1000.0
    return f"{views:.1f}T"

@app.on_message(filters.command(["song", "music"]))
async def song(_, message: Message):
    try:
        await message.delete()  # Delete the command message
    except Exception:
        pass  # Silent fail if the message cannot be deleted

    m = await message.reply_text("🔎")

    query = " ".join(message.command[1:])

    try:
        # Search for the song on YouTube
        results = YoutubeSearch(query, max_results=5).to_dict()
        link = f"https://youtube.com{results[0]['url_suffix']}"
        title = results[0]["title"][:40]
        sanitized_title = sanitize_filename(title)  # Sanitize the title and shorten it
        thumbnail = results[0]["thumbnails"][0]
        thumb_name = f"downloads/thumb_{sanitized_title}.jpg"  # Save thumbnail in downloads directory
        thumb = requests.get(thumbnail, allow_redirects=True)
        with open(thumb_name, "wb") as thumb_file:
            thumb_file.write(thumb.content)
        duration = results[0]["duration"]
        duration_formatted = shorten_views(duration)
        singer = results[0]["channel"]

        # Fetch total views using yt_dlp with cookies
        ydl_opts = {
            "format": "bestaudio/best",
            "cookiefile": "AdnanXMusic/assets/cookies.txt",
            "quiet": True,
            "outtmpl": f"downloads/{sanitized_title}",  # Use sanitized title for download path
            "postprocessors": [{
                "key": "FFmpegExtractAudio",
                "preferredcodec": "mp3",
                "preferredquality": "320",  # Ensure highest quality audio (320kbps)
            }],
        }

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info_dict = ydl.extract_info(link, download=True)  # Force download, not just extract info
            total_views = info_dict.get("view_count", "N/A")
            total_views_short = shorten_views(total_views)

            # Get the actual downloaded file name
            downloaded_file = f"{(ydl.prepare_filename(info_dict))}.mp3"
            print(downloaded_file)


    except Exception as ex:
        return await m.edit_text(
            f"<b>Failed to fetch or download the track from YouTube.\n● Reason:</b> `{ex}`"
        )

    await m.edit_text("⏳ Downloading the song, please wait...")

    try:
        # Ensure the MP3 file exists before sending it
        if not os.path.exists(downloaded_file):
            raise FileNotFoundError(f"MP3 file not found: {downloaded_file}")

        bot_username = _.me.username
        rep = (
            f"<b>➠ Title:</b> {title[:20]}\n"
            f"<b>➠ Duration:</b> {duration_formatted}\n"
            f"<b>➠ Total Views:</b> {total_views_short}\n\n"
            f"<b>➥ Uploaded by:</b> @{bot_username}"
        )

        # Convert duration to seconds
        secmul, dur, dur_arr = 1, 0, duration.split(":")
        for i in range(len(dur_arr) - 1, -1, -1):
            dur += int(dur_arr[i]) * secmul
            secmul *= 60

        # Send the audio file to Telegram chat
        await app.send_audio(
            chat_id=message.chat.id,
            audio=downloaded_file,  # Use the correct MP3 file
            caption=rep,
            thumb=thumb_name,
            title=title,
            duration=dur,
        )
        await m.delete()  # Delete the "downloading" message
    except Exception as e:
        return await m.edit_text(f"Failed to send audio. Error: {e}")

    # Cleanup the downloaded files
    try:
        os.remove(downloaded_file)  # Ensure the MP3 file is removed
        os.remove(thumb_name)  # Ensure the thumbnail is removed
    except Exception:
        pass  # Silent fail for file cleanup
