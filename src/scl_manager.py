# -*- coding: utf-8 -*-
from datetime import datetime, timedelta
import const
import date_manager
import re
from models.user import User
import urllib2
import json


class Task:
    def __init__(self, name, room, lecturer, tp, time):
        self.name = name
        self.room = room
        self.lecturer = lecturer
        self.tp = tp
        self.time = time

pt = re.compile(r'(?:(кр|)\s*([0-9]+(?:,|\s*[0-9]+)*)+\s*(н|ч)+\s*)?\s*(.+)', re.UNICODE)

_api_url = 'http://localhost:9000/'

start_dt = datetime.strptime('03.09.2018', '%d.%m.%Y')
end_dt = datetime.strptime('31.05.2019', '%d.%m.%Y')
start_holy_dt = datetime.strptime('29.05.2019', '%d.%m.%Y')

study_year = "2018-2019"

scl_time = {
    1: "09:00-10:30",
    2: "10:40-12:10",
    3: "13:00-14:30",
    4: "14:40-16:10",
    5: "16:20-17:50",
    6: "18:00-19:30"
}  
        
m_bold = lambda s: '*' + s + '*'

def get_week_scl(dt, id):
    date = date_manager.m_now()
    user = User.get(id)
    if dt:
        date = dt      

    start = date - timedelta(days=date.weekday())
    end = start + timedelta(days=6)  

    if start < start_dt:
        return u'Учеба еще на началась'  

    out = ''
    for i in range(0, 6):
        if i > 0:
            out = out + '\n'
        out = out + get_scl(date_manager.get_day_over(i, start), id)
        
    return out


def choose_tsk(entity, wleft):
    res = pt.match(entity.encode('utf-8'))
    if res and res.group(1) and res.group(2):
        num_weeks = re.split(r',', res.group(2).replace(' ', ''))
        for num in num_weeks:
            if int(num) == int(wleft):
                return None
        return res.group(4)
    elif res and res.group(2):
        num_weeks = re.split(r',', res.group(2).replace(' ', ''))
        for num in num_weeks:
            if int(num) == int(wleft):
                return res.group(4)
    elif res and res.group(4):
        return res.group(4)



def get_task(entity, wleft):
    result = None
    entities = re.split(r'\n|\/', entity)
    # Вариативности нет
    if len(entities) == 1:
        result = choose_tsk(entity, wleft)
    elif len(entities) > 1:
        for ent in entities:
            task = choose_tsk(ent, wleft)
            if task:
                result = task
    return result



def get_scl(dt, id):
    tasks = []
    date = date_manager.get_day_over(0, date_manager.m_now())
    user = User.get(id)
    if dt is not None:
        date = dt

    wleft = ((date - start_dt).days + 1) / 7 + 1  # номер текущей недели

    if date < start_dt:
        return u'Учеба еще не началась'

    if date >= end_dt:
        return u'Учеба закончилась. Удачи на сессии'

    if date >= start_holy_dt:
        return u'Летние каникулы. Отдыхай!'

    dow = date.weekday()
    if dow == 6:
        return u"Пар нет. Отдыхай!\n"
    daynum = dow
    index = 0
    if wleft % 2 == 0:
        index = 1
    
    daynum = daynum + index
    request_url = _api_url + "scl?year=" + study_year + "&group=" + user.group_name.encode("utf-8") + "&dow=" + str(dow)
    day = urllib2.urlopen(request_url).read()
    subjects = json.loads(day)["subjects"]

    for i in range(0, 12, 2):
        daynum = i
        if wleft % 2 == 0:
            daynum = daynum + 1
        s = subjects[daynum]
        sub_name = s["name"]
        sub_class = s["class"]
        sub_lecturer = s["lecturer"]
        sub_type = s["type"]
        # проверяем существует ли вариативность пар на один и тот же промежуток времени
        if sub_name == '-':
            continue

        task_name = get_task(sub_name, wleft)

        if not task_name:
            continue

        tp = ''
        if sub_type.encode('utf-8') == 'пр':
            tp = '❗'
        elif sub_type.encode('utf-8') == 'лр':
            tp = '👩‍🔬'
        else:
            tp = '▫️'

        cl = ''
        if sub_class != '-':
            cl = ' (' + sub_class.encode("utf-8") + ')'

        task = Task(task_name, cl, sub_lecturer, tp, scl_time[i / 2 + 1])
        tasks.append(task)

    out = m_bold('Расписание пар на {} ({}):'.format(date.strftime('%d.%m.%Y'), date_manager.rus_week_day[date.weekday()])) + '\n\n'
     
    if tasks:
        for t in tasks:
            out = out + t.tp + t.time + ' ' + t.name + t.room + '\n'
    else:
        out = out + "Пар нет. Отдыхай!\n"

    return out


def institutes():
    institutes = json.loads(urllib2.urlopen(_api_url + "institutes").read())
    return institutes

def root_groups(inst):
    root_gps = json.loads(urllib2.urlopen(_api_url + "rootGroups?inst="+inst.encode('utf-8')).read())
    return root_gps

def groups(root_gp):
    groups = json.loads(urllib2.urlopen(_api_url + "groups?rootGroup="+root_gp.encode('utf-8')).read())
    return groups