from telebot.types import Message
from utils.database import get_user_orders, is_user_subscribed
from config import CHANNEL_USERNAME

def register(bot):
    @bot.message_handler(func=lambda m: m.text == "🛍️ مشترياتي")
    def purchase_history(message: Message):
        if not is_user_subscribed(bot, message.from_user.id, CHANNEL_USERNAME):
            bot.send_message(
                message.chat.id,
                "⚠️ عذرًا يا نجم، ما تشترك بالقناة حتى الآن.\n"
                f"📢 <a href='https://t.me/{CHANNEL_USERNAME}'>اشترك  أول</a> ورجع تشوف مشترياتك 👌",
                parse_mode="HTML"
            )
            return

        orders = get_user_orders(message.chat.id)
        if not orders:
            bot.send_message(message.chat.id, "🛒 للأسف، مفيش مشتريات لك حتى الآن.")
            return

        history = "\n\n".join(
            [f"🆔 الطلب: {o['id']}\n📦 المنتج: {o['product']}\n💰 السعر: {o['price']} ل.س\n📅 التاريخ: {o['date']}\n📌 الحالة: {o['status']}" for o in orders]
        )
        bot.send_message(message.chat.id, f"📜 دي كل مشترياتك يا نجم:\n\n{history}")