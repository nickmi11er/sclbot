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
    row.append(KeyboardButton('Академический план'))
    row.append(KeyboardButton('Уведомлять о событиях'))
    markup.append(row)

    row = []
    row.append(KeyboardButton('Отписаться от уведомлений'))
    row.append(KeyboardButton('Выбрать группу'))
    markup.append(row)
    keyboard = ReplyKeyboardMarkup(markup, resize_keyboard=True)
    return keyboard


def groups_kb(groups, private_ch):
    murkup = []

    if private_ch:
        pref = 'gp-'
    else:
        pref = 'gp-p-'
    
    for g in groups:
        row = []
        row.append(InlineKeyboardButton(g['group_name'], callback_data=pref + str(g['group_id'])))
        murkup.append(row)

    return InlineKeyboardMarkup(murkup)