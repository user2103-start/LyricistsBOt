import os
import requests
import threading
import lyricsgenius
from flask import Flask
from pyrogram import Client, filters
from yt_dlp import YoutubeDL

# --- 🌐 ZEABUR ALIVE HACK ---
web_app = Flask(__name__)
@web_app.route('/')
def home(): return "Bot is God Mode! ⚡"

def run_web():
    port = int(os.environ.get("PORT", 8080))
    web_app.run(host="0.0.0.0", port=port)

threading.Thread(target=run_web, daemon=True).start()

# --- 🟢 CONFIG ---
API_ID = 38456866
API_HASH = "30a8f347f538733a1d57dae8cc458ddc"
BOT_TOKEN = "8454384380:AAEsXBAm3IrtW3Hf1--2mH3xAyhnan-J3lg"
GENIUS_TOKEN = "w-XTArszGpAQaaLu-JlViwy1e-0rxx4dvwqQzOEtcmmpYndHm_nkFTvAB5BsY-ww"

app = Client("LyricistBot_Final", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)
genius = lyricsgenius.Genius(GENIUS_TOKEN)

# --- 🎵 DOWNLOADER ENGINE ---
def download_audio(query):
    # Ye engine bina cookies ke best chalta hai
    ydl_opts = {
        'format': 'bestaudio/best',
        'default_search': 'ytsearch',
        'outtmpl': 'downloads/%(title)s.%(ext)s',
        'postprocessors': [{'key': 'FFmpegExtractAudio','preferredcodec': 'mp3','preferredquality': '192'}],
        'quiet': True
    }
    with YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(query, download=True)
        # Extract filename safely
        if 'entries' in info:
            info = info['entries'][0]
        return ydl.prepare_filename(info).replace('.webm', '.mp3').replace('.m4a', '.mp3'), info.get('title'), info.get('thumbnail')

@app.on_message(filters.command("song"))
async def song_handler(client, message):
    if len(message.command) < 2:
        return await message.reply_text("Bhai, gaane ka naam likho!")

    query = " ".join(message.command[1:])
    m = await message.reply_text("🚀 **Engine Starting...**")

    try:
        # Step 1: Search and Download via YT-DLP (Universal)
        await m.edit("🎼 **Finding & Processing...**")
        file_path, title, thumb = download_audio(query)

        # Step 2: Parallel Lyrics Search
        await m.edit("✍️ **Writing Lyrics...**")
        try:
            g_song = genius.search_song(title)
            lyrics = g_song.lyrics.split('Lyrics', 1)[-1].strip() if g_song else "Lyrics not found."
        except:
            lyrics = "Lyrics error."

        # Step 3: Send
        await m.edit("📤 **Uploading to Telegram...**")
        caption = f"🎵 **{title}**\n\n📜 **LYRICS:**\n`{lyrics[:1000]}`"
        
        await message.reply_photo(photo=thumb, caption=caption)
        await message.reply_audio(audio=open(file_path, 'rb'), title=title)
        
        if os.path.exists(file_path): os.remove(file_path)
        await m.delete()

    except Exception as e:
        await m.edit(f"❌ Error: {e}")

app.run()
