from flask import Flask
from threading import Thread

app = Flask('')

@app.route('/')
def home():
    return "Bot is online"

def run():
  # app.run(host='0.0.0.0',port=8080)
    app.run(port=5000)

def keep_alive():  
    t = Thread(target=run)
    t.start()

if __name__ == "__main__":
    keep_alive()
    import bot