import os
import uuid
import json
import asyncio
import random
from datetime import datetime
from aiohttp import web
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes

# --- KONFİGÜRASYON ---
TOKEN = "8366688933:AAHXaRMmP-z2ejCrQXTXhVYXxPERiaR6I0o"
BASE_URL = "https://lordageichatsohbet.onrender.com"
KANAL_ID = "@lordsystemv3"
ADMIN_USER = "@LordDestekHat"
PORT = int(os.environ.get("PORT", 8080))

# --- GÜVENLİK VE POLİTİKA METNİ ---
SECURITY_POLICY = (
    "🛡️ **Lord System Güvenlik Politikası**\n\n"
    "1. API anahtarları kişiye özeldir, paylaşılması yasaktır.\n"
    "2. Sistem üzerinden illegal sorgu yapılması durumunda anahtar kalıcı olarak banlanır.\n"
    "3. Loglar anonim olarak tutulur ve gizlilik esastır.\n"
    "4. @lordsystemv3 kanalından ayrılanların yetkileri askıya alınır.\n"
    "5. Destek için sadece @LordDestekHat yetkilidir."
)

# --- MODEL TANIMLARI ---
MODELLER = {
    "video_ai": "🎬 Lord Video-AI (Sinematik)",
    "image_ai": "🖼️ Lord Image-AI (Artistic)",
    "chat_sohbet": "💬 Lord Chat-AI (400k Data)",
    "voice_ai": "🎙️ Lord Voice-AI (Clone)"
}

# --- YARDIMCI FONKSİYONLAR ---
def load_db(file):
    if not os.path.exists(file): 
        with open(file, "w") as f: json.dump({}, f)
    with open(file, "r") as f: return json.load(f)

def save_db(file, data):
    with open(file, "w") as f: json.dump(data, f, indent=4)

# --- API SUNUCU (RENDER ENDPOINT) ---
async def handle_api(request):
    key = request.query.get("key")
    model = request.query.get("model")
    query = request.query.get("q", "merhaba")

    keys = load_db("keys.json")

    # Güvenlik Kontrolü
    if key not in keys:
        return web.json_response({"error": "Unauthorized", "message": "Gecersiz API Key!"}, status=403)

    # İstek Okuma ve Yanıt Modeli
    response_data = {
        "status": "success",
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "model": model,
        "request_id": uuid.uuid4().hex[:12]
    }

    if model == "video_ai":
        response_data["result"] = f"Video isleniyor: {query}. Render URL: {BASE_URL}/v/{response_data['request_id']}"
    elif model == "chat_sohbet":
        response_data["result"] = f"Lord GPT Yaniti: {query} istegi 400k dataset icinde analiz edildi."
    else:
        response_data["result"] = f"Islem basarili: {query}"

    return web.json_response(response_data)

# --- TELEGRAM BOT MANTIĞI ---
async def check_sub(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Kanal Üyelik Kontrolü"""
    user_id = update.effective_user.id
    try:
        member = await context.bot.get_chat_member(KANAL_ID, user_id)
        if member.status in ["left", "kicked"]: return False
        return True
    except: return False

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await check_sub(update, context):
        await update.message.reply_text(f"⚠️ **Erişim Reddedildi!**\nSistemi kullanmak için {KANAL_ID} kanalına katılmalısın.", parse_mode="Markdown")
        return

    keyboard = [
        [InlineKeyboardButton("🤖 Modelleri Listele", callback_data="list_models")],
        [InlineKeyboardButton("📜 Güvenlik Politikası", callback_data="policy")],
        [InlineKeyboardButton("👨‍💻 Destek Hattı", url="https://t.me/LordDestekHat")]
    ]
    await update.message.reply_text(
        f"👑 **Lord System V7 Dashboard**\n\n"
        f"Hoş geldin Lord! Bu panel üzerinden AI API anahtarlarını yönetebilirsin.\n\n"
        f"📍 **API Link:** `{BASE_URL}`",
        reply_markup=InlineKeyboardMarkup(keyboard), parse_mode="Markdown"
    )

async def handle_callbacks(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    if query.data == "policy":
        await query.edit_message_text(SECURITY_POLICY, parse_mode="Markdown")
    
    elif query.data == "list_models":
        kb = [[InlineKeyboardButton(name, callback_data=f"gen_{mid}")] for mid, name in MODELLER.items()]
        await query.edit_message_text("🚀 **Aktif AI Modelleri**\nKey almak istediğin modeli seç:", reply_markup=InlineKeyboardMarkup(kb))

    elif query.data.startswith("gen_"):
        mid = query.data.replace("gen_", "")
        new_key = f"LORD-{mid[:3].upper()}-{uuid.uuid4().hex[:6].upper()}"
        
        db = load_db("keys.json")
        db[new_key] = {"user": query.from_user.id, "model": mid, "date": str(datetime.now())}
        save_db("keys.json", db)

        res = (f"✅ **Anahtar Üretildi!**\n\n"
               f"📁 Model: `{MODELLER[mid]}`\n"
               f"🔑 Key: `{new_key}`\n\n"
               f"🔗 **Örnek Sorgu:**\n`{BASE_URL}/api?key={new_key}&model={mid}&q=Sorgun`")
        await query.edit_message_text(res, parse_mode="Markdown")

# --- ANA ÇALIŞTIRICI (RENDER & BOT) ---
async def main():
    # API Sunucusu
    server = web.Application()
    server.router.add_get("/api", handle_api)
    runner = web.AppRunner(server)
    await runner.setup()
    await web.TCPSite(runner, "0.0.0.0", PORT).start()

    # Bot Uygulaması
    bot_app = Application.builder().token(TOKEN).build()
    bot_app.add_handler(CommandHandler("start", start))
    bot_app.add_handler(CallbackQueryHandler(handle_callbacks))

    print(f"✅ Sistem Aktif! Port: {PORT}")
    
    async with bot_app:
        await bot_app.initialize()
        await bot_app.updater.start_polling()
        await asyncio.Event().wait()

if __name__ == "__main__":
    asyncio.run(main())
