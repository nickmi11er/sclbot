# coding=utf-8
import logging
import scl_manager
import date_manager
from telegram.ext import Updater, CommandHandler, CallbackQueryHandler
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
import sqlite3
import datetime
import data_manager
import err_handler

logging.basicConfig(filename='log.txt', level=logging.INFO,
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

_db_name = 'data.sqlite'
_bot_token = '299937300:AAG7z1stwDIBPTBwr4L_sg1dlq2A9TaFIiA'

updater = Updater(_bot_token)
dispatcher = updater.dispatcher
dm = date_manager


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
    date = datetime.datetime.now()
    if dt is not None:
        date = dt

    out = u"Расписание пар на " + unicode(dm.rus_week_day[date.weekday()], 'utf8') + ": \n\n"
    res = scl_manager.get_with(date)
    for r in res:
        out = out + r + "\n"

    return out


# CommandHandler: Расписание пар на текущий день
def schedule(bot, update):
    log_bot_request(update.message, 'Schedule')
    update.message.reply_text(get_scl_with(None))


# CommandHandler: Расписание пар на заданный день недели
def schedule_with(bot, update):
    log_bot_request(update.message, 'Schedule With')

    future_days = 7 - dm.today.weekday()

    keyboard = []
    exist_days = future_days
    current_day = dm.today.weekday()

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
                row.append(InlineKeyboardButton(dm.rus_week_day[current_day], callback_data=str(current_day)))
                exist_days -= 1
                current_day += 1

        keyboard.append(row)

    reply_markup = InlineKeyboardMarkup(keyboard)

    update.message.reply_text('На какой день недели?', reply_markup=reply_markup)


def button(bot, update):
    query = update.callback_query
    _type = int(query.data)

    res = get_scl_with(dm.get_day_over(_type - dm.today.weekday()))

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
        res = data_manager.users_list(conn)
    else:
        res = err_handler.permission_error

    update.message.reply_text(res)
    conn.close()


# CommandHandler(Admin request): Добавить нового пользователя
def add_user(update, args):
    log_bot_request(update.message, 'Add User')

    res = ""
    if len(args) < 3:
        res += u"Для добавления пользователя необходимо передать параметры в виде: /add_user id_пользователя роль(1 - "\
               u"админ) имя "
    else:
        conn = sqlite3.connect(_db_name)

        if check_permission(conn, update.message.from_user.id):
            username = u''
            if len(args) == 3:
                username += args[2]
            elif len(args) == 4:
                username + u'{} {}'.format(args[2], args[3])

            res = data_manager.add_user(conn, username, args[0], args[1])
        else:
            res = err_handler.permission_error

        conn.close()

    update.message.reply_text(res)


def error(bot, update, _error):
    logging.warning('Update "%s" caused error "%s"' % (update, _error))


dispatcher.add_handler(CommandHandler('schedule', schedule))
dispatcher.add_handler(CommandHandler('schedule_with', schedule_with))
dispatcher.add_handler(CommandHandler('academy_plan', academy_plan))
dispatcher.add_handler(CommandHandler('my_id', my_id))
dispatcher.add_handler(CallbackQueryHandler(button))
dispatcher.add_error_handler(error)

# Админский блок
dispatcher.add_handler(CommandHandler('users_list', users_list))
dispatcher.add_handler(CommandHandler('add_user', add_user, pass_args=True))

updater.start_polling()
print('Bot is started...')

updater.idle()
