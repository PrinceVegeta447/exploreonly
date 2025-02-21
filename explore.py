import asyncio
import random
import logging
import os
import glob
import threading
from flask import Flask
from telethon import TelegramClient, events

# Configure logging
logging.basicConfig(format="[%(asctime)s] %(levelname)s: %(message)s", level=logging.INFO)

# API credentials (should be the same for all sessions)
API_ID = 29848170  # Replace with your API ID
API_HASH = "e2b1cafae7b2492c625e19db5ec7f513"

# Group ID where the script will run
GROUP_ID = -1002348881334

# Bots to send /explore
BOTS = ["@CollectCricketersBot", "@CollectYourPlayerxBot"]

# Flask app for TCP health check
app = Flask(__name__)

@app.route("/healthz")
def health_check():
    return "OK", 200

async def send_explore(client):
    """ Sends /explore to both bots in the group with a randomized delay """
    while True:
        for bot in BOTS:
            try:
                await client.send_message(GROUP_ID, f"/explore {bot}")
                logging.info(f"Sent /explore to {bot}")
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
                
async def run_client(session_file):
    """ Starts a client with a specific session file """
    session_name = os.path.splitext(session_file)[0]
    client = TelegramClient(session_name, API_ID, API_HASH)
    
    try:
        await client.start()
    except Exception as e:
        logging.error(f"Failed to start session {session_name}: {e}")
        return  # Skip this session if it fails

    # Register event handler
    client.add_event_handler(handle_buttons, events.NewMessage(chats=GROUP_ID))

    logging.info(f"Bot {session_name} is running...")

    # Run send_explore in parallel
    await asyncio.gather(
        send_explore(client),  # Ensure this runs continuously
        client.run_until_disconnected()
            )

async def main():
    """ Main function to initialize multiple clients """
    session_files = glob.glob("*.session")  # Get all .session files
    if not session_files:
        logging.error("No session files found!")
        return

    tasks = [run_client(session) for session in session_files]
    await asyncio.gather(*tasks)  # Run all sessions concurrently

def start_flask():
    """ Runs Flask for health checks """
    app.run(host="0.0.0.0", port=5000)

# Run Flask in a separate thread
threading.Thread(target=start_flask, daemon=True).start()

# Run Telegram clients
asyncio.run(main())
