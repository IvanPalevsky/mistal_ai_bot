import os
import telebot
import base64
from mistralai import Mistral
from config import *
from logic import save_feedback

model_text = "ministral-8b-latest"
model_image = "pixtral-12b-2409"

client = Mistral(api_key=API_KEY)
bot = telebot.TeleBot(API_TOKEN)

def encode_image(image_path):
    """Encode the image to base64."""
    try:
        with open(image_path, "rb") as image_file:
            return base64.b64encode(image_file.read()).decode('utf-8')
    except FileNotFoundError:
        print(f"Error: The file {image_path} was not found.")
        return None
    except Exception as e:  # Added general exception handling
        print(f"Error: {e}")
        return None

@bot.message_handler(commands=['help', 'start'])
def send_welcome(message):
    welcome_text = """
Привет! Я бот с искусственным интеллектом.

Что я умею:
1. Отвечать на ваши текстовые сообщения
2. Анализировать картинки (просто отправьте мне фото)
3. Принимать отзывы (используйте команду /feedback и ваш отзыв)

Пример отзыва: /feedback Отличный бот!
"""
    bot.reply_to(message, welcome_text)

@bot.message_handler(commands=['feedback'])
def handle_feedback(message):
    feedback_text = message.text.replace('/feedback', '').strip()
    if feedback_text:
        save_feedback(message.from_user.id, feedback_text)
        bot.reply_to(message, "Спасибо за ваш отзыв!")
    else:
        bot.reply_to(message, "Пожалуйста, добавьте текст отзыва после команды /feedback")

@bot.message_handler(content_types=['photo'])
def handle_photo(message):
    file_info = bot.get_file(message.photo[-1].file_id)
    downloaded_file = bot.download_file(file_info.file_path)
    
    with open("temp_image.jpg", 'wb') as new_file:
        new_file.write(downloaded_file)

    
    base64_image = encode_image("temp_image.jpg")
    promt = message.caption if message.caption else 'Что на фото?'
    messages = [
        {
            "role": "user",
            "content": [
                {"type": "text", "text": promt },
                {"type": "image_url", "image_url": f"data:image/jpeg;base64,{base64_image}"}
            ]
        }
    ]
    
    chat_response = client.chat.complete(
        model=model_image,
        messages=messages
    )
    
    bot.reply_to(message, chat_response.choices[0].message.content)
    os.remove("temp_image.jpg")

@bot.message_handler(func=lambda message: True)
def echo_message(message):
    chat_response = client.chat.complete(
        model=model_text,
        messages=[
            {
                "role": "user", 
                "content": message.text
            },
    ]
    )
    bot.reply_to(message, chat_response.choices[0].message.content)

bot.infinity_polling()