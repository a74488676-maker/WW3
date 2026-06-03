from flask import Flask
import threading
import os

app = Flask(__name__)

@app.route('/')
def home():
    return "WW3 Bot is running!"

@app.route('/health')
def health():
    return "OK", 200

def run_bot():
    # اجرای ربات اصلی
    os.system("python ww3.py")

if __name__ == "__main__":
    # ربات را در یک ترد جداگانه اجرا کن
    bot_thread = threading.Thread(target=run_bot)
    bot_thread.start()
    # وب سرویس را شروع کن
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 8080)))
