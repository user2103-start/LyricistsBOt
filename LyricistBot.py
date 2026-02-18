import os
import requests
import threading
import lyricsgenius
from flask import Flask
from pyrogram import Client, filters

# --- 🌐 ZEABUR ALIVE HACK ---
web_app = Flask(__name__)
@web_app.route('/')
def home(): return "Bot is Alive on Bridge Mode! 🚀"

def run_web():
    port = int(os.environ.get("PORT", 8080))
    web_app.run(host="0.0.0.0", port=port)

threading.Thread(target=run_web, daemon=True).start()

# --- 🟢 CONFIG ---
API_ID = 38456866
API_HASH = "30a8f347f538733a1d57dae8cc458ddc"
BOT_TOKEN = "8454384380:AAEsXBAm3IrtW3Hf1--2mH3xAyhnan-J3lg"
GENIUS_TOKEN = "w-XTArszGpAQaaLu-JlViwy1e-0rxx4dvwqQzOEtcmmpYndHm_nkFTvAB5BsY-ww"

app = Client("LyricistBot_Final_Final", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)
genius = lyricsgenius.Genius(GENIUS_TOKEN)

# --- 🎵 DOWNLOAD BRIDGE LOGIC ---
def get_song_bridge(query):
    # Hum ek free API server use kar rahe hain jo blocked nahi hai
    search_url = f"https://api.pop-song.vercel.app/search?q={query}"
    try:
        data = requests.get(search_url, timeout=10).json()
        if data and 'results' in data:
            res = data['results'][0]
            # Ye API humein direct download link degi
            return res['download_url'], res['title'], res['thumbnail'], res['artist']
    except:
        return None, None, None, None

@app.on_message(filters.command("song"))
async def song_handler(client, message):
    if len(message.command) < 2:
        return await message.reply_text("Bhai, gaane ka naam likho!")

    query = " ".join(message.command[1:])
    m = await message.reply_text("💎 **Connecting to Music Cloud...**")

    # Step 1: Search & Link Generation
    dl_url, title, thumb, artist = get_song_bridge(query)
    
    if not dl_url:
        # Agar bridge fail ho, toh backup API try karo
        return await m.edit("❌ Abhi servers busy hain. Ek baar phir try karo!")

    try:
        # Step 2: Fetch Lyrics
        await m.edit("✍️ **Fetching Lyrics...**")
        try:
            g_song = genius.search_song(title, artist)
            lyrics = g_song.lyrics.split('Lyrics', 1)[-1].strip() if g_song else "Lyrics not found."
        except:
            lyrics = "Lyrics fetch error."

        # Step 3: Stream Download
        await m.edit("📥 **Downloading...**")
        file_path = f"{title}.mp3".replace("/", "-")
        
        response = requests.get(dl_url, stream=True)
        with open(file_path, 'wb') as f:
            for chunk in response.iter_content(chunk_size=1024):
                if chunk: f.write(chunk)

        # Step 4: Send Everything
        caption = f"🎵 **{title}**\n👤 **{artist}**\n\n📜 **LYRICS:**\n`{lyrics[:900]}`"
        
        await message.reply_photo(photo=thumb, caption=caption)
        await message.reply_audio(audio=open(file_path, 'rb'), title=title, performer=artist)
        
        if os.path.exists(file_path): os.remove(file_path)
        await m.delete()

    except Exception as e:
        await m.edit(f"❌ Error: {e}")

app.run()
