# -*- coding: utf-8 -*-
from datetime import datetime as dm
import logging
import sqlite3

from telegram import InlineKeyboardButton, InlineKeyboardMarkup, KeyboardButton, ReplyKeyboardMarkup
from telegram.ext import Updater, CommandHandler, CallbackQueryHandler, MessageHandler, Filters

import data_manager
import date_manager
import const
import scl_manager
import telecal

logging.basicConfig(filename=const.root_path + '/log.txt', level=logging.INFO,
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

_db_name = const.assets_dir + '/data.sqlite'
_bot_token = '299937300:AAG7z1stwDIBPTBwr4L_sg1dlq2A9TaFIiA'

updater = Updater(_bot_token)
dispatcher = updater.dispatcher

current_shown_dates={}


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
def check_permission(conn, user_id):
    user = data_manager.get_user(conn, user_id)

    if user is not None:
        if user[3] == 1:
            return True
        else:
            return False
    else:
        return False


# Возвращает id пользователя, сделавшего запрос
def my_id(bot, update):
    update.message.reply_text("Ваш ID: {}".format(update.message.from_user.id))


# Получение списка пар из exel
def get_scl_with(dt):
    date = dm.now()
    if dt is not None:
        date = dt

    if date < scl_manager.start_dt:
        return u'Учеба еще на началась'

    out = "Расписание пар на " + date_manager.rus_week_day[date.weekday()] + ": \n\n"
    res = scl_manager.get_scl(date)
    #res = scl_manager.get_with(date)
    if res:
        for r in res:
            out = out + r + "\n"
    else:
        out = u"Пар нет. Отдыхай!"

    return out


def updscl(bot, update):
    scl_manager.updscl()
    update.message.reply_text('Расписание успешно обновлено!')


# CommandHandler: Расписание пар на текущий день
def schedule(bot, update, args):
    res = u''

    if len(args) > 0:
        res = get_scl_with(date_manager.get_day_over(int(args[0])))   
    else:
        res = get_scl_with(None) 

    log_bot_request(update.message, 'Schedule')
    update.message.reply_text(res)


def get_weekday_kb(current_day, is_nex_week):

    future_days = 7 - current_day # оставшееся количество дней в неделе
    exist_days = future_days

    keyboard = []

    for i in range(0, (future_days / 3)):  # i - количество строк
        row = []

        for j in range(0, 3):   # j - количество столбцов
            if current_day == 6:    # если воскресенье, пропускаем цикл
                exist_days -= 1
                continue

            if i == 0 and j == 0 and exist_days > 0:
                day_name = ''
                start_day = current_day
                if not is_nex_week:
                    day_name = "Сегодня"
                else:
                    start_day = current_day + 7
                    day_name = date_manager.rus_week_day[current_day]

                row.append(InlineKeyboardButton(day_name, callback_data=str(start_day)))
                exist_days -= 1
                current_day += 1
                continue
            if i == 0 and j == 1 and exist_days > 0:
                day_name = ''
                start_day = current_day
                if not is_nex_week:
                    day_name = "Завтра"
                else:
                    start_day = current_day + 7
                    day_name = date_manager.rus_week_day[current_day]

                row.append(InlineKeyboardButton(day_name, callback_data=str(start_day)))
                exist_days -= 1
                current_day += 1
                continue
            if exist_days > 0:
                start_day = current_day
                if is_nex_week:
                    start_day = current_day + 7
                row.append(InlineKeyboardButton(date_manager.rus_week_day[current_day], callback_data=str(start_day)))
                exist_days -= 1
                current_day += 1

        keyboard.append(row)

    row = []
    if not is_nex_week:
        row.append(InlineKeyboardButton("След. неделя", callback_data='-1'))
    else:
        row.append(InlineKeyboardButton("Пред. неделя", callback_data='-2'))

    row.append(InlineKeyboardButton("Календарь", callback_data='-3'))
    keyboard.append(row)
    return keyboard


# CommandHandler: Расписание пар на заданный день недели
def schedule_with(bot, update):
    log_bot_request(update.message, 'Schedule With')
    
    reply_markup = InlineKeyboardMarkup(get_weekday_kb(dm.now().weekday(), False))

    update.message.reply_text('На какой день недели?', reply_markup=reply_markup)


def button(bot, update):
    query = update.callback_query
    if query.data[0:13] == 'calendar-day-':
        chat_id = query.message.chat_id
        saved_date = current_shown_dates.get(chat_id)
        if(saved_date is not None):
            day=query.data[13:]
            date = dm.strptime('{}{}{}'.format(saved_date[0],int(saved_date[1]), int(day)), '%Y%m%d')
            res = get_scl_with(date)
            bot.edit_message_text(text=res,
                            chat_id=query.message.chat_id,
                            message_id=query.message.message_id,
                            reply_markup=None)
            bot.answer_callback_query(query.id, text="")
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
            markup= telecal.create_calendar(year,month)
            bot.edit_message_text(text="Выберите дату.", 
                        chat_id=query.message.chat_id,
                        message_id=query.message.message_id,
                        reply_markup=markup)
            bot.answer_callback_query(query.id, text="")
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
            markup= telecal.create_calendar(year,month)
            bot.edit_message_text("Выберите дату.", 
                        chat_id=query.message.chat_id,
                        message_id=query.message.message_id,
                        reply_markup=markup)
            bot.answer_callback_query(query.id, text="")
        return

    if query.data == 'back':
        reply_markup = InlineKeyboardMarkup(get_weekday_kb(dm.now().weekday(), False))
        bot.edit_message_text(text='На какой день недели?',
                        chat_id=query.message.chat_id,
                        message_id=query.message.message_id,
                        reply_markup=reply_markup)
        bot.answer_callback_query(query.id, text="")
        return
    
    _type = int(query.data)
    if _type == -1:
        reply_markup = InlineKeyboardMarkup(get_weekday_kb(0, True))
        bot.edit_message_text(text='На какой день недели?',
                        chat_id=query.message.chat_id,
                        message_id=query.message.message_id,
                        reply_markup=reply_markup)
    elif _type == -2:
        reply_markup = InlineKeyboardMarkup(get_weekday_kb(dm.now().weekday(), False))
        bot.edit_message_text(text='На какой день недели?',
                        chat_id=query.message.chat_id,
                        message_id=query.message.message_id,
                        reply_markup=reply_markup)
    elif _type == -3:
        now = dm.now() 
        chat_id = query.message.chat_id
        date = (now.year,now.month)
        current_shown_dates[chat_id] = date
        reply_markup = telecal.create_calendar(now.year, now.month)
        bot.edit_message_text(text='Выберите дату.',
                        chat_id=query.message.chat_id,
                        message_id=query.message.message_id,
                        reply_markup=reply_markup)
    else:
        res = get_scl_with(date_manager.get_day_over(_type - dm.now().weekday()))
        bot.edit_message_text(text=res,
                            chat_id=query.message.chat_id,
                            message_id=query.message.message_id)

    bot.answer_callback_query(query.id, text="")
            


# CommandHandler: Акакдемический план
def academy_plan(bot, update):
    log_bot_request(update.message, 'Academy Plan')
    conn = sqlite3.connect(_db_name)

    update.message.reply_text(data_manager.get_academy_plan(conn))
    conn.close()


# CommandHandler(Admin request): Список пользователей
def users_list(bot, update):
    log_bot_request(update.message, 'Users List')
    conn = sqlite3.connect(_db_name)

    if check_permission(conn, update.message.from_user.id):
        res = u"Список пользователей: \n"

        for row in data_manager.users_list(conn):
            res += '{}: {} (role: {})\n'.format(row[0], row[1], row[2])
    else:
        res = const.permission_error

    update.message.reply_text(res)
    conn.close()


# CommandHandler(Admin request): Добавить нового пользователя
def add_user(update, args):
    log_bot_request(update.message, 'Add User')

    res = ""
    if len(args) < 3:
        res += u"Для добавления пользователя необходимо передать параметры в виде: /add_user id_пользователя роль(1 - " \
               u"админ) имя "
    else:
        conn = sqlite3.connect(_db_name)

        if check_permission(conn, update.message.from_user.id):
            username = u''
            if len(args) == 3:
                username += args[2]
            elif len(args) == 4:
                username + u'{} {}'.format(args[2], args[3])

            res = data_manager.add_or_update_user(conn, username, args[0], args[1])
        else:
            res = const.permission_error

        conn.close()

    update.message.reply_text(res)


def error(bot, update, _error):
    logging.warning('Update "%s" caused error "%s"' % (update, _error))


def lecturers_list(bot, update):
    connection = sqlite3.connect(_db_name)
    log_bot_request(update.message, 'get lecturers list')
    update.message.reply_text(data_manager.get_lecturers(connection))


def notify_me(bot, update):
    log_bot_request(update.message, 'Notify Me')
    conn = sqlite3.connect(_db_name)

    msg = ''
    subscriber = data_manager.get_subscriber(conn, update.message.chat.id)
    if subscriber is None:
        data_manager.add_subscriber(conn, update.message.chat.id, update.message.from_user.id)
        msg = 'Теперь вам будут приходить уведомления'
    else:
        msg = 'Вы уже подписаны на уведомления'

    update.message.reply_text(msg)
    conn.close()


def unsubscribe(bot, update):
    log_bot_request(update.message, 'Unsubscribe')
    conn = sqlite3.connect(_db_name)

    msg = ''
    subscriber = data_manager.get_subscriber(conn, update.message.chat.id)
    if subscriber is not None:
        data_manager.delete_subscriber(conn, update.message.chat.id)
        msg = 'Вам больше не будут приходить уведомления'
    else:
        msg = 'Вы не подписаны на уведомления'

    update.message.reply_text(msg)
    conn.close()


def day_x(bot, update):
    log_bot_request(update.message, 'Day X')
    conn = sqlite3.connect(_db_name)

    output = ''
    res = scl_manager.scl_info(conn)
    output += u"Сейчас идет " + str(res['weeknum']) + u" неделя\n"
    output += u"Осталось до сессии недель: " + str(res['days'] / 7) + u", дней: " + str(res['days'] % 7) + "\n"
    output += u"Пройдено: " + str(res['percentage']) + "%"

    update.message.reply_text(output)
    conn.close()


def start(bot, update):
    log_bot_request(update.message, 'Start')
    markup = []
    row = []
    row.append(KeyboardButton('Расписание на сегодня'))
    row.append(KeyboardButton('Расписание на указанный день'))
    markup.append(row)

    row = []
    row.append(KeyboardButton('Академический план'))
    row.append(KeyboardButton('Уведомлять о событиях'))
    markup.append(row)

    row = []
    row.append(KeyboardButton('Отписаться от уведомлений'))
    row.append(KeyboardButton('Выбрать группу'))
    markup.append(row)
    keyboard = ReplyKeyboardMarkup(markup, resize_keyboard=True)
    bot.send_message(chat_id = update.message.chat_id, text = 'Выберите команду', reply_markup=keyboard)


def echo(bot, update):
    if update.message.text == u'Расписание на сегодня':
        schedule(bot, update, [])
    elif update.message.text == u'Расписание на указанный день':
        schedule_with(bot, update)
    elif update.message.text == u'Академический план':
        academy_plan(bot, update)
    elif update.message.text == u'Уведомлять о событиях':
        notify_me(bot, update)
    elif update.message.text == u'Отписаться от уведомлений':
        unsubscribe(bot, update)
    elif update.message.text == u'Выбрать группу':
        update.message.reply_text('Данная функция временно недоступна')
        


dispatcher.add_handler(CommandHandler('s', schedule, pass_args=True))
dispatcher.add_handler(CommandHandler('sb', schedule_with))
dispatcher.add_handler(CommandHandler('ap', academy_plan))
dispatcher.add_handler(CommandHandler('my_id', my_id))
dispatcher.add_handler(CommandHandler('notime', notify_me))
dispatcher.add_handler(CommandHandler('unsub', unsubscribe))
dispatcher.add_handler(CommandHandler('day_x', day_x))
dispatcher.add_handler(CommandHandler('start', start))

echo_handler = MessageHandler(Filters.text, echo)
dispatcher.add_handler(echo_handler)


dispatcher.add_handler(CallbackQueryHandler(button))
dispatcher.add_error_handler(error)
dispatcher.add_handler(CommandHandler("ll", lecturers_list))

# Админский блок
dispatcher.add_handler(CommandHandler('users_list', users_list))
dispatcher.add_handler(CommandHandler('add_user', add_user, pass_args=True))
dispatcher.add_handler(CommandHandler("updscl", updscl)) # add permission

updater.start_polling()
print('Bot is started...')

# =================================================================


notified = False


def callback_scl_notifier(bot, job):
    if dm.now().weekday() == 6:
        return

    global notified
    current_hour = dm.now().hour
    if 7 <= current_hour < 8 and not notified:
        notified = True
        conn = sqlite3.connect(_db_name)

        for subscriber in data_manager.get_subscribers(conn):
            bot.send_message(chat_id=subscriber[0], text=get_scl_with(None))

        conn.close()
    elif current_hour >= 9:
        notified = False


schedule_notifier = updater.job_queue.run_repeating(callback_scl_notifier, interval=60*15, first=0)
print('Schedule notifier started...')

# =================================================================

updater.idle()
