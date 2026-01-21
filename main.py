import os
import sqlite3
import uuid
import asyncio
import requests
from datetime import datetime
from aiohttp import web
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup, KeyboardButton
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

# --- ⚙️ AYARLAR ---
TOKEN = os.getenv("BOT_TOKEN")
PORT = int(os.environ.get("PORT", 10000))
BASE_URL = "https://lordageichatsohbet.onrender.com"
KANAL_URL = "https://t.me/lordsystemv3"
DESTEK_URL = "https://t.me/LordDestekHat"

# --- 📁 DATABASE SİSTEMİ ---
def init_db():
    conn = sqlite3.connect('lord_v201_ref.db')
    c = conn.cursor()
    c.execute("CREATE TABLE IF NOT EXISTS users (id TEXT PRIMARY KEY, balance INTEGER, referred_by TEXT)")
    c.execute("CREATE TABLE IF NOT EXISTS keys (key TEXT PRIMARY KEY, user_id TEXT)")
    conn.commit()
    conn.close()

init_db()

# --- 🧠 GERÇEK AI BEYNİ (DeepSeek-V3) ---
async def get_real_ai_logic(user_query):
    try:
        url = "https://api.blackbox.ai/api/chat"
        payload = {
            "messages": [{"role": "user", "content": user_query}],
            "model": "deepseek-v3",
            "max_tokens": 4096
        }
        response = requests.post(url, json=payload, timeout=40)
        if response.status_code == 200:
            try: return response.json()["choices"][0]["message"]["content"]
            except: return response.text
        return "⚠️ AI Sunucusu meşgul Lord."
    except: return "🚨 Bağlantı hatası."

# --- 🔗 BUTONLAR ---
def pro_markup():
    return InlineKeyboardMarkup([[InlineKeyboardButton("📢 Kanal", url=KANAL_URL), InlineKeyboardButton("🛠️ Destek", url=DESTEK_URL)]])

# --- 🌐 API ---
async def handle_api(request):
    key, q = request.query.get("key"), request.query.get("q")
    if not key or not q: return web.json_response({"error": "Eksik parametre"}, status=400)
    conn = sqlite3.connect('lord_v201_ref.db'); c = conn.cursor()
    c.execute("SELECT user_id FROM keys WHERE key=?", (key,))
    k_res = c.fetchone()
    if not k_res: conn.close(); return web.json_response({"error": "Geçersiz Key"}, status=403)
    c.execute("SELECT balance FROM users WHERE id=?", (k_res[0],))
    u_res = c.fetchone()
    if not u_res or u_res[0] <= 0: conn.close(); return web.json_response({"error": "Bakiye bitti"}, status=402)
    c.execute("UPDATE users SET balance = balance - 1 WHERE id=?", (k_res[0],))
    conn.commit(); conn.close()
    ans = await get_real_ai_logic(q)
    return web.json_response({"status": "success", "response": ans, "remaining_balance": u_res[0]-1})

# --- 🤖 BOT MANTIĞI ---
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    uid = str(update.effective_user.id)
    args = context.args # /start [ref_id]
    conn = sqlite3.connect('lord_v201_ref.db'); c = conn.cursor()
    
    c.execute("SELECT id FROM users WHERE id=?", (uid,))
    user_exists = c.fetchone()

    if not user_exists:
        ref_id = args[0] if args and args[0] != uid else None
        c.execute("INSERT INTO users VALUES (?, ?, ?)", (uid, 10, ref_id))
        if ref_id:
            c.execute("UPDATE users SET balance = balance + 3 WHERE id=?", (ref_id,))
            try: await context.bot.send_message(chat_id=ref_id, text="🎁 **Tebrikler!** Bir arkadaşın linkinle katıldı, +3 Jeton kazandın!")
            except: pass
        conn.commit()

    conn.close()
    kb = [[KeyboardButton("🤖 AI Chat"), KeyboardButton("💰 Bakiye & Ref")], [KeyboardButton("🔑 API & Profil")]]
    await update.message.reply_text("👑 **Lord V201: Ref & Real AI**\nHoş geldin Lord!", reply_markup=ReplyKeyboardMarkup(kb, resize_keyboard=True))

async def msg_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text, uid = update.message.text, str(update.effective_user.id)
    conn = sqlite3.connect('lord_v201_ref.db'); c = conn.cursor()

    if text == "💰 Bakiye & Ref":
        c.execute("SELECT balance FROM users WHERE id=?", (uid,))
        bal = c.fetchone()[0]
        bot_info = await context.bot.get_me()
        ref_link = f"https://t.me/{bot_info.username}?start={uid}"
        await update.message.reply_text(f"💰 **Bakiyeniz:** `{bal} Jeton`\n\n👥 **Arkadaşını Davet Et:**\nHer davet için **+3 Jeton** kazanırsın!\n\n🔗 **Ref Linkin:** `{ref_link}`", parse_mode="Markdown")

    elif text == "🔑 API & Profil":
        c.execute("SELECT key FROM keys WHERE user_id=?", (uid,))
        res = c.fetchone()
        if not res:
            key = f"LORD-{uuid.uuid4().hex[:8].upper()}"
            c.execute("INSERT INTO keys VALUES (?, ?)", (key, uid))
            conn.commit()
        else: key = res[0]
        await update.message.reply_text(f"🔑 Key: `{key}`\n🔗 API: `{BASE_URL}/api?key={key}&q=Naber`", parse_mode="Markdown", reply_markup=pro_markup())

    elif not text.startswith("/"):
        c.execute("SELECT balance FROM users WHERE id=?", (uid,))
        u_bal = c.fetchone()[0]
        if u_bal > 0:
            c.execute("UPDATE users SET balance = balance - 1 WHERE id=?", (uid,)); conn.commit()
            await update.message.reply_chat_action("typing")
            ans = await get_real_ai_logic(text)
            await update.message.reply_text(ans, parse_mode="Markdown", reply_markup=pro_markup())
        else: await update.message.reply_text("❌ Jeton bitti! Arkadaşını davet ederek kazanabilirsin.")
    conn.close()

async def main():
    app_web = web.Application()
    app_web.router.add_get("/api", handle_api)
    runner = web.AppRunner(app_web); await runner.setup()
    await web.TCPSite(runner, "0.0.0.0", PORT).start()
    app = Application.builder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, msg_handler))
    async with app:
        await app.initialize(); await app.start(); await app.updater.start_polling(); await asyncio.Event().wait()

if __name__ == "__main__": asyncio.run(main())
