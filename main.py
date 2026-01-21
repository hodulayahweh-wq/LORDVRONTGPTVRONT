import os
import uuid
import json
import asyncio
from datetime import datetime
from aiohttp import web
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes

# --- 🔐 GÜVENLİK VE AYARLAR ---
TOKEN = os.getenv("BOT_TOKEN")
BASE_URL = "https://lordageichatsohbet.onrender.com"
KANAL_ID = "@lordsystemv3"
ADMIN_USER = "@LordDestekHat"
# Render portu dinamik olarak atar, bulamazsa 10000 varsayılanı kullanır.
PORT = int(os.environ.get("PORT", 10000))

# --- 🤖 MODELLER ---
MODELLER = {
    "video_ai": "🎬 Lord Video-AI (Sinematik)",
    "image_ai": "🖼️ Lord Image-AI (HD)",
    "chat_sohbet": "💬 Lord Chat (400k Veri)",
    "voice_ai": "🎙️ Lord Voice-AI (Ses Klon)"
}

# --- 📂 VERİTABANI YÖNETİMİ ---
def load_db():
    try:
        if not os.path.exists("keys.json") or os.stat("keys.json").st_size == 0:
            with open("keys.json", "w") as f: json.dump({}, f)
        with open("keys.json", "r") as f: return json.load(f)
    except:
        return {}

def save_db(data):
    with open("keys.json", "w") as f:
        json.dump(data, f, indent=4)

# --- 🌐 API SUNUCUSU (WEB ENDPOINT) ---
async def handle_api(request):
    key = request.query.get("key")
    model = request.query.get("model")
    query = request.query.get("q", "Merhaba")
    
    db = load_db()
    if not key or key not in db:
        return web.json_response({"hata": "Erişim Reddedildi", "mesaj": "Geçersiz API Anahtarı."}, status=403)
    
    return web.json_response({
        "status": "success",
        "model": MODELLER.get(model, "Genel"),
        "cevap": f"Lord {model} servisi isteğinizi işledi: {query}"
    })

# --- 💬 TELEGRAM BOT KOMUTLARI ---
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("🚀 Modelleri Listele", callback_data="list_models")],
        [InlineKeyboardButton("🆘 Destek & İletişim", url=f"https://t.me/{ADMIN_USER.replace('@','')}")]
    ]
    await update.message.reply_text(
        f"👑 **Lord System V11 Dashboard**\n\n"
        f"📍 Sunucu: `{BASE_URL}`\n"
        f"📢 Kanal: {KANAL_ID}\n\n"
        "Yapay zeka modellerini kullanmak için bir seçenek belirleyin:",
        reply_markup=InlineKeyboardMarkup(keyboard), parse_mode="Markdown"
    )

async def handle_callbacks(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    if query.data == "list_models":
        kb = [[InlineKeyboardButton(name, callback_data=f"gen_{mid}")] for mid, name in MODELLER.items()]
        await query.edit_message_text("🛠 **Lütfen model seçin:**", reply_markup=InlineKeyboardMarkup(kb))

    elif query.data.startswith("gen_"):
        mid = query.data.replace("gen_", "")
        new_key = f"LORD-{uuid.uuid4().hex[:8].upper()}"
        
        db = load_db()
        db[new_key] = {"user": query.from_user.id, "model": mid, "time": str(datetime.now())}
        save_db(db)

        res = (f"✅ **API Key Hazır!**\n\n"
               f"🔑 Key: `{new_key}`\n"
               f"📂 Model: {MODELLER[mid]}\n\n"
               f"🔗 **API URL:**\n`{BASE_URL}/api?key={new_key}&model={mid}&q=Lord`")
        await query.edit_message_text(res, parse_mode="Markdown")

# --- 🚀 RENDER ANA ÇALIŞTIRICI ---
async def main():
    if not TOKEN:
        print("❌ HATA: 'BOT_TOKEN' Environment Variable bulunamadı!")
        return

    # 1. API Sunucusunu Port Dinlemesiyle Başlat (Render Sağlığı İçin)
    server = web.Application()
    server.router.add_get("/api", handle_api)
    # Render'ın "Health Check" yapabilmesi için ana dizine bir yanıt ekleyelim
    server.router.add_get("/", lambda r: web.Response(text="Lord System Online ✅"))
    
    runner = web.AppRunner(server)
    await runner.setup()
    await web.TCPSite(runner, "0.0.0.0", PORT).start()
    print(f"✅ Web Sunucusu Port {PORT} üzerinde aktif.")

    # 2. Bot Uygulamasını Kur
    bot_app = Application.builder().token(TOKEN).build()
    bot_app.add_handler(CommandHandler("start", start))
    bot_app.add_handler(CallbackQueryHandler(handle_callbacks))

    # 3. Botu Polling Modunda Başlat
    async with bot_app:
        await bot_app.initialize()
        await bot_app.start()
        print("✅ Bot Polling Başlatıldı...")
        await bot_app.updater.start_polling()
        
        # Render'ın botu kapatmaması için sonsuz döngü
        while True:
            await asyncio.sleep(3600)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except Exception as e:
        print(f"🚨 KRİTİK HATA: {e}")
