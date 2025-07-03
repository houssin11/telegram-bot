from telebot.types import CallbackQuery, Message
from utils.database import approve_payment_request, reject_payment_request, is_blocked
from config import ADMIN_ID

def register(bot):
    @bot.callback_query_handler(func=lambda call: call.data.startswith("approve_"))
    def handle_approve_payment(call: CallbackQuery):
        try:
            _, user_id_str = call.data.split("_", 1)
            user_id = int(user_id_str)

            if is_blocked(user_id):
                bot.answer_callback_query(call.id, "\ud83d\udeab العميل محظور، لا يمكن تنفيذ العملية.")
                bot.send_message(ADMIN_ID, f"\ud83d\udeab العميل {user_id} محظور.")
                return

            if approve_payment_request(user_id, invoice=None):
                bot.answer_callback_query(call.id, "\u2705 تم قبول الطلب!")
                bot.send_message(
                    user_id,
                    "\ud83c\udf89 تم قبول طلبك!\n"
                    "\ud83d\udcb0 تم إضافة المبلغ إلى محفظتك.\n"
                    "\ud83e\udeaa شكرًا لثقتكم بنا \u2764\ufe0f",
                    parse_mode="HTML"
                )
                bot.send_message(
                    ADMIN_ID,
                    f"\ud83e\uddd1\u200d\ud83d\udcbb الأدمن وافق على طلب العميل <code>{user_id}</code>.",
                    parse_mode="HTML"
                )
            else:
                bot.answer_callback_query(call.id, "\u274c الطلب غير موجود أو قد تم التعامل معه.")

        except Exception as e:
            bot.answer_callback_query(call.id, "\u274c حصل خطأ أثناء المعالجة.")
            print(f"[ERROR] Approval failed: {e}")

    @bot.callback_query_handler(func=lambda call: call.data.startswith("reject_"))
    def handle_reject_payment(call: CallbackQuery):
        try:
            _, user_id_str = call.data.split("_", 1)
            user_id = int(user_id_str)

            if is_blocked(user_id):
                bot.answer_callback_query(call.id, "\ud83d\udeab العميل محظور.")
                bot.send_message(ADMIN_ID, f"\ud83d\udeab العميل {user_id} محظور.")
                return

            if reject_payment_request(user_id, invoice=None):
                bot.answer_callback_query(call.id, "\u274c تم رفض الطلب!")

                bot.send_message(
                    user_id,
                    "\u274c تم رفض طلبك.\n"
                    "\ud83d\udee0\ufe0f يرجى التأكد من صحة البيانات وإعادة المحاولة.",
                    parse_mode="HTML"
                )

                bot.send_message(
                    ADMIN_ID,
                    f"\ud83e\uddd1\u200d\ud83d\udcbb الأدمن رفض طلب العميل <code>{user_id}</code>.",
                    parse_mode="HTML"
                )
            else:
                bot.answer_callback_query(call.id, "\u274c الطلب غير موجود أو قد تم التعامل معه.")

        except Exception as e:
            bot.answer_callback_query(call.id, "\u274c حصل خطأ أثناء المعالجة.")
            print(f"[ERROR] Rejection failed: {e}")

    @bot.callback_query_handler(func=lambda call: call.data.startswith("approve_transfer_"))
    def handle_approve_transfer(call: CallbackQuery):
        try:
            _, from_id_str, to_id_str, amount_str = call.data.split("_", 3)
            from_id = int(from_id_str)
            to_id = int(to_id_str)
            amount = float(amount_str)

            if is_blocked(from_id) or is_blocked(to_id):
                bot.answer_callback_query(call.id, "\ud83d\udeab أحد العملاء محظور.")
                bot.send_message(ADMIN_ID, "\ud83d\udeab لا يمكن تنفيذ التحويل مع مستخدم محظور.")
                return

            if not approve_payment_request(from_id, invoice=amount) or not approve_payment_request(to_id, invoice=amount):
                bot.answer_callback_query(call.id, "\u274c خطأ في تنفيذ التحويل.")
                return

            bot.answer_callback_query(call.id, "\ud83d\udcb8 تم تنفيذ التحويل بنجاح!")

            bot.send_message(
                from_id,
                f"\u2705 تم تحويل {amount} ل.س إلى العميل `{to_id}`.",
                parse_mode="Markdown"
            )
            bot.send_message(
                to_id,
                f"\ud83d\udcc5 تم استلام {amount} ل.س من العميل `{from_id}`.",
                parse_mode="Markdown"
            )

            bot.send_message(
                ADMIN_ID,
                f"\ud83e\uddd1\u200d\ud83d\udcbb الأدمن وافق على تحويل:\n"
                f"\ud83d\udcc4 من: {from_id}\n"
                f"\ud83d\udcc5 إلى: {to_id}\n"
                f"\ud83d\udcb0 المبلغ: {amount} ل.س",
                parse_mode="HTML"
            )

        except Exception as e:
            bot.answer_callback_query(call.id, "\u274c حصل خطأ أثناء معالجة التحويل.")
            print(f"[ERROR] Transfer approval failed: {e}")

    @bot.callback_query_handler(func=lambda call: call.data.startswith("reject_transfer_"))
    def handle_reject_transfer(call: CallbackQuery):
        try:
            _, from_id_str, to_id_str = call.data.split("_", 2)
            from_id = int(from_id_str)
            to_id = int(to_id_str)

            if is_blocked(from_id) or is_blocked(to_id):
                bot.answer_callback_query(call.id, "\ud83d\udeab أحد العملاء محظور.")
                bot.send_message(ADMIN_ID, "\ud83d\udeab لا يمكن تنفيذ التحويل مع مستخدم محظور.")
                return

            bot.answer_callback_query(call.id, "\u274c تم رفض التحويل!")

            bot.send_message(
                from_id,
                "\ud83d\udeab تم رفض طلب التحويل.",
                parse_mode="HTML"
            )
            bot.send_message(
                to_id,
                "\ud83d\udeab تم رفض التحويل لكسب السبب.",
                parse_mode="HTML"
            )

            bot.send_message(
                ADMIN_ID,
                f"\ud83e\uddd1\u200d\ud83d\udcbb الأدمن رفض تحويل:\n"
                f"\ud83d\udcc4 من: {from_id}\n"
                f"\ud83d\udcc5 إلى: {to_id}",
                parse_mode="HTML"
            )

        except Exception as e:
            bot.answer_callback_query(call.id, "\u274c حصل خطأ أثناء معالجة التحويل.")
            print(f"[ERROR] Transfer rejection failed: {e}")
