from telebot.types import Message, ReplyKeyboardMarkup, KeyboardButton
from utils.keyboards import product_menu, main_menu_keyboard
from utils.database import is_user_subscribed, get_user_balance
from config import CHANNEL_USERNAME

def register(bot):
    @bot.message_handler(func=lambda m: m.text == "🏭️ عرض المنتجات")
    def show_products(message: Message):
        if not is_user_subscribed(bot, message.from_user.id, CHANNEL_USERNAME):
            bot.send_message(
                message.chat.id,
                "⚠️ عذرًا يا نجم، ما تشترك بالقناة حتى الآن.\n"
                f"📢 <a href='https://t.me/{CHANNEL_USERNAME}'>اشترك أول</a> ورجع تستخدم القسم ده 👌",
                parse_mode="HTML",
                reply_markup=main_menu_keyboard()
            )
            return

        balance = get_user_balance(message.from_user.id)

        bot.send_message(
            message.chat.id,
            "🌟 اختار نوع المنتج اللي بدك تشتريه من القائمة تحت، ولا تضيع وقتنا 😎👇\n\n"
            f"💰 رصيدك الحالي: {balance} ل.س",
            reply_markup=product_menu(),
            parse_mode="HTML"
        )

    # ✅ عرض منتجات الألعاب
    @bot.message_handler(func=lambda m: m.text == "🎮 شحن ألعاب")
    def show_game_products(message: Message):
        kb = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=False)
        kb.row(KeyboardButton("🔥 شحن شدات ببجي"), KeyboardButton("💎 شحن جواهر فري فاير"))
        kb.row(KeyboardButton("⬅️ رجوع"), KeyboardButton("🚀 Start"))
        bot.send_message(
            message.chat.id,
            "🎮 اختار نوع الشحن اللي بدك إياه 👇",
            reply_markup=kb
        )

    # ✅ باقات ببجي
    @bot.message_handler(func=lambda m: m.text == "🔥 شحن شدات ببجي")
    def show_pubg_products(message: Message):
        kb = ReplyKeyboardMarkup(resize_keyboard=True)
        kb.add(KeyboardButton("60 شدة"), KeyboardButton("325 شدة"))
        kb.add(KeyboardButton("660 شدة"), KeyboardButton("1800 شدة"))
        kb.add(KeyboardButton("3850 شدة"), KeyboardButton("8100 شدة"))
        kb.add(KeyboardButton("⬅️ رجوع"))
        bot.send_message(
            message.chat.id,
            "🔥 اختار الباقة اللي تناسبك من عروض PUBG:",
            reply_markup=kb
        )

    # ✅ باقات فري فاير
    @bot.message_handler(func=lambda m: m.text == "💎 شحن جواهر فري فاير")
    def show_freefire_products(message: Message):
        kb = ReplyKeyboardMarkup(resize_keyboard=True)
        kb.add(KeyboardButton("100 جوهرة"), KeyboardButton("310 جوهرة"))
        kb.add(KeyboardButton("520 جوهرة"), KeyboardButton("1060 جوهرة"))
        kb.add(KeyboardButton("2180 جوهرة"))
        kb.add(KeyboardButton("⬅️ رجوع"))
        bot.send_message(
            message.chat.id,
            "💎 اختار عدد الجواهر اللي بدك تشتريها من Free Fire:",
            reply_markup=kb
        )

    # ✅ زر منتج قريبًا
    @bot.message_handler(func=lambda m: m.text == "🧰 منتج قريبًا")
    def upcoming_product(message: Message):
        bot.send_message(
            message.chat.id,
            "🚧 ترقبوا منتج جديد قريبًا! 😍",
            parse_mode="HTML"
        )

    # ✅ زر الرجوع ⬅️ يعيد للقائمة الرئيسية للمنتجات
    @bot.message_handler(func=lambda m: m.text == "⬅️ رجوع")
    def go_back_to_products(message: Message):
        bot.send_message(
            message.chat.id,
            "🔙 رجعناك لقائمة المنتجات يا نجم:",
            reply_markup=product_menu()
        )

    # ✅ زر Start
    @bot.message_handler(func=lambda m: m.text == "🚀 Start")
    def restart(message: Message):
        from handlers.start import send_welcome
        send_welcome(bot, message.chat.id)
