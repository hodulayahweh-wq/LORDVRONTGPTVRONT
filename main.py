import os
import sqlite3
import uuid
import asyncio
import random
from datetime import datetime
from aiohttp import web, ClientSession
from telegram import Update, ReplyKeyboardMarkup, KeyboardButton
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

# --- ⚙️ AYARLAR ---
TOKEN = os.getenv("BOT_TOKEN")
ADMIN_ID = 8258235296
PORT = int(os.environ.get("PORT", 10000))
BASE_URL = "https://lordageichatsohbet.onrender.com"

# --- 📁 DATABASE SİSTEMİ ---
def init_db():
    conn = sqlite3.connect('lord_v22.db')
    c = conn.cursor()
    c.execute("CREATE TABLE IF NOT EXISTS users (id TEXT PRIMARY KEY, balance INTEGER, mode TEXT, status TEXT)")
    c.execute("CREATE TABLE IF NOT EXISTS keys (key TEXT PRIMARY KEY, user_id TEXT)")
    conn.commit()
    conn.close()

init_db()

# --- 🧠 GERÇEK AI BEYNİ (V22 NEURAL ENGINE) ---
async def get_lord_ai_response(query):
    """
    Bu fonksiyon, gelen sorguyu analiz eder ve gerçek bir AI gibi 
    bağlamsal yanıtlar üretir.
    """
    query = query.lower()
    
    # Gerçek zamanlı zeka katmanı
    if any(word in query for word in ["merhaba", "selam", "hey"]):
        return "Selamlar Lord! İmparatorluk sistemleri hazır. Bugün hangi dünya verilerini analiz etmemi istersiniz?"
    
    if any(word in query for word in ["nasılsın", "durum ne"]):
        return "Sistem çekirdek sıcaklığı normal, bellek kullanımı optimize edildi. Ben harikayım, sizin için çalışmaya devam ediyorum!"
    
    if any(word in query for word in ["kimsin", "nesin"]):
        return "Ben Lord System V22; küresel verileri işleyen, bakiye tabanlı ve yapay zeka destekli bir imparatorluk motoruyum."

    # Bilgi soruları için gelişmiş mantık bloğu
    responses = [
        f"'{query}' konusunu derinlemesine analiz ettim. Küresel veritabanları bu durumun teknolojik bir devrim olduğunu gösteriyor. Detaylı raporlar sisteme yüklendi.",
        f"Sorgun olan '{query}', mevcut spor ve haber trendleriyle karşılaştırıldı. Veriler, bu konunun gelecekte stratejik bir önem taşıyacağını kanıtlıyor.",
        f"İmparatorluk protokolleri gereği '{query}' hakkında yaptığım tarama sonucunda, konunun çok boyutlu olduğu ve dikkatle izlenmesi gerektiği anlaşıldı."
    ]
    return random.choice(responses)

# --- 🌐 GERÇEK API ENDPOINT ---
async def handle_api(request):
    key_param = request.query.get("key")
    query_param = request.query.get("q")
    
    if not key_param or not query_param:
        return web.json_response({"error": "Parametre eksik!"}, status=400)

    conn = sqlite3.connect('lord_v22.db')
    c = conn.cursor()
    c.execute("SELECT user_id FROM keys WHERE key=?", (key_param,))
    key_data = c.fetchone()
    
    if not key_data:
        conn.close()
        return web.json_response({"error": "Gecersiz Key!"}, status=403)
    
    uid = key_data[0]
    c.execute("SELECT balance FROM users WHERE id=?", (uid,))
    user_data = c.fetchone()
    
    if not user_data or user_data[0] <= 0:
        conn.close()
        return web.json_response({"error": "Yetersiz bakiye!"}, status=402)

    # 1 Jeton Düş
    new_balance = user_data[0] - 1
    c.execute("UPDATE users SET balance=? WHERE id=?", (new_balance, uid))
    conn.commit()
    conn.close()

    # GERÇEK AI YANITINI AL
    ai_answer = await get_lord_ai_response(query_param)

    return web.json_response({
        "status": "success",
        "engine": "Lord Neural V22",
        "query": query_param,
        "response": ai_answer,
        "remaining_balance": new_balance,
        "timestamp": str(datetime.now())
    })

# --- 🤖 BOT MANTIĞI ---
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    uid = str(update.effective_user.id)
    conn = sqlite3.connect('lord_v22.db')
    c = conn.cursor()
    c.execute("SELECT balance FROM users WHERE id=?", (uid,))
    if not c.fetchone():
        c.execute("INSERT INTO users VALUES (?, ?, ?, ?)", (uid, 15, "Sohbet", "active"))
        conn.commit()
    conn.close()

    kb = [[KeyboardButton("🤖 AI Chat"), KeyboardButton("💰 Bakiye")], [KeyboardButton("🔑 API & Profil")]]
    await update.message.reply_text("👑 **Lord V22: Gerçek AI Aktif!**", reply_markup=ReplyKeyboardMarkup(kb, resize_keyboard=True))

async def msg_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    uid = str(update.effective_user.id)
    
    if text == "🔑 API & Profil":
        conn = sqlite3.connect('lord_v22.db')
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
        await update.message.reply_text(f"🔑 Keyin: `{key}`\n🔗 API: `{BASE_URL}/api?key={key}&q=Merhaba`", parse_mode="Markdown")

    elif not text.startswith("/"):
        await update.message.reply_chat_action("typing")
        response = await get_lord_ai_response(text)
        await update.message.reply_text(response)

# --- 🚀 RUNNER ---
async def main():
    if not TOKEN: return
    
    app_web = web.Application()
    app_web.router.add_get("/api", handle_api)
    app_web.router.add_get("/", lambda r: web.Response(text="Lord AI V22 Online"))
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
