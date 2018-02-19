# -*- coding: utf-8 -*-
from telegram.ext import CallbackQueryHandler, MessageHandler, Filters
import data_manager, date_manager, scl_manager
from handler import ButtonHandlerFactory
from store_manager import SettingStore
from datetime import datetime as dm
import handler as hand
import keyboard as kb
from tbot import Bot
import logging
import const
import signal
import os


s_store = SettingStore()
logging.basicConfig(filename=const.root_path + '/log.txt', level=logging.INFO,
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

DB_NAME = const._db_name
BOT_TOKEN = s_store.get(const._bot_token_name)

bot = Bot(BOT_TOKEN)
        

def sig_handler(signum, frame):
    print "Recieve signal to suicide... PID = {}".format(os.getpid())
    os._exit(0)

signal.signal(signal.SIGUSR1, sig_handler)

def log_bot_request(message, action):
    user = message.from_user
    logging.info(
        u'Action: {}, from user id: {}, {} {} ({}) - message_id: {}, chat: {}, message: '.format(action,
                                                                                                 user.id,
                                                                                                 user.last_name,
                                                                                                 user.first_name,
                                                                                                 user.username,
                                                                                                 message.message_id,
                                                                                                 message.chat.title,
                                                                                                 message.text))


# Проверка прав доступа к админским функциям
def check_permission(user_id):
    user = data_manager.get_user(user_id)
    return user and user[3] == 1


# Возвращает id пользователя, сделавшего запрос
@bot.dispatch(name='my_id')
def my_id(bt, update):
    update.message.reply_text("Ваш ID: {}".format(update.message.from_user.id))


@bot.dispatch(name='updscl')
def updscl(bt, update):
    scl_manager.updscl()
    update.message.reply_text('Расписание успешно обновлено!')


# CommandHandler: Расписание пар на текущий день
@bot.dispatch(name='s', p_args=True)
def schedule(bt, update, args=None):
    res = u''

    if private_chat(update.message.chat):
        id = update.message.from_user.id
    else:
        id = update.message.chat.id

    if args and len(args) > 0:
        res = scl_manager.get_scl_with(date_manager.get_day_over(int(args[0])), id)   
    else:
        res = scl_manager.get_scl_with(None, id) 

    log_bot_request(update.message, 'Schedule')
    update.message.reply_text(res)



# CommandHandler: Расписание пар на заданный день недели
@bot.dispatch(name='sb')
def schedule_with(bt, update):
    log_bot_request(update.message, 'Schedule With')
    keyboard = kb.weekday_kb(dm.now().weekday(), False)
    update.message.reply_text('На какой день недели?', reply_markup=keyboard)


def button(bt, update):
    query = update.callback_query
    handler = ButtonHandlerFactory().get_handler(query)
    if handler and handler.ready:
        params = handler.gen_params()
        bot.send_answer(bt, params)
        return
    elif query.data == 'ignore':
        bt.answer_callback_query(query.id, text="")
        return
            

# CommandHandler: Акакдемический план
@bot.dispatch(name='ap')
def academy_plan(bt, update):
    log_bot_request(update.message, 'Academy Plan')
    update.message.reply_text(data_manager.get_academy_plan())


@bot.dispatch(name='ll')
def lecturers_list(bt, update):
    log_bot_request(update.message, 'get lecturers list')
    update.message.reply_text(data_manager.get_lecturers())


@bot.dispatch(name='notime')
def notify_me(bt, update):
    log_bot_request(update.message, 'Notify Me')
    msg = ''
    subscriber = data_manager.get_subscriber(update.message.chat.id)
    if subscriber is None:
        data_manager.add_subscriber(update.message.chat.id, update.message.from_user.id)
        msg = 'Теперь вам будут приходить уведомления'
    else:
        msg = 'Вы уже подписаны на уведомления'

    update.message.reply_text(msg)


@bot.dispatch(name='unsub')
def unsubscribe(bt, update):
    log_bot_request(update.message, 'Unsubscribe')
    msg = ''
    subscriber = data_manager.get_subscriber(update.message.chat.id)
    if subscriber is not None:
        data_manager.delete_subscriber(update.message.chat.id)
        msg = 'Вам больше не будут приходить уведомления'
    else:
        msg = 'Вы не подписаны на уведомления'

    update.message.reply_text(msg)


@bot.dispatch(name='start')
def start(bt, update):
    log_bot_request(update.message, 'Start')
    if private_chat(update.message.chat):
        user = data_manager.get_user(update.message.from_user.id)
    else:
        user = data_manager.get_user(update.message.chat.id)

    if user is not None:
        keyboard = kb.menu_kb()
        bt.send_message(chat_id = update.message.chat_id, text = 'Выберите команду', reply_markup=keyboard)
    else:
        groups = data_manager.get_groups()
        keyboard = kb.groups_kb(groups, private_chat(update.message.chat))
        res = 'Выберите учебную группу'
        if not  private_chat(update.message.chat):
            res = 'В данный момент я нахожусь в групповом чате. Выбранная группа будет одинаковой для всех членов чата.\n' + res
        bt.send_message(chat_id = update.message.chat_id, text = res, reply_markup=keyboard)


def private_chat(chat):
    return chat.type == 'private'   


def choose_gp(bt, update):
    groups = data_manager.get_groups()
    private = private_chat(update.message.chat)
    keyboard = kb.groups_kb(groups, private)
    if private:
        user = data_manager.get_user(update.message.from_user.id)
    else:
        user = data_manager.get_user(update.message.chat.id)
    update.message.reply_text(text = u'Ваша текущая группа: {}\nВыберите учебную группу'.format(user[3]), reply_markup=keyboard)


commands = {
    u'Расписание на сегодня': schedule,
    u'Расписание на указанный день': schedule_with,
    u'Академический план': academy_plan,
    u'Уведомлять о событиях': notify_me,
    u'Выбрать группу': choose_gp
}

filter_cmd = lambda bot, upd: upd.message.text in commands and commands[upd.message.text](bot, upd)


notified = False

def callback_scl_notifier(bot, job):
    if dm.now().weekday() == 5:
        return

    global notified
    current_hour = dm.now().hour
    if 20 <= current_hour < 21 and not notified:
        notified = True

        for subscriber in data_manager.get_subscribers():
            bot.send_message(chat_id=subscriber[0], text=scl_manager.get_scl_with(date_manager.get_day_over(1), subscriber[1]))

    elif current_hour >= 21:
        notified = False


def main():
    bot.dsp.add_handler(MessageHandler(Filters.text, filter_cmd))
    bot.dsp.add_handler(CallbackQueryHandler(button))

    bot.dsp.add_error_handler(lambda bot, update, _error : logging.warning('Update "%s" caused error "%s"' % (update, _error)))

    bot.updater.start_polling()
    print('Bot is started...')

    # =================================================================

    schedule_notifier = bot.updater.job_queue.run_repeating(callback_scl_notifier, interval=60*15, first=0)
    print('Schedule notifier started...')

    # =================================================================

    bot.updater.idle()



if __name__ == '__main__':
    main()
