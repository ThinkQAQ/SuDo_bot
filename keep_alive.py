from flask import Flask
from multiprocessing import Process

app = Flask('')
server = None


@app.route('/')
def main():
    return 'Bot is alive!'


def run():
    app.run(host="0.0.0.0", port=8080)


def keep_alive():
    global server
    server = Process(target=run)
    server.start()


def shutdown():
    global server
    server.terminate()
