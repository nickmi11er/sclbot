# -*- coding: utf-8 -*-
from enum import Enum
from telegram.ext import Updater, CommandHandler

class Bot():
    def __init__(self, tk):
        self.token = tk
        self.updater = Updater(self.token)
        self.dsp = self.updater.dispatcher


    def dispatch(self, name=None, p_args=False):
        def decorator(func):
            self.dsp.add_handler(CommandHandler(name, func, pass_args=p_args))
            def _decorator(*args, **kwargs):
                func(*args, **kwargs)
            return _decorator
        return decorator


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


class AnsType(Enum):
    SEND = 1,
    EDIT = 2