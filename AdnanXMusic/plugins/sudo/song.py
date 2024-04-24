import os
import requests
from pyrogram import filters
from pyrogram.types import Message
from AdnanXMusic import app

@app.on_message(filters.command("download_mkv"))
async def download_mkv_video(_, message: Message):
    try:
        await message.delete()
    except:
        pass

    m = await message.reply_text("🔎 Downloading MKV video, please wait...")

    mkv_link = message.text.split(" ", 1)[1]

    try:
        response = requests.get(mkv_link)
        if response.status_code == 200:
            content = response.text

            # Extract the direct video link from MKV content
            direct_link = extract_direct_link_from_mkv(content)

            # Download the video
            video_file = "downloaded_mkv_video.mkv"
            with open(video_file, "wb") as f:
                video_response = requests.get(direct_link)
                f.write(video_response.content)

            # Send the video to the user
            await app.send_video(message.chat.id, video_file, caption="Downloaded MKV video")

            # Delete temporary files
            os.remove(video_file)

            await m.delete()  # Delete the message indicating downloading
        else:
            await m.edit_text("Failed to fetch MKV video link.")
    except Exception as e:
        await m.edit_text(f"Error: {e}")

def extract_direct_link_from_mkv(content):
    # Logic to extract direct video link from MKV content
    pass