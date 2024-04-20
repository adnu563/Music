import aiohttp
import asyncio
from aiogram import Bot, types
import youtube_dl
import requests
import config

bot = Bot(token=config.API_TOKEN)


async def download_video(url: str, file_name: str):
    ydl_opts = {'outtmpl': file_name}
    with youtube_dl.YoutubeDL(ydl_opts) as ydl:
        ydl.download([url])


@bot.message_handler(commands=['start'])
async def start(message: types.Message):
    await message.reply("Welcome! Send me a Facebook video link to download.")


@bot.message_handler(regexp=r'^(https?:\/\/)?(www\.)?facebook\.com\/.*\/videos\/.+$')
async def download_facebook_video(message: types.Message):
    try:
        url = message.text
        response = requests.get(url)
        print("Facebook API Response:", response.content)  # Debugging
        video_url = None
        if response.status_code == 200:
            try:
                video_url = response.json()['data'][0]['source']
            except KeyError:
                pass
        if video_url:
            file_name = f"video_{message.message_id}.mp4"
            await message.reply("Downloading video...")
            await download_video(video_url, file_name)
            await message.reply_document(types.InputFile(file_name))
        else:
            await message.reply("Sorry, couldn't find a video in the provided link.")
    except Exception as e:
        print("Error processing Facebook video link:", e)


if __name__ == '__main__':
    bot.polling()
