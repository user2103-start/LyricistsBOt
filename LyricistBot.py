import os
import asyncio
import threading
from flask import Flask
from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from pyrogram.errors import UserNotParticipant
import yt_dlp
import lyricsgenius

# --- 🌐 RENDER PORT BINDING ---
web_app = Flask(__name__)

@web_app.route('/')
def home():
    return "Bot is Running Live with Bypass Logic!"

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
            "⚠️ **Wait Bhai!**\n\nBot use karne ke liye hamare update channel ko join karna zaroori hai.",
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
    await message.reply_text(f"Hi {message.from_user.mention}!\n\nMain music aur lyrics bot hoon. Gaana dhoondne ke liye `/song [naam]` likho.")

@app.on_message(filters.command("song"))
async def song_handler(client, message):
    if not await check_fsub(client, message):
        return

    query = " ".join(message.command[1:])
    if not query:
        return await message.reply_text("Bhai, gaane ka naam toh likho! `/song Kesariya`")

    m = await message.reply_text("🔎 **Dhoond raha hoon...**")

    # --- 🛠 BYPASS OPTIONS ADDED HERE ---
    ydl_opts = {
        'format': 'bestaudio/best',
        'outtmpl': '%(title)s.mp3',
        'postprocessors': [{'key': 'FFmpegExtractAudio','preferredcodec': 'mp3','preferredquality': '192'}],
        'quiet': True,
        'default_search': 'ytsearch',
        'noplaylist': True,
        'nocheckcertificate': True,
        'geo_bypass': True,
        'http_headers': {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'en-us,en;q=0.5',
            'Sec-Fetch-Mode': 'navigate',
        }
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(query, download=True)
            if 'entries' in info:
                video = info['entries'][0]
            else:
                video = info
                
            title = video['title']
            thumbnail = video.get('thumbnail')
            file_name = ydl.prepare_filename(video)

        await m.edit("✍️ **Lyrics nikaal raha hoon...**")
        
        lyrics_text = "Lyrics nahi mil payi! 😶"
        try:
            song = genius.search_song(title)
            if song:
                lyrics_text = song.lyrics
        except:
            pass

        caption = (
            f"🎵 **Song:** `{title}`\n"
            f"👤 **By:** {message.from_user.mention}\n\n"
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
        await m.edit(f"❌ **Error:**\n`{str(e)[:200]}`\n\nBhai, YouTube ne block kiya hai. Agar ye baar-baar ho toh hume cookies use karni padengi.")

print("Bot is starting with bypass headers...")
app.run()
