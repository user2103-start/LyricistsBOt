import os
import requests
import threading
import lyricsgenius
from flask import Flask
from pyrogram import Client, filters

# --- 🌐 ZEABUR ALIVE ---
web_app = Flask(__name__)
@web_app.route('/')
def home(): return "Bot is Alive (No YT-DLP)! 💎"

def run_web():
    port = int(os.environ.get("PORT", 8080))
    web_app.run(host="0.0.0.0", port=port)

threading.Thread(target=run_web, daemon=True).start()

# --- 🟢 CONFIG ---
API_ID = 38456866
API_HASH = "30a8f347f538733a1d57dae8cc458ddc"
BOT_TOKEN = "8454384380:AAEsXBAm3IrtW3Hf1--2mH3xAyhnan-J3lg"
GENIUS_TOKEN = "w-XTArszGpAQaaLu-JlViwy1e-0rxx4dvwqQzOEtcmmpYndHm_nkFTvAB5BsY-ww"

app = Client("NoYTDLPBot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)
genius = lyricsgenius.Genius(GENIUS_TOKEN)

# --- 🎵 CLEAN API SEARCH & DOWNLOAD ---
def fetch_music_data(query):
    # Hum ek external API bridge use kar rahe hain jo Zeabur ko hide rakhta hai
    search_api = f"https://api.vyt-dlp.workers.dev/search?q={query}"
    try:
        search_res = requests.get(search_api, timeout=10).json()
        if search_res and 'results' in search_res:
            vid_id = search_res['results'][0]['id']
            title = search_res['results'][0]['title']
            thumb = search_res['results'][0]['thumbnail']
            
            # Direct link generator without using yt-dlp on local server
            dl_url = f"https://api.vyt-dlp.workers.dev/download?id={vid_id}"
            return dl_url, title, thumb
    except Exception as e:
        print(f"Search Error: {e}")
    return None, None, None

@app.on_message(filters.command("song"))
async def song_handler(client, message):
    if len(message.command) < 2:
        return await message.reply_text("Bhai, naam likho!")

    query = " ".join(message.command[1:])
    m = await message.reply_text("⚡ **Fetching via API Bridge...**")

    dl_url, title, thumb = fetch_music_data(query)

    if not dl_url:
        return await m.edit("❌ API Error: Music source unreachable.")

    try:
        # Step 2: Lyrics from Genius
        await m.edit("✍️ **Getting Lyrics...**")
        try:
            g_song = genius.search_song(title)
            lyrics = g_song.lyrics.split('Lyrics', 1)[-1].strip() if g_song else "Lyrics not found."
        except:
            lyrics = "Lyrics error."

        # Step 3: Stream and Upload
        await m.edit("📥 **Downloading...**")
        file_name = f"song_{message.from_user.id}.mp3"
        
        # Requests based download (Very light)
        with requests.get(dl_url, stream=True) as r:
            r.raise_for_status()
            with open(file_name, 'wb') as f:
                for chunk in r.iter_content(chunk_size=8192):
                    f.write(chunk)

        await message.reply_photo(photo=thumb, caption=f"🎵 **{title}**\n\n📜 `{lyrics[:800]}`")
        await message.reply_audio(audio=open(file_name, 'rb'), title=title)
        
        if os.path.exists(file_name): os.remove(file_name)
        await m.delete()

    except Exception as e:
        await m.edit(f"❌ Failed: {e}")

app.run()
