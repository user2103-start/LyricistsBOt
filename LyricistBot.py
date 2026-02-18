import os
import asyncio
import threading
from flask import Flask
from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from pyrogram.errors import UserNotParticipant
import yt_dlp
import lyricsgenius

# --- 🌐 RENDER PORT BINDING FIX ---
# Ye hissa Render ko 'Live' dikhane ke liye hai
web_app = Flask(__name__)

@web_app.route('/')
def home():
    return "Bot is Running Live!"

def run_web():
    # Render default port 10000 use karta hai, ye wahi bind karega
    port = int(os.environ.get("PORT", 8080))
    web_app.run(host="0.0.0.0", port=port)

# Background mein web server start karein
threading.Thread(target=run_web, daemon=True).start()

# --- 🟢 CONFIGURATION (Updated with your data) ---
API_ID = 28456866  # Maine isse integer bana diya hai
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
        # Agar koi error aaye (like bot admin nahi hai), toh bypass kar do
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

    ydl_opts = {
        'format': 'bestaudio/best',
        'outtmpl': '%(title)s.mp3',
        'postprocessors': [{'key': 'FFmpegExtractAudio','preferredcodec': 'mp3','preferredquality': '192'}],
        'quiet': True,
        'default_search': 'ytsearch',
        'noplaylist': True
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
            # Lyrics search with song title
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
        await m.edit(f"Galti ho gayi: {str(e)}")

print("Bot is starting...")
app.run()
