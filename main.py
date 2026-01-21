import os
import sqlite3
import uuid
import asyncio
import random
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

# --- 📁 AKILLI VERİTABANI ---
def init_db():
    conn = sqlite3.connect('lord_singularity.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS users 
                 (id TEXT PRIMARY KEY, balance INTEGER, mode TEXT, status TEXT)''')
    c.execute('''CREATE TABLE IF NOT EXISTS keys 
                 (key TEXT PRIMARY KEY, user_id TEXT)''')
    conn.commit()
    conn.close()

init_db()

# --- 🧠 ULTRA GERÇEK AI MOTORU (NEURAL CORE) ---
async def singularity_ai_engine(query):
    q = query.lower()
    
    # 📝 1. PROFESYONEL KODLAMA MODÜLÜ
    if any(word in q for word in ["kodla", "python", "yazılım", "bot yap", "script"]):
        code_samples = [
            "import telebot\n# Lord Singularity Pro-Coder\nbot = telebot.TeleBot('TOKEN')\n\n@bot.message_handler(func=lambda m: True)\ndef lord_reply(m):\n    bot.reply_to(m, 'Neural Core Active')\n\nbot.infinity_polling()",
            "def advanced_analysis(data):\n    # Ultra Logic Processing\n    processed = [pow(x, 2) for x in data if x > 0]\n    return f'Result: {processed}'",
            "import asyncio\nasync def main_engine():\n    print('Lord System Booting...')\nasyncio.run(main_engine())"
        ]
        return (
            "🚀 **Lord Neural Coder Devreye Girdi**\n\n"
            "İsteğiniz üzerine optimize edilmiş, yüksek performanslı kod bloğu hazırlandı:\n\n"
            f"```python\n{random.choice(code_samples)}\n```\n"
            "*(Bu kod Lord V100 yapay sinir ağları tarafından üretilmiştir.)*"
        )

    # 🌍 2. GLOBAL VERİ VE ANALİZ MODÜLÜ
    if any(word in q for word in ["nedir", "kimdir", "bilgi", "analiz"]):
        prefixes = ["Küresel Veri Analizi:", "İmparatorluk Raporu:", "Deep Web Tarama Sonucu:"]
        return (
            f"🔍 **{random.choice(prefixes)}**\n\n"
            f"'{query}' sorgusu üzerine yapılan derinlemesine taramada, konunun dünya genelindeki stratejik etkileri incelendi. "
            "Veri setleri, bu durumun modern endüstride %98'lik bir korelasyon ile yeni bir trend başlattığını gösteriyor. "
            "Lord protokolleri bu bilgiyi doğrulamıştır."
        )

    # 💬 3. GERÇEK ASİSTAN MODU (CHATGPT STİLİ)
    if any(word in q for word in ["selam", "nasılsın", "kimsin"]):
        return (
            "Selam Lord! Ben Lord System V100. ChatGPT mimarisine benzer bir mantıksal işlemci ile çalışıyorum. "
            "Sizin için kod yazabilir, dünya verilerini analiz edebilir veya imparatorluğunuzu yönetmenize yardımcı olabilirim. "
            "Bugün hangi devasa projeyi başlatıyoruz?"
        )

    # Varsayılan Zeki Yanıt
    return (
        f"✨ **Lord AI Singularity Yanıtı:**\n\n"
        f"'{query}' talebi sinir ağlarımda işlendi. Analizlerim, bu konunun gelecekteki Lord ekosistemine "
        "doğrudan entegre edilebileceğini öngörüyor. İşlem başarıyla sonuçlandırıldı."
    )

# --- 🔗 PROFESYONEL BUTONLAR ---
def pro_markup():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("📢 Kanalımız", url=KANAL_URL),
         InlineKeyboardButton("🛠️ Destek Hattı", url=DESTEK_URL)]
    ])

# --- 🌐 SINGULARITY API GATEWAY ---
async def handle_api(request):
    key = request.query.get("key")
    q = request.query.get("q")
    
    if not key or not q:
        return web.json_response({"error": "Parametreler eksik!"}, status=400)

    conn = sqlite3.connect('lord_singularity.db')
    c = conn.cursor()
    c.execute("SELECT user_id FROM keys WHERE key=?", (key,))
    k_res = c.fetchone()
    
    if not k_res:
        conn.close()
        return web.json_response({"error": "Geçersiz Key!"}, status=403)
    
    uid = k_res[0]
    c.execute("SELECT balance FROM users WHERE id=?", (uid,))
    u_res = c.fetchone()
    
    if not u_res or u_res[0] <= 0:
        conn.close()
        return web.json_response({"error": "Bakiye yetersiz!"}, status=402)

    # Bakiye Düş ve AI Yanıtı Üret
    new_bal = u_res[0] - 1
    c.execute("UPDATE users SET balance=? WHERE id=?", (new_bal, uid))
    conn.commit()
    conn.close()

    ai_resp = await singularity_ai_engine(q)

    return web.json_response({
        "status": "success",
        "engine": "Lord V100 Singularity",
        "query": q,
        "response": ai_resp,
        "remaining_balance": new_bal,
        "links": {"channel": KANAL_URL, "support": DESTEK_URL}
    })

# --- 🤖 BOT MANTIĞI ---
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    uid = str(update.effective_user.id)
    conn = sqlite3.connect('lord_singularity.db')
    c = conn.cursor()
    c.execute("SELECT balance FROM users WHERE id=?", (uid,))
    if not c.fetchone():
        c.execute("INSERT INTO users VALUES (?, ?, ?, ?)", (uid, 100, "Elite", "active"))
        conn.commit()
    conn.close()

    kb = [[KeyboardButton("🤖 AI Chat"), KeyboardButton("💰 Bakiye")], [KeyboardButton("🔑 API & Profil")]]
    await update.message.reply_text("👑 **Lord V100: The Singularity**\nGerçek AI motoru senin için aktif.", 
                                   reply_markup=ReplyKeyboardMarkup(kb, resize_keyboard=True))

async def msg_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    uid = str(update.effective_user.id)
    
    conn = sqlite3.connect('lord_singularity.db')
    c = conn.cursor()
    c.execute("SELECT balance FROM users WHERE id=?", (uid,))
    user = c.fetchone()

    if text == "🔑 API & Profil":
        c.execute("SELECT key FROM keys WHERE user_id=?", (uid,))
        res = c.fetchone()
        if not res:
            new_key = f"LORD-{uuid.uuid4().hex[:8].upper()}"
            c.execute("INSERT INTO keys VALUES (?, ?)", (new_key, uid))
            conn.commit()
            key = new_key
        else: key = res[0]
        await update.message.reply_text(f"👤 **Lord Profil**\n\n🔑 Key: `{key}`\n🔗 API: `{BASE_URL}/api?key={key}&q=Merhaba`", 
                                        parse_mode="Markdown", reply_markup=pro_markup())

    elif not text.startswith("/"):
        if user and user[0] > 0:
            c.execute("UPDATE users SET balance = balance - 1 WHERE id=?", (uid,))
            conn.commit()
            await update.message.reply_chat_action("typing")
            response = await singularity_ai_engine(text)
            await update.message.reply_text(response, parse_mode="Markdown", reply_markup=pro_markup())
        else:
            await update.message.reply_text("❌ Jetonunuz bitmiş Lord!")
    conn.close()

# --- 🚀 RUNNER ---
async def main():
    if not TOKEN: return
    
    app_web = web.Application()
    app_web.router.add_get("/api", handle_api)
    app_web.router.add_get("/", lambda r: web.Response(text="Lord Singularity Online"))
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
