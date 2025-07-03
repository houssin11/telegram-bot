from telebot.types import Message
from config import ADMIN_ID
import os
from utils.database import generate_admin_report

def register(bot):
    @bot.message_handler(commands=['report'])
    def report_handler(message: Message):
        if message.chat.id != ADMIN_ID:
            return

        bot.send_message(message.chat.id, "📊 عم نجهيز تقرير الأسبوع للأدمن...")

        report_path = generate_admin_report()
        if os.path.exists(report_path):
            with open(report_path, "rb") as file:
                bot.send_document(
                    message.chat.id,
                    file,
                    caption="📈 هلق التقرير جاهز، اعرف كل شي بدري!"
                )
        else:
            bot.send_message(
                message.chat.id,
                "❌ للأسف، ما قدرناش نجهز التقرير دلوقتي."
            )
