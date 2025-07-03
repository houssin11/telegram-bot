from telebot.types import CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from utils.database import load_users, save_users, update_user_balance
from config import ADMIN_ID
from handlers.buy import buy_sessions
from utils.keyboards import main_menu_keyboard

def register(bot):
    # ✅ تأكيد التحويل من الأدمن
    @bot.callback_query_handler(func=lambda call: call.data.startswith("approve_transfer_"))
    def approve_transfer(call: CallbackQuery):
        _, from_id, to_id, amount_str = call.data.split("_", 3)
        amount = float(amount_str.strip())

        users = load_users()

        if from_id not in users or to_id not in users:
            bot.answer_callback_query(call.id, "❌ أحد الحسابات غير موجود.")
            return

        # خصم وإضافة الرصيد
        users[from_id]["balance"] -= amount
        users[to_id]["balance"] += amount

        # تحديث السجلات
        from_history = users[from_id].setdefault("history", [])
        to_history = users[to_id].setdefault("history", [])

        from datetime import datetime
        now = datetime.now().strftime("%Y-%m-%d %H:%M")

        from_history.append({
            "type": "sent",
            "amount": f"{amount} ل.س",
            "target": to_id,
            "time": now
        })
        to_history.append({
            "type": "received",
            "amount": f"{amount} ل.س",
            "target": from_id,
            "time": now
        })

        save_users(users)

        bot.send_message(from_id, f"✅ تم تحويل {amount} ل.س بنجاح للآيدي `{to_id}`.", parse_mode="Markdown")
        bot.send_message(to_id, f"📥 استلمت {amount} ل.س من الآيدي `{from_id}`.", parse_mode="Markdown")
        bot.answer_callback_query(call.id, "✅ تم تنفيذ التحويل.")

    # ❌ رفض التحويل من الأدمن
    @bot.callback_query_handler(func=lambda call: call.data.startswith("reject_transfer_"))
    def reject_transfer(call: CallbackQuery):
        _, from_id, to_id = call.data.split("_", 2)
        bot.send_message(from_id, f"❌ تم رفض طلب تحويل الرصيد للآيدي `{to_id}` من قبل الإدارة.", parse_mode="Markdown")
        bot.answer_callback_query(call.id, "🚫 تم الرفض.")

    # ✅ تأكيد طلب الشراء
    @bot.callback_query_handler(func=lambda call: call.data == "confirm_order")
    def confirm_order(call: CallbackQuery):
        user_id = call.from_user.id
        chat_id = call.message.chat.id

        if user_id not in buy_sessions:
            bot.answer_callback_query(call.id, "⛔ انتهت الجلسة.")
            return

        session = buy_sessions[user_id]
        product = session["product"]
        syp_price = session["syp_price"]
        player_id = session["player_id"]
        order_id = session["order_id"]
        full_name = call.from_user.first_name or ""
        username = call.from_user.username or "بدون يوزر"

        # إرسال الطلب للأدمن
        admin_text = (
            f"📩 <b>طلب شراء جديد</b>\n\n"
            f"🛒 المنتج: {product}\n"
            f"🎮 ID اللاعب: <code>{player_id}</code>\n"
            f"💵 السعر بالليرة: {syp_price} ل.س\n"
            f"👤 العميل: {full_name}\n"
            f"🔗 يوزر: @{username}\n"
            f"🆔 آيدي: <code>{user_id}</code>\n"
            f"🧾 رقم العملية: <code>{order_id}</code>"
        )

        kb = InlineKeyboardMarkup()
        kb.row(
            InlineKeyboardButton("✅ موافقة", callback_data=f"approve_order_{user_id}_{syp_price}_{product}_{player_id}"),
            InlineKeyboardButton("❌ غير متوفر", callback_data=f"reject_order_{user_id}_{syp_price}_{product}_{player_id}")
        )

        for admin in ADMIN_ID:
            bot.send_message(admin, admin_text, reply_markup=kb, parse_mode="HTML")

        bot.send_message(chat_id, "⏳ تم إرسال طلبك للإدارة، جاري مراجعته.\n📮 هيوصلك إشعار بعد الموافقة أو الرفض.")
        del buy_sessions[user_id]

    # ❌ إلغاء طلب الشراء
    @bot.callback_query_handler(func=lambda call: call.data == "cancel_order")
    def cancel_order(call: CallbackQuery):
        user_id = call.from_user.id
        chat_id = call.message.chat.id
        if user_id in buy_sessions:
            del buy_sessions[user_id]
        bot.send_message(chat_id, "🔙 تم إلغاء الطلب.", reply_markup=main_menu_keyboard())
        bot.answer_callback_query(call.id, "❌ تم الإلغاء.")

    # ✅ موافقة الأدمن على الشراء
    @bot.callback_query_handler(func=lambda call: call.data.startswith("approve_order_"))
    def approve_order(call: CallbackQuery):
        _, user_id, syp_price, product, player_id = call.data.split("_", 4)
        user_id = int(user_id)
        syp_price = int(syp_price)

        users = load_users()
        current_balance = users.get(str(user_id), {}).get("balance", 0)

        if current_balance >= syp_price:
            update_user_balance(user_id, -syp_price)
            bot.send_message(user_id, f"✅ تم تنفيذ طلبك بنجاح، وتم شحن {product} لحساب اللاعب <code>{player_id}</code>.", parse_mode="HTML")
            bot.answer_callback_query(call.id, "✅ تم خصم الرصيد وتنفيذ الطلب.")
        else:
            bot.send_message(user_id, f"❌ تعذر تنفيذ طلبك بسبب عدم كفاية الرصيد.")
            bot.answer_callback_query(call.id, "❌ الرصيد غير كافٍ.")

    # ❌ رفض طلب الشراء
    @bot.callback_query_handler(func=lambda call: call.data.startswith("reject_order_"))
    def reject_order(call: CallbackQuery):
        _, user_id, *_ = call.data.split("_", 3)
        user_id = int(user_id)
        bot.send_message(user_id, f"❌ للأسف، تم رفض طلبك من قبل الإدارة. جرب لاحقًا أو تواصل معنا.")
        bot.answer_callback_query(call.id, "🚫 تم الرفض.")
