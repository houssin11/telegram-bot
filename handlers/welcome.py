from telebot.types import Message

def register(bot):
    @bot.message_handler(func=lambda m: m.text == "أهلاً")
    def welcome_handler(message: Message):
        bot.send_message(
            message.chat.id,
            "👋 يا ألف هلا ونور! مستنيينك تجرب الخدمات القوية اللي عندنا 💪"
        )
