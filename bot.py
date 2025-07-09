import os
from pyrogram import Client, filters
from pytgcalls import PyTgCalls, idle
from pytgcalls.types.input_stream import InputStream, AudioPiped
from yt_dlp import YoutubeDL

api_id = int(os.getenv("API_ID"))
api_hash = os.getenv("API_HASH")
bot_token = os.getenv("BOT_TOKEN")
session_string = os.getenv("SESSION")
owner_id = int(os.getenv("OWNER_ID"))

app = Client(name="hamada", api_id=api_id, api_hash=api_hash, bot_token=bot_token)
user = Client(name="user", session_string=session_string, api_id=api_id, api_hash=api_hash)
call = PyTgCalls(user)

ydl_opts = {'format': 'bestaudio', 'outtmpl': 'downloads/%(id)s.%(ext)s'}
queue = []

@app.on_message(filters.command("play") & filters.chat_type.groups)
async def play(_, msg):
    if len(msg.command) < 2:
        return await msg.reply("❌ Masukkan judul atau link YouTube.")
    query = " ".join(msg.command[1:])
    m = await msg.reply("🔍 Mencari...")
    with YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(f"ytsearch:{query}", download=False)['entries'][0]
        url = info['webpage_url']
        title = info['title']
        ydl.download([url])
    file_path = os.path.join("downloads", f"{info['id']}.{info['ext']}")
    queue.append(file_path)
    await m.edit(f"🎶 Menambahkan ke antrian: {title}")
    if len(queue) == 1:
        await call.join_group_call(msg.chat.id, InputStream(AudioPiped(file_path)))

@app.on_message(filters.command("pause") & filters.user(owner_id))
async def pause(_, msg): await call.pause_stream(msg.chat.id); await msg.reply("⏸ Dijeda.")

@app.on_message(filters.command("resume") & filters.user(owner_id))
async def resume(_, msg): await call.resume_stream(msg.chat.id); await msg.reply("▶ Dilanjut.")

@app.on_message(filters.command("skip") & filters.user(owner_id))
async def skip(_, msg):
    if queue:
        queue.pop(0)
        if queue:
            await call.change_stream(msg.chat.id, AudioPiped(queue[0]))
            await msg.reply("⏭ Lagu berikutnya.")
        else:
            await call.leave_group_call(msg.chat.id)
            await msg.reply("✅ Antrian habis, keluar VC.")

@app.on_message(filters.command("queue"))
async def list_queue(_, msg):
    if not queue:
        return await msg.reply("🎧 Antrian kosong.")
    txt = "\n".join([f"{i+1}. {os.path.basename(q)}" for i, q in enumerate(queue)])
    await msg.reply(f"🎵 Antrian:\n{txt}")

async def main():
    await app.start()
    await user.start()
    await call.start()
    print("Bot aktif!")
    await idle()
    await app.stop()
    await user.stop()

import asyncio
if __name__ == "__main__":
    asyncio.run(main())
