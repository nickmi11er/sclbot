# -*- coding: utf-8 -*-
from enum import Enum
import logging
from datetime import datetime as dm
from models.user import User
from telegram import ParseMode
from telegram.ext import Updater, CommandHandler, MessageHandler, CallbackQueryHandler, Filters
from telegram.error import (TelegramError, Unauthorized, BadRequest, 
                            TimedOut, ChatMigrated, NetworkError)

class AnsType(Enum):
    SEND = 1,
    EDIT = 2

class HandlerType(Enum):
    COMMAND = 1,
    MESSAGE = 2,
    BUTTON = 3

class Message():
    def __init__(self, chat_id, msg_id):
        self.init_time = dm.now()
        self.chat_id = chat_id
        self.msg_id = msg_id

class Bot():
    def __init__(self, tk):
        self.listened_msgs = []
        self.token = tk
        self.updater = Updater(self.token)
        self.dsp = self.updater.dispatcher
        self.dsp.add_error_handler(lambda bot, update, _error: logging.warning('Update "%s" caused error "%s"' % (update, _error)))


    def handle(self, name=None, p_args=False, type=HandlerType.COMMAND):
        def decorator(func):
            if type == HandlerType.COMMAND:
                self.dsp.add_handler(CommandHandler(command=name, callback=func, pass_args=p_args))
            elif type == HandlerType.MESSAGE:
                self.dsp.add_handler(MessageHandler(Filters.text, func))
            elif type == HandlerType.BUTTON:
                self.dsp.add_handler(CallbackQueryHandler(func))
            def _decorator(*args, **kwargs):
                func(*args, **kwargs)
            return _decorator
        return decorator


    def polling(self):
        self.updater.start_polling()

    def idle(self):
        self.updater.idle()

    def add_repeating_job(self, job, i=60*15, f=0):
        return self.updater.job_queue.run_repeating(job, interval=i, first=f)

    def listen_for_message(self, chat_id, msg_id):
        self.listened_msgs.append(Message(chat_id, msg_id))

    def pop_listened_msg(self, msg):
        for message in self.listened_msgs:
            if msg.chat_id == message.chat_id and msg.message_id == message.msg_id:
                self.listened_msgs.remove(message)
                return msg
        return None

    def echo_for_all(self, message):
        users = User.getAll()
        for u in users:
            if u.tg_user_id > 0: # skip negative numbers for groups 
                logging.info(u'Send \'{}\' to {}'.format(message, u.tg_user_id))
                try:
                    self.updater.bot.send_message(chat_id=u.tg_user_id, text=message)
                except TelegramError:
                    logging.error('Cant send message to {}'.format(u.tg_user_id))

    def send_answer(self, bt, args):
        qy = args['query']
        if args['type'] == AnsType.EDIT:
            bt.edit_message_text(text=args['text'],
                                    chat_id=qy.message.chat_id,
                                    message_id=qy.message.message_id,
                                    reply_markup=args['kb'],
                                    parse_mode=ParseMode.MARKDOWN)
            if 'extra_msg' in args and args['extra_msg']:
                bt.send_message(chat_id = qy.message.chat_id, text = args['extra_msg_text'], reply_markup=args['extra_kb'], parse_mode=ParseMode.MARKDOWN)
        bt.answer_callback_query(qy.id, text="")


    def reply(self, update, text, keyboard=None):
        update.message.reply_text(text, reply_markup=keyboard, parse_mode=ParseMode.MARKDOWN)