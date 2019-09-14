# -*- coding: utf-8 -*-
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, KeyboardButton, ReplyKeyboardMarkup
import calendar
import date_manager as dm

def create_calendar(year,month):
    markup = []
    #First row - Month and Year
    row=[]
    row.append(InlineKeyboardButton(calendar.month_name[month]+" "+str(year),callback_data="ignore"))
    markup.append(row)
    #Second row - Week Days
    week_days=["П","В","С","Ч","П","С","В"]
    row=[]
    for day in week_days:
        row.append(InlineKeyboardButton(day,callback_data="ignore"))
    markup.append(row)

    my_calendar = calendar.monthcalendar(year, month)
    for week in my_calendar:
        row=[]
        for day in week:
            if(day==0):
                row.append(InlineKeyboardButton(" ",callback_data="ignore"))
            else:
                row.append(InlineKeyboardButton(str(day),callback_data="calendar-day-"+str(day)))
        markup.append(row)
    #Last row - Buttons
    row=[]
    row.append(InlineKeyboardButton("<",callback_data="previous-month"))
    row.append(InlineKeyboardButton("Назад",callback_data="wd--1"))
    row.append(InlineKeyboardButton(">",callback_data="next-month"))
    markup.append(row)
    return InlineKeyboardMarkup(markup)


def weekday_kb(current_day, is_nex_week):
    pref = 'wd-'
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
                    day_name = dm.rus_week_day[current_day]

                row.append(InlineKeyboardButton(day_name, callback_data=pref + str(start_day)))
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
                    day_name = dm.rus_week_day[current_day]

                row.append(InlineKeyboardButton(day_name, callback_data=pref + str(start_day)))
                exist_days -= 1
                current_day += 1
                continue
            if exist_days > 0:
                start_day = current_day
                if is_nex_week:
                    start_day = current_day + 7
                row.append(InlineKeyboardButton(dm.rus_week_day[current_day], callback_data=pref + str(start_day)))
                exist_days -= 1
                current_day += 1

        keyboard.append(row)

    row = []
    if not is_nex_week:
        row.append(InlineKeyboardButton("➡️", callback_data=pref + '-1'))
    else:
        row.append(InlineKeyboardButton("⬅️", callback_data=pref + '-2'))

    if not is_nex_week:
        week_sql_code = '-4'
    else:
        week_sql_code = '-5'
    row.append(InlineKeyboardButton("📃", callback_data=pref + week_sql_code))

    row.append(InlineKeyboardButton("📆", callback_data='calendar-day--3'))
    keyboard.append(row)
    return InlineKeyboardMarkup(keyboard)


def menu_kb():
    markup = []
    row = []
    row.append(KeyboardButton('Расписание на сегодня'))
    row.append(KeyboardButton('Расписание на указанный день'))
    markup.append(row)

    row = []
    row.append(KeyboardButton('Уведомлять о событиях'))
    row.append(KeyboardButton('Отписаться от уведомлений'))
    markup.append(row)

    row = []
    row.append(KeyboardButton('Выбрать группу'))
    row.append(KeyboardButton('Еще'))

    markup.append(row)
    keyboard = ReplyKeyboardMarkup(markup, resize_keyboard=True)
    return keyboard


def groups_kb(groups, private_ch):
    markup = []
    row_count = int(len(groups) / 2)

    if private_ch:
        pref = 'gp-p-'
    else:
        pref = 'gp-'


    for i in range(row_count):
        gp1 = groups[i * 2]
        gp2 = groups[i * 2 + 1]
        row = []
        row.append(InlineKeyboardButton(gp1, callback_data=pref + gp1))
        row.append(InlineKeyboardButton(gp2, callback_data=pref + gp2))
        markup.append(row)

    if float(len(groups)) % 2 > 0:
        row = []
        row.append(InlineKeyboardButton(groups[len(groups) - 1], callback_data=pref + groups[len(groups) - 1]))
        markup.append(row)

    return InlineKeyboardMarkup(markup)


def inst_kb(institutes, private_ch):
    markup = []

    for i in institutes:
        if not i or i == "":
            institutes.remove(i)
    row_count = int(len(institutes) / 2)

    if private_ch:
        pref = 'inst-p-'
    else:
        pref = 'inst-'

    for i in range(row_count):
        inst1 = institutes[i * 2]
        inst2 = institutes[i * 2 + 1]
        row = []
        row.append(InlineKeyboardButton(inst1, callback_data=pref + inst1))
        row.append(InlineKeyboardButton(inst2, callback_data=pref + inst2))
        markup.append(row)

    if float(len(institutes)) % 2 > 0:
        row = []
        row.append(InlineKeyboardButton(institutes[len(institutes) - 1], callback_data=pref + institutes[len(institutes) - 1]))
        markup.append(row)

    return InlineKeyboardMarkup(markup)


def root_groups_kb(root_gps, private_ch):
    markup = []
    row_count = int(len(root_gps) / 2)
    pref = 'rgp-'

    if private_ch:
        pref = 'rgp-p-'
    else:
        pref = 'rgp-'

    for i in range(row_count):
        r_gp1 = root_gps[i * 2]
        r_gp2 = root_gps[i * 2 + 1]
        row = []
        row.append(InlineKeyboardButton(r_gp1, callback_data=pref + r_gp1))
        row.append(InlineKeyboardButton(r_gp2, callback_data=pref + r_gp2))
        markup.append(row)

    if float(len(root_gps)) % 2 > 0:
        row = []
        row.append(InlineKeyboardButton(root_gps[len(root_gps) - 1], callback_data=pref + root_gps[len(root_gps) - 1]))
        markup.append(row)

    return InlineKeyboardMarkup(markup)


def more_kb(lecturer_is_shown):
    markup = []

    row = []
    row.append(InlineKeyboardButton('Легенда', callback_data='more-legend'))
    markup.append(row)
    row = []
    if lecturer_is_shown:
        row.append(InlineKeyboardButton('Не показывать преподавателей', callback_data='more-show-lecturer'))
    else:
        row.append(InlineKeyboardButton('Показывать преподавателей', callback_data='more-hide-lecturer'))
    markup.append(row)
    return InlineKeyboardMarkup(markup)

def one_btn_kb(title, callback):
    markup = []
    row = []
    row.append(InlineKeyboardButton(title, callback_data=callback))
    markup.append(row)
    return InlineKeyboardMarkup(markup)

def poll_kb(poll_id, answeres):
    markup = []

    inc = 1
    for answer in answeres:
        ans_id = poll_id + inc
        inc += 1
        row = []
        row.append(InlineKeyboardButton(answer, callback_data='poll-' + str(poll_id) + '-' + str(ans_id)))
        markup.append(row)
    return InlineKeyboardMarkup(markup)