import os
import asyncio
import requests
import threading
import lyricsgenius
from flask import Flask
from pyrogram import Client, filters

# --- 🌐 WEB SERVER (RENDER KEEP-ALIVE) ---
web_app = Flask(__name__)
@web_app.route('/')
def home(): return "SoundStat Engine on Render is ALIVE! 🚀"

def run_web():
    port = int(os.environ.get("PORT", 8080))
    web_app.run(host="0.0.0.0", port=port)

# --- 🟢 CONFIG ---
API_ID = 38456866
API_HASH = "30a8f347f538733a1d57dae8cc458ddc"
BOT_TOKEN = "8454384380:AAEsXBAm3IrtW3Hf1--2mH3xAyhnan-J3lg"
GENIUS_TOKEN = "w-XTArszGpAQaaLu-JlViwy1e-0rxx4dvwqQzOEtcmmpYndHm_nkFTvAB5BsY-ww"

app = Client("LyricistBot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)
genius = lyricsgenius.Genius(GENIUS_TOKEN)

# --- 🎵 MUSIC FETCH LOGIC ---
def get_music_link(query):
    # Render ke liye direct fast bridge
    return f"https://api.vyt-dlp.workers.dev/download_query?q={query}"

@app.on_message(filters.command("song"))
async def song_handler(client, message):
    if len(message.command) < 2:
        return await message.reply_text("Bhai, naam toh likh!")

    query = " ".join(message.command[1:])
    m = await message.reply_text("🎬 **Fetching from SoundStat + Render Bridge...**")

    try:
        title = query 
        dl_url = get_music_link(title)
        file_path = f"song_{message.from_user.id}.mp3"

        # Lyrics fetch (Optional but cool)
        try:
            g_song = genius.search_song(title)
            lyrics = g_song.lyrics.split('Lyrics', 1)[-1].strip() if g_song else "No lyrics."
        except:
            lyrics = "Lyrics fetch error."

        # Direct Stream download
        r = requests.get(dl_url, stream=True, timeout=60)
        with open(file_path, 'wb') as f:
            for chunk in r.iter_content(chunk_size=1024*1024): # 1MB chunks for Render speed
                if chunk: f.write(chunk)

        await message.reply_audio(audio=open(file_path, 'rb'), title=title, caption=f"📜 `{lyrics[:600]}`")
        await m.delete()
        if os.path.exists(file_path): os.remove(file_path)

    except Exception as e:
        await m.edit(f"❌ Error: {str(e)[:50]}")

# --- 🚀 ASYNC LOOP FIX FOR RENDER ---
async def main():
    # Start Flask in a background thread
    threading.Thread(target=run_web, daemon=True).start()
    # Start Bot
    await app.start()
    print("Bot is started on Render!")
    await asyncio.Event().wait() # Keep it running

if __name__ == "__main__":
    # Naye Python versions ke liye loop handle karne ka sahi tareeka
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        pass
