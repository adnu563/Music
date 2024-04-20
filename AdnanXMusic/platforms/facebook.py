import os
import aiohttp
import asyncio
from aiogram import Bot, types
from aiogram.dispatcher import Dispatcher
from aiogram.types import ParseMode
from aiogram.utils import executor
import requests
from confiq import
from AdnanXMusic.utils.database import is_on_off
from AdnanXMusic.utils.formatters import time_to_seconds

BOT MENTION = "AdnanXMusic"

API_TOKEN = '6613472799:AAFeDrOP1k_Ipie5KOUAn_Kj5tN7ZshriWw'

bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot)


async def download_video(url: str, file_name: str):
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as resp:
            if resp.status == 200:
                with open(file_name, 'wb') as f:
                    f.write(await resp.read())


@dp.message_handler(commands=['start'])
async def start(message: types.Message):
    await message.reply("Welcome! Send me a Facebook video link to download.")


@dp.message_handler(regexp=r'^(https?:\/\/)?(www\.)?facebook\.com\/.*\/videos\/.+$')
async def download_facebook_video(message: types.Message):
    url = message.text
    response = requests.get(url)
    video_url = None
    if response.status_code == 200:
        video_url = response.json()['data'][0]['source']
    if video_url:
        file_name = f"video_{message.message_id}.mp4"
        await message.reply("Downloading video...")
        await download_video(video_url, file_name)
        await message.reply_document(types.InputFile(file_name))
    else:
        await message.reply("Sorry, couldn't find a video in the provided link.")


if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
