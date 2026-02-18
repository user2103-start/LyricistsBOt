import os
from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from pyrogram.errors import UserNotParticipant
import yt_dlp
import lyricsgenius

# --- 🟢 CONFIGURATION ---
API_ID = "38456866" # Yahan apni API ID daalo
API_HASH = "30a8f347f538733a1d57dae8cc458ddc" # Yahan apna API HASH daalo
BOT_TOKEN = "8454384380:AAEsXBAm3IrtW3Hf1--2mH3xAyhnan-J3lg" # BotFather wala token
GENIUS_TOKEN = "w-XTArszGpAQaaLu-JlViwy1e-0rxx4dvwqQzOEtcmmpYndHm_nkFTvAB5BsY-ww"

ADMIN_ID = 6593129349 # Apni numerical ID daalo (example: 12345678)
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
        'quiet': True
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(f"ytsearch:{query}", download=True)
            video = info['entries'][0]
            title = video['title']
            thumbnail = video['thumbnail']
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

        await message.reply_photo(photo=thumbnail, caption=caption)
        await message.reply_audio(audio=open(file_name, 'rb'), title=title)
        
        await m.delete()
        os.remove(file_name)

    except Exception as e:
        await m.edit(f"Galti ho gayi: {str(e)}")

app.run()