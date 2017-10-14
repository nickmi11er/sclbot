# coding=utf-8
from datetime import datetime as dm
import logging
import sqlite3

from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Updater, CommandHandler, CallbackQueryHandler

import data_manager
import date_manager
import const
import scl_manager

logging.basicConfig(filename=const.root_path + '/log.txt', level=logging.INFO,
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

_db_name = const.assets_dir + '/data.sqlite'
_bot_token = '299937300:AAG7z1stwDIBPTBwr4L_sg1dlq2A9TaFIiA'

updater = Updater(_bot_token)
dispatcher = updater.dispatcher


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

    out = u"Расписание пар на " + unicode(date_manager.rus_week_day[date.weekday()], 'utf8') + ": \n\n"
    res = scl_manager.get_with(date)
    if res:
        for r in res:
            if '**' in r:
                #print(u' '.join(r).encode('utf-8'))
                r = r.replace('**', '')

                r = u'❗' + r

            out = out + r + "\n"
    else:
        out = u"Пар нет. Отдыхай!"

    return out


# CommandHandler: Расписание пар на текущий день
def schedule(bot, update, args):
    res = u''

    if len(args) > 0:
        res = get_scl_with(date_manager.get_day_over(int(args[0])))   
    else:
        res = get_scl_with(None) 

    log_bot_request(update.message, 'Schedule')
    update.message.reply_text(res)


# CommandHandler: Расписание пар на заданный день недели
def schedule_with(bot, update):
    log_bot_request(update.message, 'Schedule With')

    future_days = 7 - dm.now().weekday()

    keyboard = []
    exist_days = future_days
    current_day = dm.now().weekday()

    for i in range(0, (future_days / 3)):
        row = []

        for j in range(0, 3):
            if current_day == 5 or current_day == 6:
                exist_days -= 1
                continue

            if i == 0 and j == 0 and exist_days > 0:
                row.append(InlineKeyboardButton("Сегодня", callback_data=str(current_day)))
                exist_days -= 1
                current_day += 1
                continue
            if i == 0 and j == 1 and exist_days > 0:
                row.append(InlineKeyboardButton("Завтра", callback_data=str(current_day)))
                exist_days -= 1
                current_day += 1
                continue
            if exist_days > 0:
                row.append(InlineKeyboardButton(date_manager.rus_week_day[current_day], callback_data=str(current_day)))
                exist_days -= 1
                current_day += 1

        keyboard.append(row)

    reply_markup = InlineKeyboardMarkup(keyboard)

    update.message.reply_text('На какой день недели?', reply_markup=reply_markup)


def button(bot, update):
    query = update.callback_query
    _type = int(query.data)

    res = get_scl_with(date_manager.get_day_over(_type - dm.now().weekday()))

    bot.edit_message_text(text=res,
                          chat_id=query.message.chat_id,
                          message_id=query.message.message_id)


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


dispatcher.add_handler(CommandHandler('schedule', schedule, pass_args=True))
dispatcher.add_handler(CommandHandler('schedule_with', schedule_with))
dispatcher.add_handler(CommandHandler('academy_plan', academy_plan))
dispatcher.add_handler(CommandHandler('my_id', my_id))
dispatcher.add_handler(CommandHandler('notify_me', notify_me))
dispatcher.add_handler(CommandHandler('unsubscribe', unsubscribe))
dispatcher.add_handler(CommandHandler('day_x', day_x))
dispatcher.add_handler(CallbackQueryHandler(button))
dispatcher.add_error_handler(error)
dispatcher.add_handler(CommandHandler("lecturers_list", lecturers_list))

# Админский блок
dispatcher.add_handler(CommandHandler('users_list', users_list))
dispatcher.add_handler(CommandHandler('add_user', add_user, pass_args=True))

updater.start_polling()
print('Bot is started...')

# =================================================================


notified = False


def callback_scl_notifier(bot, job):
    if dm.now().weekday() == 5 or dm.now().weekday() == 6:
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


schedule_notifier = updater.job_queue.run_repeating(callback_scl_notifier, interval=60, first=0)
print('Schedule notifier started...')

# =================================================================

updater.idle()
