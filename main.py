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

# --- ⚙️ KONFİGÜRASYON ---
TOKEN = os.getenv("BOT_TOKEN")
PORT = int(os.environ.get("PORT", 10000))
BASE_URL = "https://lordageichatsohbet.onrender.com"
KANAL_URL = "https://t.me/lordsystemv3"
DESTEK_URL = "https://t.me/LordDestekHat"

# --- 📁 DATABASE SİSTEMİ ---
def init_db():
    conn = sqlite3.connect('lord_god_particle.db')
    c = conn.cursor()
    c.execute("CREATE TABLE IF NOT EXISTS users (id TEXT PRIMARY KEY, balance INTEGER, referred_by TEXT)")
    c.execute("CREATE TABLE IF NOT EXISTS keys (key TEXT PRIMARY KEY, user_id TEXT)")
    conn.commit()
    conn.close()

init_db()

# --- 🧠 GERÇEK LLM BEYNİ (Absolute AI - DeepSeek/GPT Altyapısı) ---
async def get_absolute_ai_response(user_query):
    """
    Bu fonksiyon statik metin üretmez. 
    Gerçek zamanlı olarak dünyanın en güçlü LLM modellerine bağlanır.
    """
    try:
        # Gerçek zamanlı AI Gateway (Sınırsız ve Profesyonel Kodlama Destekli)
        url = "https://api.blackbox.ai/api/chat"
        headers = {"Content-Type": "application/json"}
        payload = {
            "messages": [{"role": "user", "content": user_query}],
            "model": "deepseek-v3", # Dünyanın en iyi kod yazan modellerinden biri
            "max_tokens": 4096,
            "temperature": 0.7,
            "top_p": 0.9
        }
        
        response = requests.post(url, json=payload, headers=headers, timeout=45)
        
        if response.status_code == 200:
            try:
                # API bazen ham metin, bazen JSON döner. Her iki durumu da yönetiyoruz.
                data = response.json()
                return data.get("choices", [{}])[0].get("message", {}).get("content", "Yanıt üretilemedi.")
            except:
                return response.text
        else:
            return "⚠️ Lord AI Sunucusu şu an çok yoğun. Lütfen 5 saniye sonra tekrar deneyin."
            
    except Exception as e:
        return f"🚨 Sistem Hatası: Gerçek AI bağlantısı kurulamadı. Hata: {str(e)}"

# --- 🔗 PROFESYONEL BUTONLAR ---
def pro_markup():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("📢 Kanal", url=KANAL_URL),
         InlineKeyboardButton("🛠️ Destek", url=DESTEK_URL)]
    ])

# --- 🌐 ULTRA PROFESYONEL API GATEWAY ---
async def handle_api(request):
    key = request.query.get("key")
    q = request.query.get("q")
    
    if not key or not q:
        return web.json_response({"error": "Parametreler eksik"}, status=400)

    conn = sqlite3.connect('lord_god_particle.db'); c = conn.cursor()
    c.execute("SELECT user_id FROM keys WHERE key=?", (key,))
    k_res = c.fetchone()
    
    if not k_res:
        conn.close()
        return web.json_response({"error": "Geçersiz API Key"}, status=403)
    
    uid = k_res[0]
    c.execute("SELECT balance FROM users WHERE id=?", (uid,))
    u_res = c.fetchone()
    
    if not u_res or u_res[0] <= 0:
        conn.close()
        return web.json_response({"error": "Bakiye bitti"}, status=402)

    # Jeton düş ve GERÇEK AI BEYNİNİ çalıştır
    c.execute("UPDATE users SET balance = balance - 1 WHERE id=?", (uid,))
    conn.commit(); conn.close()

    ai_answer = await get_absolute_ai_response(q)

    return web.json_response({
        "status": "success",
        "engine": "Lord V300 Final Reality",
        "response": ai_answer,
        "remaining_balance": u_res[0] - 1
    })

# --- 🤖 BOT MANTIĞI ---
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    uid = str(update.effective_user.id)
    args = context.args # Referans kontrolü
    conn = sqlite3.connect('lord_god_particle.db'); c = conn.cursor()
    
    c.execute("SELECT id FROM users WHERE id=?", (uid,))
    if not c.fetchone():
        ref_id = args[0] if args and args[0] != uid else None
        c.execute("INSERT INTO users VALUES (?, ?, ?)", (uid, 20, ref_id)) # 20 Başlangıç
        if ref_id:
            c.execute("UPDATE users SET balance = balance + 3 WHERE id=?", (ref_id,))
            try: await context.bot.send_message(chat_id=ref_id, text="🎁 Arkadaşın katıldı! **+3 Jeton** kazandın.")
            except: pass
        conn.commit()
    conn.close()

    kb = [[KeyboardButton("🤖 AI Chat"), KeyboardButton("💰 Bakiye & Ref")], [KeyboardButton("🔑 API & Profil")]]
    await update.message.reply_text("👑 **Lord V300: Absolute Reality**\nGerçek bir zekaya hoş geldin.", 
                                   reply_markup=ReplyKeyboardMarkup(kb, resize_keyboard=True))

async def msg_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    uid = str(update.effective_user.id)
    conn = sqlite3.connect('lord_god_particle.db'); c = conn.cursor()
    
    if text == "💰 Bakiye & Ref":
        c.execute("SELECT balance FROM users WHERE id=?", (uid,))
        bal = c.fetchone()[0]
        ref_link = f"https://t.me/{(await context.bot.get_me()).username}?start={uid}"
        await update.message.reply_text(f"💰 Bakiyeniz: `{bal} Jeton`\n🔗 Ref Linkin: `{ref_link}`\n*(Her arkadaşın için +3 Jeton)*")

    elif text == "🔑 API & Profil":
        c.execute("SELECT key FROM keys WHERE user_id=?", (uid,))
        res = c.fetchone()
        if not res:
            key = f"LORD-{uuid.uuid4().hex[:8].upper()}"
            c.execute("INSERT INTO keys VALUES (?, ?)", (key, uid))
            conn.commit()
        else: key = res[0]
        await update.message.reply_text(f"🔑 Key: `{key}`\n🔗 API: `{BASE_URL}/api?key={key}&q=Merhaba`", 
                                        parse_mode="Markdown", reply_markup=pro_markup())

    elif not text.startswith("/"):
        c.execute("SELECT balance FROM users WHERE id=?", (uid,))
        bal = c.fetchone()[0]
        if bal > 0:
            c.execute("UPDATE users SET balance = balance - 1 WHERE id=?", (uid,)); conn.commit()
            await update.message.reply_chat_action("typing")
            # GERÇEK LLM BEYNİ ÇALIŞIYOR
            response = await get_absolute_ai_response(text)
            await update.message.reply_text(response, parse_mode="Markdown", reply_markup=pro_markup())
        else:
            await update.message.reply_text("❌ Jetonun bitti! Arkadaşlarını davet ederek kazanabilirsin.")
    conn.close()

async def main():
    app_web = web.Application()
    app_web.router.add_get("/api", handle_api)
    runner = web.AppRunner(app_web); await runner.setup()
    await web.TCPSite(runner, "0.0.0.0", PORT).start()
    
    application = Application.builder().token(TOKEN).build()
    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, msg_handler))

    async with application:
        await application.initialize(); await application.start(); await application.updater.start_polling(); await asyncio.Event().wait()

if __name__ == "__main__":
    asyncio.run(main())
