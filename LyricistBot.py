import os
import requests
import threading
import lyricsgenius
from flask import Flask
from pyrogram import Client, filters
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

# --- 🌐 ZEABUR PORT HANDLING ---
web_app = Flask(__name__)
@web_app.route('/')
def home(): return "Tunneling Engine Active! 🛰️"

def run_web():
    port = int(os.environ.get("PORT", 8080))
    web_app.run(host="0.0.0.0", port=port)

threading.Thread(target=run_web, daemon=True).start()

# --- 🟢 CONFIG ---
API_ID = 38456866
API_HASH = "30a8f347f538733a1d57dae8cc458ddc"
BOT_TOKEN = "8454384380:AAEsXBAm3IrtW3Hf1--2mH3xAyhnan-J3lg"
GENIUS_TOKEN = "w-XTArszGpAQaaLu-JlViwy1e-0rxx4dvwqQzOEtcmmpYndHm_nkFTvAB5BsY-ww"

app = Client("FirewallBreaker", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)
genius = lyricsgenius.Genius(GENIUS_TOKEN)

# --- 🛡️ ANTI-BLOCK REQUEST SESSION ---
def get_secure_session():
    session = requests.Session()
    # Retry logic: Agar connection fail ho toh 5 baar try karo automatically
    retry = Retry(total=5, backoff_factor=1, status_forcelist=[502, 503, 504])
    adapter = HTTPAdapter(max_retries=retry)
    session.mount('https://', adapter)
    session.mount('http://', adapter)
    # Fake User-Agent taaki Zeabur bot na lage
    session.headers.update({
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36"
    })
    return session

@app.on_message(filters.command("song"))
async def song_handler(client, message):
    if len(message.command) < 2:
        return await message.reply_text("Bhai, naam toh likho!")

    query = " ".join(message.command[1:])
    m = await message.reply_text("🌪️ **Breaking Firewall...**")

    # Bridge URLs
    dl_url = f"https://api.vyt-dlp.workers.dev/download_query?q={query}"
    
    file_path = f"song_{message.from_user.id}.mp3"
    session = get_secure_session()

    try:
        # Step 1: Lyrics pehle nikaal lo (Ispe block kam hota hai)
        try:
            g_song = genius.search_song(query)
            lyrics = g_song.lyrics.split('Lyrics', 1)[-1].strip() if g_song else "Lyrics missing."
        except:
            lyrics = "Lyrics error."

        # Step 2: Download with Tunneling logic
        await m.edit("🛰️ **Routing through Tunnel...**")
        
        # Zeabur connection pool fix: stream=True ke saath timeout bada rakho
        with session.get(dl_url, stream=True, timeout=45) as r:
            r.raise_for_status()
            with open(file_path, 'wb') as f:
                for chunk in r.iter_content(chunk_size=262144): # 256KB chunks
                    if chunk: f.write(chunk)

        await message.reply_photo(
            photo="https://graph.org/file/default-thumb.jpg",
            caption=f"🎵 **{query.capitalize()}**\n\n📜 `{lyrics[:800]}`"
        )
        await message.reply_audio(audio=open(file_path, 'rb'), title=query)
        await m.delete()

    except Exception as e:
        error_msg = str(e)
        if "Max retries exceeded" in error_msg:
            await m.edit("❌ Zeabur IP is Hard-Blocked. I'm trying an emergency port...")
        else:
            await m.edit(f"❌ Error: {error_msg[:100]}")

    if os.path.exists(file_path): os.remove(file_path)

app.run()
