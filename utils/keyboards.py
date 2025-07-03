from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardMarkup, KeyboardButton
from config import CHANNEL_LINK

# ⬇️ كيبورد الاشتراك في القناة
def start_keyboard():
    kb = InlineKeyboardMarkup()
    kb.add(InlineKeyboardButton("✅ اشترك بالقناة", url=CHANNEL_LINK))
    return kb

# ⬇️ القائمة الرئيسية
def main_menu_keyboard():
    kb = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=False)
    kb.row(KeyboardButton("🏭️ عرض المنتجات"), KeyboardButton("💳 طرق الدفع"))
    kb.row(KeyboardButton("💻 المحفظة"), KeyboardButton("🛍️ مشترياتي"))
    kb.row(KeyboardButton("🗘️ تواصل مع الأدمن"))
    kb.row(KeyboardButton("🚀 Start"))
    return kb

# ✅ قائمة عرض المنتجات
def product_menu():
    kb = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=False)
    kb.row(KeyboardButton("🎮 شحن ألعاب"))
    kb.row(KeyboardButton("💸 تحويلات كاش"))
    kb.row(KeyboardButton("💰 تحويل رصيد سوري"))
    kb.row(KeyboardButton("🌐 دفع مزودات إنترنت"))
    kb.row(KeyboardButton("🧰 منتج قريبًا"))
    kb.row(KeyboardButton("⬅️ رجوع"), KeyboardButton("🚀 Start"))
    return kb

# ✅ قائمة داخل شحن الألعاب
def game_products_menu():
    kb = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=False)
    kb.row(KeyboardButton("🔥 شحن شدات ببجي"))
    kb.row(KeyboardButton("💎 شحن جواهر فري فاير"))
    kb.row(KeyboardButton("⬅️ رجوع"))
    return kb

# ⬇️ طرق الدفع
def payment_methods():
    kb = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=False)
    kb.row(KeyboardButton("📱 سيرياتيل كاش"), KeyboardButton("📲 MTN كاش"))
    kb.row(KeyboardButton("💳 شام كاش"), KeyboardButton("🏦 حوالة بنكية"))
    kb.row(KeyboardButton("🧑‍💻 شحن مباشر من الأدمن"))
    kb.row(KeyboardButton("💸 pay 1"), KeyboardButton("💸 pay 2"))
    kb.row(KeyboardButton("⬅️ رجوع"), KeyboardButton("🚀 Start"))
    return kb

# ⬇️ قائمة المحفظة
def wallet_menu():
    kb = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=False)
    kb.row(KeyboardButton("🛍️ مشترياتي"), KeyboardButton("📤 تحويل رصيد لعميل"))
    kb.row(KeyboardButton("📒 سجل التحويلات"))
    kb.row(KeyboardButton("⬅️ رجوع"), KeyboardButton("🚀 Start"))
    return kb

# ⬇️ كيبورد تأكيد الآيدي ✅ / 🔙
def confirm_id_keyboard():
    kb = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    kb.row(KeyboardButton("✅"), KeyboardButton("🔙"))
    return kb

# ⬇️ أزرار Inline للأدمن (موافقة / رفض)
def admin_payment_confirmation_kb():
    kb = InlineKeyboardMarkup(row_width=2)
    kb.add(
        InlineKeyboardButton("✅ موافقة", callback_data="approve_payment"),
        InlineKeyboardButton("❌ رفض", callback_data="reject_payment")
    )
    return kb

# ⬇️ كيبورد الأدمن (لوحة الأوامر)
def admin_dashboard_keyboard():
    kb = InlineKeyboardMarkup(row_width=2)
    kb.add(
        InlineKeyboardButton("📊 تقرير أسبوعي", callback_data="admin_report"),
        InlineKeyboardButton("📢 إرسال رسالة للكل", callback_data="admin_broadcast")
    )
    kb.add(
        InlineKeyboardButton("💰 إضافة رصيد", callback_data="admin_addbalance"),
        InlineKeyboardButton("🚫 حظر / فك حظر", callback_data="admin_block_unblock")
    )
    return kb

# ⬇️ كيبورد للموافقة/الرفض من الأدمن (للطلبات الفردية) - تم التعديل هنا
def admin_action_kb(user_id, payment_code):
    kb = InlineKeyboardButton("✅ موافقة", callback_data=f"approve_{user_id}_{payment_code}")
    kb2 = InlineKeyboardButton("❌ رفض", callback_data=f"reject_{user_id}_{payment_code}")

    markup = InlineKeyboardMarkup()
    markup.row(kb, kb2)
    return markup