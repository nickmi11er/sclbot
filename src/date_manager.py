# -*- coding: utf-8 -*-
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


def get_day_over(count):
    return datetime.datetime.now() + datetime.timedelta(days=count)
