import os
import requests
import threading
from flask import Flask
from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
import lyricsgenius

# --- 🌐 ZEABUR PORT BINDING ---
web_app = Flask(__name__)
@web_app.route('/')
def home(): return "Bot is Healthy and Running!"

def run_web():
    port = int(os.environ.get("PORT", 8080))
    web_app.run(host="0.0.0.0", port=port)

threading.Thread(target=run_web, daemon=True).start()

# --- 🟢 CONFIGURATION ---
API_ID = int(os.environ.get("API_ID", 38456866))
API_HASH = os.environ.get("API_HASH", "30a8f347f538733a1d57dae8cc458ddc")
BOT_TOKEN = os.environ.get("BOT_TOKEN", "8454384380:AAEsXBAm3IrtW3Hf1--2mH3xAyhnan-J3lg")
GENIUS_TOKEN = os.environ.get("GENIUS_TOKEN", "w-XTArszGpAQaaLu-JlViwy1e-0rxx4dvwqQzOEtcmmpYndHm_nkFTvAB5BsY-ww")

# Teri ID JSON se uthayi hai
OWNER_ID = 6593129349 

app = Client("LyricistBot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)

# --- 🎵 SEARCH FUNCTION ---
def search_saavn(query):
    search_url = f"https://jiosaavn-api-v3.vercel.app/search/songs?query={query}"
    try:
        response = requests.get(search_url, timeout=10)
        if response.status_code == 200:
            data = response.json()
            return data[0] if data else None
    except: return None

@app.on_message(filters.command("start"))
async def start(client, message):
    await message.reply_text(f"Hello {message.from_user.first_name}!\nBot is online on Zeabur! Send /song [name]")

@app.on_message(filters.command("song"))
async def song_handler(client, message):
    # FSUB bypass for testing
    query = " ".join(message.command[1:])
    if not query: 
        return await message.reply_text("Bhai, gaane ka naam toh likh! (e.g. /song Kesariya)")

    m = await message.reply_text("🔎 Searching and Downloading...")
    song_data = search_saavn(query)

    if not song_data:
        return await m.edit("❌ Song nahi mila ya API down hai.")

    try:
        title = song_data.get('song')
        download_url = song_data.get('media_url')
        thumb = song_data.get('image')
        
        audio_file = f"{title}.mp3"
        res = requests.get(download_url)
        with open(audio_file, 'wb') as f: 
            f.write(res.content)

        await message.reply_photo(photo=thumb, caption=f"🎵 **Title:** {title}\n⚡ **Powered by:** Zeabur")
        await message.reply_audio(audio=open(audio_file, 'rb'), title=title)
        
        if os.path.exists(audio_file):
            os.remove(audio_file)
        await m.delete()
        
    except Exception as e:
        await m.edit(f"Error: {e}")

print("Bot is starting...")
app.run()
