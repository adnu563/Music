import os
import requests
import yt_dlp
from pyrogram import filters
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup, Message
from youtube_search import YoutubeSearch
from AdnanXMusic import app
from AdnanXMusic.logging import LOGGER

BOT_MENTION = "AdnanXMusic"

@app.on_message(filters.command(["song", "vsong", "video", "music"]))
async def song(_, message: Message):
    try:
        await message.delete()
    except:
        pass
    m = await message.reply_text("🔎")

    query = " ".join(message.command[1:])
    ydl_opts = {"format": "bestaudio[ext=m4a]"}
    try:
        results = YoutubeSearch(query, max_results=5).to_dict()
        title = results[0]["title"][:40]
        thumbnail = results[0]["thumbnails"][0]
        thumb_name = f"thumb{title}.jpg"
        thumb = requests.get(thumbnail, allow_redirects=True)
        open(thumb_name, "wb").write(thumb.content)
        link = f'https://www.youtube.com{results[0]["url_suffix"]}'
        duration = results[0]["duration"]

    except Exception as ex:
        LOGGER.error(ex)
        return await m.edit_text(
            f"Failed to fetch track from YouTube.\n\n**Reason: `{ex}`"
        )

    await m.edit_text("» ⏳Downloading song, please wait..")
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info_dict = ydl.extract_info(link, download=False)
            audio_file = ydl.prepare_filename(info_dict)
            ydl.process_info(info_dict)
        rep = f"☁️Title: [{title[:23]}]\n⏱ Duration: `{duration}`\n ⏳Uploaded by: {BOT_MENTION}"
        secmul, dur, dur_arr = 1, 0, duration.split(":")
        for i in range(len(dur_arr) - 1, -1, -1):
            dur += int(dur_arr[i]) * secmul
            secmul *= 60
        try:
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
            await app.send_audio(
                chat_id=message.from_user.id,
                audio=audio_file,
                caption=rep,
                thumb=thumb_name,
                title=title,
                duration=dur,
                reply_markup=visit_butt,
            )
            if message.chat.type != 'private':
                await message.reply_text(
                    "Please check your PM, sent the requested song there."
                )
        except Exception as e:
            LOGGER.error(e)
            start_butt = InlineKeyboardMarkup(
                [
                    [
                        InlineKeyboardButton(
                            text="Click Here",
                            url=f"https://t.me/{BOT_USERNAME}?start",
                        )
                    ]
                ]
            )
            return await m.edit_text(
                text="Click on the button below and start me for downloading songs.",
                reply_markup=start_butt,
            )
        await m.delete()
    except Exception as e:
        LOGGER.error(e)
        return await m.edit_text("Failed to upload audio on Telegram servers.")

    try:
        os.remove(audio_file)
        os.remove(thumb_name)
        except Exception as e:
                print(f"Error sending message: {e}")

