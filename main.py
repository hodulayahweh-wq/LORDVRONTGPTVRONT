import os
import sqlite3
import uuid
import asyncio
import requests
import json
from datetime import datetime
from aiohttp import web
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup, KeyboardButton
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

# --- ⚙️ LORD V200 KONFİGÜRASYON ---
TOKEN = os.getenv("BOT_TOKEN")
ADMIN_ID = 8258235296
PORT = int(os.environ.get("PORT", 10000))
BASE_URL = "https://lordageichatsohbet.onrender.com"

KANAL_URL = "https://t.me/lordsystemv3"
DESTEK_URL = "https://t.me/LordDestekHat"

# --- 📁 DATABASE SİSTEMİ ---
def init_db():
    conn = sqlite3.connect('lord_v200_brain.db')
    c = conn.cursor()
    c.execute("CREATE TABLE IF NOT EXISTS users (id TEXT PRIMARY KEY, balance INTEGER)")
    c.execute("CREATE TABLE IF NOT EXISTS keys (key TEXT PRIMARY KEY, user_id TEXT)")
    conn.commit()
    conn.close()

init_db()

# --- 🧠 GERÇEK AI BEYNİ (ChatGPT / DeepSeek API) ---
async def get_real_ai_brain(user_query):
    """
    Bu fonksiyon statik metin üretmez. 
    Gerçek bir AI sunucusuna (Blackbox/GPT-4) bağlanır.
    """
    try:
        # Gerçek zamanlı AI isteği (Sınırsız ve Profesyonel Kodlama Destekli)
        url = "https://api.blackbox.ai/api/chat"
        payload = {
            "messages": [{"role": "user", "content": user_query}],
            "model": "deepseek-v3", # En iyi kod yazan ve mantık kuran model
            "max_tokens": 4096
        }
        
        headers = {"Content-Type": "application/json"}
        
        # İstek gönderiliyor (Gerçek Beyin Bağlantısı)
        response = requests.post(url, json=payload, headers=headers, timeout=30)
        
        if response.status_code == 200:
            # Yanıt metnini ayıkla
            data = response.text
            # Blackbox bazen ham metin döndürür, bazen json.
            try:
                json_res = response.json()
                return json_res.get("choices", [{}])[0].get("message", {}).get("content", "Yanıt alınamadı.")
            except:
                return data # Ham metin dönerse
        else:
            return "⚠️ Lord AI Sunucusu şu an yoğun. Lütfen tekrar deneyin."
            
    except Exception as e:
        return f"🚨 Sistem Hatası: {str(e)}"

# --- 🔗 PROFESYONEL BUTONLAR ---
def pro_buttons():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("📢 Kanalımız", url=KANAL_URL),
         InlineKeyboardButton("🛠️ Destek Hattı", url=DESTEK_URL)]
    ])

# --- 🌐 ULTRA PROFESYONEL API ---
async def handle_api(request):
    key = request.query.get("key")
    q = request.query.get("q")
    
    if not key or not q:
        return web.json_response({"error": "Eksik parametre!"}, status=400)

    conn = sqlite3.connect('lord_v200_brain.db')
    c = conn.cursor()
    c.execute("SELECT user_id FROM keys WHERE key=?", (key,))
    key_res = c.fetchone()
    
    if not key_res:
        conn.close()
        return web.json_response({"error": "Geçersiz Key!"}, status=403)
    
    uid = key_res[0]
    c.execute("SELECT balance FROM users WHERE id=?", (uid,))
    user = c.fetchone()
    
    if not user or user[0] <= 0:
        conn.close()
        return web.json_response({"error": "Bakiye bitti!"}, status=402)

    # Bakiye Düş
    c.execute("UPDATE users SET balance = balance - 1 WHERE id=?", (uid,))
    conn.commit()
    conn.close()

    # GERÇEK AI BEYNİNDEN CEVAP AL
    real_response = await get_real_ai_brain(q)

    return web.json_response({
        "status": "success",
        "engine": "Lord V200 Real Brain",
        "query": q,
        "response": real_response,
        "remaining_balance": user[0] - 1,
        "links": {"channel": KANAL_URL, "support": DESTEK_URL}
    })

# --- 🤖 BOT MANTIĞI ---
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    uid = str(update.effective_user.id)
    conn = sqlite3.connect('lord_v200_brain.db')
    c = conn.cursor()
    c.execute("INSERT OR IGNORE INTO users VALUES (?, ?)", (uid, 150)) # 150 Jeton Başlangıç
    conn.commit()
    conn.close()

    kb = [[KeyboardButton("🤖 AI Chat"), KeyboardButton("💰 Bakiye")], [KeyboardButton("🔑 API & Profil")]]
    await update.message.reply_text("👑 **Lord System V200: Gerçek Zeka Aktif**\n"
                                   "Şu an gerçek bir LLM (ChatGPT/DeepSeek) beynine bağlıyım. "
                                   "İstediğin her şeyi kodlayabilirim.", reply_markup=ReplyKeyboardMarkup(kb, resize_keyboard=True))

async def msg_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    uid = str(update.effective_user.id)
    
    conn = sqlite3.connect('lord_v200_brain.db')
    c = conn.cursor()
    
    if text == "🔑 API & Profil":
        c.execute("SELECT key FROM keys WHERE user_id=?", (uid,))
        res = c.fetchone()
        if not res:
            new_key = f"LORD-{uuid.uuid4().hex[:8].upper()}"
            c.execute("INSERT INTO keys VALUES (?, ?)", (new_key, uid))
            conn.commit()
            key = new_key
        else: key = res[0]
        await update.message.reply_text(f"🔑 Key: `{key}`\n🔗 API: `{BASE_URL}/api?key={key}&q=Merhaba`", 
                                        parse_mode="Markdown", reply_markup=pro_buttons())

    elif not text.startswith("/"):
        c.execute("SELECT balance FROM users WHERE id=?", (uid,))
        user = c.fetchone()
        if user and user[0] > 0:
            c.execute("UPDATE users SET balance = balance - 1 WHERE id=?", (uid,))
            conn.commit()
            
            await update.message.reply_chat_action("typing")
            # GERÇEK ZAMANLI AI YANITI (CHATGPT GİBİ)
            response = await get_real_ai_brain(text)
            
            await update.message.reply_text(response, parse_mode="Markdown", reply_markup=pro_buttons())
        else:
            await update.message.reply_text("❌ Jetonunuz bitti Lord!")
    conn.close()

# --- 🚀 RUNNER ---
async def main():
    if not TOKEN: return
    
    app_web = web.Application()
    app_web.router.add_get("/api", handle_api)
    app_web.router.add_get("/", lambda r: web.Response(text="Lord V200 Brain Online"))
    runner = web.AppRunner(app_web)
    await runner.setup()
    await web.TCPSite(runner, "0.0.0.0", PORT).start()

    app = Application.builder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, msg_handler))

    async with app:
        await app.initialize()
        await app.start()
        await app.updater.start_polling()
        await asyncio.Event().wait()

if __name__ == "__main__":
    asyncio.run(main())
