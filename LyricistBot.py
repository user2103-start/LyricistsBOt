import os
import requests
import threading
from flask import Flask
from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from pyrogram.errors import UserNotParticipant
import lyricsgenius

# --- 🌐 RENDER WEB SERVER ---
web_app = Flask(__name__)
@web_app.route('/')
def home(): return "Music Bot is Stable Now!"

def run_web():
    port = int(os.environ.get("PORT", 8080))
    web_app.run(host="0.0.0.0", port=port)

threading.Thread(target=run_web, daemon=True).start()

# --- 🟢 CONFIGURATION ---
API_ID = 38456866 
API_HASH = "30a8f347f538733a1d57dae8cc458ddc"
BOT_TOKEN = "8454384380:AAEsXBAm3IrtW3Hf1--2mH3xAyhnan-J3lg"
GENIUS_TOKEN = "w-XTArszGpAQaaLu-JlViwy1e-0rxx4dvwqQzOEtcmmpYndHm_nkFTvAB5BsY-ww"

CHANNEL_ID = -1003751644036 
CHANNEL_LINK = "https://t.me/+JPgViOHx7bdlMDZl"

app = Client("LyricistBot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)
genius = lyricsgenius.Genius(GENIUS_TOKEN)

# --- 🎵 STABLE API SEARCH ---
def search_saavn(query):
    # Using a backup stable API
    search_url = f"https://jiosaavn-api-v3.vercel.app/search/songs?query={query}"
    try:
        response = requests.get(search_url, timeout=10)
        if response.status_code == 200:
            data = response.json()
            if data and len(data) > 0:
                return data[0]
    except Exception as e:
        print(f"Search Error: {e}")
    return None

# --- 🔐 FORCE SUBSCRIBE ---
async def check_fsub(client, message):
    try:
        await client.get_chat_member(CHANNEL_ID, message.from_user.id)
        return True
    except UserNotParticipant:
        await message.reply_text(
            "⚠️ **Access Denied!**\n\nPlease join our update channel to use this bot.",
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("Join Channel 📢", url=CHANNEL_LINK)]])
        )
        return False
    except Exception: return True

@app.on_message(filters.command("song"))
async def song_handler(client, message):
    if not await check_fsub(client, message): return

    query = " ".join(message.command[1:])
    if not query:
        return await message.reply_text("Please provide a song name! Example: `/song Peaches`")

    m = await message.reply_text("🔎 **Searching for your song...**")

    song_data = search_saavn(query)
    if not song_data:
        return await m.edit("❌ **API Error:** Could not find the song or API is down. Try again later.")

    try:
        title = song_data.get('song', 'Unknown Title')
        album = song_data.get('album', 'Unknown Album')
        artist = song_data.get('singers', 'Unknown Artist')
        thumbnail = song_data.get('image')
        # Download Link (High Quality 320kbps)
        download_url = song_data.get('media_url')

        if not download_url:
            return await m.edit("❌ **Error:** High quality audio link not found.")

        await m.edit("✍️ **Fetching lyrics...**")
        lyrics_text = "Lyrics not found. 😶"
        try:
            song_lyric = genius.search_song(title, artist.split(',')[0])
            if song_lyric: lyrics_text = song_lyric.lyrics
        except: pass

        caption = (
            f"🎵 **Song:** `{title}`\n"
            f"👤 **Artist:** {artist}\n"
            f"💿 **Album:** {album}\n\n"
            f"━━━━━━━━━━━━━━━━━━\n"
            f"📜 **LYRICS:**\n\n"
            f"{lyrics_text[:700]}..." 
            f"\n━━━━━━━━━━━━━━━━━━"
        )

        audio_file = f"{title}.mp3"
        await m.edit("📥 **Downloading...**")
        
        # Download Audio
        audio_data = requests.get(download_url).content
        with open(audio_file, 'wb') as f:
            f.write(audio_data)

        await message.reply_photo(photo=thumbnail, caption=caption)
        await message.reply_audio(audio=open(audio_file, 'rb'), title=title, performer=artist)
        
        await m.delete()
        os.remove(audio_file)

    except Exception as e:
        await m.edit(f"❌ **System Error:** `{str(e)[:100]}`")

print("Bot is starting with V3 API Engine...")
app.run()
