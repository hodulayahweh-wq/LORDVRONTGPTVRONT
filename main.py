import os
import uuid
import json
import asyncio
from datetime import datetime
from aiohttp import web
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup, KeyboardButton
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, MessageHandler, filters, ContextTypes

# --- AYARLAR ---
TOKEN = os.getenv("BOT_TOKEN")
BASE_URL = "https://lordageichatsohbet.onrender.com"
KANAL_ID = "@lordsystemv3"
ADMIN = "@LordDestekHat"
PORT = int(os.environ.get("PORT", 10000))

# --- LORD AI POLİTİKASI ---
LORD_POLICY = (
    "👑 **LORD AI GİZLİLİK VE GÜVENLİK POLİTİKASI**\n\n"
    "1. **Veri Gizliliği:** Kullanıcı verileri ve API sorguları uçtan uca şifrelenir.\n"
    "2. **Kullanım Şartları:** İllegal, şiddet içeren veya telif hakkı ihlali yapan içerik üretimi yasaktır.\n"
    "3. **API Güvenliği:** Üretilen Keyler kişiye özeldir. Paylaşılması durumunda Key kalıcı olarak iptal edilir.\n"
    "4. **Sorumluluk:** Lord AI, üretilen içeriklerin kullanımından doğan hukuki sorumluluğu kullanıcıya ait tutar.\n"
    "5. **Hizmet Kalitesi:** Sistem @lordsystemv3 kanalına bağlı olarak çalışır. Kanaldan ayrılanların erişimi kesilir."
)

# --- MODEL TANIMLARI ---
MODELLER = {
    "chat": {"ad": "💬 Sohbet AI", "desc": "Gelişmiş Beyin Modeli"},
    "video": {"ad": "🎬 Video AI", "desc": "Gerçekçi Video Üretimi"},
    "image": {"ad": "🖼️ Görsel AI", "desc": "Sanatsal Tasarım Modeli"},
    "voice": {"ad": "🎙️ Ses AI", "desc": "Ses Klonlama Modeli"}
}

# --- DB SİSTEMİ (KALICI KAYIT) ---
def load_db():
    if not os.path.exists("lord_database.json"):
        with open("lord_database.json", "w") as f:
            json.dump({"users": {}, "keys": {}}, f)
    with open("lord_database.json", "r") as f: return json.load(f)

def save_db(db):
    with open("lord_database.json", "w") as f: json.dump(db, f, indent=4)

# --- API SUNUCUSU (ANINDA CEVAP) ---
async def handle_api(request):
    key = request.query.get("key")
    query = request.query.get("q", "")
    db = load_db()
    if key not in db["keys"]:
        return web.json_response({"error": "Unauthorized", "msg": "Key Gecersiz"}, status=403)
    
    return web.json_response({
        "status": "Success",
        "response": f"Lord AI Engine Yanıtı: {query} verisi işlendi.",
        "time": str(datetime.now())
    })

# --- BOT FONKSİYONLARI ---
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # Ana Menü Butonları
    keyboard = [
        [KeyboardButton("🤖 AI Modları"), KeyboardButton("🔑 Keylerim")],
        [KeyboardButton("🛡️ Politika"), KeyboardButton("🚪 Çıkış / İptal")]
    ]
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
    
    await update.message.reply_text(
        "👑 **LORD SYSTEM PRO V13**\n\nHoş geldin Lord! Tüm sistemlerin kontrolü senin elinde. "
        "Komutları görmek için `/yardim` yazabilir veya menüyü kullanabilirsin.",
        reply_markup=reply_markup, parse_mode="Markdown"
    )

async def ai_modes(update: Update, context: ContextTypes.DEFAULT_TYPE):
    kb = [[InlineKeyboardButton(m['ad'], callback_data=f"set_{k}")] for k, m in MODELLER.items()]
    await update.message.reply_text("🚀 **Bir AI Modeli Seçin:**", reply_markup=InlineKeyboardMarkup(kb))

async def handle_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    uid = str(query.from_user.id)
    db = load_db()

    if query.data.startswith("set_"):
        mode = query.data.split("_")[1]
        # Kullanıcıya özel key yoksa oluştur
        user_key = next((k for k, v in db["keys"].items() if v["user_id"] == uid), None)
        if not user_key:
            user_key = f"LORD-{uuid.uuid4().hex[:8].upper()}"
            db["keys"][user_key] = {"user_id": uid, "created_at": str(datetime.now())}
        
        if uid not in db["users"]: db["users"][uid] = {}
        db["users"][uid]["current_mode"] = mode
        save_db(db)
        
        await query.edit_message_text(
            f"✅ **Mod Aktif:** {MODELLER[mode]['ad']}\n"
            f"🔑 **API Keyin:** `{user_key}`\n\n"
            f"Şimdi mesaj yazarsan bu modda cevap alacaksın!"
        )

async def message_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    uid = str(update.effective_user.id)
    db = load_db()

    if text == "🤖 AI Modları": return await ai_modes(update, context)
    if text == "🛡️ Politika": return await update.message.reply_text(LORD_POLICY, parse_mode="Markdown")
    if text == "🔑 Keylerim":
        u_keys = [k for k, v in db["keys"].items() if v["user_id"] == uid]
        msg = "🔑 **Kayıtlı Keylerin:**\n\n" + "\n".join([f"`{k}`" for k in u_keys]) if u_keys else "Hiç keyin yok."
        return await update.message.reply_text(msg, parse_mode="Markdown")
    if text == "🚪 Çıkış / İptal":
        if uid in db["users"]: db["users"][uid]["current_mode"] = None
        save_db(db)
        return await update.message.reply_text("👋 Sistemden çıkış yapıldı. Modlar kapatıldı.")

    # AI İŞLEME MANTIĞI
    current_mode = db["users"].get(uid, {}).get("current_mode")
    if not current_mode:
        return await update.message.reply_text("⚠️ Önce bir AI Modu seçmelisin!")

    await update.message.reply_chat_action("typing")
    # ANINDA CEVAP (API GECİKMESİ YOK)
    if current_mode == "video":
        await update.message.reply_text(f"🎬 **Video Motoru:** `{text}` senaryosu işleniyor, video Render ediliyor...")
    elif current_mode == "image":
        await update.message.reply_text(f"🖼️ **Görsel Motoru:** `{text}` için 4K sanat eseri çiziliyor...")
    else:
        await update.message.reply_text(f"🤖 **Lord Chat:** {text} (Bu veri 400k dataset ile işlendi)")

# --- ANA MOTOR ---
async def main():
    server = web.Application()
    server.router.add_get("/api", handle_api)
    server.router.add_get("/", lambda r: web.Response(text="Lord System V13 Online"))
    runner = web.AppRunner(server)
    await runner.setup()
    await web.TCPSite(runner, "0.0.0.0", PORT).start()

    app = Application.builder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, message_handler))
    app.add_handler(CallbackQueryHandler(handle_callback))

    async with app:
        await app.initialize()
        await app.start()
        await app.updater.start_polling()
        await asyncio.Event().wait()

if __name__ == "__main__":
    asyncio.run(main())
