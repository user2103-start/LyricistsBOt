import os
import asyncio
import threading
from flask import Flask
from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from pyrogram.errors import UserNotParticipant
import yt_dlp
import lyricsgenius

# --- 🌐 RENDER WEB SERVER ---
web_app = Flask(__name__)

@web_app.route('/')
def home():
    return "Bot is Running!"

def run_web():
    port = int(os.environ.get("PORT", 8080))
    web_app.run(host="0.0.0.0", port=port)

threading.Thread(target=run_web, daemon=True).start()

# --- 🟢 CONFIGURATION ---
API_ID = 38456866 
API_HASH = "30a8f347f538733a1d57dae8cc458ddc"
BOT_TOKEN = "8454384380:AAEsXBAm3IrtW3Hf1--2mH3xAyhnan-J3lg"
GENIUS_TOKEN = "w-XTArszGpAQaaLu-JlViwy1e-0rxx4dvwqQzOEtcmmpYndHm_nkFTvAB5BsY-ww"

ADMIN_ID = 6593129349
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
            reply_markup=InlineKeyboardMarkup([[
                InlineKeyboardButton("Join Channel 📢", url=CHANNEL_LINK)
            ]])
        )
        return False
    except Exception:
        return True

# --- 🎵 MUSIC & LYRICS ---
@app.on_message(filters.command("start"))
async def start(client, message):
    await message.reply_text(f"Hello {message.from_user.mention}!\n\nI am a Music & Lyrics Downloader bot. Use `/song [song name]` to start.")

@app.on_message(filters.command("song"))
async def song_handler(client, message):
    if not await check_fsub(client, message):
        return

    query = " ".join(message.command[1:])
    if not query:
        return await message.reply_text("Please provide a song name! Example: `/song Blinding Lights`")

    m = await message.reply_text("🔎 **Searching for the song...**")

    # Check if cookies file exists
    cookie_dict = {}
    if os.path.exists("cookies.txt"):
        cookie_dict['cookiefile'] = 'cookies.txt'

    ydl_opts = {
        'format': 'bestaudio/best',
        'outtmpl': '%(title)s.mp3',
        'postprocessors': [{'key': 'FFmpegExtractAudio','preferredcodec': 'mp3','preferredquality': '192'}],
        'quiet': True,
        'default_search': 'ytsearch',
        'noplaylist': True,
        'nocheckcertificate': True,
        **cookie_dict # This injects cookies if the file exists
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(query, download=True)
            video = info['entries'][0] if 'entries' in info else info
            title = video['title']
            thumbnail = video.get('thumbnail')
            file_name = ydl.prepare_filename(video)

        await m.edit("✍️ **Fetching lyrics...**")
        
        lyrics_text = "Lyrics not found! 😶"
        try:
            song = genius.search_song(title)
            if song:
                lyrics_text = song.lyrics
        except:
            pass

        caption = (
            f"🎵 **Song:** `{title}`\n"
            f"👤 **Requested by:** {message.from_user.mention}\n\n"
            f"━━━━━━━━━━━━━━━━━━\n"
            f"📜 **LYRICS:**\n\n"
            f"{lyrics_text[:900]}..." 
            f"\n━━━━━━━━━━━━━━━━━━"
        )

        if thumbnail:
            await message.reply_photo(photo=thumbnail, caption=caption)
        else:
            await message.reply_text(caption)
            
        await message.reply_audio(audio=open(file_name, 'rb'), title=title)
        
        await m.delete()
        os.remove(file_name)

    except Exception as e:
        error_msg = str(e)
        if "Sign in to confirm" in error_msg:
            await m.edit("❌ **Error:** YouTube is blocking the request. Please make sure the `cookies.txt` file is uploaded and valid.")
        else:
            await m.edit(f"❌ **An unexpected error occurred:**\n`{error_msg[:200]}`")

print("Bot is starting with English interface...")
app.run()
