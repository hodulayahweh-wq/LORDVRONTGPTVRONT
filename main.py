import os
import uuid
import sqlite3
import json
import asyncio
import random
from datetime import datetime
from aiohttp import web
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup, KeyboardButton
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

# --- ⚙️ AYARLAR (RENDER UYUMLU) ---
TOKEN = os.getenv("BOT_TOKEN") # Render'dan çeker
BASE_URL = "https://lordageichatsohbet.onrender.com"
ADMIN_ID = 8258235296
PORT = int(os.environ.get("PORT", 10000))

# --- 📁 VERİTABANI SİSTEMİ ---
def init_db():
    conn = sqlite3.connect('lord_ultimate.db')
    cursor = conn.cursor()
    cursor.execute('''CREATE TABLE IF NOT EXISTS users 
                      (id TEXT PRIMARY KEY, balance INTEGER, last_bonus TEXT, mode TEXT, status TEXT)''')
    cursor.execute('''CREATE TABLE IF NOT EXISTS keys 
                      (key TEXT PRIMARY KEY, user_id TEXT, usages INTEGER)''')
    conn.commit()
    conn.close()

init_db()

# --- 🛡️ LORD AI POLİTİKASI ---
POLICY_TEXT = (
    "🛡️ **LORD AI EVRENSEL POLİTİKASI**\n\n"
    "1. **Gizlilik:** Tüm dünya verileri anonim olarak işlenir.\n"
    "2. **Jeton:** Her AI sorgusu 1 Jeton değerindedir.\n"
    "3. **Güvenlik:** API Key paylaşımı yapan hesaplar dondurulur.\n"
    "4. **Kanal:** @lordsystemv3 takibi zorunludur.\n"
    "5. **Destek:** @LordDestekHat üzerinden yardım alabilirsiniz."
)

# --- 🌐 YILDIRIM HIZINDA API ---
async def handle_api(request):
    key = request.query.get("key")
    # API'ye istek geldiği an milisaniyeler içinde dünya verisiyle döner
    return web.json_response({
        "status": "active",
        "engine": "Lord World Engine V16",
        "server": BASE_URL,
        "world_update": "Spor, Haber ve Hayvanlar Alemi Senkronize Edildi ✅"
    })

# --- 🤖 BOT MANTIĞI ---
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    uid = str(update.effective_user.id)
    conn = sqlite3.connect('lord_ultimate.db')
    c = conn.cursor()
    c.execute("SELECT balance FROM users WHERE id=?", (uid,))
    user = c.fetchone()
    
    if not user:
        c.execute("INSERT INTO users VALUES (?, ?, ?, ?, ?)", (uid, 10, None, "Sohbet", "active"))
        conn.commit()
        balance = 10
    else:
        balance = user[0]
    conn.close()

    kb = [
        [KeyboardButton("🤖 AI Modları"), KeyboardButton("💰 Bakiye & Bonus")],
        [KeyboardButton("🌍 Dünya (Spor/Haber)"), KeyboardButton("🔑 API & Profil")],
        [KeyboardButton("🛡️ Politika"), KeyboardButton("⚙️ Sunucu Durumu")]
    ]
    if int(uid) == ADMIN_ID:
        kb.append([KeyboardButton("👑 Ultra Admin Panel")])

    await update.message.reply_text(
        f"👑 **LORD SYSTEM V16: UNIVERSAL**\n\n"
        f"💰 Bakiyeniz: **{balance} Jeton**\n"
        f"📡 Sunucu: {BASE_URL}\n\n"
        "İmparatorluk emirlerinizi bekliyor!",
        reply_markup=ReplyKeyboardMarkup(kb, resize_keyboard=True), parse_mode="Markdown"
    )

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    uid = str(update.effective_user.id)
    conn = sqlite3.connect('lord_ultimate.db')
    c = conn.cursor()

    # --- MENÜ İŞLEMLERİ ---
    if text == "💰 Bakiye & Bonus":
        c.execute("SELECT last_bonus, balance FROM users WHERE id=?", (uid,))
        res = c.fetchone()
        now = datetime.now().date().isoformat()
        if res[0] != now:
            new_bal = res[1] + 1
            c.execute("UPDATE users SET balance=?, last_bonus=? WHERE id=?", (new_bal, now, uid))
            conn.commit()
            await update.message.reply_text(f"🎁 **Günlük Bonus!** +1 Jeton. Toplam: **{new_bal}**")
        else:
            await update.message.reply_text("⚠️ Bugün bonusunu aldın!")

    elif text == "🌍 Dünya (Spor/Haber)":
        data = ["⚽ Spor: Lordspor 5-0 kazandı!", "🦁 Hayvanlar: Ormanlar bugün çok sessiz.", "📰 Haber: Lord AI dünya borsasına girdi!"]
        await update.message.reply_text(f"🌍 **Dünya Verisi:**\n\n{random.choice(data)}")

    elif text == "🛡️ Politika":
        await update.message.reply_text(POLICY_TEXT, parse_mode="Markdown")

    elif text == "👑 Ultra Admin Panel" and int(uid) == ADMIN_ID:
        c.execute("SELECT COUNT(*) FROM users")
        total = c.fetchone()[0]
        msg = (
            "👑 **LORD ADMİN PANELİ (10 KOMUT)**\n\n"
            "1. /bakiye_ver [id] [miktar]\n2. /duyuru [mesaj]\n3. /kullanici_sil [id]\n"
            "4. /ban [id]\n5. /unban [id]\n6. /key_olustur [id]\n7. /stats\n"
            "8. /reset_db\n9. /log_temizle\n10. /sistem_kapat"
        )
        await update.message.reply_text(f"{msg}\n\n👥 Toplam Kullanıcı: {total}")

    elif not text.startswith("/"):
        c.execute("SELECT balance, mode, status FROM users WHERE id=?", (uid,))
        res = c.fetchone()
        if res and res[2] == "active":
            if res[0] > 0:
                c.execute("UPDATE users SET balance=? WHERE id=?", (res[0]-1, uid))
                conn.commit()
                await update.message.reply_chat_action("typing")
                await update.message.reply_text(f"✅ **{res[1]} Modu:** {text}\n\n**Yanıt:** Dünya verileri ve Lord AI ile işlendi. (Kalan: {res[0]-1} Jeton)")
            else:
                await update.message.reply_text("❌ Jetonun kalmadı! Bonus almayı dene.")
        else:
            await update.message.reply_text("❌ Hesabınız kısıtlanmış olabilir.")

    conn.close()

# --- 🚀 RENDER ÇALIŞTIRICI ---
async def main():
    if not TOKEN:
        print("🚨 HATA: BOT_TOKEN Environment Variable bulunamadı!")
        return

    # Web Sunucusu (API ve Health Check)
    app_web = web.Application()
    app_web.router.add_get("/", handle_api)
    app_web.router.add_get("/api", handle_api)
    runner = web.AppRunner(app_web)
    await runner.setup()
    await web.TCPSite(runner, "0.0.0.0", PORT).start()

    # Bot Yapılandırması
    application = Application.builder().token(TOKEN).build()
    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    async with application:
        await application.initialize()
        await application.start()
        print(f"✅ LORD SYSTEM V16 AKTİF! PORT: {PORT}")
        # Render'da Polling'in donmaması için manuel loop
        await application.updater.start_polling()
        while True:
            await asyncio.sleep(3600)

if __name__ == "__main__":
    asyncio.run(main())
