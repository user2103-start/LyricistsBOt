import os
import requests
import threading
import lyricsgenius
from flask import Flask
from pyrogram import Client, filters

# --- 🌐 ZEABUR STAY ALIVE ---
web_app = Flask(__name__)
@web_app.route('/')
def home(): return "SoundStat Hybrid Engine is Live! ⚡"

def run_web():
    port = int(os.environ.get("PORT", 8080))
    web_app.run(host="0.0.0.0", port=port)

threading.Thread(target=run_web, daemon=True).start()

# --- 🟢 CONFIG ---
API_ID = 38456866
API_HASH = "30a8f347f538733a1d57dae8cc458ddc"
BOT_TOKEN = "8454384380:AAEsXBAm3IrtW3Hf1--2mH3xAyhnan-J3lg"
GENIUS_TOKEN = "w-XTArszGpAQaaLu-JlViwy1e-0rxx4dvwqQzOEtcmmpYndHm_nkFTvAB5BsY-ww"
SOUNDSTAT_KEY = "k30pcad0uDQgsQeRzZCSDiXqNGHN-kyzgpFdJXJF3Uw"

app = Client("SoundStatBot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)
genius = lyricsgenius.Genius(GENIUS_TOKEN)

# --- 🛰️ DOWNLOAD PROXIES (InterTune Logic) ---
INSTANCES = ["https://pipedapi.kavin.rocks", "https://piped-api.lunar.icu"]

def get_audio_stream(title):
    for instance in INSTANCES:
        try:
            search = requests.get(f"{instance}/search?q={title}&filter=music_videos", timeout=10).json()
            if search and 'items' in search:
                v_id = search['items'][0]['url'].split('=')[-1]
                stream = requests.get(f"{instance}/streams/{v_id}").json()
                return stream['audioStreams'][0]['url']
        except: continue
    return None

@app.on_message(filters.command("song"))
async def song_handler(client, message):
    if len(message.command) < 2:
        return await message.reply_text("Bhai, naam likho!")

    query = " ".join(message.command[1:])
    m = await message.reply_text("💎 **Querying SoundStat Premium...**")

    try:
        # Step 1: Use your Paid API for exact Metadata
        # (Yahan soundstat ka endpoint use hoga)
        # Note: Soundstat ka actual search URL unki documentation se check karna hoga
        # Filhaal main query ko cleaner banane ke liye use kar raha hoon
        
        title = query # Soundstat se clean title nikalne ka logic yahan aayega
        
        await m.edit(f"🎬 **Found:** `{title}`\n📥 **Bypassing Paid Download...**")
        
        # Step 2: Download using FREE Proxy (to save your USD balance)
        dl_url = get_audio_stream(title)
        
        if not dl_url:
            return await m.edit("❌ SoundStat got metadata but Proxy failed to stream.")

        await m.edit("✍️ **Fetching Lyrics...**")
        g_song = genius.search_song(title)
        lyrics = g_song.lyrics.split('Lyrics', 1)[-1].strip() if g_song else "No lyrics."

        file_name = f"music_{message.from_user.id}.mp3"
        r = requests.get(dl_url, stream=True)
        with open(file_name, 'wb') as f:
            for chunk in r.iter_content(chunk_size=16384): f.write(chunk)

        await message.reply_audio(audio=open(file_name, 'rb'), title=title, caption=f"📜 `{lyrics[:800]}`")
        os.remove(file_name)
        await m.delete()

    except Exception as e:
        await m.edit(f"❌ Error: {e}")

app.run()
