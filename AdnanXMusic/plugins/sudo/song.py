import os
import requests
from pyrogram import filters
from pyrogram.types import Message
from AdnanXMusic import app

@app.on_message(filters.command("download"))
async def download_video(_, message: Message):
    try:
        await message.delete()
    except:
        pass

    m = await message.reply_text("🔎 Downloading video, please wait...")

    link = message.text.split(" ", 1)[1]

    try:
        response = requests.get(link)
        if response.status_code == 200:
            content = response.text

            # Check if it's an index link or m3u8 link
            if "m3u8" in content:
                # Extract the direct video link from m3u8 content
                direct_link = extract_direct_link_from_m3u8(content)
            elif "index" in content:
                # Extract the direct video link from index content
                direct_link = extract_direct_link_from_index(content)
            else:
                raise ValueError("Unsupported link format")

            # Download the video
            video_file = "downloaded_video.mp4"
            with open(video_file, "wb") as f:
                video_response = requests.get(direct_link)
                f.write(video_response.content)

            # Send the video to the user
            await app.send_video(message.chat.id, video_file, caption="Downloaded video")

            # Delete temporary files
            os.remove(video_file)

            await m.delete()  # Delete the message indicating downloading
        else:
            await m.edit_text("Failed to fetch video link.")
    except Exception as e:
        await m.edit_text(f"Error: {e}")

def extract_direct_link_from_m3u8(content):
    # Logic to extract direct video link from m3u8 content
    pass

def extract_direct_link_from_index(content):
    # Logic to extract direct video link from index content
    pass