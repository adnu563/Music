import os
import re
import requests
import yt_dlp
from pyrogram import filters
from pyrogram.types import Message
from youtube_search import YoutubeSearch
from PIL import Image  # For resizing the video thumbnail
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
        img = img.resize((1280, 720))  # Resizing to 1280x720 resolution
        img.save(output_path, "JPEG", quality=85)  # Saving as JPEG with 85% quality to reduce file size

@app.on_message(filters.command(["song", "music", "video", "yt"], prefixes=["/", "!", ".", ",", "#", "|"]))
async def download_media(_, message: Message):
    try:
        await message.delete()  # Delete the command message
    except Exception:
        pass  # Silent fail if the message cannot be deleted

    query = " ".join(message.command[1:])
    media_type = message.command[0].lower()

    # Respond based on the command type
    if media_type in ["song", "music"]:
        m = await message.reply_text("Downloading the song, Please Wait...")
    elif media_type in ["video", "yt"]:
        m = await message.reply_text("Downloading the video, please wait...")

    try:
        # Search for the media on YouTube
        results = YoutubeSearch(query, max_results=5).to_dict()
        link = f"https://youtube.com{results[0]['url_suffix']}"
        title = results[0]["title"][:40]
        sanitized_title = sanitize_filename(title)  # Sanitize the title and shorten it
        thumbnail = results[0]["thumbnails"][0]
        thumb_name = f"downloads/thumb_{sanitized_title}.jpg"  # Save thumbnail in downloads directory
        thumb = requests.get(thumbnail, allow_redirects=True)
        with open(thumb_name, "wb") as thumb_file:
            thumb_file.write(thumb.content)

        # Resize the thumbnail for video to 1280x720 if video
        if media_type in ["video", "yt"]:
            resized_thumb_name = f"downloads/thumb_{sanitized_title}_resized.jpg"
            resize_thumbnail(thumb_name, resized_thumb_name)

        duration = results[0]["duration"]
        duration_formatted = shorten_views(duration)
        singer = results[0]["channel"]

        if media_type in ["song", "music"]:
            # Song download options
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

        elif media_type in ["video", "yt"]:
            # Video download options
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

            if media_type in ["song", "music"]:
                # Get the actual downloaded file name for song
                downloaded_file = f"{(ydl.prepare_filename(info_dict))}.mp3"
                print(f"Downloaded song path: {downloaded_file}")
            elif media_type in ["video", "yt"]:
                # Get the actual downloaded file name and ensure .mp4 is used
                downloaded_file = ydl.prepare_filename(info_dict)
                downloaded_file = downloaded_file.replace(".webm", ".mp4")  # Remove .webm extension if exists
                print(f"Downloaded video path: {downloaded_file}")

    except Exception as ex:
        return await m.edit_text(
            f"<b>Failed to fetch or download the {media_type} from YouTube.\n● Reason:</b> `{ex}`"
        )

    try:
        # Ensure the media file exists before sending it
        if not os.path.exists(downloaded_file):
            raise FileNotFoundError(f"{media_type.capitalize()} file not found: {downloaded_file}")

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

        if media_type in ["song", "music"]:
            # Send the audio file to Telegram chat
            await app.send_audio(
                chat_id=message.chat.id,
                audio=downloaded_file,  # Use the correct MP3 file
                caption=rep,
                thumb=thumb_name,
                title=title,
                duration=dur,
            )

        elif media_type in ["video", "yt"]:
            # Send the video file to Telegram chat with resized thumbnail
            await app.send_video(
                chat_id=message.chat.id,
                video=downloaded_file,  # Use the correct video file
                caption=rep,
                thumb=resized_thumb_name,  # Use the resized 1280x720 thumbnail
                duration=dur,
            )

        await m.delete()  # Delete the "downloading" message
        
        # After successful upload, remove the video and thumbnails
        if os.path.exists(downloaded_file):
            os.remove(downloaded_file)
        if media_type in ["video", "yt"]:
            if os.path.exists(resized_thumb_name):
                os.remove(resized_thumb_name)
        if os.path.exists(thumb_name):
            os.remove(thumb_name)

    except Exception as e:
        # Handle message editing error
        try:
            return await m.edit_text(f"Failed to send {media_type}. Error: {e}")
        except pyrogram.errors.exceptions.bad_request_400.MessageIdInvalid:
            # The message might be already deleted or invalid, so just pass silently
            pass
