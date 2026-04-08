import logging
from telegram import Update, ReplyKeyboardMarkup, ReplyKeyboardRemove
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    filters,
    ConversationHandler,
    ContextTypes
)

# ==================== CONFIGURATION ====================
BOT_TOKEN = "8586521300:AAE3dpE5IBRPvA0vFmQJRzsZaEYE48qPPFk"       # Replace with your bot token from @BotFather
ADMIN_CHAT_ID =632522025           # Replace with your Telegram user ID (get from @userinfobot)
# =======================================================

# Enable logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Conversation states
(
    ASK_ISMI,
    ASK_TUGILGAN_YIL,
    ASK_MA_LUMOT,
    ASK_MANZIL,
    ASK_TELEFON,
    ASK_OILAVIY,
    ASK_OLDIN_ISH,
    ASK_OYLIK_MAOSH,
    ASK_MUDDAT,
    ASK_QIZIQISH,
    ASK_RASM,
    ASK_REKLAMA
) = range(12)

# Temporary user data storage
user_data = {}

# ---------- Handlers ----------
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    user_id = update.effective_user.id
    user_data[user_id] = {}
    await update.message.reply_text(
        "Assalomu alaykum! Ushbu anketani to‘liq to‘ldirib qayta jo‘natishingizni so‘raymiz.\n\n"
        "Ism familiyangizni yozing:"
    )
    return ASK_ISMI

async def ask_ismi(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    user_id = update.effective_user.id
    user_data[user_id]['ism_familiya'] = update.message.text
    await update.message.reply_text("Tug‘ilgan yilingiz (masalan: 1990):")
    return ASK_TUGILGAN_YIL

async def ask_tugilgan_yil(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    user_id = update.effective_user.id
    user_data[user_id]['tugilgan_yil'] = update.message.text
    await update.message.reply_text("Ma’lumotingiz (masalan: Oliy, O‘rta maxsus):")
    return ASK_MA_LUMOT

async def ask_ma_lumot(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    user_id = update.effective_user.id
    user_data[user_id]['ma_lumot'] = update.message.text
    await update.message.reply_text("Yashash manzilingiz (viloyat, tuman, ko‘cha):")
    return ASK_MANZIL

async def ask_manzil(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    user_id = update.effective_user.id
    user_data[user_id]['manzil'] = update.message.text
    await update.message.reply_text("Telefon raqamingiz (+998 xx xxx xx xx):")
    return ASK_TELEFON

async def ask_telefon(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    user_id = update.effective_user.id
    user_data[user_id]['telefon'] = update.message.text

    reply_keyboard = [["Turmush qurgan", "Bo‘ydoq / Turmushga chiqmagan"],
                      ["Ajrashgan", "Beva"]]
    await update.message.reply_text(
        "Oilaviy holatingiz?",
        reply_markup=ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True, resize_keyboard=True)
    )
    return ASK_OILAVIY

async def ask_oilaviy(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    user_id = update.effective_user.id
    user_data[user_id]['oilaviy_holat'] = update.message.text
    await update.message.reply_text(
        "Oldin qayerda ishlagansiz? (Ish joyingiz yoki tajribangiz)",
        reply_markup=ReplyKeyboardRemove()
    )
    return ASK_OLDIN_ISH

async def ask_oldin_ish(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    user_id = update.effective_user.id
    user_data[user_id]['oldin_ish'] = update.message.text
    await update.message.reply_text("Qancha oylikka ishlamoqchisiz? (Masalan: 3 000 000 so‘m)")
    return ASK_OYLIK_MAOSH

async def ask_oylik_maosh(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    user_id = update.effective_user.id
    user_data[user_id]['oylik_maosh'] = update.message.text
    await update.message.reply_text("Qancha muddat ishlamoqchisiz? (Masalan: 6 oy, 1 yil)")
    return ASK_MUDDAT

async def ask_muddat(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    user_id = update.effective_user.id
    user_data[user_id]['muddat'] = update.message.text
    await update.message.reply_text("Kitob o‘qishga, gul yasashga qiziqasizmi? (Ha/Yo‘q yoki qisqa javob)")
    return ASK_QIZIQISH

async def ask_qiziqish(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    user_id = update.effective_user.id
    user_data[user_id]['qiziqish'] = update.message.text
    await update.message.reply_text("Iltimos, rasmingizni yuboring (selfi yoki surat):")
    return ASK_RASM

async def ask_rasm(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    user_id = update.effective_user.id
    # Get the largest photo (best quality)
    photo = update.message.photo[-1]
    user_data[user_id]['rasm_file_id'] = photo.file_id
    await update.message.reply_text("Reklama ma’lumotini qayerdan olgansiz? (Telegram, Instagram, do‘stlar va h.k.)")
    return ASK_REKLAMA

async def ask_reklama(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    user_id = update.effective_user.id
    user_data[user_id]['reklama_manbai'] = update.message.text
    data = user_data[user_id]

    # Prepare the summary for admin
    admin_text = (
        f"📝 **Yangi anketa!**\n"
        f"👤 Ism familiya: {data['ism_familiya']}\n"
        f"🎂 Tug‘ilgan yil: {data['tugilgan_yil']}\n"
        f"📚 Ma’lumot: {data['ma_lumot']}\n"
        f"🏠 Manzil: {data['manzil']}\n"
        f"📞 Telefon: {data['telefon']}\n"
        f"💑 Oilaviy holat: {data['oilaviy_holat']}\n"
        f"💼 Oldin ishlagan: {data['oldin_ish']}\n"
        f"💰 Oylik maosh: {data['oylik_maosh']}\n"
        f"⏳ Muddat: {data['muddat']}\n"
        f"❤️ Qiziqish: {data['qiziqish']}\n"
        f"📢 Reklama manbai: {data['reklama_manbai']}\n"
    )

    # Send to admin
    try:
        await context.bot.send_message(chat_id=ADMIN_CHAT_ID, text=admin_text, parse_mode="Markdown")
        await context.bot.send_photo(chat_id=ADMIN_CHAT_ID, photo=data['rasm_file_id'])
        logger.info(f"Anketa from user {user_id} successfully sent to admin.")
    except Exception as e:
        logger.error(f"Failed to send to admin: {e}")
        # Optional: inform user about technical issue
        await update.message.reply_text("Texnik xatolik yuz berdi. Iltimos, keyinroq urinib ko‘ring.")

    # Confirm to user
    await update.message.reply_text(
        "Hurmatli nomzod, arizangiz qabul qilindi ✅\n"
        "Ko‘rib chiqilgandan so‘ng siz bilan bog‘lanamiz 📞\n\n"
        "E’tiboringiz uchun rahmat!"
    )

    # Clean up stored data for this user (optional)
    if user_id in user_data:
        del user_data[user_id]

    return ConversationHandler.END

async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    await update.message.reply_text(
        "Anketa bekor qilindi. Qayta boshlash uchun /start yuboring.",
        reply_markup=ReplyKeyboardRemove()
    )
    return ConversationHandler.END

# ---------- Main ----------
def main() -> None:
    # Create the Application
    application = Application.builder().token(BOT_TOKEN).build()

    # Conversation handler
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

    # Start the bot
    print("Bot is running...")
    application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == "__main__":
    main()