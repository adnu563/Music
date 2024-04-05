import requests

def new_group_info(chat_name, chat_id, username, total_chat, added_by):
    message = "➻ ʙᴏᴛ ᴀᴅᴅᴇᴅ ᴛᴏ ɴᴇᴡ ɢʀᴏᴜᴘ! 🥳\n\n"
    message += "‣ ᴄʜᴀᴛ ɴᴀᴍᴇ: {}\n".format(chat_name)
    message += "‣ ᴄʜᴀᴛ ɪᴅ: {}\n".format(chat_id)
    message += "‣ ᴜsᴇʀɴᴀᴍᴇ: {}\n".format(username)
    message += "‣ ᴛᴏᴛᴀʟ ᴄʜᴀᴛ: {}\n".format(total_chat)
    message += "‣ ᴀᴅᴅᴇᴅ ʙʏ: {}\n".format(added_by)
    return message

def send_message_to_group(chat_id, message):
    url = f"https://api.telegram.org/botYOUR_BOT_TOKEN/sendMessage"
    payload = {"chat_id": chat_id, "text": message}
    response = requests.post(url, json=payload)
    return response.json()

def get_user_info(user_id):
    url = f"https://api.telegram.org/botYOUR_BOT_TOKEN/getChatMember"
    payload = {"chat_id": "YOUR_GROUP_CHAT_ID", "user_id": user_id}
    response = requests.get(url, params=payload)
    return response.json()

def kick_user_from_group(chat_id, user_id):
    url = f"https://api.telegram.org/botYOUR_BOT_TOKEN/kickChatMember"
    payload = {"chat_id": chat_id, "user_id": user_id}
    response = requests.post(url, json=payload)
    return response.json()