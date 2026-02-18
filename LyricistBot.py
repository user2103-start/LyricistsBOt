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
def home(): return "Bot is Online and Rocking! 🎸"

def run_web():
    port = int(os.environ.get("PORT", 8080))
    web_app.run(host="0.0.0.0", port=port)

threading.Thread(target=run_web, daemon=True).start()

# --- 🟢 CONFIGURATION ---
# Ye values tumne pehle di thi, wahi use kar raha hoon
API_ID = 38456866
API_HASH = "30a8f347f538733a1d57dae8cc458ddc"
BOT_TOKEN = "8454384380:AAEsXBAm3IrtW3Hf1--2mH3xAyhnan-J3lg"
GENIUS_TOKEN = "w-XTArszGpAQaaLu-JlViwy1e-0rxx4dvwqQzOEtcmmpYndHm_nkFTvAB5BsY-ww"

app = Client("LyricistBot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)
genius = lyricsgenius.Genius(GENIUS_TOKEN)
genius.verbose = False
genius.remove_section_headers = True

# --- 🎵 MULTI-SOURCE SEARCH FUNCTION ---
def search_song(query):
    # Source 1: Saavn.me (Current best)
    urls = [
        f"https://saavn.me/search/songs?query={query}",
        f"https://saavn.dev/api/search/songs?query={query}",
        f"https://jiosaavn-api-v3.vercel.app/search/songs?query={query}"
    ]
    
    for url in urls:
        try:
            res = requests.get(url, timeout=5).json()
            # Handling different API structures
            if isinstance(res, dict) and res.get('status') == 'SUCCESS':
                data = res.get('data', {}).get('results', [])
                if data: return data[0]
            elif isinstance(res, list) and len(res) > 0:
                return res[0]
        except:
            continue
    return None

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
        return await message.reply_text("Bhai, gaane ka naam toh likh! Jaise: `/song Kesariya`")

    query = " ".join(message.command[1:])
    m = await message.reply_text("🔎 **Searching for your song...**")

    song = search_song(query)
    if not song:
        return await m.edit("❌ Gaana nahi mila! Ek baar spelling check karo ya artist ka naam bhi saath likho.")

    try:
        # Data Extraction with Fallbacks
        title = song.get('name') or song.get('song') or "Unknown Title"
        artist = song.get('artists', {}).get('primary', [{}])[0].get('name') or song.get('primary_artists') or "Unknown Artist"
        
        # Audio Link Extraction
        download_url = ""
        if 'downloadUrl' in song:
            download_url = song['downloadUrl'][-1]['url']
        else:
            download_url = song.get('media_url')

        # Thumbnail
        thumb = ""
        if 'image' in song:
            thumb = song['image'][-1]['url']
        else:
            thumb = song.get('image')

        await m.edit("✍️ **Fetching Clean Lyrics...**")
        try:
            g_song = genius.search_song(title, artist)
            lyrics_text = g_song.lyrics.split('Lyrics', 1)[-1].strip() if g_song else "Lyrics nahi mil paye. 😔"
        except:
            lyrics_text = "Lyrics search mein error aaya."

        if len(lyrics_text) > 3500: lyrics_text = lyrics_text[:3500] + "..."

        caption = (
            f"🎵 **Song:** `{title}`\n"
            f"👤 **Artist:** `{artist}`\n"
            f"━━━━━━━━━━━━━━━━━━━\n\n"
            f"📜 **LYRICS:**\n\n`{lyrics_text}`\n\n"
            f"━━━━━━━━━━━━━━━━━━━\n"
            f"⚡ **Powered by:** @Zeabur"
        )

        await m.edit("📥 **Downloading Audio...**")
        file_name = f"{title}.mp3".replace("/", "-")
        audio_data = requests.get(download_url).content
        with open(file_name, 'wb') as f: f.write(audio_data)

        # Delivery
        await message.reply_photo(photo=thumb, caption=caption)
        await message.reply_audio(
            audio=open(file_name, 'rb'), 
            title=title, 
            performer=artist,
            thumb=thumb if thumb.startswith("http") else None
        )
        
        if os.path.exists(file_name): os.remove(file_name)
        await m.delete()

    except Exception as e:
        await m.edit(f"Error: {e}\n\nAPI ne data thoda alag format mein bheja hai, please try another song.")

print("Bot is ready for Zeabur!")
app.run()
