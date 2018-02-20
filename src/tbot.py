# -*- coding: utf-8 -*-
from enum import Enum
import logging
from telegram.ext import Updater, CommandHandler, MessageHandler, CallbackQueryHandler, Filters

class AnsType(Enum):
    SEND = 1,
    EDIT = 2

class HandlerType(Enum):
    COMMAND = 1,
    MESSAGE = 2,
    BUTTON = 3

class Bot():
    def __init__(self, tk):
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

    def send_answer(self, bt, args):
        qy = args['query']
        if args['type'] == AnsType.EDIT:
            bt.edit_message_text(text=args['text'],
                                    chat_id=qy.message.chat_id,
                                    message_id=qy.message.message_id,
                                    reply_markup=args['kb'])
            if 'extra_msg' in args and args['extra_msg']:
                bt.send_message(chat_id = qy.message.chat_id, text = args['extra_msg_text'], reply_markup=args['extra_kb'])
        bt.answer_callback_query(qy.id, text="")