from telebot.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
from config import ADMIN_ID
from utils.database import (
    calculate_price_syp, generate_order_id,
    save_order, is_user_subscribed, is_blocked
)
from utils.keyboards import main_menu_keyboard, confirm_id_keyboard

# 🛒 الجلسات المؤقتة للمستخدمين
buy_sessions = {}

def register(bot):

    # 📌 استقبال اختيار منتج
    @bot.message_handler(func=lambda m: m.text in [
        "60 شدة", "325 شدة", "660 شدة", "1800 شدة", "3850 شدة", "8100 شدة",
        "100 جوهرة", "310 جوهرة", "520 جوهرة", "1060 جوهرة", "2180 جوهرة"
    ])
    def start_buy(message: Message):
        user_id = message.from_user.id

        if not is_user_subscribed(bot, user_id, 'fire_fast_fire') or is_blocked(user_id):
            bot.send_message(
                message.chat.id,
                "⚠️ لازم تكون مشترك بالقناة أول يا نجم 🔒",
                parse_mode="HTML",
                reply_markup=main_menu_keyboard()
            )
            return

        product = message.text
        buy_sessions[user_id] = {"step": "player_id", "product": product}
        bot.send_message(message.chat.id, f"🎮 تمام، اكتبلي آيدي اللاعب اللي بدك نشحن له {product}:")

    # ⌨️ استقبال آيدي اللاعب
    @bot.message_handler(func=lambda m: m.from_user.id in buy_sessions and buy_sessions[m.from_user.id]["step"] == "player_id")
    def confirm_player_id(message: Message):
        user_id = message.from_user.id
        player_id = message.text.strip()

        buy_sessions[user_id]["player_id"] = player_id
        buy_sessions[user_id]["step"] = "confirm_id"

        bot.send_message(
            message.chat.id,
            f"🔁 هل الآيدي اللي كتبته صحيح؟\n\n<code>{player_id}</code>\n\nاكتب ✅ لو تمام أو 🔙 لو بدك ترجّع وتعدله.",
            parse_mode="HTML",
            reply_markup=confirm_id_keyboard()
        )

    # ✅ تأكيد أو إلغاء الآيدي
    @bot.message_handler(func=lambda m: m.from_user.id in buy_sessions and buy_sessions[m.from_user.id]["step"] == "confirm_id")
    def handle_id_confirmation(message: Message):
        user_id = message.from_user.id
        text = message.text.strip()

        if text == "🔙":
            buy_sessions[user_id]["step"] = "player_id"
            bot.send_message(message.chat.id, "✏️ تمام، اكتب الآيدي من جديد:")
            return

        if text != "✅":
            bot.send_message(message.chat.id, "❌ اكتب ✅ للتأكيد أو 🔙 للرجوع.")
            return

        # ✅ حساب السعر
        session = buy_sessions[user_id]
        product = session["product"]
        price_map = {
            "60 شدة": 0.87, "325 شدة": 4.41, "660 شدة": 8.81,
            "1800 شدة": 22.04, "3850 شدة": 43.00, "8100 شدة": 86.00,
            "100 جوهرة": 0.95, "310 جوهرة": 2.44, "520 جوهرة": 4.70,
            "1060 جوهرة": 9.37, "2180 جوهرة": 18.75
        }

        dollar_price = price_map.get(product, 0)
        syp_price = int(calculate_price_syp(dollar_price))
        player_id = session["player_id"]
        order_id = generate_order_id(user_id)

        session["syp_price"] = syp_price
        session["order_id"] = order_id

        # ✅ زر التأكيد أو الإلغاء (يُعالَج في callback_handler.py)
        confirm_keyboard = InlineKeyboardMarkup(row_width=2)
        confirm_keyboard.add(
            InlineKeyboardButton("✅ تأكيد الطلب", callback_data="confirm_order"),
            InlineKeyboardButton("🔙 رجوع", callback_data="cancel_order")
        )

        bot.send_message(
            message.chat.id,
            f"🔔 <b>مراجعة الطلب:</b>\n\n"
            f"🛒 المنتج: {product}\n"
            f"🎮 ID اللاعب: <code>{player_id}</code>\n"
            f"💵 السعر: {syp_price} ل.س\n\n"
            f"💡 سيتم خصم المبلغ من محفظتك بعد موافقة الأدمن.\n"
            f"📌 رقم العملية: <code>{order_id}</code>",
            parse_mode="HTML",
            reply_markup=confirm_keyboard
        )
