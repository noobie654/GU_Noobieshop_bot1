import asyncio
import logging
import os
import re
from telethon import TelegramClient, events
from telethon.tl.types import Channel, PeerChannel
from flask import Flask
import threading

# Configure logging
logging.basicConfig(level=logging.INFO)

# Use environment variables for API ID, API hash, and bot token
api_id = int(os.getenv('API_ID', ''))
api_hash = os.getenv('API_HASH', '')
bot_token = os.getenv('BOT_TOKEN', '')

# Ensure API ID is an integer
try:
    api_id = int(api_id)
except ValueError:
    logging.error("Invalid API ID. Please check your environment variables.")
    exit(1)

# Initialize the Telegram client
client = TelegramClient('GU_Noobieshop_bot_new', api_id, api_hash).start(bot_token=bot_token)

# Set passwords
BOT_PASSWORDS = ['@Antor1040', '@NoobieNoiso', '@RionMental26']

# Dictionary to track unlocked users
unlocked_users = {}

# Regular expression to match URLs
url_pattern = re.compile(r'(https://t.me/\w+)')

# Flask app setup
app = Flask(__name__)

@app.route('/')
def hello():
    return "GU_Noobieshop Bot is running!"

# Function to run the Flask app
def run_flask():
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))

# Event to handle /start command
@client.on(events.NewMessage(pattern='/start'))
async def start(event):
    await event.respond(
        "Welcome to GU_Noobieshop Bot! Please get the password from the admin:\n"
        "Contact Support: [Noobie Support](https://t.me/NoobieXNoiso)\n"
        "Join our Channel: [Noobie Channel](https://t.me/NoobieShopp)",
        parse_mode='markdown'
    )

# Event to handle new messages
@client.on(events.NewMessage)
async def handle_message(event):
    user_id = event.sender_id

    if unlocked_users.get(user_id):
        group_url = event.text.strip()

        if not url_pattern.match(group_url):
            await event.respond("Please provide a valid group or channel URL.")
            return

        try:
            group = await client.get_entity(group_url)
            if isinstance(group, (PeerChannel, Channel)):
                usernames = []
                async for member in client.iter_participants(group):
                    if member.username:
                        usernames.append(f"@{member.username}")

                if usernames:
                    await send_long_message(event, "Usernames:\n" + "\n".join(usernames))
                else:
                    await event.respond("No usernames found in this group or channel.")
            else:
                await event.respond("The provided link is not a valid group or channel URL.")
        except Exception as e:
            logging.error(f"Error fetching usernames: {str(e)}")
            await event.respond(f"Error fetching usernames: {str(e)}")
    elif event.text in BOT_PASSWORDS:
        unlocked_users[user_id] = True
        await event.respond("✅ Bot unlocked successfully! Please enter the group or channel URL:")
    else:
        await event.respond("Incorrect password. Please try again.")

# Function to send long messages
async def send_long_message(event, message):
    max_length = 4096
    for i in range(0, len(message), max_length):
        await event.respond(message[i:i + max_length])
        await asyncio.sleep(1)

# Run the Telegram bot in a separate thread
def run_telegram():
    client.run_until_disconnected()

if __name__ == "__main__":
    # Start Flask in a separate thread
    flask_thread = threading.Thread(target=run_flask)
    flask_thread.start()

    # Start Telegram bot
    run_telegram()
