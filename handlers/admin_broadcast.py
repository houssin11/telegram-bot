from telebot.types import Message
from config import ADMIN_ID
from utils.database import load_users
from utils.logger import log_admin_action

def register(bot):
    @bot.message_handler(commands=["broadcast"])
    def broadcast_handler(message: Message):
        if message.chat.id != ADMIN_ID:
            return

        args = message.text.split(maxsplit=1)
        if len(args) < 2:
            bot.send_message(message.chat.id, "❌ لازم تكتب الرسالة اللي بدك ترسلها.\nمثال:\n<code>/broadcast مرحباً بالجميع!</code>", parse_mode="HTML")
            return

        msg = args[1]
        users = load_users()
        success = 0

        for user_id in users:
            try:
                bot.send_message(int(user_id), msg)
                success += 1
            except Exception:
                continue

        bot.send_message(message.chat.id, f"📢 تم إرسال الرسالة إلى {success} عميل.")
        log_admin_action(f"📢 أرسل الأدمن رسالة جماعية إلى {success} مستخدم.")
