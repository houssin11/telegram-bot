import os
import json
from datetime import datetime
from config import USD_RATE_1, USD_RATE_2, USD_RATE_3, ADMIN_CHAT_ID
from notification import notify_new_payment  # استيراد الدالة الجديدة
from logger import log_error  # استيراد تسجيل الأخطاء

# 🔧 مسارات البيانات
USER_DATA_PATH = "data/users.json"
ORDERS_PATH = "data/orders.json"
REPORT_PATH = "data/reports/report.txt"
TRANSFERS_PATH = "data/transfers.json"

# ✅ تحميل بيانات المستخدمين
def load_users():
    if os.path.exists(USER_DATA_PATH):
        with open(USER_DATA_PATH, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}

# ✅ حفظ بيانات المستخدمين بعد أي تعديل
def save_users(data):
    os.makedirs(os.path.dirname(USER_DATA_PATH), exist_ok=True)
    with open(USER_DATA_PATH, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

# ✅ معرفة رصيد المستخدم
def get_user_balance(user_id):
    data = load_users()
    return float(data.get(str(user_id), {}).get("balance", 0))

# ✅ تحديث رصيد المستخدم
def update_user_balance(user_id, amount):
    data = load_users()
    user_id_str = str(user_id)

    if user_id_str not in data:
        data[user_id_str] = {
            "balance": 0,
            "pending_payments": {},
            "history": [],
            "blocked": False
        }

    data[user_id_str]["balance"] = float(data[user_id_str].get("balance", 0)) + float(amount)
    save_users(data)

# ✅ التحقق من الاشتراك في القناة
def is_user_subscribed(bot, user_id, channel_username):
    try:
        status = bot.get_chat_member(f"@{channel_username}", user_id).status
        return status in ["member", "administrator", "creator"]
    except Exception as e:
        log_error(f"خطأ في التحقق من الاشتراك: {str(e)}")
        return False

# ✅ تحميل سجل الطلبات للمستخدم
def get_user_orders(user_id):
    if not os.path.exists(ORDERS_PATH):
        return []
    try:
        with open(ORDERS_PATH, "r", encoding="utf-8") as f:
            data = json.load(f)
        return data.get(str(user_id), [])
    except Exception as e:
        log_error(f"خطأ في تحميل الطلبات: {str(e)}")
        return []

# ✅ إنشاء تقرير أسبوعي للأدمن
def generate_admin_report():
    report = []
    total_balance = 0
    total_orders = 0
    total_deductions = 0
    total_delivered = 0

    try:
        users = load_users()
        for user in users.values():
            total_balance += float(user.get("balance", 0))

        if os.path.exists(ORDERS_PATH):
            with open(ORDERS_PATH, "r", encoding="utf-8") as f:
                orders = json.load(f)
                for user_orders in orders.values():
                    for order in user_orders:
                        total_orders += 1
                        total_deductions += float(order.get("price", 0))
                        if order.get("status") == "مقبول":
                            total_delivered += 1

        report.append(f"📆 تقرير بتاريخ: {datetime.now().strftime('%Y-%m-%d %H:%M')}")
        report.append(f"👥 إجمالي رصيد العملاء: {total_balance:.2f} ل.س")
        report.append(f"🛒 عدد المشتريات: {total_orders}")
        report.append(f"💸 إجمالي المبالغ المخصومة: {total_deductions:.2f} ل.س")
        report.append(f"🚚 إجمالي الشحنات المنفذة: {total_delivered}")

        os.makedirs(os.path.dirname(REPORT_PATH), exist_ok=True)
        with open(REPORT_PATH, "w", encoding="utf-8") as f:
            f.write("\n".join(report))

        return REPORT_PATH
    except Exception as e:
        log_error(f"خطأ في إنشاء التقرير: {str(e)}")
        return None

# ✅ التحقق من رقم الإشعار
def check_invoice(invoice_number):
    users = load_users()
    for user_id, user_data in users.items():
        if invoice_number in user_data.get("payments", {}):
            return True
    return False

# ✅ حفظ طلب جديد مؤقتًا (قبل موافقة الأدمن)
def save_payment_request(user_id, method, code, amount, bot=None):
    try:
        data = load_users()
        user_id_str = str(user_id)

        if user_id_str not in data:
            data[user_id_str] = {
                "balance": 0,
                "pending_payments": {},
                "history": [],
                "blocked": False
            }

        data[user_id_str]["pending_payments"][code] = {
            "method": method,
            "amount": amount,
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M")
        }

        save_users(data)

        # إرسال إشعار للأدمن إذا تم تمرير bot
        if bot:
            notify_new_payment(bot, user_id, method, code, amount)

        return True
    except Exception as e:
        log_error(f"خطأ في حفظ طلب الدفع: {str(e)}")
        return False

# ✅ قبول الطلب (تحويل الرصيد للمستخدم)
def approve_payment_request(user_id, code=None):
    try:
        data = load_users()
        user_id_str = str(user_id)

        if user_id_str not in data or "pending_payments" not in data[user_id_str]:
            return False

        if code is None:
            pending = data[user_id_str]["pending_payments"]
            if not pending:
                return False
            code = next(iter(pending.keys()))

        if code in data[user_id_str]["pending_payments"]:
            payment_info = data[user_id_str]["pending_payments"][code]
            amount = float(payment_info["amount"].replace(" ل.س", ""))
            now = datetime.now().strftime("%Y-%m-%d %H:%M")

            data[user_id_str]["balance"] = float(data[user_id_str].get("balance", 0)) + amount
            data[user_id_str].setdefault("history", []).append({
                "type": "deposit",
                "amount": f"{amount} ل.س",
                "method": payment_info["method"],
                "code": code,
                "time": now,
                "status": "مقبول"
            })

            del data[user_id_str]["pending_payments"][code]
            save_users(data)
            return True
        return False
    except Exception as e:
        log_error(f"خطأ في قبول الدفع: {str(e)}")
        return False

# ✅ رفض الطلب مع سبب
def reject_payment_request(user_id, code=None, reason="لم يتم ذكر سبب"):
    try:
        data = load_users()
        user_id_str = str(user_id)

        if user_id_str not in data or "pending_payments" not in data[user_id_str]:
            return False

        if code is None:
            pending = data[user_id_str]["pending_payments"]
            if not pending:
                return False
            code = next(iter(pending.keys()))

        if code in data[user_id_str]["pending_payments"]:
            payment_info = data[user_id_str]["pending_payments"][code]
            now = datetime.now().strftime("%Y-%m-%d %H:%M")

            data[user_id_str].setdefault("history", []).append({
                "type": "rejection",
                "amount": payment_info["amount"],
                "method": payment_info["method"],
                "code": code,
                "time": now,
                "status": "مرفوض",
                "reason": reason
            })

            del data[user_id_str]["pending_payments"][code]
            save_users(data)
            return True
        return False
    except Exception as e:
        log_error(f"خطأ في رفض الدفع: {str(e)}")
        return False

# ✅ حساب السعر بالليرة حسب الدولار
def calculate_price_syp(dollar_amount):
    try:
        if dollar_amount <= 10:
            return dollar_amount * USD_RATE_1
        elif dollar_amount <= 20:
            return dollar_amount * USD_RATE_2
        else:
            return dollar_amount * USD_RATE_3
    except Exception as e:
        log_error(f"خطأ في حساب السعر: {str(e)}")
        return 0

# ✅ توليد رقم عملية فريد
def generate_order_id(user_id):
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    return f"{user_id}_{timestamp}"

# ✅ حفظ عملية شراء
def save_order(user_id, product_name, dollar_price, syp_price, player_id, status="قيد الانتظار"):
    try:
        os.makedirs(os.path.dirname(ORDERS_PATH), exist_ok=True)

        orders = {}
        if os.path.exists(ORDERS_PATH):
            with open(ORDERS_PATH, "r", encoding="utf-8") as f:
                orders = json.load(f)

        order = {
            "product": product_name,
            "price_usd": dollar_price,
            "price": syp_price,
            "player_id": player_id,
            "status": status,
            "time": datetime.now().strftime("%Y-%m-%d %H:%M")
        }

        user_orders = orders.get(str(user_id), [])
        user_orders.append(order)
        orders[str(user_id)] = user_orders

        with open(ORDERS_PATH, "w", encoding="utf-8") as f:
            json.dump(orders, f, ensure_ascii=False, indent=2)

        return True
    except Exception as e:
        log_error(f"خطأ في حفظ الطلب: {str(e)}")
        return False

# ✅ حذف الطلب من سجل الطلبات (عند الرفض)
def delete_order(user_id, player_id, product_name):
    try:
        if not os.path.exists(ORDERS_PATH):
            return False

        with open(ORDERS_PATH, "r", encoding="utf-8") as f:
            orders = json.load(f)

        order_list = orders.get(str(user_id), [])
        orders[str(user_id)] = [
            order for order in order_list
            if order["player_id"] != player_id or order["product"] != product_name
        ]

        with open(ORDERS_PATH, "w", encoding="utf-8") as f:
            json.dump(orders, f, ensure_ascii=False, indent=2)

        return True
    except Exception as e:
        log_error(f"خطأ في حذف الطلب: {str(e)}")
        return False

# ✅ لإبقاء التوافق مع باقي أجزاء البوت
def add_balance(user_id, amount):
    update_user_balance(user_id, amount)

# ✅ التحقق إن كان المستخدم محظور
def is_blocked(user_id):
    data = load_users()
    user = data.get(str(user_id), {})
    return user.get("blocked", False)

# ✅ حفظ طلب تحويل رصيد
def save_transfer_request(from_id, to_id, amount):
    try:
        now = datetime.now().strftime("%Y-%m-%d %H:%M")

        if not os.path.exists(TRANSFERS_PATH):
            transfers = []
        else:
            with open(TRANSFERS_PATH, "r", encoding="utf-8") as f:
                transfers = json.load(f)

        transfers.append({
            "from": str(from_id),
            "to": str(to_id),
            "amount": amount,
            "time": now
        })

        os.makedirs(os.path.dirname(TRANSFERS_PATH), exist_ok=True)
        with open(TRANSFERS_PATH, "w", encoding="utf-8") as f:
            json.dump(transfers, f, ensure_ascii=False, indent=2)

        return True
    except Exception as e:
        log_error(f"خطأ في حفظ التحويل: {str(e)}")
        return False

# ✅ حظر مستخدم
def block_user(user_id):
    try:
        data = load_users()
        user_id_str = str(user_id)

        if user_id_str not in data:
            data[user_id_str] = {
                "balance": 0,
                "pending_payments": {},
                "history": [],
                "blocked": True
            }
        else:
            data[user_id_str]["blocked"] = True

        save_users(data)
        return True
    except Exception as e:
        log_error(f"خطأ في حظر المستخدم: {str(e)}")
        return False

# ✅ إلغاء الحظر
def unblock_user(user_id):
    try:
        data = load_users()
        user_id_str = str(user_id)

        if user_id_str in data:
            data[user_id_str]["blocked"] = False
            save_users(data)
            return True
        return False
    except Exception as e:
        log_error(f"خطأ في إلغاء حظر المستخدم: {str(e)}")
        return False