# support.py
import json
import os
from telebot import types
from utils.database import is_user_subscribed, is_blocked
from config import CHANNEL_USERNAME, CHANNEL_LINK, ADMIN_ID, BOT_ACTIVE

SUPPORT_SESSIONS_FILE = "data/support_sessions.json"
os.makedirs(os.path.dirname(SUPPORT_SESSIONS_FILE), exist_ok=True)

def load_support_sessions():
    if os.path.exists(SUPPORT_SESSIONS_FILE):
        with open(SUPPORT_SESSIONS_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}

def save_support_sessions(sessions):
    with open(SUPPORT_SESSIONS_FILE, "w", encoding="utf-8") as f:
        json.dump(sessions, f, ensure_ascii=False, indent=2)

support_sessions = load_support_sessions()

def register(bot):
    @bot.message_handler(func=lambda m: m.text == "🗘️ تواصل مع الأدمن")
    def support_handler(message: types.Message):
        if not BOT_ACTIVE:
            bot.send_message(message.chat.id, "🚧 البوت تحت الصيانة مؤقتًا، حاول لاحقًا.")
            return

        if not is_user_subscribed(bot, message.from_user.id, CHANNEL_USERNAME) or is_blocked(message.from_user.id):
            bot.send_message(
                message.chat.id,
                "⚠️ عذرًا يا نجم، ما تشترك بالقناة أو حسابك محظور.\n"
                f"📢 <a href='{CHANNEL_LINK}'>اشترك أول</a> ورجع تتواصل مع الأدمن 👌",
                parse_mode="HTML"
            )
            return

        user_id = str(message.from_user.id)
        support_sessions[user_id] = {'step': 'waiting_for_message'}
        save_support_sessions(support_sessions)

        bot.send_message(
            message.chat.id,
            "📬 تمام، اكتب الرسالة اللي بدك تحولها للأدمن، ولا تضيع وقتنا 😎👇",
            parse_mode="HTML"
        )

    @bot.message_handler(func=lambda m: str(m.from_user.id) in support_sessions and support_sessions[str(m.from_user.id)]['step'] == 'waiting_for_message')
    def receive_support_message(message: types.Message):
        user_id = str(message.from_user.id)
        user_text = message.text.strip()

        if user_text.lower() == "الغاء":
            del support_sessions[user_id]
            save_support_sessions(support_sessions)
            bot.send_message(message.chat.id, "🚫 تم إلغاء جلسة الدعم الفني.")
            return

        user = message.from_user
        username = f"@{user.username}" if user.username else f"{user.first_name or ''} {user.last_name or ''}".strip()

        caption = (
            f"📬 رسالة جديدة من العميل:\n\n"
            f"👤 الاسم: {username or 'غير معروف'}\n"
            f"🆔 الآيدي: {user_id}\n"
            f"📝 الرسالة: {user_text}"
        )

        keyboard = types.InlineKeyboardMarkup()
        keyboard.add(types.InlineKeyboardButton("📞 رد على العميل", callback_data=f"reply_{user_id}"))

        try:
            bot.send_message(ADMIN_ID, caption, reply_markup=keyboard, parse_mode="HTML")
            bot.send_message(user_id, "✅ تم إرسال رسالتك للأدمن. سيتم الرد عليك قريبًا!")

            support_sessions[user_id]['step'] = 'awaiting_admin_reply'
            save_support_sessions(support_sessions)

        except Exception as e:
            bot.send_message(user_id, f"❌ حصل خطأ أثناء إرسال الرسالة للأدمن: {e}")

    @bot.callback_query_handler(func=lambda call: call.data.startswith("reply_"))
    def handle_admin_reply(call: types.CallbackQuery):
        customer_id = str(call.data.split("_")[1])

        if customer_id not in support_sessions:
            bot.answer_callback_query(call.id, "❌ الجلسة مش متاحة الآن.")
            return

        current_step = support_sessions[customer_id].get('step')
        if current_step != 'awaiting_admin_reply':
            bot.answer_callback_query(call.id, "❌ الجلسة مش متوفرة أو أنها انتهت.")
            return

        support_sessions[customer_id]['admin_replied'] = True
        support_sessions[customer_id]['step'] = 'waiting_for_admin_message'
        support_sessions[customer_id]['admin_id'] = str(call.from_user.id)
        save_support_sessions(support_sessions)

        bot.answer_callback_query(call.id, "✍️ تمام، اكتب الرسالة اللي بدك ترد فيها على العميل.")
        bot.send_message(ADMIN_ID, "✍️ تمام، اكتب الرسالة اللي بدك ترد فيها على العميل.", parse_mode="HTML")

    @bot.message_handler(func=lambda m: m.chat.id == ADMIN_ID and m.text and not m.from_user.is_bot)
    def send_admin_reply(message: types.Message):
        found = False
        for customer_id, session in list(support_sessions.items()):
            if session.get('admin_replied') and session['step'] == 'waiting_for_admin_message':
                found = True
                reply_text = message.text.strip()

                try:
                    bot.send_message(customer_id, f"🧑‍💻 رسالة من الأدمن:\n\n{reply_text}", parse_mode="HTML")
                    bot.send_message(ADMIN_ID, "✅ تم إرسال الرسالة للعميل.")
                except Exception as e:
                    bot.send_message(ADMIN_ID, f"❌ حصل خطأ أثناء الإرسال: {e}")
                finally:
                    del support_sessions[customer_id]
                    save_support_sessions(support_sessions)
                break

        if not found:
            bot.send_message(ADMIN_ID, "⚠️ ما في أحد ينتظر ردك الآن.")
