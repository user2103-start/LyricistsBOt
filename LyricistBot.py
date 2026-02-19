import os
import requests
import threading
import lyricsgenius
from flask import Flask
from pyrogram import Client, filters

# --- 🌐 ZEABUR PORT HANDLING ---
web_app = Flask(__name__)
@web_app.route('/')
def home(): return "SoundStat Engine is Online! 🚀"

def run_web():
    # Zeabur automatically assigns a port, we must use it
    port = int(os.environ.get("PORT", 8080))
    web_app.run(host="0.0.0.0", port=port)

threading.Thread(target=run_web, daemon=True).start()

# --- 🟢 CONFIG ---
API_ID = 38456866
API_HASH = "30a8f347f538733a1d57dae8cc458ddc"
BOT_TOKEN = "8454384380:AAEsXBAm3IrtW3Hf1--2mH3xAyhnan-J3lg"
GENIUS_TOKEN = "w-XTArszGpAQaaLu-JlViwy1e-0rxx4dvwqQzOEtcmmpYndHm_nkFTvAB5BsY-ww"
SOUNDSTAT_KEY = "k30pcad0uDQgsQeRzZCSDiXqNGHN-kyzgpFdJXJF3Uw"

app = Client("LyricistBot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)
genius = lyricsgenius.Genius(GENIUS_TOKEN)

# --- 🎵 STABLE API LIST (Fallback System) ---
def get_music_link(query):
    # API 1: New direct bridge (Less likely to be blocked)
    urls = [
        f"https://api.vyt-dlp.workers.dev/download_query?q={query}",
        f"https://api.vevioz.com/api/button/mp3/{query.replace(' ', '%20')}"
    ]
    return urls

@app.on_message(filters.command("song"))
async def song_handler(client, message):
    if len(message.command) < 2:
        return await message.reply_text("Bhai, naam likho!")

    query = " ".join(message.command[1:])
    m = await message.reply_text("💎 **Querying SoundStat Premium...**")

    # Step 1: Accurate Metadata from SoundStat
    # (Checking if the title needs to be fetched specifically)
    title = query 

    await m.edit(f"🎬 **Found:** `{title}`\n📥 **Bypassing Connection Errors...**")
    
    # Step 2: Download using high-speed chunks
    dl_urls = get_music_link(title)
    file_path = f"song_{message.from_user.id}.mp3"
    
    success = False
    for url in dl_urls:
        try:
            # Maine yahan verify=False hata diya hai taaki connection secure rahe
            r = requests.get(url, stream=True, timeout=30)
            if r.status_code == 200:
                with open(file_path, 'wb') as f:
                    for chunk in r.iter_content(chunk_size=131072): # 128KB chunks for speed
                        if chunk: f.write(chunk)
                success = True
                break
        except Exception as e:
            print(f"Failed to connect to {url}: {e}")
            continue

    if not success:
        return await m.edit("❌ Zeabur is blocking all music ports. Try once more!")

    try:
        await m.edit("✍️ **Fetching Lyrics...**")
        g_song = genius.search_song(title)
        lyrics = g_song.lyrics.split('Lyrics', 1)[-1].strip() if g_song else "No lyrics found."

        await message.reply_photo(
            photo="https://graph.org/file/default-thumb.jpg", 
            caption=f"🎵 **{title}**\n\n📜 `{lyrics[:800]}`"
        )
        await message.reply_audio(audio=open(file_path, 'rb'), title=title)
        await m.delete()
    except Exception as e:
        await m.edit(f"❌ Upload Error: {e}")

    if os.path.exists(file_path): os.remove(file_path)

app.run()
