import os
import requests
import threading
from flask import Flask
from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from pyrogram.errors import UserNotParticipant
import lyricsgenius

# --- 🌐 ZEABUR PORT BINDING (Isse Delete Mat Karna) ---
web_app = Flask(__name__)
@web_app.route('/')
def home(): return "Bot is Healthy and Running!"

def run_web():
    # Zeabur automatically assigns a port, we pick it from env
    port = int(os.environ.get("PORT", 8080))
    web_app.run(host="0.0.0.0", port=port)

threading.Thread(target=run_web, daemon=True).start()

# --- 🟢 CONFIGURATION ---
# Note: Inhe Zeabur ke "Variables" tab mein zaroor daalna
API_ID = int(os.environ.get("API_ID", 38456866))
API_HASH = os.environ.get("API_HASH", "30a8f347f538733a1d57dae8cc458ddc")
BOT_TOKEN = os.environ.get("BOT_TOKEN", "8454384380:AAEsXBAm3IrtW3Hf1--2mH3xAyhnan-J3lg")
GENIUS_TOKEN = os.environ.get("GENIUS_TOKEN", "w-XTArszGpAQaaLu-JlViwy1e-0rxx4dvwqQzOEtcmmpYndHm_nkFTvAB5BsY-ww")

CHANNEL_ID = -1003751644036 
CHANNEL_LINK = "https://t.me/+JPgViOHx7bdlMDZl"

app = Client("LyricistBot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)
genius = lyricsgenius.Genius(GENIUS_TOKEN)

# --- 🎵 STABLE SEARCH ---
def search_saavn(query):
    search_url = f"https://jiosaavn-api-v3.vercel.app/search/songs?query={query}"
    try:
        response = requests.get(search_url, timeout=10)
        if response.status_code == 200:
            data = response.json()
            return data[0] if data else None
    except: return None

# --- 🔐 FSUB ---
async def check_fsub(client, message):
    try:
        await client.get_chat_member(CHANNEL_ID, message.from_user.id)
        return True
    except:
        await message.reply_text("Join channel first!", 
        reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("Join", url=CHANNEL_LINK)]]))
        return False

@app.on_message(filters.command("start"))
async def start(client, message):
    await message.reply_text("Bot is online on Zeabur! Send /song [name]")

@app.on_message(filters.command("song"))
async def song_handler(client, message):
    if not await check_fsub(client, message): return
    
    query = " ".join(message.command[1:])
    if not query: return await message.reply_text("Song name?")

    m = await message.reply_text("🔎 Searching...")
    song_data = search_saavn(query)

    if not song_data:
        return await m.edit("❌ API Error. Try another song.")

    try:
        title = song_data.get('song')
        download_url = song_data.get('media_url')
        thumb = song_data.get('image')
        
        audio_file = f"{title}.mp3"
        res = requests.get(download_url)
        with open(audio_file, 'wb') as f: f.write(res.content)

        await message.reply_photo(photo=thumb, caption=f"🎵 {title}")
        await message.reply_audio(audio=open(audio_file, 'rb'), title=title)
        
        os.remove(audio_file)
        await m.delete()
    except Exception as e:
        await m.edit(f"Error: {e}")

print("Zeabur Bot Started...")
app.run()
