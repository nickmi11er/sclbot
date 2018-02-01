# coding=utf-8
import calendar
from telegram import InlineKeyboardButton, InlineKeyboardMarkup

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
    row.append(InlineKeyboardButton("Назад",callback_data="back"))
    row.append(InlineKeyboardButton(">",callback_data="next-month"))
    markup.append(row)
    return InlineKeyboardMarkup(markup)