import time
import subprocess
import random
import json
from instagrapi import Client
import os
from dotenv import python-dotenv

load_dotenv()
BOT_USERNAME = os.getenv("BOT_USERNAME")
BOT_PASSWORD = os.getenv("BOT_PASSWORD")
ALLOWED_USERS = set(os.getenv("ALLOWED_USERS", "").split(","))

PREFIX = f"@{BOT_USERNAME}"
SESSION_FILE = "session.json"

# Whitelist of Instagram user IDs allowed to run commands

cl = Client()

def login():
    try:
        cl.load_settings(SESSION_FILE)
        cl.login(BOT_USERNAME, BOT_PASSWORD)
        print("Logged in from session")
    except:
        cl.login(BOT_USERNAME, BOT_PASSWORD)
        cl.dump_settings(SESSION_FILE)
        print("Fresh login, session saved")

def run_command(cmd):
    try:
        result = subprocess.run(
            cmd, shell=True, capture_output=True,
            text=True, timeout=10
        )
        output = result.stdout or result.stderr or "(no output)"
    except subprocess.TimeoutExpired:
        output = "Error: command timed out"
    except Exception as e:
        output = f"Error: {e}"

    # Split into chunks of 900 chars for Instagram's limit
    chunks = [output[i:i+900] for i in range(0, len(output), 900)]
    return chunks

def poll():
    seen = set()
    print("Bot is running...")
    while True:
        try:
            threads = cl.direct_threads()
            for thread in threads:
                for msg in thread.messages:
                    if msg.id in seen:
                        continue
                    seen.add(msg.id)

                    text = msg.text or ""
                    if not text.lower().startswith(PREFIX.lower()):
                        continue

                    # Auth check
                    if str(msg.user_id) not in ALLOWED_USERS:
                        cl.direct_send("❌ Not authorized.", thread_ids=[thread.id])
                        continue

                    cmd = text[len(PREFIX):].strip()
                    if not cmd:
                        continue

                    print(f"[CMD] {cmd}")
                    chunks = run_command(cmd)
                    for chunk in chunks:
                        cl.direct_send(f"```\n{chunk}\n```", thread_ids=[thread.id])
                        time.sleep(1)

        except Exception as e:
            print(f"Error: {e}")
            time.sleep(30)  # wait longer on error

        time.sleep(random.uniform(6, 12))

login()
poll()