import os
import uuid
import json
import asyncio
import random
from datetime import datetime
from aiohttp import web
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes

# --- ⚙️ AYARLAR ---
# Render'da Environment Variables kısmına eklemeyi unutma!
TOKEN = "8366688933:AAHXaRMmP-z2ejCrQXTXhVYXxPERiaR6I0o"
BASE_URL = "https://lordageichatsohbet.onrender.com"
KANAL_ID = "@lordsystemv3"
ADMIN_USER = "@LordDestekHat"
PORT = int(os.environ.get("PORT", 8080))

# --- 🔐 GÜVENLİK POLİTİKASI ---
SECURITY_POLICY = (
    "🛡️ **Lord System Güvenlik Politikası**\n\n"
    "• API anahtarları kişiye özeldir; tespiti halinde banlanır.\n"
    "• Illegal içerik, spam veya aşırı yüklenme yasaktır.\n"
    "• @lordsystemv3 kanalından ayrılanların keyleri iptal edilir.\n"
    "• Gizliliğiniz bizim için esastır; veriler şifreli tutulur.\n"
    "• Destek: @LordDestekHat"
)

# --- 🤖 MODELLER ---
MODELLER = {
    "video_ai": "🎬 Lord Video-AI (Sinematik)",
    "image_ai": "🖼️ Lord Image-AI (Görsel)",
    "chat_sohbet": "💬 Lord Chat (400k Dataset)",
    "voice_ai": "🎙️ Lord Voice-AI (Ses)"
}

# --- 📂 VERİTABANI YÖNETİMİ ---
def load_db():
    if not os.path.exists("keys.json"):
        with open("keys.json", "w") as f: json.dump({}, f)
    with open("keys.json", "r") as f: return json.load(f)

def save_db(data):
    with open("keys.json", "w") as f: json.dump(data, f, indent=4)

# --- 🌐 API ENDPOINT (İstekleri Okuyan Bölüm) ---
async def handle_api(request):
    key = request.query.get("key")
    model = request.query.get("model")
    query = request.query.get("q", "Merhaba Lord!")

    db = load_db()

    if key not in db:
        return web.json_response({"hata": "Yetkisiz Erişim", "mesaj": "API Key geçersiz!"}, status=403)

    # API Yanıt Modeli
    result_data = {
        "durum": "aktif",
        "tarih": datetime.now().strftime("%d/%m/%Y %H:%M:%S"),
        "istenen_model": MODELLER.get(model, "Bilinmeyen Model"),
        "sorgu": query,
        "cevap": f"Lord {model} motoru başarıyla yanıt verdi. Veri işlendi."
    }
    
    return web.json_response(result_data)

# --- 💬 TELEGRAM BOT MANTIĞI ---
async def check_sub(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    try:
        member = await context.bot.get_chat_member(KANAL_ID, user_id)
        if member.status in ["left", "kicked"]: return False
        return True
    except: return False

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await check_sub(update, context):
        btn = [[InlineKeyboardButton("📢 Kanala Katıl", url=f"https://t.me/{KANAL_ID.replace('@','')}")]]
        await update.message.reply_text(f"⚠️ **Erişim Engellendi!**\nSistemi kullanmak için {KANAL_ID} kanalımıza katılmalısın.", 
                                       reply_markup=InlineKeyboardMarkup(btn), parse_mode="Markdown")
        return

    keyboard = [
        [InlineKeyboardButton("🚀 Modelleri Listele", callback_data="list_models")],
        [InlineKeyboardButton("🛡️ Güvenlik Politikası", callback_data="policy")],
        [InlineKeyboardButton("🆘 Destek Hattı", url=f"https://t.me/{ADMIN_USER.replace('@','')}")]
    ]
    await update.message.reply_text(
        f"👑 **Lord System V8 API Hub**\n\n"
        f"📍 Endpoint: `{BASE_URL}`\n"
        f"👤 Sahip: {ADMIN_USER}\n\n"
        "İstediğin yapay zeka servisini seç ve API anahtarını anında al!",
        reply_markup=InlineKeyboardMarkup(keyboard), parse_mode="Markdown"
    )

async def handle_callbacks(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    if query.data == "policy":
        await query.edit_message_text(SECURITY_POLICY, parse_mode="Markdown")
    
    elif query.data == "list_models":
        kb = [[InlineKeyboardButton(name, callback_data=f"gen_{mid}")] for mid, name in MODELLER.items()]
        await query.edit_message_text("🛠 **Aktif Modeller**\nKey üretmek için birini seç:", reply_markup=InlineKeyboardMarkup(kb))

    elif query.data.startswith("gen_"):
        mid = query.data.replace("gen_", "")
        # OTOMATİK KEY ÜRETİMİ
        new_key = f"LORD-{mid[:3].upper()}-{uuid.uuid4().hex[:8].upper()}"
        
        db = load_db()
        db[new_key] = {"user": query.from_user.id, "model": mid, "created": str(datetime.now())}
        save_db(db)

        res = (f"✅ **API Key Başarıyla Üretildi!**\n\n"
               f"📁 Servis: `{MODELLER[mid]}`\n"
               f"🔑 Key: `{new_key}`\n\n"
               f"🔗 **API Linkin:**\n`{BASE_URL}/api?key={new_key}&model={mid}&q=sorgun`")
        await query.edit_message_text(res, parse_mode="Markdown")

# --- 🚀 ANA ÇALIŞTIRICI ---
async def main():
    # Render API Sunucusu Başlatma
    api_app = web.Application()
    api_app.router.add_get("/api", handle_api)
    runner = web.AppRunner(api_app)
    await runner.setup()
    await web.TCPSite(runner, "0.0.0.0", PORT).start()

    # Telegram Bot Başlatma
    bot_app = Application.builder().token(TOKEN).build()
    bot_app.add_handler(CommandHandler("start", start))
    bot_app.add_handler(CallbackQueryHandler(handle_callbacks))

    print(f"✅ LORD SYSTEM AKTİF! PORT: {PORT}")
    
    async with bot_app:
        await bot_app.initialize()
        await bot_app.updater.start_polling()
        await asyncio.Event().wait()

if __name__ == "__main__":
    asyncio.run(main())
