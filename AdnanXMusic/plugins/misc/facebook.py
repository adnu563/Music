import aiohttp
import asyncio
from aiogram import Bot, types, Dispatcher
from aiogram.dispatcher import executor
import requests
import config

bot = Bot(token=config.API_TOKEN)
dp = Dispatcher(bot)


async def download_video(url: str, file_name: str):
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as resp:
                if resp.status == 200:
                    with open(file_name, 'wb') as f:
                        f.write(await resp.read())
    except Exception as e:
        print("Error downloading video:", e)


@dp.message_handler(commands=['start'])
async def start(message: types.Message):
    await message.reply("Welcome! Send me a Facebook video link to download.")


@dp.message_handler(commands=['fb'])
async def download_facebook_video_command(message: types.Message):
    await download_facebook_video(message)


@dp.message_handler(regexp=r'^(https?:\/\/)?(www\.)?facebook\.com\/.*\/videos\/.+$')
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
    executor.start_polling(dp, skip_updates=True)
