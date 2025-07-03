import os
import json
import telebot
import logging

# 📁 التأكد من وجود ملف الجلسات المؤقتة
SESSIONS_FILE = "data/support_sessions.json"
os.makedirs(os.path.dirname(SESSIONS_FILE), exist_ok=True)

if not os.path.exists(SESSIONS_FILE):
    with open(SESSIONS_FILE, "w", encoding="utf-8") as f:
        json.dump({}, f)

# 🔐 استيراد توكن البوت وبيانات الأدمن والقناة
from config import BOT_TOKEN, CHANNEL_ID, BOT_USERNAME, ADMIN_ID

# 🤖 تهيئة البوت مع دعم HTML
bot = telebot.TeleBot(BOT_TOKEN, parse_mode="HTML")

# 🚫 إزالة Webhook إن وُجد
bot.remove_webhook()

# 🧪 تسجيل كل Callback Query لتتبع الأزرار الداخلية
logging.basicConfig(level=logging.INFO)

@bot.callback_query_handler(func=lambda call: True)
def log_all_callbacks(call):
    print(f"[DEBUG] 🔄 تم استقبال callback_data: {call.data}")
    if call.data.startswith("reply_"):
        print("[INFO] ✅ تم استقبال ضغطة الزر 'رد على العميل'")
        bot.answer_callback_query(call.id, "📨 جاري المعالجة...")

# 📢 رسالة ترحيب في القناة عند تشغيل البوت
try:
    from handlers.start import send_welcome
    send_welcome(bot, CHANNEL_ID)
    bot.send_message(
        CHANNEL_ID,
        f"🚨 بوتنـا عاد شغال ومستنيكم!\n"
        f"⚡️ اسرعوا بالدخول قبل ما نسد الباب:\n"
        f"🔗 <a href='https://t.me/{BOT_USERNAME}'>اضغط  هنا</a> وابدأ التسوق الآن 👌",
        parse_mode="HTML"
    )
except Exception as e:
    print(f"⚠️ حصل خطأ أثناء إرسال الرسالة للقناة: {e}")

# 🧾 تسجيل المعالجات (Handlers)
from handlers import (
    start, welcome, products, payment, wallet, transfer, history,
    support, admin_report, admin_panel, admin_broadcast, callback_handler, buy
)

start.register(bot)
welcome.register(bot)
products.register(bot)
payment.register(bot)
wallet.register(bot)
transfer.register(bot)
history.register(bot)
support.register(bot)
admin_report.register(bot)
admin_panel.register(bot)
admin_broadcast.register(bot)
callback_handler.register(bot)
buy.register(bot)  # ✅ تسجيل قسم الشراء الجديد (ببجي + فري فاير)

# ================================
# 🧾 تسجيل المعالجات الجديدة
# ================================

# 🔔 استيراد معالج إشعارات الدفع وقرارات الأدمن
import notification  # لتسجيل إشعارات الدفع
import admin_handlers  # لمعالجة قرارات الأدمن (موافقة/رفض)

# ================================
# 🚀 تشغيل البوت
# ================================
print("✅ البوت شغال كمان زي الفل يا بيك!")
print("✨ اختبره بالضغط على /start")
bot.infinity_polling()