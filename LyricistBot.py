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
def home(): return "Music Bot is Live!"

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

# --- 🎵 MUSIC SEARCH (JioSaavn) ---
def search_saavn(query):
    # Using a public JioSaavn API
    search_url = f"https://saavn.me/search/songs?query={query}"
    response = requests.get(search_url).json()
    if response['status'] == 'SUCCESS' and response['data']['results']:
        return response['data']['results'][0]
    return None

@app.on_message(filters.command("start"))
async def start(client, message):
    await message.reply_text(f"Hello {message.from_user.mention}!\n\nI am your **Premium Music Bot**. Send `/song [name]` to download.")

@app.on_message(filters.command("song"))
async def song_handler(client, message):
    if not await check_fsub(client, message): return

    query = " ".join(message.command[1:])
    if not query:
        return await message.reply_text("Please provide a song name! Example: `/song Peaches`")

    m = await message.reply_text("🔎 **Searching on JioSaavn...**")

    song_data = search_saavn(query)
    if not song_data:
        return await m.edit("❌ **Song not found!** Try another name.")

    title = song_data['name']
    album = song_data['album']['name']
    duration = song_data['duration']
    thumbnail = song_data['image'][2]['link'] # High quality image
    download_url = song_data['downloadUrl'][4]['link'] # 320kbps link
    artist = song_data['primaryArtists']

    await m.edit("✍️ **Fetching lyrics...**")
    
    lyrics_text = "Lyrics not available for this track. 😶"
    try:
        song_lyric = genius.search_song(title, artist.split(',')[0])
        if song_lyric: lyrics_text = song_lyric.lyrics
    except: pass

    # --- PREMIUM CAPTION DESIGN ---
    caption = (
        f"🎵 **Song:** `{title}`\n"
        f"💿 **Album:** {album}\n"
        f"👤 **Artist:** {artist}\n"
        f"⏱️ **Duration:** {duration} sec\n\n"
        f"━━━━━━━━━━━━━━━━━━\n"
        f"📜 **LYRICS:**\n\n"
        f"{lyrics_text[:800]}..." 
        f"\n━━━━━━━━━━━━━━━━━━"
    )

    buttons = InlineKeyboardMarkup([[
        InlineKeyboardButton("📢 Updates", url=CHANNEL_LINK)
    ]])

    try:
        # Download file
        audio_file = f"{title}.mp3"
        doc = requests.get(download_url)
        with open(audio_file, 'wb') as f:
            f.write(doc.content)

        await message.reply_photo(photo=thumbnail, caption=caption, reply_markup=buttons)
        await message.reply_audio(
            audio=open(audio_file, 'rb'), 
            title=title, 
            performer=artist,
            thumb=None # Saavn images are webp, Telegram prefers jpg for thumbs
        )
        
        await m.delete()
        os.remove(audio_file)
    except Exception as e:
        await m.edit(f"❌ **Error:** `{str(e)[:100]}`")

print("Bot is running on JioSaavn Engine!")
app.run()
