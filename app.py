from flask import Flask, render_template, request, send_file
from pytubefix import YouTube  # Импортируем YouTube из pytubefix
import ssl
import re
import os

app = Flask(__name__)

@app.route("/", methods=['GET', 'POST'])
def index():
    return render_template('index.html')

@app.route('/download', methods=['POST'])
def download_video():
    try:
        # Отключение проверки SSL сертификатов
        ssl._create_default_https_context = ssl._create_unverified_context

        # Получение URL с YouTube
        youtube_url = request.form.get('url', '').strip()
        print(f"Полученный URL: {youtube_url}")  # Для отладки

        # Преобразование URL в формат https://youtu.be/{video_id}
        youtube_url = convert_youtube_url(youtube_url)
        
        # Проверка на корректность URL
        if not youtube_url:
            return "Некорректный URL. Пожалуйста, введите правильную ссылку на YouTube."

        # Получение YouTube объекта
        yt = YouTube(youtube_url)

        # Получение видео в максимальном качестве
        video_stream = yt.streams.filter(progressive=True, file_extension='mp4').order_by('resolution').desc().first()

        if not video_stream:
            return "Не удалось найти подходящее видео для скачивания."

        # Временное сохранение видео
        download_path = video_stream.download()

        # Отправка файла пользователю
        return send_file(download_path, as_attachment=True, download_name=f"{yt.title}.mp4")

    except Exception as e:
        return f"Произошла ошибка при скачивании видео: {str(e)}"

def convert_youtube_url(url):
    """
    Преобразование URL YouTube в формат короткой ссылки.
    """
    # Регулярные выражения для извлечения ID видео
    short_url_pattern = r"^https://youtu.be/([a-zA-Z0-9_-]+)"
    long_url_pattern = r"^https://www.youtube.com/watch\?v=([a-zA-Z0-9_-]+)"
    
    match = re.match(short_url_pattern, url)
    if match:
        return url  # Уже в нужном формате

    match = re.match(long_url_pattern, url)
    if match:
        video_id = match.group(1)
        return f"https://youtu.be/{video_id}"
    
    return None  # Неверный формат URL

if __name__ == "__main__":
    app.run(debug=True)
