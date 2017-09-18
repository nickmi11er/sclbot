# coding=utf-8
import logging
import scl_manager
from telegram.ext import Updater, CommandHandler

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

updater = Updater('299937300:AAG7z1stwDIBPTBwr4L_sg1dlq2A9TaFIiA')


def start(bot, update):
    update.message.reply_text('Hello World!')

def schedule(bot, update):
    out = ""
    res = scl_manager.get_with(scl_manager.now)
    for r in res:
        out = out + r + "\n"

    update.message.reply_text(out)


updater.dispatcher.add_handler(CommandHandler('start', start))
updater.dispatcher.add_handler(CommandHandler(u'расписание', schedule))

updater.start_polling()
updater.idle()
