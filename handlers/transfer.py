from telebot.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
from utils.database import is_user_subscribed, is_blocked, save_transfer_request
from config import CHANNEL_USERNAME, ADMIN_ID
from utils.keyboards import admin_action_kb

# ⬇️ تخزين جلسة التحويل المؤقتة
transfer_sessions = {}

def register(bot):
    @bot.message_handler(func=lambda m: m.text == "📤 تحويل رصيد لعميل")
    def transfer_handler(message: Message):
        if not is_user_subscribed(bot, message.from_user.id, CHANNEL_USERNAME) or is_blocked(message.from_user.id):
            bot.send_message(
                message.chat.id,
                "⚠️ عذرًا يا نجم، ما تشترك بالقناة أو حسابك محظور.\n"
                f"📢 <a href='https://t.me/{CHANNEL_USERNAME}'>اشترك  أول</a> ورجع تتواصل معنا.",
                parse_mode="HTML"
            )
            return

        bot.send_message(
            message.chat.id,
            "📝 تمام، ارسللي الآيدي والمبلغ اللي بدك تحوله بهذا الشكل:\n\n"
            "`123456789 - 5000`\n\n"
            "🔒 وهنجهز الطلب للأدمن فورًا!",
            parse_mode="Markdown"
        )

        transfer_sessions[message.from_user.id] = {
            'step': 'waiting_for_details'
        }

    @bot.message_handler(func=lambda m: m.from_user.id in transfer_sessions and transfer_sessions[m.from_user.id]['step'] == 'waiting_for_details')
    def receive_transfer_details(message: Message):
        user_id = message.from_user.id
        text = message.text.strip()

        if "-" not in text:
            bot.send_message(message.chat.id, "❌ الشكل مش صحيح. خليك على شكل `ايدي - مبلغ`.")
            return

        try:
            to_id_str, amount_str = text.split("-")
            to_id = to_id_str.strip()
            amount = int(amount_str.strip())

            if amount < 5000:
                bot.send_message(message.chat.id, "❌ الحد الأدنى للتحويل هو 5000 ل.س.")
                return

            # حفظ الجلسة المؤقتة
            transfer_sessions[user_id].update({
                'to_id': to_id,
                'amount': f"{amount} ل.س",
                'step': 'confirmed'
            })

            confirm_keyboard = InlineKeyboardMarkup()
            confirm_keyboard.add(InlineKeyboardButton("✔️ تأكيد", callback_data="confirm_transfer"))
            bot.send_message(
                message.chat.id,
                "✅ هل ترغب بإرسال طلب التحويل للأدمن؟\n"
                f"📌 الآيدي: {to_id}\n"
                f"💰 المبلغ: {amount} ل.س",
                reply_markup=confirm_keyboard
            )

        except ValueError:
            bot.send_message(message.chat.id, "❌ البيانات اللي أرسلتها مش صحيحة. خليك على شكل `ايدي - رقم`.")

    @bot.callback_query_handler(func=lambda call: call.data == "confirm_transfer")
    def confirm_transfer_request(call):
        user_id = call.from_user.id

        if user_id not in transfer_sessions or transfer_sessions[user_id]['step'] != 'confirmed':
            bot.answer_callback_query(call.id, "❌ الطلب غير موجود.")
            return

        session = transfer_sessions[user_id]
        from_id = user_id
        to_id = session['to_id']
        amount = session['amount']

        # ✅ تخزين الطلب مؤقتًا في users.json
        save_transfer_request(from_id, to_id, amount)

        details = (
            f"💸 <b>طلب تحويل رصيد</b>\n\n"
            f"👤 من: `{from_id}`\n"
            f"👥 إلى: `{to_id}`\n"
            f"💰 المبلغ: {amount}"
        )

        confirm_keyboard = InlineKeyboardMarkup(row_width=2)
        confirm_keyboard.row(
            InlineKeyboardButton("✅ موافقة", callback_data=f"approve_transfer_{from_id}_{to_id}_{amount.replace(' ', '_')}"),
            InlineKeyboardButton("❌ رفض", callback_data=f"reject_transfer_{from_id}_{to_id}")
        )

        bot.send_message(ADMIN_ID, details, reply_markup=confirm_keyboard, parse_mode="HTML")
        bot.answer_callback_query(call.id, "🚀 تم إرسال الطلب للأدمن!")
        bot.send_message(
            user_id,
            "⏳ تم إرسال طلبك للأدمن. سيتم التواصل معك فور الموافقة.",
            parse_mode="HTML"
        )

        del transfer_sessions[user_id]
