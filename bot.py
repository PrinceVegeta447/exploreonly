import os
import random
import asyncio
from flask import Flask
from telethon import TelegramClient, events
from telethon.errors import rpcerrorlist

# Flask app for Koyeb health check
app = Flask(__name__)

@app.route("/")
def health_check():
    return "OK", 200  # TCP health check

# Telegram API credentials
API_ID = 3710681  # Replace with your API_ID
API_HASH = "1e3d595aca458a77e200bdf5b4032721"  # Replace with your API_HASH
BOT_USERNAME = "@CollectCricketersBot"  # Replace with your bot's username

# Get all Telethon session files
session_files = [f for f in os.listdir() if f.endswith(".session")]

# Function to automate /explore command
async def explore(client):
    while True:
        try:
            # Send the /explore command
            await client.send_message(BOT_USERNAME, "/explore")
            await asyncio.sleep(2)  # Wait for bot response

            # Fetch latest messages with buttons
            async for message in client.iter_messages(BOT_USERNAME, limit=5):
                if message.buttons:
                    buttons = message.buttons
                    button = random.choice(random.choice(buttons))  # Random button
                    await message.click(button.index)  # Click the button
                    break

            # Wait 310-320 seconds before repeating
            wait_time = random.randint(310, 320)
            await asyncio.sleep(wait_time)

        except rpcerrorlist.FloodWaitError as e:
            print(f"Rate limit hit! Sleeping for {e.seconds} seconds.")
            await asyncio.sleep(e.seconds)
        except Exception as e:
            print(f"Error: {e}")
            await asyncio.sleep(10)

# Start Telegram clients
async def start_clients():
    tasks = []
    for session in session_files:
        client = TelegramClient(session, API_ID, API_HASH)
        await client.start()
        print(f"{session} started!")
        tasks.append(asyncio.create_task(explore(client)))

    await asyncio.gather(*tasks)

# Run everything
if __name__ == "__main__":
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.create_task(start_clients())
    
    # Run Flask in a separate thread to avoid blocking the event loop
    from threading import Thread
    Thread(target=app.run, kwargs={"host": "0.0.0.0", "port": 8000}).start()

    loop.run_forever()
