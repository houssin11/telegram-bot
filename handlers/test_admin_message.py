import telebot

# 🟢 تأكد أن التوكن هو نفس توكن بوتك Fire_fast_bot
BOT_TOKEN = '7810634186:AAFWXuXVX0ALuWyk3URf0JsGQSxFCNUqIgM'
bot = telebot.TeleBot(BOT_TOKEN)

# 🔵 هذا هو آيديك الشخصي
ADMIN_ID = 6935846121

# 📨 أرسل رسالة خاصة لك كأدمن
bot.send_message(ADMIN_ID, "📩 هذا اختبار مباشر: هل وصلتني الرسالة لحسابي الشخصي؟")

print("✅ تم الإرسال!")
