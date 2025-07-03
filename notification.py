from config import ADMIN_CHAT_ID
from src.keyboards import admin_action_kb  # تم التعديل هنا
from logger import log_error

def notify_new_payment(bot, user_id, method, code, amount):
    """
    📤 إرسال إشعار للأدمن بطلب دفع جديد
    """
    try:
        # بناء رسالة الإشعار
        message = (
            f"📬 طلب دفع جديد\n"
            f"👤 المستخدم: {user_id}\n"
            f"💳 الطريقة: {method}\n"
            f"💰 المبلغ: {amount} ليرة\n"
            f"🔢 كود الإشعار: {code}"
        )

        # إرسال الرسالة مع كيبورد الموافقة/الرفض
        bot.send_message(
            ADMIN_CHAT_ID,
            message,
            reply_markup=admin_action_kb(user_id, code)
        )
        return True
    except Exception as e:
        # تسجيل الخطأ في حالة فشل الإرسال
        log_error(f"فشل إرسال إشعار الدفع: {str(e)}")
        return False
