import telegram
from telegram.ext import Updater, CommandHandler
import requests

# Telegram Bot Token
TOKEN = 'YOUR_TELEGRAM_BOT_TOKEN'

# Daisy API Key
DAISY_API_KEY = 'sVxZkVBLQJiqSAwDCSXcniPu7oH3rs'

# Daisy API Endpoint for OTP generation
DAISY_API_URL = 'https://api.daisy.com/generate_otp'

# Daisy Pricing Endpoint
DAISY_PRICING_URL = 'https://api.daisy.com/pricing'

# Handler for /start command
def start(update, context):
    update.message.reply_text('Welcome to the OTP generator bot! Use /generate_otp to get your OTP number.')

# Handler for /generate_otp command
def generate_otp(update, context):
    # Call Daisy API to generate OTP
    headers = {'Authorization': f'Bearer {DAISY_API_KEY}'}
    try:
        response = requests.get(DAISY_API_URL, headers=headers)
        if response.status_code == 200:
            otp = response.json().get('otp')
            update.message.reply_text(f'Your OTP is: {otp}')
            
            # Fetch Daisy pricing and service name
            pricing_response = requests.get(DAISY_PRICING_URL, headers=headers)
            if pricing_response.status_code == 200:
                pricing_data = pricing_response.json()
                service_name = pricing_data.get('service_name')
                pricing_list = pricing_data.get('pricing_list')
                update.message.reply_text(f'Service Name: {service_name}\n\nPricing List:\n{pricing_list}')
            else:
                update.message.reply_text('Failed to fetch Daisy pricing information.')
        else:
            update.message.reply_text('Failed to generate OTP. Please try again later.')
    except requests.RequestException as e:
        update.message.reply_text('Failed to connect to Daisy API. Please try again later.')

def main():
    updater = Updater(TOKEN, use_context=True)
    dp = updater.dispatcher

    # Add command handlers
    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CommandHandler("generate_otp", generate_otp))

    # Start the Bot
    updater.start_polling()
    updater.idle()

if __name__ == '__main__':
    main()
