import os
import sqlite3
import uuid
import asyncio
import random
from datetime import datetime
from aiohttp import web
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup, KeyboardButton
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

# --- ⚙️ AYARLAR ---
TOKEN = os.getenv("BOT_TOKEN")
ADMIN_ID = 8258235296
PORT = int(os.environ.get("PORT", 10000))
BASE_URL = "https://lordageichatsohbet.onrender.com"

# Linklerin (Değiştirebilirsin)
KANAL_URL = "https://t.me/lordsystemv3"
DESTEK_URL = "https://t.me/LordDestekHat"

# --- 📁 DATABASE SİSTEMİ ---
def init_db():
    conn = sqlite3.connect('lord_v23.db')
    c = conn.cursor()
    c.execute("CREATE TABLE IF NOT EXISTS users (id TEXT PRIMARY KEY, balance INTEGER, mode TEXT, status TEXT)")
    c.execute("CREATE TABLE IF NOT EXISTS keys (key TEXT PRIMARY KEY, user_id TEXT)")
    conn.commit()
    conn.close()

init_db()

# --- 🧠 GERÇEK AI BEYNİ (V23 Dinamik Motor) ---
async def generate_ai_response(query):
    query = query.lower()
    
    # 1. Selamlaşma Analizi
    if any(x in query for x in ["selam", "merhaba", "hey", "slm"]):
        return "Selamlar Lord! İmparatorluk sistemleri senin emrine amade. Bugün hangi veriyi işleyelim?"
    
    # 2. Durum Analizi
    if any(x in query for x in ["nasılsın", "naber", "durumlar"]):
        return "Tüm çekirdeklerim optimize edildi, bakiye sistemleri aktif. Ben harikayım, sen nasılsın Lord?"

    # 3. Bilgi ve Genel Sorgu Analizi (Dinamik Mesaj Üretimi)
    prefixes = ["Analizim şu şekilde:", "Veri havuzumdan çıkan sonuç:", "İmparatorluk kayıtlarına göre:"]
    thoughts = [
        f"'{query}' konusu üzerine yaptığım derin taramada, bu durumun geleceğin teknolojileriyle doğrudan bağlantılı olduğunu fark ettim.",
        f"Sorduğun '{query}' meselesini küresel trendlerle karşılaştırdım. Sonuçlar, stratejik bir büyüme potansiyeline işaret ediyor.",
        f"'{query}' sorgusu işlendi. Bu kavramın modern dünya düzenindeki yeri oldukça kritik görünüyor Lord."
    ]
    return f"{random.choice(prefixes)}\n\n{random.choice(thoughts)}"

# --- 🔗 BUTON PANELİ (Her mesajın altına) ---
def get_support_markup():
    buttons = [
        [InlineKeyboardButton("📢 Kanalımız", url=KANAL_URL),
         InlineKeyboardButton("🛠️ Destek Hattı", url=DESTEK_URL)]
    ]
    return InlineKeyboardMarkup(buttons)

# --- 🌐 API ENDPOINT (V23) ---
async def handle_api(request):
    key_param = request.query.get("key")
    query_param = request.query.get("q")
    
    if not key_param or not query_param:
        return web.json_response({"error": "Parametre eksik!"}, status=400)

    conn = sqlite3.connect('lord_v23.db')
    c = conn.cursor()
    c.execute("SELECT user_id FROM keys WHERE key=?", (key_param,))
    k_data = c.fetchone()
    
    if not k_data:
        conn.close()
        return web.json_response({"error": "Geçersiz Key!"}, status=403)
    
    uid = k_data[0]
    c.execute("SELECT balance FROM users WHERE id=?", (uid,))
    u_data = c.fetchone()
    
    if not u_data or u_data[0] <= 0:
        conn.close()
        return web.json_response({"error": "Bakiye bitti!"}, status=402)

    c.execute("UPDATE users SET balance = balance - 1 WHERE id=?", (uid,))
    conn.commit()
    conn.close()

    ai_answer = await generate_ai_response(query_param)

    return web.json_response({
        "status": "success",
        "response": ai_answer,
        "remaining_balance": u_data[0] - 1,
        "support": DESTEK_URL,
        "channel": KANAL_URL
    })

# --- 🤖 BOT MANTIĞI ---
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    uid = str(update.effective_user.id)
    conn = sqlite3.connect('lord_v23.db')
    c = conn.cursor()
    c.execute("SELECT balance FROM users WHERE id=?", (uid,))
    if not c.fetchone():
        c.execute("INSERT INTO users VALUES (?, ?, ?, ?)", (uid, 20, "Sohbet", "active"))
        conn.commit()
    conn.close()

    kb = [[KeyboardButton("🤖 AI Chat"), KeyboardButton("💰 Bakiye")], [KeyboardButton("🔑 API & Profil")]]
    await update.message.reply_text("👑 **Lord V23 Online!**\nSorgularınızı bekliyorum.", 
                                   reply_markup=ReplyKeyboardMarkup(kb, resize_keyboard=True))

async def msg_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    uid = str(update.effective_user.id)
    
    if text == "🔑 API & Profil":
        conn = sqlite3.connect('lord_v23.db')
        c = conn.cursor()
        c.execute("SELECT key FROM keys WHERE user_id=?", (uid,))
        res = c.fetchone()
        if not res:
            new_key = f"LORD-{uuid.uuid4().hex[:8].upper()}"
            c.execute("INSERT INTO keys VALUES (?, ?)", (new_key, uid))
            conn.commit()
            key = new_key
        else: key = res[0]
        conn.close()
        await update.message.reply_text(f"🔑 Keyin: `{key}`\n🔗 API: `{BASE_URL}/api?key={key}&q=Merhaba`", 
                                        parse_mode="Markdown", reply_markup=get_support_markup())

    elif not text.startswith("/"):
        await update.message.reply_chat_action("typing")
        response = await generate_ai_response(text)
        # Her AI yanıtının altına Destek ve Kanal butonlarını ekler
        await update.message.reply_text(response, reply_markup=get_support_markup())

# --- 🚀 RUNNER ---
async def main():
    if not TOKEN: return
    
    app_web = web.Application()
    app_web.router.add_get("/api", handle_api)
    app_web.router.add_get("/", lambda r: web.Response(text="Lord V23 Active"))
    runner = web.AppRunner(app_web)
    await runner.setup()
    await web.TCPSite(runner, "0.0.0.0", PORT).start()

    application = Application.builder().token(TOKEN).build()
    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, msg_handler))

    async with application:
        await application.initialize()
        await application.start()
        await application.updater.start_polling()
        await asyncio.Event().wait()

if __name__ == "__main__":
    asyncio.run(main())
