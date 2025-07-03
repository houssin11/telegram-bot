from logger import log_error

def broadcast_message(bot, user_ids, text):
    """📢 إرسال رسالة جماعية لجميع المستخدمين"""
    for uid in user_ids:
        try:
            bot.send_message(uid, text)
        except Exception as e:
            error_msg = f"فشل الإرسال إلى {uid}: {str(e)}"
            log_error(error_msg)  # ❗ تسجيل الخطأ في ملف الأخطاء