import os
import asyncio
import random
import logging
from flask import Flask, jsonify
from telethon import TelegramClient, events

# Flask app for health checks
app = Flask(__name__)

@app.route("/health", methods=["GET"])
def health_check():
    return jsonify({"status": "running"}), 200

# Logging setup
logging.basicConfig(format="[%(asctime)s] %(levelname)s: %(message)s", level=logging.INFO)

# Telegram API credentials
API_ID = 20061115  # Replace with your API ID
API_HASH = "c30d56d90d59b3efc7954013c580e076"

# Session files for multiple accounts
SESSIONS = ["session_1.session", "session_2.session", "session_3.session", "session_4.session", "session_5.session", "session_6.session", "session_7.session", "session_8.session"]


# Group where explore commands are sent
EXPLORE_GROUP = -1002348881334
BOTS = ["@CollectCricketersBot", "@CollectYourPlayerxBot"]

# Explore delay range
MIN_EXPLORE_DELAY, MAX_EXPLORE_DELAY = 310, 330  

# Create clients for multiple sessions
clients = {}

async def send_explore(client, session_name):
    """Sends /explore command to bots at regular intervals."""
    logging.info(f"{session_name}: send_explore() started!")  # NEW LOG ADDED
    while True:
        logging.info(f"{session_name}: Checking if we can send /explore...")  # Debug
        for bot in BOTS:
            try:
                await client.send_message(EXPLORE_GROUP, f"/explore {bot}")
                logging.info(f"{session_name}: Sent /explore to {bot}")
            except Exception as e:
                logging.error(f"{session_name}: Failed to send /explore - {e}")
        delay = random.randint(MIN_EXPLORE_DELAY, MAX_EXPLORE_DELAY)
        logging.info(f"{session_name}: Waiting {delay} sec before next /explore...")
        await asyncio.sleep(delay)
        
async def handle_buttons(event):
    """Clicks random inline buttons when bots send messages with buttons."""
    if event.reply_markup and hasattr(event.reply_markup, 'rows'):
        buttons = [btn for row in event.reply_markup.rows for btn in row.buttons if hasattr(btn, "data")]
        if buttons:
            button = random.choice(buttons)
            await asyncio.sleep(random.randint(3, 6))
            try:
                await event.click(buttons.index(button))
                logging.info(f"Clicked a button in response to {event.sender_id}")
            except Exception as e:
                logging.error(f"Failed to click button: {e}")

async def start_client(session_name):
    """Starts a single client."""
    client = TelegramClient(session_name, API_ID, API_HASH)
    
    logging.info(f"{session_name}: Starting client...")  
    await client.start()
    
    # ✅ Confirm bot is logged in before proceeding
    me = await client.get_me()
    if not me:
        logging.error(f"{session_name}: Login failed! Check session file.")
        return  # Exit if login fails
    
    logging.info(f"{session_name}: Logged in as {me.username or me.id}")  

    client.add_event_handler(handle_buttons, events.NewMessage(chats=EXPLORE_GROUP))

    asyncio.create_task(send_explore(client, session_name))  # ✅ Ensure explore function runs
    await client.run_until_disconnected()


async def start_clients():
    """Starts all clients asynchronously."""
    tasks = [start_client(session) for session in SESSIONS]
    await asyncio.gather(*tasks)

async def main():
    """Main entry point for running bots."""
    await start_clients()
    logging.info("Bots are running...")
    await asyncio.Future()  # Keep running indefinitely

# Start the Flask health check in the background
def run_flask():
    app.run(host="0.0.0.0", port=8000)

if __name__ == "__main__":
    import threading
    threading.Thread(target=run_flask, daemon=True).start()
    asyncio.run(main())
