from telebot import types
from utils.database import is_user_subscribed, save_payment_request, add_balance
from config import CHANNEL_USERNAME, ADMIN_ID
from utils.keyboards import payment_methods
import uuid  # لإنشاء معرّف فريد لكل طلب

# ⬇️ تخزين الجلسة المؤقتة لكل عميل
payment_sessions = {}

def register(bot):
    @bot.message_handler(func=lambda m: m.text == "💳 طرق الدفع")
    def show_payment_methods(message: types.Message):
        if not is_user_subscribed(bot, message.from_user.id, CHANNEL_USERNAME):
            bot.send_message(
                message.chat.id,
                "⚠️ عذرًا يا نجم، ما تشترك بقناة البوت حتى الآن.\n"
                f"📢 اشترك أول ورجع تلعب معنا 👌",
                parse_mode="HTML"
            )
            return
        bot.send_message(
            message.chat.id,
            "💸 اختار طريقة الدفع اللي تناسبك، وخلينا نساعدك بعدين 💼\n"
            "كل شي واضح ومباشر، مو عندا وقت نضيعه 😎👇",
            reply_markup=payment_methods(),
            parse_mode="HTML"
        )

    # 📱 سيرياتيل كاش
    @bot.message_handler(func=lambda m: m.text == "📱 سيرياتيل كاش")
    def seriatel_cash(message: types.Message):
        bot.send_message(
            message.chat.id,
            "🔄 حول المبلغ على أحد الأرقام التالية وانسخ الرقم اللي بدك تحوّل عليه:\n\n"
            "0932164415\n"
            "093333\n"
            "0900000\n\n"
            "📸 بعد التحويل، ابعت صورة الإشعار.",
            parse_mode="HTML"
        )
        payment_sessions[message.from_user.id] = {
            'method': 'seriatel_cash',
            'step': 'waiting_for_image'
        }

    # 📲 MTN كاش
    @bot.message_handler(func=lambda m: m.text == "📲 MTN كاش")
    def mtn_cash(message: types.Message):
        bot.send_message(
            message.chat.id,
            "🔄 حول المبلغ على أحد الأرقام التالية وانسخ الرقم اللي بدك تحوّل عليه:\n\n"
            "0932164415\n"
            "093333\n"
            "0900000\n\n"
            "📸 بعد التحويل، ابعت صورة الإشعار.",
            parse_mode="HTML"
        )
        payment_sessions[message.from_user.id] = {
            'method': 'mtn_cash',
            'step': 'waiting_for_image'
        }

    # 💳 شام كاش
    @bot.message_handler(func=lambda m: m.text == "💳 شام كاش")
    def sham_cash(message: types.Message):
        bot.send_message(
            message.chat.id,
            "🔄 حول المبلغ إلى الكود التالي وانسخه:\n\n"
            "578344c08da57a5b0ce8c2b915614d2b\n\n"
            "📸 بعد التحويل، ابعت صورة الإشعار.",
            parse_mode="HTML"
        )
        payment_sessions[message.from_user.id] = {
            'method': 'sham_cash',
            'step': 'waiting_for_image'
        }

    # 🧑‍💻 شحن مباشر من الأدمن
    @bot.message_handler(func=lambda m: m.text == "🧑‍💻 شحن مباشر من الأدمن")
    def admin_charge(message: types.Message):
        bot.send_message(
            message.chat.id,
            "📜 اكتب المبلغ اللي بدك تشحنو للمحفظة.\n"
            "✅ سيتم الموافقة أو الرفض من الأدمن مباشرة.",
            parse_mode="HTML"
        )
        payment_sessions[message.from_user.id] = {
            'method': 'admin_charge',
            'step': 'waiting_for_amount'
        }

    # 📸 استقبال صورة الإشعار
    @bot.message_handler(content_types=['photo'])
    def receive_image(message: types.Message):
        user_id = message.from_user.id
        if user_id in payment_sessions and payment_sessions[user_id]['step'] == 'waiting_for_image':
            try:
                photo_id = message.photo[-1].file_id
                payment_sessions[user_id]['payment_image'] = photo_id
                payment_sessions[user_id]['step'] = 'waiting_for_code'
                bot.send_message(message.chat.id, "📸 الصورة تم حفظها!\n🔢 تمام، دلوقتي ابعت رقم الإشعار.")
            except Exception as e:
                bot.send_message(message.chat.id, "❌ حصل خطأ أثناء استقبال الصورة. جرب مرة أخرى.")
        else:
            bot.send_message(message.chat.id, "❌ خطأ في الخطوات. ابدأ من جديد.")

    # 🔤 استقبال الكود
    @bot.message_handler(func=lambda m: m.content_type != 'photo' and m.from_user.id in payment_sessions and payment_sessions[m.from_user.id]['step'] == 'waiting_for_code')
    def receive_code(message: types.Message):
        user_id = message.from_user.id
        code = message.text.strip()
        if not code:
            bot.send_message(message.chat.id, "❌ الكود مش فاضي. رجاءً ادخل الكود الصحيح.")
            return
        payment_sessions[user_id]['code'] = code
        payment_sessions[user_id]['step'] = 'waiting_for_amount'
        bot.send_message(message.chat.id, "🔢 الكود تم حفظه!\n💰 تمام، دلوقتي ابعت المبلغ اللي قمت بتحويله.")

    # 💰 استقبال المبلغ
    @bot.message_handler(func=lambda m: m.content_type != 'photo' and m.from_user.id in payment_sessions and payment_sessions[m.from_user.id]['step'] == 'waiting_for_amount')
    def receive_amount(message: types.Message):
        user_id = message.from_user.id
        amount_text = message.text.strip()
        if amount_text.replace('.', '', 1).isdigit():
            amount = float(amount_text)
            payment_sessions[user_id]['amount'] = amount
            payment_sessions[user_id]['step'] = 'confirmed'
            method = payment_sessions.get(user_id, {}).get('method', 'غير موجود')
            code = payment_sessions.get(user_id, {}).get('code', 'غير موجود')
            confirm_kb = types.InlineKeyboardMarkup()
            confirm_kb.add(types.InlineKeyboardButton("✔️ تأكيد العملية", callback_data="confirm_payment"))
            bot.send_message(
                message.chat.id,
                f"📌 الكود: {code}\n"
                f"💰 المبلغ: {amount:.2f} ل.س\n\n"
                "✅ هل ترغب بإرسال الطلب للأدمن؟",
                reply_markup=confirm_kb
            )
        else:
            bot.send_message(message.chat.id, "❌ المبلغ لازم يكون رقم صحيح.")
            bot.send_message(message.chat.id, "🔄 أرسل المبلغ مرة أخرى.")

    # ✔️ تأكيد العملية وإرسال البيانات للأدمن
    @bot.callback_query_handler(func=lambda call: call.data == "confirm_payment")
    def confirm_payment(call: types.CallbackQuery):
        try:
            user_id = call.from_user.id
            if user_id in payment_sessions and payment_sessions[user_id]['step'] == 'confirmed':
                request_id = str(uuid.uuid4())  # ← معرّف فريد للطلب
                payment_sessions[user_id]['request_id'] = request_id
                method = payment_sessions[user_id].get('method', 'غير معروف')
                code = payment_sessions[user_id].get('code', 'غير موجود')
                amount = payment_sessions[user_id].get('amount', 0)
                username = f"@{call.from_user.username}" if call.from_user.username else "بدون اسم"
                details = (
                    f"👤 العميل: {username} (ID: {user_id})\n"
                    f"💳 الطريقة: {method}\n"
                    f"🔢 الكود: {code}\n"
                    f"💰 المبلغ: {amount:.2f} ل.س\n"
                    f"📌 معرف الطلب: {request_id}"
                )
                confirm_kb = types.InlineKeyboardMarkup(row_width=2)
                confirm_kb.row(
                    types.InlineKeyboardButton("✅ موافقة", callback_data=f"approve_{user_id}_{request_id}"),
                    types.InlineKeyboardButton("❌ رفض", callback_data=f"reject_{user_id}_{request_id}")
                )
                photo_id = payment_sessions[user_id].get('payment_image')
                for admin in ADMIN_ID:
                    if photo_id:
                        bot.send_photo(admin, photo_id, caption=details, reply_markup=confirm_kb, parse_mode="HTML")
                    else:
                        bot.send_message(admin, details, reply_markup=confirm_kb, parse_mode="HTML")
                bot.answer_callback_query(call.id, "🚀 الطلب جاهز للأدمن!")
                bot.send_message(user_id, "⏳ تم إرسال الطلب للأدمن. سيتم التواصل معك قريبًا.")
            else:
                bot.answer_callback_query(call.id, "❌ الجلسة مش موجودة أو البيانات ناقصة.")
                bot.send_message(user_id, "🚫 بيانات الطلب غير مكتملة. خليك مرتب وابدأ من جديد.")
        except Exception as e:
            bot.send_message(call.message.chat.id, f"🛠️ حصل خطأ تقني. جرب مرة أخرى.\nالخطأ: {e}")
            print(f"[ERROR] confirm_payment: {e}")

    # ✅ موافقة الأدمن
    @bot.callback_query_handler(func=lambda call: call.data.startswith("approve_"))
    def approve_payment(call: types.CallbackQuery):
        try:
            _, user_id_str, request_id = call.data.split("_")
            user_id = int(user_id_str)
            if user_id in payment_sessions and payment_sessions[user_id].get('request_id') == request_id:
                amount = payment_sessions[user_id]['amount']
                add_balance(user_id, amount)
                approved_by = f"@{call.from_user.username}" if call.from_user.username else call.from_user.first_name
                msg_text = f"✅ الطلب #{request_id} تمت الموافقة عليه بواسطة {approved_by}"
                for admin in ADMIN_ID:
                    if admin == call.from_user.id:
                        bot.edit_message_reply_markup(chat_id=admin, message_id=call.message.message_id, reply_markup=None)
                        bot.send_message(admin, f"✅ تم الموافقة على الطلب #{request_id}")
                    else:
                        bot.edit_message_reply_markup(chat_id=admin, message_id=call.message.message_id, reply_markup=None)
                        bot.send_message(admin, msg_text)
                bot.answer_callback_query(call.id, "✅ تم الموافقة!")
                bot.send_message(user_id, f"🎉 تم قبول طلبك!\n💰 تم إضافة {amount:.2f} ل.س إلى محفظتك.")
                del payment_sessions[user_id]
            else:
                bot.answer_callback_query(call.id, "⚠️ هذا الطلب تم التعامل معه بالفعل.")
        except Exception as e:
            bot.answer_callback_query(call.id, "❌ حصل خطأ أثناء المعالجة.")
            print(f"[ERROR] approve_payment: {e}")

    # ❌ رفض الأدمن
    @bot.callback_query_handler(func=lambda call: call.data.startswith("reject_"))
    def reject_payment(call: types.CallbackQuery):
        try:
            _, user_id_str, request_id = call.data.split("_")
            user_id = int(user_id_str)
            if user_id in payment_sessions and payment_sessions[user_id].get('request_id') == request_id:
                rejected_by = f"@{call.from_user.username}" if call.from_user.username else call.from_user.first_name
                reason = "الصور غير واضحة"
                msg_text = f"❌ الطلب #{request_id} تم رفضه بواسطة {rejected_by}\n📝 السبب: {reason}"
                for admin in ADMIN_ID:
                    if admin == call.from_user.id:
                        bot.edit_message_reply_markup(chat_id=admin, message_id=call.message.message_id, reply_markup=None)
                        bot.send_message(admin, f"❌ تم رفض الطلب #{request_id}")
                    else:
                        bot.edit_message_reply_markup(chat_id=admin, message_id=call.message.message_id, reply_markup=None)
                        bot.send_message(admin, msg_text)
                bot.answer_callback_query(call.id, "❌ تم الرفض!")
                bot.send_message(user_id, f"❌ تم رفض طلبك.\n🛠️ السبب: {reason}")
                del payment_sessions[user_id]
            else:
                bot.answer_callback_query(call.id, "⚠️ هذا الطلب تم التعامل معه بالفعل.")
        except Exception as e:
            bot.answer_callback_query(call.id, "❌ حصل خطأ أثناء المعالجة.")
            print(f"[ERROR] reject_payment: {e}")