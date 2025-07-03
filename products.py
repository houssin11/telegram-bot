from telebot.types import Message
from utils.keyboards import product_menu, main_menu_keyboard, game_products_menu
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
            "🌟 اختار نوع المنتج اللي بدك تشتريه من القائمة تحت 👇\n\n"
            f"💰 رصيدك الحالي: {balance} ل.س",
            reply_markup=product_menu(),
            parse_mode="HTML"
        )

    # ⬇️ عند اختيار 🎮 شحن ألعاب
    @bot.message_handler(func=lambda m: m.text == "🎮 شحن ألعاب")
    def show_game_products(message: Message):
        bot.send_message(
            message.chat.id,
            "🎮 اختار نوع الشحن اللي بدك إياه 👇",
            reply_markup=game_products_menu()
        )

    # ⬇️ نترك أزرار 🔥 و 💎 تمر لمنطق الشراء (buy.py)
    # لأن التعامل معها سيكون من هناك حسب الجلسة

    # ⬅️ رجوع للقائمة السابقة
    @bot.message_handler(func=lambda m: m.text == "⬅️ رجوع")
    def go_back(message: Message):
        bot.send_message(
            message.chat.id,
            "🔙 رجعناك لقائمة المنتجات، اختار من جديد:",
            reply_markup=product_menu()
        )

    @bot.message_handler(func=lambda m: m.text == "🚀 Start")
    def restart(message: Message):
        from handlers.start import send_welcome
        send_welcome(bot, message.chat.id)
