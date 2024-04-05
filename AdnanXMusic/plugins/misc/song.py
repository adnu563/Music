import os
import configparser
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters
from youtube_dl import YoutubeDL

# Load bot token from config.ini file
config = configparser.ConfigParser()
config.read('config.ini')
TOKEN = config['telegram']['token']

# Define the function to handle the /start command
def start(update, context):
    update.message.reply_text("Welcome to Song Downloader Bot! Send me the name of the song you want to download.")

# Define the function to handle messages containing song names
def download_song(update, context):
    song_name = update.message.text
    try:
        # Search and download the song from YouTube
        ydl_opts = {
            'format': 'bestaudio/best',
            'outtmpl': '%(title)s.%(ext)s',
        }
        with YoutubeDL(ydl_opts) as ydl:
            result = ydl.extract_info(f"ytsearch1:{song_name}", download=False)
            if 'entries' in result:
                song_url = result['entries'][0]['webpage_url']
                ydl.download([song_url])
                song_file = f"{result['entries'][0]['title']}.mp3"
                update.message.reply_audio(open(song_file, 'rb'))
                os.remove(song_file)  # Remove the downloaded file after sending
            else:
                update.message.reply_text("Song not found.")
    except Exception as e:
        update.message.reply_text(f"An error occurred: {e}")

# Create the Telegram bot updater and dispatcher
updater = Updater(TOKEN, use_context=True)
dispatcher = updater.dispatcher

# Register the command handlers
dispatcher.add_handler(CommandHandler("start", start))
dispatcher.add_handler(MessageHandler(Filters.text & ~Filters.command, download_song))

# Start the bot
updater.start_polling()
updater.idle()