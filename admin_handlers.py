from telebot.types import CallbackQuery
from database import approve_payment_request, reject_payment_request
from logger import log_admin_action, log_error
from config import bot  # تأكد من أن bot معرف في config أو main

@bot.callback_query_handler(func=lambda call: call.data.startswith(('approve_', 'reject_')))
def handle_admin_decision(call: CallbackQuery):
    """
    🛠️ معالجة قرار الأدمن (قبول/رفض طلب الدفع)
    """
    try:
        # تجزئة بيانات الـ callback
        data_parts = call.data.split('_')
        action = data_parts[0]  # 'approve' أو 'reject'
        user_id = int(data_parts[1])  # معرف المستخدم
        payment_code = data_parts[2]  # كود الدفع

        if action == "approve":
            # قبول طلب الدفع
            if approve_payment_request(user_id, payment_code):
                # إرسال تأكيد للأدمن
                bot.answer_callback_query(call.id, "تم قبول الطلب ✅")
                log_admin_action(f"تمت الموافقة على طلب الدفع {payment_code} للمستخدم {user_id}")
            else:
                bot.answer_callback_query(call.id, "❌ فشل: الطلب غير موجود")

        elif action == "reject":
            # رفض طلب الدفع
            if reject_payment_request(user_id, payment_code, "رفض من الأدمن"):
                bot.answer_callback_query(call.id, "تم رفض الطلب ❌")
                log_admin_action(f"تم رفض طلب الدفع {payment_code} للمستخدم {user_id}")
            else:
                bot.answer_callback_query(call.id, "❌ فشل: الطلب غير موجود")

    except Exception as e:
        # تسجيل أي أخطاء تحدث أثناء المعالجة
        log_error(f"خطأ في معالجة قرار الأدمن: {str(e)}")
        bot.answer_callback_query(call.id, "❌ حدث خطأ أثناء المعالجة")