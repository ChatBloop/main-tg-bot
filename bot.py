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

# ==================== HARDCODED CONFIGURATION ====================
BOT_TOKEN = "8586521300:AAE3dpE5IBRPvA0vFmQJRzsZaEYE48qPPFk"
ADMIN_CHAT_ID = "632522025"
# ================================================================

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# ---------- Health check server ----------
flask_app = Flask(__name__)

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
    context.user_data.clear()
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
        await update.message.reply_text("❌ Tug‘ilgan yilni to‘g‘ri yozing (masalan: 1995).")
        return ASK_TUGILGAN_YIL
    context.user_data['tugilgan_yil'] = text
    await update.message.reply_text("Ma’lumotingiz (masalan: Oliy, O‘rta maxsus):")
    return ASK_MA_LUMOT


async def ask_ma_lumot(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    context.user_data['ma_lumot'] = update.message.text.strip()
    await update.message.reply_text("Yashash manzilingiz (viloyat, tuman, ko‘cha):")
    return ASK_MANZIL


async def ask_manzil(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    context.user_data['manzil'] = update.message.text.strip()
    await update.message.reply_text("Telefon raqamingiz (+998 xx xxx xx xx):")
    return ASK_TELEFON


async def ask_telefon(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    text = update.message.text.strip()
    
    # Bo'shliq, chiziqcha, nuqta va boshqa belgilarni olib tashlaymiz
    cleaned = ''.join(c for c in text if c.isdigit() or c == '+')
    
    if not cleaned.startswith("+998") or len(cleaned) != 13 or not cleaned[1:].isdigit():
        await update.message.reply_text(
            "❌ Telefon raqamni +998 xx xxx xx xx formatida yozing.\n"
            "Bo‘shliq bilan yoki bo‘shliqsiz, chiziqcha bilan ham yozsa bo‘ladi.\n"
            "Masalan: +998 90 123 45 67"
        )
        return ASK_TELEFON
    
    # Toza formatda saqlaymiz
    context.user_data['telefon'] = cleaned
    reply_keyboard = [["Turmush qurgan", "Bo‘ydoq / Turmushga chiqmagan"],
                      ["Ajrashgan", "Beva"]]
    await update.message.reply_text(
        "Oilaviy holatingiz?",
        reply_markup=ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True, resize_keyboard=True)
    )
    return ASK_OILAVIY


async def ask_oilaviy(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    context.user_data['oilaviy_holat'] = update.message.text
    await update.message.reply_text(
        "Oldin qayerda ishlagansiz? (Ish joyingiz yoki tajribangiz)",
        reply_markup=ReplyKeyboardRemove()
    )
    return ASK_OLDIN_ISH


async def ask_oldin_ish(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    context.user_data['oldin_ish'] = update.message.text
    await update.message.reply_text("Qancha oylikka ishlamoqchisiz? (Masalan: 3 000 000 so‘m)")
    return ASK_OYLIK_MAOSH


async def ask_oylik_maosh(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    context.user_data['oylik_maosh'] = update.message.text
    await update.message.reply_text("Qancha muddat ishlamoqchisiz? (Masalan: 6 oy, 1 yil)")
    return ASK_MUDDAT


async def ask_muddat(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    context.user_data['muddat'] = update.message.text
    await update.message.reply_text("Kitob o‘qishga, gul yasashga qiziqasizmi? (Ha/Yo‘q yoki qisqa javob)")
    return ASK_QIZIQISH


async def ask_qiziqish(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    context.user_data['qiziqish'] = update.message.text
    await update.message.reply_text("Iltimos, rasmingizni yuboring (selfi yoki surat):")
    return ASK_RASM


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
        await context.bot.send_message(chat_id=ADMIN_CHAT_ID, text=admin_text, parse_mode="Markdown")
        await context.bot.send_photo(chat_id=ADMIN_CHAT_ID, photo=data['rasm_file_id'])
        logger.info(f"Anketa from user {update.effective_user.id} sent to admin.")
    except Exception as e:
        logger.error(f"Failed to send to admin: {e}")

    await update.message.reply_text(
        "Hurmatli nomzod, arizangiz qabul qilindi ✅\n"
        "Ko‘rib chiqilgandan so‘ng siz bilan bog‘lanamiz 📞\n\n"
        "E’tiboringiz uchun rahmat!"
    )

    context.user_data.clear()
    return ConversationHandler.END


async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    await update.message.reply_text(
        "Anketa bekor qilindi. Qayta boshlash uchun /start yuboring.",
        reply_markup=ReplyKeyboardRemove()
    )
    context.user_data.clear()
    return ConversationHandler.END


# ---------- Main ----------
def main() -> None:
    start_health_server()
    application = Application.builder().token(BOT_TOKEN).build()

    conv_handler = ConversationHandler(
        entry_points=[CommandHandler("start", start)],
        states={
            ASK_ISMI: [MessageHandler(filters.TEXT & ~filters.COMMAND, ask_ismi)],
            ASK_TUGILGAN_YIL: [MessageHandler(filters.TEXT & ~filters.COMMAND, ask_tugilgan_yil)],
            ASK_MA_LUMOT: [MessageHandler(filters.TEXT & ~filters.COMMAND, ask_ma_lumot)],
            ASK_MANZIL: [MessageHandler(filters.TEXT & ~filters.COMMAND, ask_manzil)],
            ASK_TELEFON: [MessageHandler(filters.TEXT & ~filters.COMMAND, ask_telefon)],
            ASK_OILAVIY: [MessageHandler(filters.TEXT & ~filters.COMMAND, ask_oilaviy)],
            ASK_OLDIN_ISH: [MessageHandler(filters.TEXT & ~filters.COMMAND, ask_oldin_ish)],
            ASK_OYLIK_MAOSH: [MessageHandler(filters.TEXT & ~filters.COMMAND, ask_oylik_maosh)],
            ASK_MUDDAT: [MessageHandler(filters.TEXT & ~filters.COMMAND, ask_muddat)],
            ASK_QIZIQISH: [MessageHandler(filters.TEXT & ~filters.COMMAND, ask_qiziqish)],
            ASK_RASM: [MessageHandler(filters.PHOTO, ask_rasm)],
            ASK_REKLAMA: [MessageHandler(filters.TEXT & ~filters.COMMAND, ask_reklama)],
        },
        fallbacks=[CommandHandler("cancel", cancel)],
    )

    application.add_handler(conv_handler)
    print("✅ Bot is running...")
    application.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()
