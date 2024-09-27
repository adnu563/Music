import os
import re
import requests
import yt_dlp
from pyrogram import filters
from pyrogram.types import Message
from youtube_search import YoutubeSearch
from PIL import Image  # Import to resize the thumbnail
from AdnanXMusic import app

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

def resize_thumbnail(input_path, output_path):
    """Resize the thumbnail to 1280x720 and save it."""
    with Image.open(input_path) as img:
        img = img.resize((1280, 720))
        img.save(output_path)

@app.on_message(filters.command(["video", "yt"]))
async def video(_, message: Message):
    try:
        await message.delete()  # Delete the command message
    except Exception:
        pass  # Silent fail if the message cannot be deleted

    m = await message.reply_text("🔎")

    query = " ".join(message.command[1:])

    try:
        # Search for the video on YouTube
        results = YoutubeSearch(query, max_results=5).to_dict()
        link = f"https://youtube.com{results[0]['url_suffix']}"
        title = results[0]["title"][:40]
        sanitized_title = sanitize_filename(title)  # Sanitize the title and shorten it
        thumbnail = results[0]["thumbnails"][0]
        thumb_name = f"downloads/thumb_{sanitized_title}.jpg"  # Save thumbnail in downloads directory
        thumb = requests.get(thumbnail, allow_redirects=True)
        with open(thumb_name, "wb") as thumb_file:
            thumb_file.write(thumb.content)

        # Resize the thumbnail to 1280x720
        resized_thumb_name = f"downloads/thumb_{sanitized_title}_resized.jpg"
        resize_thumbnail(thumb_name, resized_thumb_name)

        duration = results[0]["duration"]
        duration_formatted = shorten_views(duration)
        singer = results[0]["channel"]

        # Fetch total views using yt_dlp with cookies, ensuring only mp4 format is used
        ydl_opts = {
            "format": "bestvideo[ext=mp4]+bestaudio[ext=m4a]/mp4",  # Force mp4 format
            "cookiefile": "AdnanXMusic/assets/cookies.txt",
            "quiet": True,
            "outtmpl": f"downloads/{sanitized_title}.%(ext)s",  # Ensure file extension is included
        }

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info_dict = ydl.extract_info(link, download=True)  # Force download, not just extract info
            total_views = info_dict.get("view_count", "N/A")
            total_views_short = shorten_views(total_views)

            # Get the actual downloaded file name and ensure .mp4 is used
            downloaded_file = ydl.prepare_filename(info_dict)
            downloaded_file = downloaded_file.replace(".webm", ".mp4")  # Remove .webm extension if exists
            print(f"Downloaded file path: {downloaded_file}")

    except Exception as ex:
        return await m.edit_text(
            f"<b>Failed to fetch or download the video from YouTube.\n● Reason:</b> `{ex}`"
        )

    await m.edit_text("⏳ Downloading the video, please wait...")

    try:
        # Ensure the video file exists before sending it
        if not os.path.exists(downloaded_file):
            raise FileNotFoundError(f"Video file not found: {downloaded_file}")

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

        # Send the video file to Telegram chat with resized thumbnail
        await app.send_video(
            chat_id=message.chat.id,
            video=downloaded_file,  # Use the correct video file
            caption=rep,
            thumb=resized_thumb_name,  # Use the resized thumbnail
            duration=dur,
        )
        await m.delete()  # Delete the "downloading" message
    except Exception as e:
        return await m.edit_text(f"Failed to send video. Error: {e}")

    # Cleanup the downloaded files
    try:
        os.remove(downloaded_file)  # Ensure the video file is removed
        os.remove(thumb_name)  # Ensure the original thumbnail is removed
        os.remove(resized_thumb_name)  # Ensure the resized thumbnail is removed
    except Exception:
        pass  # Silent fail for file cleanup
