# coding=utf-8
import datetime

rus_week_day = {
    0: "Понедельник",
    1: "Вторник",
    2: "Среда",
    3: "Четверг",
    4: "Пятница",
    5: "Суббота",
    6: "Восскресенье"
}

today = datetime.datetime.now()


def get_day_over(count):
    return today + datetime.timedelta(days=count)
