import os
import logging
from threading import Thread
from flask import Flask
from telegram import Update, ReplyKeyboardMarkup, ReplyKeyboardRemove
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    filters,
    ConversationHandler,
    ContextTypes
)

# ==================== CONFIG (ENVIRONMENT VARIABLES) ====================
BOT_TOKEN = os.getenv("8586521300:AAE3dpE5IBRPvA0vFmQJRzsZaEYE48qPPFk")
ADMIN_CHAT_ID = os.getenv("632522025")  # string bo'lsa ham yaxshi

if not BOT_TOKEN or not ADMIN_CHAT_ID:
    raise ValueError("❌ BOT_TOKEN yoki ADMIN_CHAT_ID environment variable sifatida o'rnatilmagan!")

# Enable logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# ---------- Health check server for Railway ----------
flask_app = Flask(__name__)  # '' emas, __name__ yaxshiroq

@flask_app.route('/')
def home():
    return "Bot is running! ✅"

def run_health_server():
    port = int(os.environ.get('PORT', 8080))
    flask_app.run(host='0.0.0.0', port=port, debug=False)

def start_health_server():
    t = Thread(target=run_health_server, daemon=True)
    t.start()

# Conversation states
(
    ASK_ISMI, ASK_TUGILGAN_YIL, ASK_MA_LUMOT, ASK_MANZIL,
    ASK_TELEFON, ASK_OILAVIY, ASK_OLDIN_ISH, ASK_OYLIK_MAOSH,
    ASK_MUDDAT, ASK_QIZIQISH, ASK_RASM, ASK_REKLAMA
) = range(12)

# ==================== HANDLERS ====================
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    user_id = update.effective_user.id
    context.user_data.clear()  # oldingi ma'lumotlarni tozalaydi
    await update.message.reply_text(
        "Assalomu alaykum! Ushbu anketani to‘liq to‘ldirib qayta jo‘natishingizni so‘raymiz.\n\n"
        "Ism familiyangizni yozing:"
    )
    return ASK_ISMI


async def ask_ismi(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    context.user_data['ism_familiya'] = update.message.text.strip()
    await update.message.reply_text("Tug‘ilgan yilingiz (masalan: 1990):")
    return ASK_TUGILGAN_YIL


async def ask_tugilgan_yil(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    text = update.message.text.strip()
    if not text.isdigit() or not (1950 <= int(text) <= 2015):
        await update.message.reply_text("❌ Tug‘ilgan yilni to‘g‘ri formatda yozing (masalan: 1995).")
        return ASK_TUGILGAN_YIL
    context.user_data['tugilgan_yil'] = text
    await update.message.reply_text("Ma’lumotingiz (masalan: Oliy, O‘rta maxsus):")
    return ASK_MA_LUMOT


async def ask_telefon(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    text = update.message.text.strip()
    if not text.startswith("+998") or len(text) != 13 or not text[1:].isdigit():
        await update.message.reply_text("❌ Telefon raqamni +998 xx xxx xx xx formatida yozing.")
        return ASK_TELEFON
    context.user_data['telefon'] = text
    reply_keyboard = [["Turmush qurgan", "Bo‘ydoq / Turmushga chiqmagan"],
                      ["Ajrashgan", "Beva"]]
    await update.message.reply_text(
        "Oilaviy holatingiz?",
        reply_markup=ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True, resize_keyboard=True)
    )
    return ASK_OILAVIY


# ... (qolgan handlerlar deyarli o'zgarmagan, faqat user_data → context.user_data)

async def ask_rasm(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    photo = update.message.photo[-1]
    context.user_data['rasm_file_id'] = photo.file_id
    await update.message.reply_text("Reklama ma’lumotini qayerdan olgansiz? (Telegram, Instagram, do‘stlar va h.k.)")
    return ASK_REKLAMA


async def ask_reklama(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    context.user_data['reklama_manbai'] = update.message.text
    data = context.user_data

    admin_text = (
        f"📝 **Yangi anketa!**\n"
        f"👤 Ism familiya: {data.get('ism_familiya')}\n"
        f"🎂 Tug‘ilgan yil: {data.get('tugilgan_yil')}\n"
        f"📚 Ma’lumot: {data.get('ma_lumot')}\n"
        f"🏠 Manzil: {data.get('manzil')}\n"
        f"📞 Telefon: {data.get('telefon')}\n"
        f"💑 Oilaviy holat: {data.get('oilaviy_holat')}\n"
        f"💼 Oldin ishlagan: {data.get('oldin_ish')}\n"
        f"💰 Oylik maosh: {data.get('oylik_maosh')}\n"
        f"⏳ Muddat: {data.get('muddat')}\n"
        f"❤️ Qiziqish: {data.get('qiziqish')}\n"
        f"📢 Reklama manbai: {data.get('reklama_manbai')}\n"
    )

    try:
        admin_id = int(ADMIN_CHAT_ID)
        await context.bot.send_message(chat_id=admin_id, text=admin_text, parse_mode="Markdown")
        await context.bot.send_photo(chat_id=admin_id, photo=data['rasm_file_id'])
        logger.info(f"Anketa from user {update.effective_user.id} sent to admin.")
    except Exception as e:
        logger.error(f"Failed to send to admin: {e}")
        await update.message.reply_text("Texnik xatolik yuz berdi. Iltimos, keyinroq urinib ko‘ring.")

    await update.message.reply_text(
        "Hurmatli nomzod, arizangiz qabul qilindi ✅\n"
        "Ko‘rib chiqilgandan so‘ng siz bilan bog‘lanamiz 📞\n\n"
        "E’tiboringiz uchun rahmat!"
    )

    context.user_data.clear()  # tozalash
    return ConversationHandler.END


# cancel va qolgan handlerlar o'zgarmagan (faqat context.user_data ishlatiladi)
