import os
import requests
from AdnanXMusic import app
from telethon import TelegramClient, events
import config
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize the Telegram Client
client = TelegramClient('bot_session', config.API_ID, config.API_HASH)

async def main():
    await client.start(bot_token=config.BOT_TOKEN)
    logger.info("Bot has been started successfully.")

    @client.on(events.NewMessage(pattern=r'/info (\@\w+)'))
    async def handler(event):
        username = event.pattern_match.group(1)  # Extract the username from the command
        if username:
            try:
                user = await client.get_entity(username)
                user_full_name = f"{user.first_name} {user.last_name if user.last_name else ''}".strip()
                user_id = user.id
                username = user.username
                response_message = (
                    f"User ID: {user_id}\n"
                    f"Full Name: {user_full_name}\n"
                    f"Username: @{username if username else 'No username'}"
                )
                await event.respond(response_message)
                logger.info(f"Provided info for username {username}.")
            except Exception as e:
                await event.respond("Failed to retrieve information for the given username.")
                logger.error(f"Error retrieving user info: {str(e)}")
        else:
            await event.respond("Please provide a valid username after the /info command.")

    await client.run_until_disconnected()

if __name__ == '__main__':
    client.loop.run_until_complete(main())
