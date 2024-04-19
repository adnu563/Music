import asyncio
import importlib

from pyrogram import idle
from pytgcalls.exceptions import NoActiveGroupCall

import config
from AdnanXMusic import LOGGER, app, userbot
from AdnanXMusic.core.call import Adnany
from AdnanXMusic.misc import sudo
from AdnanXMusic.plugins import ALL_MODULES
from AdnanXMusic.utils.database import get_banned_users, get_gbanned
from config import BANNED_USERS


async def init():
    if (
        not config.STRING1
        and not config.STRING2
        and not config.STRING3
        and not config.STRING4
        and not config.STRING5
    ):
        LOGGER(__name__).error("Assistant client variables not defined, exiting...")
        exit()
    await sudo()
    try:
        users = await get_gbanned()
        for user_id in users:
            BANNED_USERS.add(user_id)
        users = await get_banned_users()
        for user_id in users:
            BANNED_USERS.add(user_id)
    except:
        pass
    await app.start()
    for all_module in ALL_MODULES:
        importlib.import_module("AdnanXMusic.plugins" + all_module)
    LOGGER("AdnanXMusic.plugins").info("Successfully Imported Modules...")
    await userbot.start()
    await Adnany.start()
    try:
        await Adnany.stream_call("https://te.legra.ph/file/29f784eb49d230ab62e9e.mp4")
    except NoActiveGroupCall:
        LOGGER("AdnanXMusic").error(
            "Please turn on the videochat of your log group\channel.\n\nStopping Bot..."
        )
        exit()
    except:
        pass
    await Adnany.decorators()
    LOGGER("AdnanXMusic").info(
        "\x41\x64\x6e\x61\x6e\x58\x4d\x75\x73\x69\x63\x20\x53\x74\x61\x72\x74\x65\x64\x20\x53\x75\x63\x63\x65\x73\x73\x66\x75\x6c\x6c\x79\x2e\x20\x44\x6f\x6e\x27\x74\x20\x46\x6f\x72\x67\x65\x74\x20\x54\x6f\x20\x56\x69\x73\x69\x74\x20\x40\x4d\x75\x73\x69\x63\x42\x6f\x74\x47\x68\x6f\x72\x20\x26\x20\x40\x4d\x75\x73\x69\x63\x47\x68\x6f\x72"
    )
    await idle()
    await app.stop()
    await userbot.stop()
    LOGGER("AdnanXMusic").info("Stopping AdnanX Music Bot...")


if __name__ == "__main__":
    asyncio.get_event_loop().run_until_complete(init())
