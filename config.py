# config.py
# 🔐 توكن البوت الخاص بك من BotFather
BOT_TOKEN = '7936418161:AAHY1OM3g898oJFqq1KuL16wNJ4FEH0DUHA'

# 👤 معرفات الأدمن (قائمة)
ADMIN_ID = [
    6935846121  # ← @Houssin363
]

# معرف الأدمن الرئيسي (مطلوب للإشعارات)
ADMIN_CHAT_ID = ADMIN_ID[0]  # ⬅️ اختيار أول أدمن في القائمة

# 📢 بيانات القناة المرتبطة بالبوت
CHANNEL_USERNAME = 'shop100sho'  # ← بدون @
CHANNEL_LINK = 'https://t.me/shop100sho'  # ← بدون مسافة زائدة
CHANNEL_ID = -1002852510917  # ← آيدي القناة الحقيقي بصيغة -100...

# 🤖 اسم المستخدم الرسمي للبوت
BOT_USERNAME = 'my_fast_shop_bot'  # ← بدون @

# 🚧 حالة تشغيل البوت
BOT_ACTIVE = True  # ← غيّر إلى False لإيقاف البوت مؤقتًا برسالة "البوت تحت الصيانة"

# 💵 أسعار صرف الدولار حسب الشرائح
USD_RATE_1 = 12500  # ≤ 10$
USD_RATE_2 = 11300  # > 10$ و ≤ 20$
USD_RATE_3 = 10700  # > 20$