# git commit -am 'commit' & git push heroku master

import datetime
import json
import os
import logging
import sys

from flask import Flask, request
import telegram
from storage import Storage

logging.basicConfig(handlers=[logging.StreamHandler(sys.stdout)],
                    level=logging.INFO,
                    format='%(levelname)-8s|'
                           '%(process)d|%(name)s|%(module)s|%(funcName)s::%(lineno)d|%(message)s')

HOST = 'HOST'
PORT = int(os.environ.get("PORT", 5000))
TOKEN = 'TOKEN'

app = Flask(__name__)
bot = None
storage = Storage('storage.txt')


def action_start(message):
    chat_id = message.chat_id
    bot.sendMessage(chat_id, text="Hi")


def action_digest(message):
    chat_id = message.chat_id
    items = storage.getAll()
    if len(items) > 0:
        for item in items:
            text = 'time: ' + item['time'] + '\n' + \
                   'args: ' + json.dumps(item['args'], indent=4, separators=(',', ': ')) + '\n' + \
                   'form: ' + json.dumps(item['form'], indent=4, separators=(',', ': '))
            bot.sendMessage(chat_id, text=text)
        storage.erase()
    else:
        bot.sendMessage(chat_id, text='No messages')


def action_unknown(message):
    chat_id = message.chat_id
    bot.sendMessage(chat_id, text='Don\'t understand you: ' + message.text)


@app.route('/telegram/' + TOKEN, methods=['POST'])
def telegram_hook():
    try:
        update = telegram.Update.de_json(request.get_json(force=True))
        message = update.message
        if message.text:
            if message.text.startswith('/'):
                if message.text == '/start':
                    action_start(message)
                elif message.text == '/digest':
                    action_digest(message)
                else:
                    action_unknown(message)
        return "ok", 200
    except Exception as e:
        logging.exception('telegram_hook')
        return "not ok", 500


@app.route('/request')
def http_request():
    try:
        storage.put({
            'time': str(datetime.datetime.now()),
            'args': request.args,
            'form': request.form
        })
        return 'ok', 200
    except Exception as e:
        logging.exception('http_request')
        return 'not ok!', 500


@app.route('/raw_storage')
def get_raw():
    return storage.getRaw()


@app.route('/')
def index():
    return "Hi!"


@app.before_first_request
def main():
    global bot
    bot = telegram.Bot(TOKEN)
    webhook_url = HOST + 'telegram/' + TOKEN
    logging.debug(webhook_url)
    bot.setWebhook(webhook_url=webhook_url)
