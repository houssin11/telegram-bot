from telebot.types import Message, InlineKeyboardButton, InlineKeyboardMarkup, CallbackQuery
from config import ADMIN_ID
from utils.database import (
    load_users, save_users, generate_admin_report, block_user, unblock_user,
    update_user_balance, save_order, delete_order
)
from utils.broadcast import broadcast_message
from utils.logger import log_admin_action
import os

def register(bot):
    @bot.message_handler(commands=["admin"])
    def admin_dashboard(message: Message):
        if message.chat.id not in ADMIN_ID:
            return

        text = (
            "🧑‍💻 <b>لوحة تحكم الأدمن</b>\n\n"
            "/report → عرض تقرير الأسبوع\n"
            "/broadcast [الرسالة] → إرسال رسالة لكل العملاء\n"
            "/addbalance [id] [amount] → إضافة رصيد لمستخدم\n"
            "/block [id] → حظر مستخدم\n"
            "/unblock [id] → إلغاء حظر مستخدم"
        )
        bot.send_message(message.chat.id, text, parse_mode="HTML")

    @bot.message_handler(commands=["report"])
    def report_handler(message: Message):
        if message.chat.id not in ADMIN_ID:
            return

        bot.send_message(message.chat.id, "📊 عم نجهيز تقرير الأسبوع للأدمن...")
        report_path = generate_admin_report()
        if os.path.exists(report_path):
            with open(report_path, "rb") as file:
                bot.send_document(message.chat.id, file, caption="📈 هلق التقرير جاهز، اعرف كل شي بدري!")
        else:
            bot.send_message(message.chat.id, "❌ للأسف، ما قدرناش نجهز التقرير دلوقتي.")
        log_admin_action("Requested weekly report")

    @bot.message_handler(commands=["broadcast"])
    def broadcast_handler(message: Message):
        if message.chat.id not in ADMIN_ID:
            return

        args = message.text.split(maxsplit=1)
        if len(args) < 2:
            bot.send_message(message.chat.id, "❌ لازم تكتب الرسالة اللي بدك ترسلها.")
            return

        msg = args[1]
        bot.send_message(message.chat.id, "📢 عم نرسل الرسالة لكل العملاء...")
        broadcast_message(bot, msg)
        bot.send_message(message.chat.id, "✅ تم إرسال الرسالة بنجاح!")
        log_admin_action(f"Sent broadcast message: {msg}")

    @bot.message_handler(commands=["addbalance"])
    def add_balance_handler(message: Message):
        if message.chat.id not in ADMIN_ID:
            return

        args = message.text.split()
        if len(args) < 3:
            bot.send_message(message.chat.id, "❌ الاستخدام الصحيح:\n/addbalance [id] [amount]")
            return

        user_id = args[1]
        amount = args[2]

        try:
            amount = int(amount)
        except ValueError:
            bot.send_message(message.chat.id, "❌ المبلغ لازم يكون رقم.")
            return

        update_user_balance(user_id, amount)

        bot.send_message(message.chat.id, f"✅ تم إضافة {amount} ل.س للمستخدم `{user_id}`", parse_mode="Markdown")
        try:
            bot.send_message(int(user_id), f"🎉 تم إضافة {amount} ل.س إلى محفظتك من قبل الأدمن!")
        except Exception:
            pass
        log_admin_action(f"Added {amount} to user {user_id}")

    @bot.message_handler(commands=["block"])
    def block_user_handler(message: Message):
        if message.chat.id not in ADMIN_ID:
            return

        args = message.text.split()
        if len(args) < 2:
            bot.send_message(message.chat.id, "❌ الاستخدام الصحيح:\n/block [id]")
            return

        user_id = args[1]
        if block_user(user_id):
            bot.send_message(message.chat.id, f"🚫 تم حظر المستخدم `{user_id}` بنجاح.", parse_mode="Markdown")
            log_admin_action(f"Blocked user {user_id}")
        else:
            bot.send_message(message.chat.id, "❌ المستخدم مش موجود أو محظور من قبل.")

    @bot.message_handler(commands=["unblock"])
    def unblock_user_handler(message: Message):
        if message.chat.id not in ADMIN_ID:
            return

        args = message.text.split()
        if len(args) < 2:
            bot.send_message(message.chat.id, "❌ الاستخدام الصحيح:\n/unblock [id]")
            return

        user_id = args[1]
        if unblock_user(user_id):
            bot.send_message(message.chat.id, f"✅ تم إلغاء حظر المستخدم `{user_id}`.", parse_mode="Markdown")
            log_admin_action(f"Unblocked user {user_id}")
        else:
            bot.send_message(message.chat.id, "❌ المستخدم مش موجود أو مو محظور.")

    # ⬇️ التعامل مع أزرار موافقة أو رفض الطلبات
    @bot.callback_query_handler(func=lambda call: call.data.startswith("approve_order_") or call.data.startswith("reject_order_"))
    def handle_order_approval(call: CallbackQuery):
        data = call.data
        parts = data.split("_")

        action = parts[0]  # approve / reject
        user_id = int(parts[2])
        syp_price = int(parts[3])
        product_name = parts[4]
        player_id = parts[5]

        if action == "approve":
            update_user_balance(user_id, -syp_price)
            save_order(user_id, product_name, 0, syp_price, player_id, status="مقبول")

            bot.send_message(user_id, f"✅ تم تنفيذ طلبك لمنتج {product_name} بنجاح.\n📦 جاري تنفيذ الشحن.")
            bot.answer_callback_query(call.id, "✅ تم قبول الطلب وخصم الرصيد.")
        elif action == "reject":
            delete_order(user_id, player_id, product_name)
            bot.send_message(user_id, f"❌ نأسف، تم رفض طلبك لمنتج {product_name}.\n🚫 السبب: غير متوفر حالياً.")
            bot.answer_callback_query(call.id, "❌ تم رفض الطلب.")

