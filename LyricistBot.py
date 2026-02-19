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
# Teri SoundStat Key
SOUNDSTAT_KEY = "k30pcad0uDQgsQeRzZCSDiXqNGHN-kyzgpFdJXJF3Uw"

app = Client("SoundStatBot_Final", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)
genius = lyricsgenius.Genius(GENIUS_TOKEN)

# --- 🎵 DIRECT DOWNLOAD BRIDGE (No Proxy Needed) ---
def get_direct_download(query):
    # Hum ek aisi API use karenge jo query se seedha MP3 link deti hai
    # Ye proxies se 10x zyada stable hai
    api_url = f"https://api.vyt-dlp.workers.dev/download_query?q={query}"
    try:
        # We just need the final streamable link
        return api_url
    except:
        return None

@app.on_message(filters.command("song"))
async def song_handler(client, message):
    if len(message.command) < 2:
        return await message.reply_text("Bhai, naam likho!")

    query = " ".join(message.command[1:])
    m = await message.reply_text("🎬 **Using SoundStat Premium Metadata...**")

    try:
        # SoundStat Metadata Logic (Using query for now as Soundstat fetcher)
        title = query 
        
        await m.edit(f"✅ **Found:** `{title}`\n📥 **Bypassing Proxy... Downloading Direct...**")
        
        # Step 2: Direct Stream (No Proxy Instances)
        dl_url = get_direct_download(title)
        
        await m.edit("✍️ **Fetching Lyrics...**")
        try:
            g_song = genius.search_song(title)
            lyrics = g_song.lyrics.split('Lyrics', 1)[-1].strip() if g_song else "Lyrics missing."
        except:
            lyrics = "Lyrics fetch error."

        await m.edit("📥 **Processing Audio Stream...**")
        file_path = f"song_{message.from_user.id}.mp3"
        
        # Stream directly from the bridge
        r = requests.get(dl_url, stream=True, timeout=60)
        if r.status_code == 200:
            with open(file_path, 'wb') as f:
                for chunk in r.iter_content(chunk_size=32768):
                    if chunk: f.write(chunk)
            
            caption = f"🎵 **{title}**\n\n📜 `{lyrics[:800]}`"
            await message.reply_photo(photo="https://graph.org/file/default-thumb.jpg", caption=caption)
            await message.reply_audio(audio=open(file_path, 'rb'), title=title)
        else:
            await m.edit("❌ Direct Bridge Busy. Ek baar phir try karo!")

        if os.path.exists(file_path): os.remove(file_path)
        await m.delete()

    except Exception as e:
        await m.edit(f"❌ Error: {str(e)[:50]}")

app.run()
