import os
import requests
import threading
import lyricsgenius
from flask import Flask
from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton

# --- 🌐 ZEABUR PORT BINDING ---
web_app = Flask(__name__)
@web_app.route('/')
def home(): return "Bot is Alive! 🎸"

def run_web():
    port = int(os.environ.get("PORT", 8080))
    web_app.run(host="0.0.0.0", port=port)

threading.Thread(target=run_web, daemon=True).start()

# --- 🟢 CONFIGURATION ---
API_ID = 38456866
API_HASH = "30a8f347f538733a1d57dae8cc458ddc"
BOT_TOKEN = "8454384380:AAEsXBAm3IrtW3Hf1--2mH3xAyhnan-J3lg"
GENIUS_TOKEN = "w-XTArszGpAQaaLu-JlViwy1e-0rxx4dvwqQzOEtcmmpYndHm_nkFTvAB5BsY-ww"

app = Client("LyricistBot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)
genius = lyricsgenius.Genius(GENIUS_TOKEN)

# --- 🎵 STABLE SEARCH FUNCTION ---
def search_song_stable(query):
    # Try multiple API versions to ensure success
    endpoints = [
        f"https://saavn.me/api/search/songs?query={query}",
        f"https://saavn.dev/api/search/songs?query={query}",
        f"https://jiosaavn-api-v3.vercel.app/search/songs?query={query}"
    ]
    
    for url in endpoints:
        try:
            r = requests.get(url, timeout=10).json()
            # Standard structure check
            if r.get('status') == 'SUCCESS' or r.get('success'):
                data = r.get('data', {}).get('results', [])
                if data: return data[0]
            # List structure check (for V3 API)
            elif isinstance(r, list) and len(r) > 0:
                return r[0]
        except:
            continue
    return None

@app.on_message(filters.command("start"))
async def start(client, message):
    await message.reply_text(f"Namaste {message.from_user.first_name}! 🙏\n\nAb API fix ho gayi hai! Try karo: `/song Kesariya`")

@app.on_message(filters.command("song"))
async def song_handler(client, message):
    if len(message.command) < 2:
        return await message.reply_text("Bhai, gaane ka naam toh likho!")

    query = " ".join(message.command[1:])
    m = await message.reply_text("🔎 **Searching...**")

    song = search_song_stable(query)
    if not song:
        return await m.edit("❌ API Error: Gaana nahi mil raha. Try another name.")

    try:
        # Handling different key names from different APIs
        title = song.get('name') or song.get('song') or "Song"
        artist = song.get('artists', {}).get('primary', [{}])[0].get('name') or song.get('primary_artists') or "Artist"
        
        # Audio URL
        download_url = ""
        if 'downloadUrl' in song:
            download_url = song['downloadUrl'][-1]['url']
        else:
            download_url = song.get('media_url')

        # Thumbnail
        thumb = song.get('image', [{}])[-1].get('url') if isinstance(song.get('image'), list) else song.get('image')

        await m.edit("✍️ **Fetching Lyrics...**")
        try:
            g_song = genius.search_song(title, artist)
            lyrics = g_song.lyrics.split('Lyrics', 1)[-1].strip() if g_song else "Lyrics not found."
        except:
            lyrics = "Lyrics error."

        caption = f"🎵 **{title}**\n👤 **{artist}**\n\n📜 **LYRICS:**\n`{lyrics[:1000]}`"

        await m.edit("📥 **Downloading...**")
        file_path = f"{title}.mp3".replace("/", "-")
        with open(file_path, 'wb') as f:
            f.write(requests.get(download_url).content)

        await message.reply_photo(photo=thumb, caption=caption)
        await message.reply_audio(audio=open(file_path, 'rb'), title=title, performer=artist)
        
        if os.path.exists(file_path): os.remove(file_path)
        await m.delete()

    except Exception as e:
        await m.edit(f"Error: {e}")

app.run()
