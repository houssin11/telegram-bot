from telebot.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
from utils.keyboards import wallet_menu, main_menu_keyboard
from utils.database import (
    load_users, save_users, is_user_subscribed, is_blocked,
    save_transfer_request, update_user_balance, save_order,
    calculate_price_syp, generate_order_id
)
from config import CHANNEL_USERNAME, ADMIN_ID

transfer_sessions = {}

def register(bot):
    @bot.message_handler(func=lambda m: m.text == "💻 المحفظة")
    def show_wallet(message: Message):
        if not is_user_subscribed(bot, message.from_user.id, CHANNEL_USERNAME) or is_blocked(message.from_user.id):
            bot.send_message(
                message.chat.id,
                "⚠️ عذرًا يا نجم، ما تشترك بالقناة أو محظور حسابك مؤقتًا.\n"
                f"📢 <a href='https://t.me/{CHANNEL_USERNAME}'>اشترك  أول</a> ورجع تستخدم القسم ده 👌",
                parse_mode="HTML"
            )
            return

        users = load_users()
        user_id = str(message.from_user.id)
        balance = users.get(user_id, {}).get("balance", 0)

        bot.send_message(message.chat.id, f"💰 رصيدك الحالي: {balance} ل.س")
        bot.send_message(message.chat.id, f"`{user_id}`", parse_mode="Markdown")
        bot.send_message(
            message.chat.id,
            "📌 تقدر تنسخ الآيدي من الرسالة اللي فوق وتبعته لأي حد علشان يستقبلك تحويل.",
            reply_markup=wallet_menu(),
            parse_mode="HTML"
        )

    @bot.message_handler(func=lambda m: m.text == "📤 تحويل رصيد لعميل")
    def start_transfer(message: Message):
        if not is_user_subscribed(bot, message.from_user.id, CHANNEL_USERNAME) or is_blocked(message.from_user.id):
            bot.send_message(
                message.chat.id,
                "⚠️ عذرًا يا نجم، ما تشترك بالقناة أو حسابك محظور.\n"
                f"📢 <a href='https://t.me/{CHANNEL_USERNAME}'>اشترك  أول</a> ورجع تستخدم التحويل 👌",
                parse_mode="HTML"
            )
            return

        transfer_sessions[message.from_user.id] = {}
        bot.send_message(message.chat.id, "🔄 اكتب آيدي العميل اللي بدك تحول له الرصيد:")

    @bot.message_handler(func=lambda m: m.from_user.id in transfer_sessions and "to_id" not in transfer_sessions[m.from_user.id])
    def receive_id(message: Message):
        to_id = message.text.strip()
        users = load_users()
        from_id = str(message.from_user.id)

        if to_id == from_id:
            bot.send_message(message.chat.id, "❌ ما ينفعش تحول لنفسك.")
            del transfer_sessions[from_id]
            return

        if is_blocked(to_id):
            bot.send_message(message.chat.id, "🚫 العميل اللي بدك تحول له محظور حاليًا.")
            del transfer_sessions[from_id]
            return

        if to_id not in users:
            bot.send_message(message.chat.id, "❌ الآيدي اللي كتبته مش موجود عندنا.")
            del transfer_sessions[from_id]
            return

        transfer_sessions[from_id]["to_id"] = to_id
        bot.send_message(message.chat.id, "💰 تمام، دلوقتي اكتبلي المبلغ اللي بدك تحوله (لازم يكون 5000 ل.س أو أكتر):")

    @bot.message_handler(func=lambda m: m.from_user.id in transfer_sessions and "amount" not in transfer_sessions[m.from_user.id])
    def receive_amount(message: Message):
        try:
            amount = int(message.text.strip())
            if amount < 5000:
                bot.send_message(message.chat.id, "❌ الحد الأدنى للتحويل هو 5000 ل.س.")
                del transfer_sessions[message.from_user.id]
                return

            users = load_users()
            from_id = str(message.from_user.id)
            from_balance = users.get(from_id, {}).get("balance", 0)

            if from_balance - amount < 5000:
                bot.send_message(message.chat.id, f"❌ لازم يفضل في محفظتك على الأقل 5000 ل.س بعد التحويل.\nرصيدك الحالي: {from_balance} ل.س")
                del transfer_sessions[message.from_user.id]
                return

            session = transfer_sessions[message.from_user.id]
            session["amount"] = amount

            bot.send_message(
                message.chat.id,
                f"⚠️ تأكيد العملية:\n\n📤 هتبعت {amount} ل.س إلى العميل `{session['to_id']}`\n\n"
                "✅ لو تمام، اكتب: تأكيد\n❌ لو عايز تلغي، اكتب: الغاء",
                parse_mode="Markdown"
            )
        except ValueError:
            bot.send_message(message.chat.id, "❌ دخل رقم صحيح للمبلغ.")
            del transfer_sessions[message.from_user.id]

    @bot.message_handler(func=lambda m: m.from_user.id in transfer_sessions and "amount" in transfer_sessions[m.from_user.id])
    def confirm_transfer(message: Message):
        text = message.text.strip().lower()
        user_id = message.from_user.id

        if text == "الغاء":
            del transfer_sessions[user_id]
            bot.send_message(message.chat.id, "🚫 تم إلغاء التحويل.")
            return

        if text != "تأكيد":
            bot.send_message(message.chat.id, "❌ خيار غير معروف. اكتب 'تأكيد' أو 'الغاء'.")
            return

        session = transfer_sessions[user_id]
        to_id = session["to_id"]
        amount = session["amount"]

        save_transfer_request(user_id, to_id, amount)

        details = (
            f"💸 <b>طلب تحويل رصيد</b>\n\n"
            f"👤 من: {user_id}\n"
            f"👥 إلى: {to_id}\n"
            f"💰 المبلغ: {amount} ل.س"
        )

        confirm_keyboard = InlineKeyboardMarkup(row_width=2)
        confirm_keyboard.row(
            InlineKeyboardButton("✅ موافقة", callback_data=f"approve_transfer_{user_id}_{to_id}_{amount}"),
            InlineKeyboardButton("❌ رفض", callback_data=f"reject_transfer_{user_id}_{to_id}")
        )

        for admin in ADMIN_ID:
            bot.send_message(
                admin,
                details,
                reply_markup=confirm_keyboard,
                parse_mode="HTML"
            )

        bot.send_message(message.chat.id, "⏳ تم إرسال الطلب للأدمن. سيتم تنفيذه بعد الموافقة.")
        del transfer_sessions[user_id]

    @bot.message_handler(func=lambda m: m.text == "📒 سجل التحويلات")
    def transfer_history(message: Message):
        if not is_user_subscribed(bot, message.from_user.id, CHANNEL_USERNAME) or is_blocked(message.from_user.id):
            bot.send_message(
                message.chat.id,
                "⚠️ عذرًا يا نجم، ما تشترك بالقناة أو حسابك محظور.\n"
                f"📢 <a href='https://t.me/{CHANNEL_USERNAME}'>اشترك  أول</a> ورجع تستخدم السجل 👌",
                parse_mode="HTML"
            )
            return

        users = load_users()
        user_id = str(message.from_user.id)
        history = users.get(user_id, {}).get("history", [])

        if not history:
            bot.send_message(message.chat.id, "📭 مفيش أي تحويلات تمت على حسابك حتى الآن.")
            return

        message_lines = ["📜 سجل آخر التحويلات:"]
        for h in reversed(history[-5:]):
            msg = f"{'📤 أرسلت' if h['type'] == 'sent' else '📥 استلمت'} {h['amount']} ل.س "
            msg += f"{'لـ' if h['type'] == 'sent' else 'من'} {h['target']}\n🕒 {h['time']}"
            message_lines.append(msg)

        bot.send_message(message.chat.id, "\n\n".join(message_lines))

    @bot.message_handler(func=lambda m: m.text == "🛍️ مشترياتي")
    def my_orders(message: Message):
        if not is_user_subscribed(bot, message.from_user.id, CHANNEL_USERNAME) or is_blocked(message.from_user.id):
            bot.send_message(
                message.chat.id,
                "⚠️ عذرًا يا نجم، ما تشترك بالقناة أو حسابك محظور.\n"
                f"📢 <a href='https://t.me/{CHANNEL_USERNAME}'>اشترك  أول</a> ورجع تستخدم المشتريات 👌",
                parse_mode="HTML"
            )
            return

        bot.send_message(message.chat.id, "🛒 دي كل مشترياتك يا نجم (جاري التطوير).")

    @bot.message_handler(func=lambda m: m.text == "⬅️ رجوع")
    def go_back(message: Message):
        bot.send_message(
            message.chat.id,
            "🔙 رجعناك للقائمة الرئيسية، تحت أمرك يا نجم:",
            reply_markup=main_menu_keyboard(),
            parse_mode="HTML"
        )

    @bot.message_handler(func=lambda m: m.text == "🚀 Start")
    def restart(message: Message):
        from handlers.start import send_welcome
        send_welcome(bot, message.chat.id)
