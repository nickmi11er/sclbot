# coding=utf-8
import logging
import scl_manager
import date_manager
from telegram.ext import Updater, CommandHandler, CallbackQueryHandler
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
import sqlite3

logging.basicConfig(filename='log.txt', level=logging.INFO,
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')


def log_message(message, action):
    user = message.from_user
    logging.info(
        'Action: {}, from user id: {}, {} {} ({}) - message_id: {}, chat: {}, message: '.format(action,
                                                                                                user.id,
                                                                                                user.last_name,
                                                                                                user.first_name,
                                                                                                user.username,
                                                                                                message.message_id,
                                                                                                message.chat.title,
                                                                                                message.text))


updater = Updater('299937300:AAG7z1stwDIBPTBwr4L_sg1dlq2A9TaFIiA')
dispatcher = updater.dispatcher
dm = date_manager


def get_scl_with(dt):
    date = dm.today
    if dt is not None:
        date = dt

    out = u"Расписание пар на " + unicode(dm.rus_week_day[date.weekday()], 'utf8') + ": \n\n"
    res = scl_manager.get_with(date)
    for r in res:
        out = out + r + "\n"

    return out


def schedule(bot, update):
    log_message(update.message, 'Schedule')
    update.message.reply_text(get_scl_with(None))


def schedule_with(bot, update):
    log_message(update.message, 'Schedule With')

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
    type = int(query.data)

    res = get_scl_with(dm.get_day_over(type - dm.today.weekday()))

    bot.edit_message_text(text=res,
                          chat_id=query.message.chat_id,
                          message_id=query.message.message_id)


def academy_plan(bot, update):
    log_message(update.message, 'Academy Plan')
    conn = sqlite3.connect('data.sqlite')
    cursor = conn.cursor()

    update.message.reply_text(scl_manager.get_academy_plan(cursor))
    conn.close()


def error(bot, update, error):
    logging.warning('Update "%s" caused error "%s"' % (update, error))


dispatcher.add_handler(CommandHandler('schedule', schedule))
dispatcher.add_handler(CommandHandler('schedule_with', schedule_with))
dispatcher.add_handler(CommandHandler('academy_plan', academy_plan))
dispatcher.add_handler(CallbackQueryHandler(button))
dispatcher.add_error_handler(error)

updater.start_polling()
print('Bot is started...')

updater.idle()

