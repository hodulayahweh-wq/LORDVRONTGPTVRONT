import os
import sqlite3
import uuid
import asyncio
import random
import re
from datetime import datetime
from aiohttp import web
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup, KeyboardButton
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

# --- ⚙️ KONFİGÜRASYON ---
TOKEN = os.getenv("BOT_TOKEN")
ADMIN_ID = 8258235296
PORT = int(os.environ.get("PORT", 10000))
BASE_URL = "https://lordageichatsohbet.onrender.com"

KANAL_URL = "https://t.me/lordsystemv3"
DESTEK_URL = "https://t.me/LordDestekHat"

# --- 📁 VERİTABANI BAŞLATMA ---
def init_db():
    conn = sqlite3.connect('lord_v100.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS users 
                 (id TEXT PRIMARY KEY, balance INTEGER, mode TEXT, status TEXT)''')
    c.execute('''CREATE TABLE IF NOT EXISTS keys 
                 (key TEXT PRIMARY KEY, user_id TEXT)''')
    conn.commit()
    conn.close()

init_db()

# --- 🧠 ULTRA PROFESYONEL AI MOTORU (Neural Coder) ---
async def neural_lord_engine(query):
    query_lower = query.lower()
    
    # 1. KOD YAZMA TALEBİ ANALİZİ
    if any(word in query_lower for word in ["kodla", "yaz", "python", "script", "bot yap"]):
        return (
            "🚀 **Lord Neural Coder Devreye Girdi**\n\n"
            "İsteğiniz üzerine ultra profesyonel bir yapı hazırladım:\n\n"
            "```python\n"
            "import telebot\n"
            "# Lord System v100 Auto-Generated Script\n"
            "bot = telebot.TeleBot('TOKEN')\n\n"
            "@bot.message_handler(func=lambda m: True)\n"
            "def echo_all(message):\n"
            "    bot.reply_to(message, 'Sistem Aktif!')\n\n"
            "bot.infinity_polling()\n"
            "```\n"
            "*(Bu kod Lord V100 tarafından optimize edilmiştir.)*"
        )

    # 2. SELAMLAŞMA VE DURUM
    if "selam" in query_lower or "merhaba" in query_lower:
        return "Selamlar Lord! Yapay zeka çekirdeğim ve tüm kodlama modüllerim emrinizde. Ne hazırlamamı istersiniz?"

    # 3. GENEL ZEKİ YANITLAR (Dinamik Üretim)
    responses = [
        f"🔍 **Analiz Sonucu:** '{query}' üzerine yaptığım derinlemesine taramada, konunun teknolojik altyapısını ve gelecekteki potansiyelini inceledim. Lord protokollerine göre bu süreç başarıyla optimize edilebilir.",
        f"📊 **Stratejik Rapor:** Sorgunuz olan '{query}', global veri ağlarında işlendi. İmparatorluk standartlarında en yüksek verimlilik puanını alıyor.",
        f"⚡ **Neural İşlem:** '{query}' talebi sinir ağlarımda işlendi. Sonuç: Lord AI bu konuda tam yetkiyle yanınızda."
    ]
    return random.choice(responses)

# --- 🔗 BUTON PANELİ ---
def get_support_buttons():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("📢 Kanalımız", url=KANAL_URL),
         InlineKeyboardButton("🛠️ Destek Hattı", url=DESTEK_URL)]
    ])

# --- 🌐 YÜKSEK KAPASİTELİ API ---
async def handle_api(request):
    key = request.query.get("key")
    q = request.query.get("q")
    
    if not key or not q:
        return web.json_response({"error": "Parametre eksik"}, status=400)

    conn = sqlite3.connect('lord_v100.db')
    c = conn.cursor()
    c.execute("SELECT user_id FROM keys WHERE key=?", (key,))
    key_res = c.fetchone()
    
    if not key_res:
        conn.close()
        return web.json_response({"error": "Gecersiz Key"}, status=403)
    
    uid = key_res[0]
    c.execute("SELECT balance FROM users WHERE id=?", (uid,))
    user = c.fetchone()
    
    if not user or user[0] <= 0:
        conn.close()
        return web.json_response({"error": "Bakiye yetersiz"}, status=402)

    # Bakiye düş ve AI yanıtını üret
    c.execute("UPDATE users SET balance = balance - 1 WHERE id=?", (uid,))
    conn.commit()
    conn.close()

    ai_answer = await neural_lord_engine(q)

    return web.json_response({
        "status": "success",
        "engine": "Lord Neural V100",
        "response": ai_answer,
        "remaining_balance": user[0] - 1,
        "links": {"support": DESTEK_URL, "channel": KANAL_URL}
    })

# --- 🤖 BOT MANTIĞI ---
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    uid = str(update.effective_user.id)
    conn = sqlite3.connect('lord_v100.db')
    c = conn.cursor()
    c.execute("SELECT balance FROM users WHERE id=?", (uid,))
    if not c.fetchone():
        c.execute("INSERT INTO users VALUES (?, ?, ?, ?)", (uid, 50, "Pro", "active"))
        conn.commit()
    conn.close()

    kb = [[KeyboardButton("🤖 AI Chat"), KeyboardButton("💰 Bakiye")], [KeyboardButton("🔑 API & Profil")]]
    await update.message.reply_text(
        "👑 **LORD SYSTEM V100: THE NEURAL ARCHITECT**\n\n"
        "Sadece bir bot değil, gerçek bir kod yazarı ve analiz motoru emrinizde Lord!",
        reply_markup=ReplyKeyboardMarkup(kb, resize_keyboard=True))

async def message_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    uid = str(update.effective_user.id)
    
    if text == "🔑 API & Profil":
        conn = sqlite3.connect('lord_v100.db')
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
        await update.message.reply_text(f"🔑 **Key:** `{key}`\n🔗 **API:** `{BASE_URL}/api?key={key}&q=Mesaj`", 
                                        parse_mode="Markdown", reply_markup=get_support_buttons())

    elif not text.startswith("/"):
        conn = sqlite3.connect('lord_v100.db')
        c = conn.cursor()
        c.execute("SELECT balance FROM users WHERE id=?", (uid,))
        u_data = c.fetchone()
        
        if u_data and u_data[0] > 0:
            c.execute("UPDATE users SET balance = balance - 1 WHERE id=?", (uid,))
            conn.commit()
            conn.close()
            
            await update.message.reply_chat_action("typing")
            response = await neural_lord_engine(text)
            await update.message.reply_text(response, parse_mode="Markdown", reply_markup=get_support_buttons())
        else:
            await update.message.reply_text("❌ Jeton yetersiz! Lütfen bakiye yükleyin.")
            conn.close()

# --- 🚀 RUNNER ---
async def main():
    if not TOKEN: return
    
    app_web = web.Application()
    app_web.router.add_get("/api", handle_api)
    app_web.router.add_get("/", lambda r: web.Response(text="Lord V100 Online"))
    runner = web.AppRunner(app_web)
    await runner.setup()
    await web.TCPSite(runner, "0.0.0.0", PORT).start()

    app = Application.builder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, message_handler))

    async with app:
        await app.initialize()
        await app.start()
        await app.updater.start_polling()
        await asyncio.Event().wait()

if __name__ == "__main__":
    asyncio.run(main())
