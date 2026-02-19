import os
import asyncio
import requests
import threading
import lyricsgenius
from flask import Flask
from pyrogram import Client, filters

# --- 🌐 WEB SERVER (For Render Keep-Alive) ---
web_app = Flask(__name__)
@web_app.route('/')
def home(): return "SoundStat Engine on Render is Online! 🚀"

def run_web():
    # Render automatically sets PORT environment variable
    port = int(os.environ.get("PORT", 8080))
    web_app.run(host="0.0.0.0", port=port)

# --- 🟢 CONFIG ---
API_ID = 38456866
API_HASH = "30a8f347f538733a1d57dae8cc458ddc"
BOT_TOKEN = "8454384380:AAEsXBAm3IrtW3Hf1--2mH3xAyhnan-J3lg"
GENIUS_TOKEN = "w-XTArszGpAQaaLu-JlViwy1e-0rxx4dvwqQzOEtcmmpYndHm_nkFTvAB5BsY-ww"
SOUNDSTAT_KEY = "k30pcad0uDQgsQeRzZCSDiXqNGHN-kyzgpFdJXJF3Uw"

app = Client("LyricistBot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)
genius = lyricsgenius.Genius(GENIUS_TOKEN)

# --- 🎵 DOWNLOAD LOGIC ---
@app.on_message(filters.command("song"))
async def song_handler(client, message):
    if len(message.command) < 2:
        return await message.reply_text("Bhai, gaane ka naam likho!")

    query = " ".join(message.command[1:])
    m = await message.reply_text("🎬 **Searching via SoundStat Premium...**")

    try:
        # Direct Download Bridge
        dl_url = f"https://api.vyt-dlp.workers.dev/download_query?q={query}"
        file_path = f"song_{message.from_user.id}.mp3"

        # Step 1: Download
        await m.edit("📥 **Downloading to Render Server...**")
        r = requests.get(dl_url, stream=True, timeout=60)
        with open(file_path, 'wb') as f:
            for chunk in r.iter_content(chunk_size=1024*1024): # 1MB chunks
                if chunk: f.write(chunk)

        # Step 2: Lyrics
        await m.edit("✍️ **Fetching Lyrics...**")
        try:
            g_song = genius.search_song(query)
            lyrics = g_song.lyrics.split('Lyrics', 1)[-1].strip() if g_song else "No lyrics."
        except:
            lyrics = "Lyrics not found."

        # Step 3: Upload
        await message.reply_audio(
            audio=open(file_path, 'rb'), 
            title=query, 
            caption=f"🎵 **{query}**\n\n📜 `{lyrics[:600]}`"
        )
        await m.delete()
        if os.path.exists(file_path): os.remove(file_path)

    except Exception as e:
        await m.edit(f"❌ Error: {str(e)[:50]}")

# --- 🚀 LOOP FIX FOR PYTHON 3.14 (RENDER) ---
async def start_bot():
    # Start Flask in background thread
    threading.Thread(target=run_web, daemon=True).start()
    
    # Start the Client
    await app.start()
    print("Bot is successfully running on Render! ✅")
    
    # Keep the bot running
    await asyncio.Event().wait()

if __name__ == "__main__":
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    try:
        loop.run_until_complete(start_bot())
    except KeyboardInterrupt:
        pass
