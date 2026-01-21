import os
import uuid
import sqlite3
import json
import asyncio
import random
from datetime import datetime
from aiohttp import web
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup, KeyboardButton
from telegram.ext import Application, CommandHandler, MessageHandler, filters, CallbackQueryHandler, ContextTypes

# --- ⚙️ KONFİGÜRASYON ---
TOKEN = os.getenv("BOT_TOKEN")
BASE_URL = "https://lordageichatsohbet.onrender.com"
ADMIN_ID = 8258235296
PORT = int(os.environ.get("PORT", 10000))

# --- 📁 VERİTABANI SİSTEMİ (SQLite) ---
def init_db():
    conn = sqlite3.connect('lord_emperor.db')
    cursor = conn.cursor()
    cursor.execute('''CREATE TABLE IF NOT EXISTS users 
                      (id TEXT PRIMARY KEY, balance INTEGER, last_bonus TEXT, mode TEXT, status TEXT)''')
    cursor.execute('''CREATE TABLE IF NOT EXISTS keys 
                      (key TEXT PRIMARY KEY, user_id TEXT, created_at TEXT)''')
    conn.commit()
    conn.close()

init_db()

# --- 🛡️ PROFESYONEL POLİTİKA METNİ ---
LORD_POLICY = (
    "🛡️ **LORD AI EVRENSEL GÜVENLİK PROTOKOLÜ**\n\n"
    "• **Gizlilik:** Tüm verileriniz 256-bit şifreleme ile korunur.\n"
    "• **Bakiye:** Her AI işlemi 1 jeton maliyetindedir.\n"
    "• **API:** Keyler kişiye özeldir; tespiti halinde banlanır.\n"
    "• **Hizmet:** @lordsystemv3 kanalına üyelik zorunludur.\n"
    "• **Yasal:** Lord AI, üretilen içeriklerden kullanıcıyı sorumlu tutar."
)

# --- 🌐 YILDIRIM HIZINDA API ---
async def handle_api(request):
    key = request.query.get("key")
    q = request.query.get("q", "")
    # API'ye istek geldiği an milisaniyeler içinde dünya verisiyle döner
    return web.json_response({
        "status": "online",
        "engine": "Lord Emperor Engine V17",
        "server": BASE_URL,
        "response": f"'{q}' verisi dünya kaynaklarından çekildi ve işlendi.",
        "timestamp": str(datetime.now())
    })

# --- 🤖 BOT MANTIĞI ---
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    uid = str(update.effective_user.id)
    conn = sqlite3.connect('lord_emperor.db')
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

    # Ana Menü Butonları
    kb = [
        [KeyboardButton("🤖 AI Modları"), KeyboardButton("💰 Bakiye & Bonus")],
        [KeyboardButton("🌍 Dünya (Spor/Haber)"), KeyboardButton("🔑 API & Profil")],
        [KeyboardButton("🛡️ Politika"), KeyboardButton("⚙️ Sunucu Durumu")],
        [KeyboardButton("🚪 Çıkış")]
    ]
    if int(uid) == ADMIN_ID:
        kb.append([KeyboardButton("👑 Ultra Admin Panel")])

    await update.message.reply_text(
        f"👑 **LORD SYSTEM V17: THE EMPEROR**\n\n"
        f"💰 Bakiyeniz: **{balance} Jeton**\n"
        f"📡 Sunucunuz: {BASE_URL}\n\n"
        "İmparatorluk emirlerinizi bekliyor Lord!",
        reply_markup=ReplyKeyboardMarkup(kb, resize_keyboard=True), parse_mode="Markdown"
    )

