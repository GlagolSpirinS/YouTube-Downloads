import os
import telebot
from pytube import YouTube
from pydub import AudioSegment
from pydub.utils import mediainfo
from PIL import Image
import requests

API_TOKEN = '7249476389:AAG5PSm5Udgq2MUblX8Qu8bmlQGZdFbXjPg'
bot = telebot.TeleBot(API_TOKEN)


@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.reply_to(message, "Welcome! Send me a YouTube link to download audio (itag: 140) with thumbnail.")


@bot.message_handler(func=lambda message: True)
def handle_message(message):
    chat_id = message.chat.id
    text = message.text

    if 'youtube.com' in text or 'youtu.be' in text:
        try:
            yt = YouTube(text)
            stream = yt.streams.get_by_itag(140)  # itag 140 for audio (m4a format)

            if stream:
                bot.send_message(chat_id, "Downloading audio...")
                output_path = 'downloads'
                if not os.path.exists(output_path):
                    os.makedirs(output_path)

                audio_file_path = stream.download(output_path=output_path, filename="audio.m4a")

                bot.send_message(chat_id, "Downloading thumbnail...")
                thumbnail_url = yt.thumbnail_url
                thumbnail_path = os.path.join(output_path, "thumbnail.jpg")
                download_thumbnail(thumbnail_url, thumbnail_path)

                audio_with_thumbnail_path = os.path.join(output_path, "audio_with_thumbnail.mp3")
                attach_thumbnail_to_audio(audio_file_path, thumbnail_path, audio_with_thumbnail_path)

                with open(audio_with_thumbnail_path, 'rb') as audio:
                    bot.send_audio(chat_id, audio, title=yt.title, performer=yt.author)

                # Clean up files
                os.remove(audio_file_path)
                os.remove(thumbnail_path)
                os.remove(audio_with_thumbnail_path)
            else:
                bot.send_message(chat_id, "Error: Stream with itag 140 is not available.")
        except Exception as e:
            bot.send_message(chat_id, f"An error occurred: {str(e)}")
    else:
        bot.send_message(chat_id, "Please send a valid YouTube link.")


def download_thumbnail(url, path):
    response = requests.get(url)
    if response.status_code == 200:
        with open(path, 'wb') as file:
            file.write(response.content)


def attach_thumbnail_to_audio(audio_path, thumbnail_path, output_path):
    audio = AudioSegment.from_file(audio_path)
    thumbnail = Image.open(thumbnail_path)

    info = mediainfo(audio_path)
    audio.export(output_path, format="mp3", tags={
        'artist': 'Unknown Artist',
        'album': 'Unknown Album',
        'title': info['TAG:title'] if 'TAG:title' in info else 'Unknown Title'
    }, cover=thumbnail_path)


if __name__ == '__main__':
    bot.polling(none_stop=True)
