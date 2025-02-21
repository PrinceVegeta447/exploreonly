import asyncio
import random
import logging
import threading
from flask import Flask
from telethon import TelegramClient, events

# Configure logging
logging.basicConfig(format="[%(asctime)s] %(levelname)s: %(message)s", level=logging.INFO)

# Flask app for health check
app = Flask(__name__)

# Telegram account details (Replace with actual API credentials)
ACCOUNTS = [
    {"session": "session1", "api_id": 29848170, "api_hash": "e2b1cafae7b2492c625e19db5ec7f513"},
    {"session": "session2", "api_id": 29848170, "api_hash": "e2b1cafae7b2492c625e19db5ec7f513"},
    {"session": "session3", "api_id": 29848170, "api_hash": "e2b1cafae7b2492c625e19db5ec7f513"},
    {"session": "session4", "api_id": 29848170, "api_hash": "e2b1cafae7b2492c625e19db5ec7f513"}
]

# Group ID where the script will run
GROUP_ID = -1002348881334

# Bots to send /explore
BOTS = ["@CollectCricketersBot", "@CollectYourPlayerxBot"]

clients = []  # Store client instances

async def send_explore(client):
    """ Sends /explore to both bots in the group with a randomized delay """
    while True:
        for bot in BOTS:
            try:
                await client.send_message(GROUP_ID, f"/explore {bot}")
                logging.info(f"Sent /explore to {bot} from {client.session.filename}")
            except Exception as e:
                logging.error(f"Failed to send /explore to {bot}: {e}")
            delay = random.randint(310, 330)  # Randomized delay (310s - 330s)
            logging.info(f"Waiting {delay} seconds before next /explore...")
            await asyncio.sleep(delay)

async def handle_buttons(event):
    """ Clicks random inline buttons when bots send a message with buttons """
    if event.reply_markup and hasattr(event.reply_markup, 'rows'):
        buttons = []
        for row in event.reply_markup.rows:
            for btn in row.buttons:
                if hasattr(btn, "data"):  # Ensure it's an inline button
                    buttons.append(btn)

        if buttons:
            button = random.choice(buttons)  # Select a random button
            await asyncio.sleep(random.randint(3, 6))  # Random delay before clicking
            try:
                await event.click(buttons.index(button))  # Click the button
                logging.info(f"Clicked a button in response to {event.sender_id}")
            except Exception as e:
                logging.error(f"Failed to click a button: {e}")

async def start_client(account):
    """ Starts a client instance and runs event handlers """
    client = TelegramClient(account["session"], account["api_id"], account["api_hash"])
    await client.start()
    clients.append(client)  # Store client instance

    # Register event handler
    client.add_event_handler(handle_buttons, events.NewMessage(chats=GROUP_ID))

    # Start explore command loop in the background
    asyncio.create_task(send_explore(client))

    logging.info(f"Bot {account['session']} is running...")
    await client.run_until_disconnected()

async def main():
    """ Starts all Telegram accounts simultaneously """
    tasks = [start_client(account) for account in ACCOUNTS]
    await asyncio.gather(*tasks)

def run_asyncio():
    """ Run the asyncio event loop in a separate thread """
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(main())

# Start the asyncio loop in a separate thread
threading.Thread(target=run_asyncio, daemon=True).start()

@app.route("/")
def health_check():
    """ Simple health check endpoint """
    return "Bot is running!", 200

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000)  # Required for Koyeb TCP health check
