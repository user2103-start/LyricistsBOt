import os
import asyncio
import requests
import threading
import lyricsgenius
from flask import Flask
from pyrogram import Client, filters
from pyrogram.errors import FloodWait

# --- 🌐 WEB SERVER FOR RENDER ---
web_app = Flask(__name__)
@web_app.route('/')
def home(): return "SoundStat Ultimate Engine is Live! 🚀"

def run_web():
    port = int(os.environ.get("PORT", 8080))
    web_app.run(host="0.0.0.0", port=port)

# --- 🟢 CONFIG ---
API_ID = 38456866
API_HASH = "30a8f347f538733a1d57dae8cc458ddc"
BOT_TOKEN = "8454384380:AAEsXBAm3IrtW3Hf1--2mH3xAyhnan-J3lg"
GENIUS_TOKEN = "w-XTArszGpAQaaLu-JlViwy1e-0rxx4dvwqQzOEtcmmpYndHm_nkFTvAB5BsY-ww"
SUDO_USER = 6593129349 # ✅ Sahi Telegram ID update kar di hai
USERS_FILE = "users.txt"

app = Client("LyricistsBot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)
genius = lyricsgenius.Genius(GENIUS_TOKEN)

# --- 🛠️ HELPERS ---
def add_user(user_id):
    if not os.path.exists(USERS_FILE): open(USERS_FILE, "w").close()
    with open(USERS_FILE, "r+") as f:
        users = f.read().splitlines()
        if str(user_id) not in users:
            f.write(f"{user_id}\n")

# --- 🤖 COMMANDS ---

@app.on_message(filters.command("start"))
async def start_cmd(client, message):
    add_user(message.from_user.id)
    await message.reply_text(
        f"👋 **Namaste {message.from_user.first_name}!**\n\n"
        "Main SoundStat Premium Music bot hoon.\n"
        "Gaana download karne ke liye likho: `/song [naam]`\n\n"
        "🚀 **Powered by Render & SoundStat**"
    )

@app.on_message(filters.command("song"))
async def song_handler(client, message):
    if len(message.command) < 2:
        return await message.reply_text("❌ Bhai, gaane ka naam toh likho!")
    
    query = " ".join(message.command[1:])
    m = await message.reply_text("🎬 **Searching & Processing...**")
    
    try:
        dl_url = f"https://api.vyt-dlp.workers.dev/download_query?q={query}"
        file_path = f"song_{message.from_user.id}.mp3"

        r = requests.get(dl_url, stream=True, timeout=120)
        if r.status_code == 200:
            with open(file_path, 'wb') as f:
                for chunk in r.iter_content(chunk_size=1024*1024):
                    if chunk: f.write(chunk)
            
            try:
                g_song = genius.search_song(query)
                lyrics = g_song.lyrics.split('Lyrics', 1)[-1].strip() if g_song else "Lyrics nahi mile."
            except:
                lyrics = "Lyrics fetch error."

            await message.reply_audio(
                audio=open(file_path, 'rb'),
                title=query,
                caption=f"🎵 **{query}**\n\n📜 `{lyrics[:800]}`"
            )
            await m.delete()
        else:
            await m.edit("❌ Download bridge busy hai, baad mein try karo.")

        if os.path.exists(file_path): os.remove(file_path)
    except Exception as e:
        await m.edit(f"❌ Error: {str(e)[:50]}")

@app.on_message(filters.command("broadcast") & filters.user(SUDO_USER))
async def broadcast_handler(client, message):
    if not message.reply_to_message:
        return await message.reply_text("❌ Kisi message ko reply karke `/broadcast` likho!")
    
    if not os.path.exists(USERS_FILE):
        return await message.reply_text("❌ Abhi tak koi user nahi hai.")

    with open(USERS_FILE, "r") as f:
        users = f.read().splitlines()

    sent = 0
    m = await message.reply_text(f"📢 **Broadcast shuru...** (Total: {len(users)})")
    
    for user_id in users:
        try:
            await message.reply_to_message.copy(int(user_id))
            sent += 1
            await asyncio.sleep(0.3)
        except FloodWait as e:
            await asyncio.sleep(e.value)
        except:
            pass
    
    await m.edit(f"✅ **Broadcast Done!**\nSent to: {sent} users.")

# --- 🚀 RENDER RUNNER (LOOP FIX) ---
async def start_bot():
    threading.Thread(target=run_web, daemon=True).start()
    await app.start()
    print("✅ Bot is online on Render!")
    await asyncio.Event().wait()

if __name__ == "__main__":
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    try:
        loop.run_until_complete(start_bot())
    except KeyboardInterrupt:
        pass
