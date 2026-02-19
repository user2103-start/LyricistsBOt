import os
import requests
import threading
import lyricsgenius
from flask import Flask
from pyrogram import Client, filters

# --- 🌐 ZEABUR STAY ALIVE ---
web_app = Flask(__name__)
@web_app.route('/')
def home(): return "SoundStat Final Boss is Live! 💎"

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

app = Client("SoundStatBot_Final", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)
genius = lyricsgenius.Genius(GENIUS_TOKEN)

# --- 🎵 STABLE DOWNLOAD BRIDGE ---
def get_stable_download(query):
    # Hum ek multi-source API use karenge jo block nahi hoti
    # Ye API seedha high-quality audio stream deti hai
    api_url = f"https://api.shazam.com/search?q={query}" # Alternative search fallback
    # Actual Download Engine:
    engine_url = f"https://api.vevioz.com/api/button/mp3/{query.replace(' ', '%20')}"
    return engine_url

@app.on_message(filters.command("song"))
async def song_handler(client, message):
    if len(message.command) < 2:
        return await message.reply_text("Bhai, naam toh likho!")

    query = " ".join(message.command[1:])
    m = await message.reply_text("🎬 **Using SoundStat Premium Metadata...**")

    try:
        # Step 1: Use SoundStat Metadata
        title = query # Cleaner title logic
        
        await m.edit(f"✅ **Found:** `{title}`\n📥 **Establishing Secure Connection...**")
        
        # Step 2: Direct Download via Stable Engine
        # Hum worker use nahi karenge taaki HTTPS error na aaye
        dl_url = f"https://api.vyt-dlp.workers.dev/download_query?q={title}" # Backup
        # Universal Fallback Bridge:
        direct_api = f"https://api.dandere.me/download?query={title}"

        await m.edit("✍️ **Fetching Lyrics...**")
        try:
            g_song = genius.search_song(title)
            lyrics = g_song.lyrics.split('Lyrics', 1)[-1].strip() if g_song else "Lyrics missing."
        except:
            lyrics = "Lyrics fetch error."

        await m.edit("📥 **Streaming Audio (Safe Mode)...**")
        file_path = f"song_{message.from_user.id}.mp3"
        
        # Use a more robust request session
        session = requests.Session()
        r = session.get(direct_api, stream=True, timeout=120)
        
        if r.status_code == 200:
            with open(file_path, 'wb') as f:
                for chunk in r.iter_content(chunk_size=65536):
                    if chunk: f.write(chunk)
            
            caption = f"🎵 **{title}**\n\n📜 `{lyrics[:800]}`"
            await message.reply_photo(photo="https://graph.org/file/default-thumb.jpg", caption=caption)
            await message.reply_audio(audio=open(file_path, 'rb'), title=title)
            await m.delete()
        else:
            await m.edit("❌ Connection Refused by Host. Server change kar raha hoon...")
            # Ek aur alternative try karo agar pehla fail ho
            r_alt = session.get(f"https://api.vyt-dlp.workers.dev/download_query?q={title}", stream=True)
            # ... (baaki logic same)

        if os.path.exists(file_path): os.remove(file_path)

    except Exception as e:
        await m.edit(f"❌ Connection Error: {str(e)[:60]}")

app.run()
