# -*- coding: utf-8 -*-
from datetime import datetime as dm
import logging
from enum import Enum


from telegram.ext import Updater, CommandHandler, CallbackQueryHandler, MessageHandler, Filters

import data_manager
import date_manager
import const
import scl_manager
import keyboard as kb
from store_manager import SettingStore
import signal
import os

s_store = SettingStore()
logging.basicConfig(filename=const.root_path + '/log.txt', level=logging.INFO,
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

DB_NAME = const._db_name
BOT_TOKEN = s_store.get(const._bot_token_name)


updater = Updater(BOT_TOKEN)
dsp = updater.dispatcher

def dispatch(name=None, p_args=False):
    def decorator(func):
        dsp.add_handler(CommandHandler(name, func, pass_args=p_args))
        def _decorator(*args, **kwargs):
            func(*args, **kwargs)
        return _decorator
    return decorator

current_shown_dates={}
        

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

    if user is not None:
        if user[3] == 1:
            return True
        else:
            return False
    else:
        return False


# Возвращает id пользователя, сделавшего запрос
@dispatch(name='my_id')
def my_id(bot, update):
    update.message.reply_text("Ваш ID: {}".format(update.message.from_user.id))


# Получение списка пар из exel
def get_scl_with(dt, id):
    date = dm.now()
    user = data_manager.get_user(id)
    gp_name = user[3]
    if dt is not None:
        date = dt

    if date < scl_manager.start_dt:
        return u'Учеба еще на началась'

    out = "Расписание пар на " + date_manager.rus_week_day[date.weekday()] + ": \n\n"
    res = scl_manager._get_scl(gp_name, date)

    if res:
        for r in res:
            out = out + r + "\n"
    else:
        out = u"Пар нет. Отдыхай!"

    return out


@dispatch(name='updscl')
def updscl(bot, update):
    scl_manager.updscl()
    update.message.reply_text('Расписание успешно обновлено!')


# CommandHandler: Расписание пар на текущий день
@dispatch(name='s', p_args=True)
def schedule(bot, update, args=None):
    res = u''

    if private_chat(update.message.chat):
        id = update.message.from_user.id
    else:
        id = update.message.chat.id

    if args and len(args) > 0:
        res = get_scl_with(date_manager.get_day_over(int(args[0])), id)   
    else:
        res = get_scl_with(None, id) 

    log_bot_request(update.message, 'Schedule')
    update.message.reply_text(res)



# CommandHandler: Расписание пар на заданный день недели
@dispatch(name='sb')
def schedule_with(bot, update):
    log_bot_request(update.message, 'Schedule With')
    keyboard = kb.weekday_kb(dm.now().weekday(), False)
    update.message.reply_text('На какой день недели?', reply_markup=keyboard)


class AnsType(Enum):
    SEND = 1,
    EDIT = 2
        

def send_answer(bot, args, type, kb):
    qy = args['query']
    if type == AnsType.EDIT:
        bot.edit_message_text(text=args['text'],
                            chat_id=qy.message.chat_id,
                            message_id=qy.message.message_id,
                            reply_markup=kb)

    bot.answer_callback_query(qy.id, text="")
        


def button(bot, update):
    query = update.callback_query
    username = ''
    if query.data[0:3] == 'gp-':
        if query.data[3:5] == 'p-':
            gp_id = query.data[5:]
            user = query.message.chat
            if user.title:
                username = user.title.encode('utf-8')
        else:
            gp_id = query.data[3:]
            user = query.from_user
            if user.first_name:
                username = user.first_name.encode('utf-8')
            if user.last_name:
                username += ' {}'.format(user.last_name.encode('utf-8'))
        
        data_manager.add_or_update_user(username, user.id, 2, gp_id)

        keyboard = kb.menu_kb()
        bot.edit_message_text(text='Группа успешно обновлена',
                            chat_id=query.message.chat_id,
                            message_id=query.message.message_id,
                            reply_markup=None)
        bot.send_message(chat_id = query.message.chat_id, text = 'Теперь вы можете воспользоваться командами', reply_markup=keyboard)
        bot.answer_callback_query(query.id, text="")
        return
    if query.data[0:13] == 'calendar-day-':
        chat_id = query.message.chat_id
        if private_chat(query.message.chat):
            id = query.from_user.id
        else:
            id = query.message.chat.id
        saved_date = current_shown_dates.get(chat_id)
        if(saved_date is not None):
            day=query.data[13:]
            date = dm.strptime('{}{}{}'.format(saved_date[0],int(saved_date[1]), int(day)), '%Y%m%d')
            res = get_scl_with(date, id)
            send_answer(bot, {'text':res, 'query':query}, AnsType.EDIT, None)
        return

    if query.data == 'next-month':
        chat_id = query.message.chat_id
        saved_date = current_shown_dates.get(chat_id)
        if(saved_date is not None):
            year,month = saved_date
            month+=1
            if month>12:
                month=1
                year+=1
            date = (year,month)
            current_shown_dates[chat_id] = date
            markup= kb.create_calendar(year,month)
            send_answer(bot, {'text':'Выберите дату.', 'query':query}, AnsType.EDIT, markup)
        return

    if query.data == 'previous-month':
        chat_id = query.message.chat.id
        saved_date = current_shown_dates.get(chat_id)
        if(saved_date is not None):
            year,month = saved_date
            month-=1
            if month<1:
                month=12
                year-=1
            date = (year,month)
            current_shown_dates[chat_id] = date
            markup= kb.create_calendar(year,month)
            send_answer(bot, {'text':'Выберите дату.', 'query':query}, AnsType.EDIT, markup)
        return

    if query.data == 'back':
        markup = kb.weekday_kb(dm.now().weekday(), False)
        send_answer(bot, {'text':'На какой день недели?', 'query':query}, AnsType.EDIT, markup)
        return
    if query.data == 'ignore':
        bot.answer_callback_query(query.id, text="")
        return
    
    _type = int(query.data)
    if _type == -1:
        markup = kb.weekday_kb(0, True)
        send_answer(bot, {'text':'На какой день недели?', 'query':query}, AnsType.EDIT, markup)
    elif _type == -2:
        markup = kb.weekday_kb(dm.now().weekday(), False)
        send_answer(bot, {'text':'На какой день недели?', 'query':query}, AnsType.EDIT, markup)
    elif _type == -3:
        now = dm.now() 
        chat_id = query.message.chat_id
        date = (now.year,now.month)
        current_shown_dates[chat_id] = date
        markup = kb.create_calendar(now.year, now.month)
        send_answer(bot, {'text':'Выберите дату.', 'query':query}, AnsType.EDIT, markup)
    else:
        if private_chat(query.message.chat):
            id = query.from_user.id
        else:
            id = query.message.chat.id
        res = get_scl_with(date_manager.get_day_over(_type - dm.now().weekday()), id)
        send_answer(bot, {'text':res, 'query':query}, AnsType.EDIT, None)
            

# CommandHandler: Акакдемический план
@dispatch(name='ap')
def academy_plan(bot, update):
    log_bot_request(update.message, 'Academy Plan')
    update.message.reply_text(data_manager.get_academy_plan())


@dispatch(name='ll')
def lecturers_list(bot, update):
    log_bot_request(update.message, 'get lecturers list')
    update.message.reply_text(data_manager.get_lecturers())


@dispatch(name='notime')
def notify_me(bot, update):
    log_bot_request(update.message, 'Notify Me')
    msg = ''
    subscriber = data_manager.get_subscriber(update.message.chat.id)
    if subscriber is None:
        data_manager.add_subscriber(update.message.chat.id, update.message.from_user.id)
        msg = 'Теперь вам будут приходить уведомления'
    else:
        msg = 'Вы уже подписаны на уведомления'

    update.message.reply_text(msg)


@dispatch(name='unsub')
def unsubscribe(bot, update):
    log_bot_request(update.message, 'Unsubscribe')
    msg = ''
    subscriber = data_manager.get_subscriber(update.message.chat.id)
    if subscriber is not None:
        data_manager.delete_subscriber(update.message.chat.id)
        msg = 'Вам больше не будут приходить уведомления'
    else:
        msg = 'Вы не подписаны на уведомления'

    update.message.reply_text(msg)


@dispatch(name='start')
def start(bot, update):
    log_bot_request(update.message, 'Start')
    if private_chat(update.message.chat):
        user = data_manager.get_user(update.message.from_user.id)
    else:
        user = data_manager.get_user(update.message.chat.id)

    if user is not None:
        keyboard = kb.menu_kb()
        bot.send_message(chat_id = update.message.chat_id, text = 'Выберите команду', reply_markup=keyboard)
    else:
        groups = data_manager.get_groups()
        keyboard = kb.groups_kb(groups, private_chat(update.message.chat))
        res = 'Выберите учебную группу'
        if not  private_chat(update.message.chat):
            res = 'В данный момент я нахожусь в групповом чате. Выбранная группа будет одинаковой для всех членов чата.\n' + res
        bot.send_message(chat_id = update.message.chat_id, text = res, reply_markup=keyboard)


def private_chat(chat):
    if chat.type == 'private':
        return True
    else:
        return False     


def choose_gp(bot, update):
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
            bot.send_message(chat_id=subscriber[0], text=get_scl_with(date_manager.get_day_over(1), subscriber[1]))

    elif current_hour >= 21:
        notified = False


def main():
    dsp.add_handler(MessageHandler(Filters.text, filter_cmd))
    dsp.add_handler(CallbackQueryHandler(button))

    dsp.add_error_handler(lambda bot, update, _error : logging.warning('Update "%s" caused error "%s"' % (update, _error)))

    updater.start_polling()
    print('Bot is started...')

    # =================================================================

    schedule_notifier = updater.job_queue.run_repeating(callback_scl_notifier, interval=60*15, first=0)
    print('Schedule notifier started...')

    # =================================================================

    updater.idle()



if __name__ == '__main__':
    main()
