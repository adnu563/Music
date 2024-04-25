import os
import requests
import yt_dlp
from pyrogram import filters
from pyrogram.types import Message
from youtube_search import YoutubeSearch
from AdnanXMusic import app
from spotipy import Spotify, SpotifyException
from spotipy.oauth2 import SpotifyClientCredentials
import logging

# Initialize the LOGGER object
LOGGER = logging.getLogger(__name__)

# Configure the LOGGER object
logging.basicConfig(level=logging.ERROR)  # Set the logging level to ERROR or any level you prefer

BOT_MENTION = "AdnanXMusic"

# Fetch Spotify client ID and client secret from environment variables
spotify_client_id = os.environ.get("SPOTIFY_CLIENT_ID")
spotify_client_secret = os.environ.get("SPOTIFY_CLIENT_SECRET")

# Set Spotipy client ID
os.environ["SPOTIPY_CLIENT_ID"] = spotify_client_id

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

def fetch_spotify_track(query, spotify):
    try:
        # Search for the track using Spotify API
        result = spotify.search(q=query, type='track', limit=1)

        # Extract relevant track information
        track_info = {
            'title': result['tracks']['items'][0]['name'],
            'artist': result['tracks']['items'][0]['artists'][0]['name'],
            'duration_ms': result['tracks']['items'][0]['duration_ms'],
            'thumbnail': result['tracks']['items'][0]['album']['images'][0]['url'],
            'spotify_url': result['tracks']['items'][0]['external_urls']['spotify']
        }

        return track_info

    except SpotifyException as e:
        # Handle Spotify API exceptions
        LOGGER.error(f"Spotify API Error: {e}")
        raise Exception("Failed to fetch track from Spotify")

    except Exception as ex:
        # Handle other exceptions
        LOGGER.error(f"Error fetching track from Spotify: {ex}")
        raise Exception("Failed to fetch track from Spotify")

@app.on_message(filters.command(["song", "music"]))
async def song(_, message: Message):
    try:
        await message.delete()
    except:
        pass
    m = await message.reply_text("🔎")

    query = "".join(" " + str(i) for i in message.command[1:])
    try:
        # Check if the query is a Spotify URL
        if "spotify.com" in query:
            # Fetch track information from Spotify
            auth_manager = SpotifyClientCredentials(client_id=spotify_client_id, client_secret=spotify_client_secret)
            spotify = Spotify(auth_manager=auth_manager)
            track_info = fetch_spotify_track(query, spotify)
        else:
            # Fetch track information from YouTube
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
            ydl_opts = {
                'format': 'bestaudio/best',
                'extractaudio': True,
                'audioformat': 'mp3',
                'outtmpl': '%(title)s.%(ext)s',
            }
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info_dict = ydl.extract_info(link, download=False)
                total_views = info_dict.get("view_count", "N/A")
                total_views_short = shorten_views(total_views)
            track_info = {
                'title': title,
                'duration': duration_formatted,
                'thumbnail': thumbnail,
                'singer': singer,
                'total_views': total_views_short
            }

        # Extract track details from the track_info
        title = track_info['title']
        duration = track_info['duration']
        thumbnail = track_info['thumbnail']
        singer = track_info['singer']
        total_views = track_info['total_views']

    except Exception as ex:
        LOGGER.error(ex)
        return await m.edit_text(
            f"<b>Failed to fetch track.\n● Reason:</b> `{ex}`"
        )

    await m.edit_text("»⏳Downloading song, please wait...")

    try:
        # Download the audio file (YouTube or Spotify)
        # ...

        # Send the audio file with details
        await app.send_audio(
            chat_id=message.chat.id,
            audio=audio_file,
            caption=rep,
            thumb=thumb_name,
            title=title,
            duration=dur,
        )
        await m.delete()
    except Exception as e:
        LOGGER.error(e)
        return await m.edit_text("Failed to send audio.")

    try:
        os.remove(audio_file)
        os.remove(thumb_name)
    except Exception as ex:
        LOGGER.error(ex)
