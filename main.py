import telebot
import yt_dlp
import instaloader
import requests
import os
from flask import Flask
from threading import Thread
env_bot=os.environ
# Flask app
app = Flask('')

@app.route('/')
def home():
    return "Bot is running!"

def run():
    app.run(host='0.0.0.0', port=8080)

def keep_alive():
    t = Thread(target=run)
    t.start()

# Bot token (Replace with your token)
API_TOKEN = env_bot['TOKEN']
bot = telebot.TeleBot(API_TOKEN)

# YouTube video download function
def download_youtube_video(url):
    if not os.path.exists('downloads'):
        os.makedirs('downloads')

    ydl_opts = {
        'format': 'best',
        'outtmpl': 'downloads/%(title)s.%(ext)s',
    }

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info_dict = ydl.extract_info(url, download=True)
        video_file = ydl.prepare_filename(info_dict)

    return video_file

# Instagram video download function
def download_instagram_video(url):
    if not os.path.exists('downloads'):
        os.makedirs('downloads')

    L = instaloader.Instaloader(save_metadata=False, quiet=True)

    try:
        post = instaloader.Post.from_shortcode(L.context, url.split("/")[-2])
        video_url = post.video_url

        # Download video using requests
        response = requests.get(video_url, stream=True)
        video_file = f"downloads/{post.shortcode}.mp4"
        with open(video_file, 'wb') as f:
            for chunk in response.iter_content(chunk_size=1024):
                f.write(chunk)

        return video_file
    except Exception as e:
        raise Exception(f"Instagram download failed: {e}")

# Bot's start command
@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.reply_to(
        message,
        "Salom! Men yordam bera olaman:\n"
        "- YouTube videolarini yuklab olish.\n"
        "- Instagram videolarini yuklab olish.\n"
        "URL-ni yuboring va men o'zimni ishga solaman!"
    )

# Handle user messages (URLs)
@bot.message_handler(func=lambda message: True)
def handle_message(message):
    url = message.text.strip()
    try:
        if "youtube.com" in url or "youtu.be" in url:
            video_file = download_youtube_video(url)
        elif "instagram.com" in url:
            video_file = download_instagram_video(url)
        else:
            bot.reply_to(message, "Hozircha faqat YouTube va Instagram URL-larini qabul qilaman.")
            return

        caption = '@otash1221_bot'
        with open(video_file, 'rb') as video:
            bot.send_video(message.chat.id, video, caption=caption)

        os.remove(video_file)  # Clean up
    except Exception as e:
        bot.reply_to(message, f"Xatolik yuz berdi: {e}")

# Run the bot
keep_alive()
bot.polling()
