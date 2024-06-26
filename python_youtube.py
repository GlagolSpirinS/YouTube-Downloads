import os
import telebot
from pytube import YouTube

API_TOKEN = '7249476389:AAG5PSm5Udgq2MUblX8Qu8bmlQGZdFbXjPg'
bot = telebot.TeleBot(API_TOKEN)


@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.reply_to(message, "Привет! Скинь мне видео с той музыкой, которую тебе хотелось бы послушать.")


@bot.message_handler(func=lambda message: True)
def handle_message(message):
    chat_id = message.chat.id
    text = message.text

    if 'youtube.com' in text or 'youtu.be' in text:
        try:
            yt = YouTube(text)
            stream = yt.streams.get_by_itag(140)  # itag 140 for audio (m4a format)

            if stream:
                bot.send_message(chat_id, "Скачивание...")
                output_path = 'downloads'
                if not os.path.exists(output_path):
                    os.makedirs(output_path)

                file_path = stream.download(output_path=output_path)

                with open(file_path, 'rb') as audio:
                    bot.send_audio(chat_id, audio)

                os.remove(file_path)  # Удаление файла после отправки
            else:
                bot.send_message(chat_id, "Ошибка: Поток с тегом 140 недоступен.")
        except Exception as e:
            bot.send_message(chat_id, f"Произошла ошибка: {str(e)}")
    else:
        bot.send_message(chat_id, "Пожалуйста, пришлите действующую ссылку на YouTube.")


if __name__ == '__main__':
    bot.polling(none_stop=True)
