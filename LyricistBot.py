import os
import requests
import threading
import lyricsgenius
from flask import Flask
from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton

# --- 🌐 ZEABUR PORT BINDING (Always Running) ---
web_app = Flask(__name__)
@web_app.route('/')
def home(): return "Bot is Healthy and Singing! 🎵"

def run_web():
    port = int(os.environ.get("PORT", 8080))
    web_app.run(host="0.0.0.0", port=port)

threading.Thread(target=run_web, daemon=True).start()

# --- 🟢 CONFIGURATION ---
API_ID = int(os.environ.get("API_ID", 38456866))
API_HASH = os.environ.get("API_HASH", "30a8f347f538733a1d57dae8cc458ddc")
BOT_TOKEN = os.environ.get("BOT_TOKEN", "8454384380:AAEsXBAm3IrtW3Hf1--2mH3xAyhnan-J3lg")
# Tera naya Genius Token yahan set kar diya hai:
GENIUS_TOKEN = "w-XTArszGpAQaaLu-JlViwy1e-0rxx4dvwqQzOEtcmmpYndHm_nkFTvAB5BsY-ww"

app = Client("LyricistBot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)
genius = lyricsgenius.Genius(GENIUS_TOKEN)
genius.verbose = False # Taaki terminal mein kachra na bhare
genius.remove_section_headers = True # [Chorus] [Verse] jaise headers hatane ke liye

# --- 🎵 FUNCTIONS ---
def get_clean_lyrics(song_title, artist_name):
    try:
        song = genius.search_song(song_title, artist_name)
        if song:
            # Lyrics ki formatting clean kar rahe hain
            lyrics = song.lyrics
            # Genius aksar pehli line mein title daal deta hai, usse hatane ke liye:
            clean_lyrics = lyrics.split('Lyrics', 1)[-1].strip()
            return clean_lyrics
        return "Sorry bhai, is gaane ke lyrics nahi mile. 🥀"
    except Exception:
        return "Lyrics fetch karne mein thoda issue aaya. 🏗️"

def search_saavn(query):
    url = f"https://saavn.dev/api/search/songs?query={query}"
    try:
        res = requests.get(url, timeout=10).json()
        if res['success'] and res['data']['results']:
            return res['data']['results'][0]
    except: return None

# --- 🤖 BOT HANDLERS ---
@app.on_message(filters.command("start"))
async def start(client, message):
    await message.reply_text(
        f"**Namaste {message.from_user.first_name}!** 🙏\n\n"
        "Main hoon tera **Lyricist Bot**. Main gaane download bhi karta hoon aur unke lyrics bhi dhoondta hoon.\n\n"
        "**Usage:** `/song [gaane ka naam]`"
    )

@app.on_message(filters.command("song"))
async def song_handler(client, message):
    if len(message.command) < 2:
        return await message.reply_text("Bhai, gaane ka naam toh likh! Jaise: `/song Safarnama`")

    query = " ".join(message.command[1:])
    m = await message.reply_text("🔎 **Dhoond raha hoon, thoda sabar...**")

    song_data = search_saavn(query)
    if not song_data:
        return await m.edit("❌ Gaana nahi mila! Kuch aur try kar.")

    try:
        title = song_data['name']
        artist = song_data['artists']['primary'][0]['name']
        download_url = song_data['downloadUrl'][-1]['url'] # Best quality
        thumb = song_data['image'][-1]['url']
        
        await m.edit(f"✍️ **'{title}' ke lyrics likh raha hoon...**")
        lyrics_text = get_clean_lyrics(title, artist)
        
        # Telegram limit handle karne ke liye (max 4096 chars)
        if len(lyrics_text) > 3500: lyrics_text = lyrics_text[:3500] + "..."

        caption = (
            f"🎵 **Song:** `{title}`\n"
            f"👤 **Artist:** `{artist}`\n"
            f"━━━━━━━━━━━━━━━━━━━\n\n"
            f"📜 **LYRICS:**\n\n`{lyrics_text}`\n\n"
            f"━━━━━━━━━━━━━━━━━━━\n"
            f"⚡ **Powered by:** @Zeabur"
        )

        await m.edit("📥 **Gaana pack kar raha hoon (Downloading)...**")
        file_name = f"{title}.mp3".replace("/", "-") # Safe filename
        audio_res = requests.get(download_url)
        with open(file_name, 'wb') as f: f.write(audio_res.content)

        # Final Delivery
        await message.reply_photo(
            photo=thumb,
            caption=caption,
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("Search More 🔎", switch_inline_query_current_chat="")]
            ])
        )
        await message.reply_audio(
            audio=open(file_name, 'rb'), 
            title=title, 
            performer=artist,
            thumb=thumb
        )
        
        if os.path.exists(file_name): os.remove(file_name)
        await m.delete()

    except Exception as e:
        await m.edit(f"Error: {e}")

print("Bot deployed successfully on Zeabur!")
app.run()
