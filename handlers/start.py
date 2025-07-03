from telebot.types import Message
from utils.keyboards import main_menu_keyboard
from config import CHANNEL_USERNAME, CHANNEL_LINK, BOT_ACTIVE
from utils.database import is_user_subscribed


# ⬇️ رسالة الترحيب المحترفة بلمسة كوميدية مختلطة
def send_welcome(bot, chat_id):
    text = (
        "👋 <b>أهلاً وسهلًا في بوت FireBuy!</b>\n\n"
        "📌 <b>شنو بنقدّم لك؟</b>\n"
        "إحنا منصة متخصصة بالبطاقات، الشحن، والخدمات الرقمية السريعة، كلشي جاهز وبنقرة واحدة 🔥\n\n"
        "🚀 <b>ليش تعتمد علينا؟</b>\n"
        "✔️ سرعة في التسليم، 24/7 بدون نوم 😴\n"
        "✔️ دعم فني بيعرف يرد قبل ما تسأل 💬\n"
        "✔️ أسعار تحفة وعروض مش هتلاقيها بمكان ثاني 🎯\n"
        "✔️ خدمات متنوعة تناسب كل اللي بدك تسد حاجتك\n\n"
        f"📢 <b>لازم تشترك بقناة البوت أول:</b>\n<a href='{CHANNEL_LINK}'>{CHANNEL_LINK}</a>"
    )
    bot.send_message(chat_id, text, parse_mode="HTML")


# ⬇️ رسالة إغلاق البوت (تحت الصيانة)
def send_closed(bot, chat_id):
    bot.send_message(
        chat_id,
        "🚧 <b>البوت تحت صيانة مؤقتة شوي</b> 🛠️\n"
        "💡 عم نضيف تحسينات علشان نرجع أسرع وأقوى من الأول 💥\n"
        f"📌 تابعنا من هنا: <a href='{CHANNEL_LINK}'>{CHANNEL_LINK}</a>",
        parse_mode="HTML"
    )


# ⬇️ تسجيل الأمر /start و زر Start
def register(bot):
    @bot.message_handler(commands=["start"])
    @bot.message_handler(func=lambda m: m.text == "🚀 Start")
    def handle_start(message: Message):
        if not BOT_ACTIVE:
            send_closed(bot, message.chat.id)
            return

        if not is_user_subscribed(bot, message.from_user.id, CHANNEL_USERNAME):
            bot.send_message(
                message.chat.id,
                f"⚠️ لازم تشترك في القناة أول، مو مسموح ندخلك بدون إذن 😉\n\n📢 <a href='{CHANNEL_LINK}'>{CHANNEL_LINK}</a>",
                parse_mode="HTML"
            )
            return

        send_welcome(bot, message.chat.id)

        # إرسال الكيبورد بعد الترحيب
        bot.send_message(
            message.chat.id,
            "👇 اختر الخدمة اللي تحتاجها أو ضغط على 'Start'، وخلينا نبدأ العمل يا محترف 💼:",
            reply_markup=main_menu_keyboard()
        )