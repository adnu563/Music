import os
import requests
from pyrogram import filters
from pyrogram.types import Message
from youtube_search import YoutubeSearch
from AdnanXMusic import app

@app.on_message(filters.command(download"))
async def download_video(_, message: Message):
    try:
        await message.delete()
    except:
        pass

    m = await message.reply_text("🔎 Downloading video, please wait...")

    link = message.text.split(" ", 1)[1]

    try:
        if link.startswith("https://www.youtube.com/") or link.startswith("https://m.youtube.com/"):
            # If it's a YouTube link
            if not link.startswith("https://www.youtube.com/watch?v="):
                # If the link is not a direct video link, search for the video
                query = link.split(" ", 1)[1]
                results = YoutubeSearch(query, max_results=1).to_dict()
                link = f"https://youtube.com{results[0]['url_suffix']}"

            # Stream the video from YouTube
            await stream_youtube_video(message.chat.id, link, m)

        elif link.endswith(".mkv"):
            # If it's an MKV file link
            await stream_mkv_video(message.chat.id, link, m)

        else:
            raise ValueError("Unsupported link format")

        await m.delete()  # Delete the message indicating downloading
    except Exception as e:
        await m.edit_text(f"Error: {e}")

async def stream_youtube_video(chat_id, link, m):
    try:
        # Logic to fetch and stream video from YouTube
        # You can use libraries like yt_dlp or pafy for this purpose
        pass
    except Exception as e:
        await m.edit_text(f"Error streaming YouTube video: {e}")

async def stream_mkv_video(chat_id, link, m):
    try:
        # Logic to fetch and stream video from MKV file link
        # You can use libraries like requests to stream the content directly
        pass
    except Exception as e:
        await m.edit_text(f"Error streaming MKV video: {e}")