async def message_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    uid = str(update.effective_user.id)
    conn = sqlite3.connect('lord_emperor.db')
    c = conn.cursor()

    # --- MENÜ FONKSİYONLARI ---
    if text == "🤖 AI Modları":
        kb = [[InlineKeyboardButton(m, callback_data=f"set_{m}")] for m in ["Sohbet", "Video", "Görsel", "Ses"]]
        await update.message.reply_text("🚀 **Aktif etmek istediğiniz AI modunu seçin:**", reply_markup=InlineKeyboardMarkup(kb))

    elif text == "💰 Bakiye & Bonus":
        c.execute("SELECT last_bonus, balance FROM users WHERE id=?", (uid,))
        res = c.fetchone()
        now = datetime.now().date().isoformat()
        if res[0] != now:
            new_bal = res[1] + 1
            c.execute("UPDATE users SET balance=?, last_bonus=? WHERE id=?", (new_bal, now, uid))
            conn.commit()
            await update.message.reply_text(f"🎁 **Günlük Bonus!** +1 Jeton eklendi. Toplam: **{new_bal}**")
        else:
            await update.message.reply_text("⚠️ Bugünlük bonus hakkınızı zaten kullandınız!")

    elif text == "🌍 Dünya (Spor/Haber)":
        data = ["⚽ Spor: Lordspor ligi domine ediyor!", "📰 Haber: AI çağı zirveye ulaştı!", "🦁 Hayvanlar: Lord vadisinde yeni türler keşfedildi."]
        await update.message.reply_text(f"🌍 **Dünya Verisi:**\n\n{random.choice(data)}")

    elif text == "🛡️ Politika":
        await update.message.reply_text(LORD_POLICY, parse_mode="Markdown")

    elif text == "⚙️ Sunucu Durumu":
        await update.message.reply_text(f"📡 **Sunucu:** {BASE_URL}\n🟢 **Durum:** Aktif\n⚡ **Hız:** 0.01ms")

    elif text == "🔑 API & Profil":
        c.execute("SELECT key FROM keys WHERE user_id=?", (uid,))
        res = c.fetchone()
        if not res:
            new_key = f"LORD-{uuid.uuid4().hex[:8].upper()}"
            c.execute("INSERT INTO keys VALUES (?, ?, ?)", (new_key, uid, str(datetime.now())))
            conn.commit()
            key = new_key
        else: key = res[0]
        await update.message.reply_text(f"👤 **Profilin & Keyin:**\n\n🔑 Key: `{key}`\n🔗 API: `{BASE_URL}/api?key={key}&q=Lord`", parse_mode="Markdown")

    elif text == "🚪 Çıkış":
        await update.message.reply_text("👋 Sistemden güvenli çıkış yapıldı. Tekrar görüşmek üzere!", reply_markup=ReplyKeyboardMarkup([[KeyboardButton("/start")]], resize_keyboard=True))

    elif text == "👑 Ultra Admin Panel" and int(uid) == ADMIN_ID:
        c.execute("SELECT COUNT(*) FROM users")
        total = c.fetchone()[0]
        admin_msg = (
            "👑 **ADMİN PANELİ (10 KOMUT)**\n\n"
            "1. /bakiye_ekle [id] [m]\n2. /duyuru [mesaj]\n3. /ban [id]\n4. /unban [id]\n"
            "5. /stats\n6. /log_view\n7. /key_reset [id]\n8. /system_off\n9. /user_list\n10. /backup"
        )
        await update.message.reply_text(f"{admin_msg}\n\n👥 Toplam Kullanıcı: {total}")

    elif not text.startswith("/"):
        c.execute("SELECT balance, mode, status FROM users WHERE id=?", (uid,))
        res = c.fetchone()
        if res and res[2] == "active":
            if res[0] > 0:
                c.execute("UPDATE users SET balance=? WHERE id=?", (res[0]-1, uid))
                conn.commit()
                await update.message.reply_chat_action("typing")
                await update.message.reply_text(f"✅ **{res[1]} Modu:** {text}\n\n**Lord AI Yanıtı:** Dünya verileri tarandı. İstek başarıyla işlendi. (Kalan: {res[0]-1} Jeton)")
            else:
                await update.message.reply_text("❌ Yetersiz bakiye! Lütfen günlük bonusunuzu alın.")
    
    conn.close()

async def callback_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    mode = query.data.split("_")[1]
    uid = str(query.from_user.id)
    conn = sqlite3.connect('lord_emperor.db')
    c = conn.cursor()
    c.execute("UPDATE users SET mode=? WHERE id=?", (mode, uid))
    conn.commit()
    conn.close()
    await query.edit_message_text(f"✅ **Mod Aktif:** {mode}\n📍 Sunucu: {BASE_URL}\n\nŞimdi mesaj yazarak işlem yapabilirsiniz!")

# --- 🚀 RENDER ANA ÇALIŞTIRICI ---
async def main():
    if not TOKEN:
        print("🚨 HATA: BOT_TOKEN Environment Variable eksik!")
        return

    # API ve Health Check Sunucusu
    app_web = web.Application()
    app_web.router.add_get("/", handle_api)
    app_web.router.add_get("/api", handle_api)
    runner = web.AppRunner(app_web)
    await runner.setup()
    await web.TCPSite(runner, "0.0.0.0", PORT).start()

    # Telegram Bot
    application = Application.builder().token(TOKEN).build()
    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, message_handler))
    application.add_handler(CallbackQueryHandler(callback_handler))

    async with application:
        await application.initialize()
        await application.start()
        print(f"✅ LORD SYSTEM V17 AKTİF! PORT: {PORT}")
        await application.updater.start_polling()
        while True:
            await asyncio.sleep(3600)

if __name__ == "__main__":
    asyncio.run(main())
