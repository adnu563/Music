import os
import requests
import yt_dlp
from pyrogram import filters
from pyrogram.types import Message
from youtube_search import YoutubeSearch
from AdnanXMusic import app
import logging
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials

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

def find_spotify_config():
    # Define possible file names for Spotify API configuration file
    possible_filenames = ['spotify_config.cfg', 'spotify_credentials.cfg', 'spotify_config.json']

    # Search for the configuration file in predefined locations or in the current directory
    for filename in possible_filenames:
        if os.path.exists(filename):
            return filename
    return None

def initialize_spotify():
    # Find the Spotify API configuration file
    config_file = find_spotify_config()

    if config_file:
        # Initialize Spotify client using the found configuration file
        sp = spotipy.Spotify(auth_manager=SpotifyClientCredentials.from_config_file(config_file))
    else:
        # Log an error if the configuration file is not found
        LOGGER.error("Spotify API configuration file not found.")
        return None

    return sp

# Initialize Spotify client
sp = initialize_spotify()

@app.on_message(filters.command(["song", "music"]))
async def song(_, message: Message):
    try:
        await message.delete()
    except:
        pass
    m = await message.reply_text("🔎")

    query = " ".join(message.command[1:])
    ydl_opts = {"format": "bestaudio[ext=m4a]"}
    try:
        if "open.spotify.com" in query:
            if "track" in query:
                track_id = query.split("/")[-1]
                track_info = sp.track(track_id)
                title = track_info["name"]
                artist = track_info["artists"][0]["name"]
                duration_ms = track_info["duration_ms"]
                duration_formatted = shorten_views(duration_ms // 1000)
                total_views_short = "N/A"  # Spotify doesn't provide view count
                # Proceed with downloading the Spotify track here
            elif "album" in query:
                album_id = query.split("/")[-1]
                album_info = sp.album(album_id)
                # Proceed with fetching album information
            elif "playlist" in query:
                playlist_id = query.split("/")[-1]
                playlist_info = sp.playlist(playlist_id)
                # Proceed with fetching playlist information
            else:
                raise ValueError("Unsupported Spotify URL/URI")

        else:
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
    except (ValueError, spotipy.SpotifyException) as ex:
        LOGGER.error(ex)
        return await m.edit_text(
            f"<b>Failed to fetch track from YouTube/Spotify.\n●ʀᴇᴀsᴏɴ:</b> `{ex}`"
        )

    await m.edit_text("»⏳ᴅᴏᴡɴʟᴏᴀᴅɪɴɢ sᴏɴɢ, ᴘʟᴇᴀsᴇ ᴡᴀɪᴛ...!")
    try:
        if "open.spotify.com" in query:
            # Download the Spotify track here
            pass
        else:
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
