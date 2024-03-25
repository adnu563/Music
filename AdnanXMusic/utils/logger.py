from config import LOGGER_ID
from AdnanXMusic import app
from AdnanXMusic.utils.database import is_on_off

async def play_logs(message, streamtype):
    if await is_on_off(LOGGER_ID):  # Replace LOG with LOGGER_ID
        if message.chat.username:
            chatusername = f"@{message.chat.username}"
        else:
            chatusername = "Private Group"
        logger_text = f"""
**AdnanXMusic PLAY LOG**

**Chat:** {message.chat.title} [`{message.chat.id}`]
**User:** {message.from_user.mention}
**Username:** @{message.from_user.username}
**User ID:** `{message.from_user.id}`
**Chat Link:** {chatusername}

**Query:** {message.text}

**StreamType:** {streamtype}"""
        if message.chat.id != LOG_GROUP_ID:
            try:
                await app.send_message(
                    LOG_GROUP_ID,
                    f"{logger_text}",
                    disable_web_page_preview=False,
                )
            except:
                pass
        return
