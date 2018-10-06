# -*- coding: utf-8 -*-
import data_manager, date_manager, scl_manager
from handler import ButtonHandlerFactory
from store_manager import SettingStore
from datetime import datetime as dm
import keyboard as kb
from tbot import Bot, HandlerType
import logging
import const
import signal
import os


s_store = SettingStore()
logging.basicConfig(filename=const.root_path + '/log.txt', level=logging.INFO,
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

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
@bot.handle(name='my_id')
def my_id(bt, update):
    bot.reply(update, "Ваш ID: {}".format(update.message.from_user.id))


# CommandHandler: Расписание пар на текущий день
@bot.handle(name='s')
def schedule(bt, update):
    res = u''

    if private_chat(update.message.chat):
        id = update.message.from_user.id
    else:
        id = update.message.chat.id

    res = scl_manager.get_scl(None, id) 
    log_bot_request(update.message, 'Schedule')
    bot.reply(update, res)



# CommandHandler: Расписание пар на заданный день недели
@bot.handle(name='sb')
def schedule_with(bt, update):
    log_bot_request(update.message, 'Schedule With')
    keyboard = kb.weekday_kb(dm.now().weekday(), False)
    bot.reply(update, 'На какой день недели?', keyboard)


@bot.handle(type=HandlerType.BUTTON)
def button(bt, update):
    query = update.callback_query
    handler = ButtonHandlerFactory().get_handler(query)
    if handler and handler.ready:
        params = handler.gen_params()
        bot.send_answer(bt, params)
    elif query.data == 'ignore':
        bt.answer_callback_query(query.id, text="")


# @bot.handle(name='ll')
# def lecturers_list(bt, update):
#     log_bot_request(update.message, 'get lecturers list')
#     update.message.reply_text(data_manager.get_lecturers())


@bot.handle(name='notime')
def notify_me(bt, update):
    log_bot_request(update.message, 'Notify Me')
    msg = ''
    subscriber = data_manager.get_subscriber(update.message.chat.id)
    if subscriber is None:
        data_manager.add_subscriber(update.message.chat.id, update.message.from_user.id)
        msg = 'Теперь вам будут приходить уведомления'
    else:
        msg = 'Вы уже подписаны на уведомления'

    bot.reply(update, msg)


@bot.handle(name='unsub')
def unsubscribe(bt, update):
    log_bot_request(update.message, 'Unsubscribe')
    msg = ''
    subscriber = data_manager.get_subscriber(update.message.chat.id)
    if subscriber is not None:
        data_manager.delete_subscriber(update.message.chat.id)
        msg = 'Вам больше не будут приходить уведомления'
    else:
        msg = 'Вы не подписаны на уведомления'

    bot.reply(update, msg)


@bot.handle(name='start')
def start(bt, update):
    log_bot_request(update.message, 'Start')
    private = private_chat(update.message.chat)
    if private:
        user = data_manager.get_user(update.message.from_user.id)
    else:
        user = data_manager.get_user(update.message.chat.id)

    if user:
        keyboard = kb.menu_kb()
        bt.send_message(chat_id = update.message.chat_id, text = 'Выберите команду', reply_markup=keyboard)
    else:
        institutes = scl_manager.institutes()
        inst_kb = kb.inst_kb(institutes, private)

        res = 'Выберите институт'
        if not  private_chat(update.message.chat):
            res = 'В данный момент я нахожусь в групповом чате. Выбранная группа будет одинаковой для всех членов чата.\n' + res
        bt.send_message(chat_id = update.message.chat_id, text = res, reply_markup=inst_kb)


def private_chat(chat):
    return chat.type == 'private'   


def choose_gp(bt, update):
    private = private_chat(update.message.chat)
    # keyboard = kb.groups_kb(groups, private)

    institutes = scl_manager.institutes()
    inst_kb = kb.inst_kb(institutes, private)

    if private:
        user = data_manager.get_user(update.message.from_user.id)
    else:
        user = data_manager.get_user(update.message.chat.id)
    bot.reply(update, u'Ваша текущая группа: {}\nВыберите учебную группу'.format(user['group_name']), inst_kb)


commands = {
    u'Расписание на сегодня': schedule,
    u'Расписание на указанный день': schedule_with,
    # u'Академический план': academy_plan,
    u'Уведомлять о событиях': notify_me,
    u'Отписаться от уведомлений':unsubscribe,
    u'Выбрать группу': choose_gp
}

@bot.handle(type=HandlerType.MESSAGE)
def filter (bt, upd): 
    msg = upd.message
    if msg.reply_to_message and bot.pop_listened_msg(msg.reply_to_message) is not None:
        bot.echo_for_all(msg.text)
    else:
        upd.message.text in commands and commands[msg.text](bt, upd)


@bot.handle(name='echo')
def echo(bt, upd):
    log_bot_request(upd.message, 'Echo')
    usr = data_manager.get_user(upd.message.from_user.id)
    if usr and usr['role'] == 1 or usr['role'] == 3 or True: # 1 - admin, 3 - group master
        msg = bt.send_message(chat_id=upd.message.chat_id, text='Хорошо! Для того чтобы отправить сообщение моим пользователям, отправь его мне в ответном сообщении.')
        bot.listen_for_message(upd.message.chat_id, msg.message_id)


notified = False
def scl_notifier(bt, job):
    dm_now = date_manager.m_now()
    if dm_now.weekday() == 5:
        return

    global notified
    current_hour = dm_now.hour
    if 20 <= current_hour < 21 and not notified:
        notified = True
        for subscriber in data_manager.get_subscribers():
            bot.send_message(bt, subscriber['chat_id'], scl_manager.get_scl(date_manager.get_day_over(1), subscriber['tg_user_id']))
    elif current_hour >= 21:
        notified = False

def local_time_check():
    dm_now = date_manager.m_now()
    return dm_now.strftime("Now %d.%m.%Y %H:%M")

def main():
    print local_time_check()
    bot.polling()
    print('Bot is started...')
    scl_notifier_job = bot.add_repeating_job(scl_notifier)
    print('Schedule notifier started...')
    bot.idle()



if __name__ == '__main__':
    main()
