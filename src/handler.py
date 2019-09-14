# -*- coding: utf-8 -*-
from datetime import datetime as dm
from tbot import AnsType
import scl_manager as sm
import keyboard as kb
import date_manager
import data_manager as dt
from models.user import User

current_shown_dates={}

class ButtonHandlerFactory():
    def get_handler(self, query):
        data = query.data
        if data[0:3] == 'gp-':
            return GroupButtonHandler(query)
        elif data[0:3] == 'wd-':
            return WeekdayButtonHandler(query)
        elif data[0:13] == 'calendar-day-':
            return CalendarDayButtonHandler(query)
        elif data == 'next-month' or data == 'previous-month':
            return MonthButtonHandler(query)
        elif data[0:5] == 'inst-':
            return InstituteButtonHandler(query)
        elif data[0:4] == 'rgp-':
            return RootGroupButtonHandler(query)
        elif data[0:5] == 'more-':
            return MoreButtonsHandler(query)

class ButtonHandler(object):
    def __init__(self, query):
        self.ready = False
        self.chat_id = query.message.chat_id
        self.saved_date = current_shown_dates.get(self.chat_id)
        self.params = {
            'query':query,
            'extra_msg':False,
            'type':AnsType.EDIT,
            'kb':None
        }    

    def gen_params(self):
        return self.params  
            
class PollButtonHandler(ButtonHandler):
    def __init__(self, query):
        super(PollButtonHandler, self).__init__(query)
        dat = query.data[5:]
        participants = dt.increment_poll_count(self.chat_id, dat[0:dat.index("-")], dat[dat.index("-") + 1:], query.message.message_id)

class MoreButtonsHandler(ButtonHandler):
    def __init__(self, query):
            super(MoreButtonsHandler, self).__init__(query)
            markup = None
            if query.data[5:11] == 'legend':
                self.params['text'] = '*Легенда*\n\n▫️- Лекция\n❗- Семинар\n👩‍🔬- Лабораторная\n📃- Расписание на неделю\n📆- Календарь'
            elif query.data[5:18] == 'show-lecturer':
                user = User.get(query.from_user.id)
                user.show_lecturer = True
                user.save()
                self.params['text'] = 'Теперь преподаватели будут отображаться'
            elif query.data[5:18] == 'hide-lecturer':
                user = User.get(query.from_user.id)
                user.show_lecturer = False
                user.save()
                self.params['text'] = 'Преподавателии больше не будут отображаться'
            self.params['kb'] = markup
            self.ready = True

class CalendarDayButtonHandler(ButtonHandler):
    def __init__(self, query):
        super(CalendarDayButtonHandler, self).__init__(query)
        markup = None
        if query.message.chat.type == 'private':
            id = query.from_user.id
        else:
            id = query.message.chat.id

        if int(query.data[13:]) == -3:
            now = dm.now() 
            date = (now.year,now.month)
            current_shown_dates[self.chat_id] = date
            markup = kb.create_calendar(now.year, now.month)
            res = 'Выберите дату.'
        elif self.saved_date:
            day=query.data[13:]
            date = dm.strptime('{}{}{}'.format(self.saved_date[0],int(self.saved_date[1]), int(day)), '%Y%m%d')
            res = sm.get_scl(date, id)
                
        self.params['text'] = res
        self.params['kb'] = markup
        self.ready = True


class GroupButtonHandler(ButtonHandler):
    def __init__(self, query):
        super(GroupButtonHandler, self).__init__(query)
        username = ''
        if query.data[3:5] == 'p-':
            gp_name = query.data[5:]
            user = query.message.chat
            if user.title:
                username = user.title.encode('utf-8')
        else:
            gp_name = query.data[3:]
            user = query.from_user
            if user.first_name:
                username = user.first_name.encode('utf-8')
            if user.last_name:
                username += ' {}'.format(user.last_name.encode('utf-8'))
        User.create({'username':username, 'tg_user_id':user.id, 'role':2, 'group_name':gp_name}).save()
        markup = kb.menu_kb()
        self.params['text'] = 'Группа успешно обновлена'
        self.params['extra_msg'] = True
        self.params['extra_kb'] = markup
        self.params['extra_msg_text'] = 'Теперь вы можете воспользоваться командами'
        self.ready = True


class RootGroupButtonHandler(ButtonHandler):
    def __init__(self, query):
            super(RootGroupButtonHandler, self).__init__(query)
            if query.data[4:6] == 'p-':
                private = True
                groups = sm.groups(query.data[6:])
            else:
                groups = sm.groups(query.data[4:])
                private = False

            markup = kb.groups_kb(groups, private)
            self.params['text'] = 'Выберите учебную группу'
            self.params['kb'] = markup
            self.ready = True


class InstituteButtonHandler(ButtonHandler):
    def __init__(self, query):
            super(InstituteButtonHandler, self).__init__(query)
            if query.data[5:7] == 'p-':
                private = True
                root_gps = sm.root_groups(query.data[7:])
            else:
                private = False
                root_gps = sm.root_groups(query.data[5:])

            markup = kb.root_groups_kb(root_gps, private)
            self.params['text'] = 'Выберите учебную группу'
            self.params['kb'] = markup
            self.ready = True


class MonthButtonHandler(ButtonHandler):
    def __init__(self, query):
        super(MonthButtonHandler, self).__init__(query)
        if self.saved_date:
            year,month = self.saved_date
            if query.data == 'next-month':
                month+=1
                if month>12:
                    month=1
                    year+=1
            elif query.data == 'previous-month':
                month-=1
                if month<1:
                    month=12
                    year-=1
            date = (year,month)
            current_shown_dates[self.chat_id] = date
            markup= kb.create_calendar(year,month)
            self.params['text'] = 'Выберите дату.'
            self.params['kb'] = markup
            self.ready = True


class WeekdayButtonHandler(ButtonHandler):
    def __init__(self, query):
        super(WeekdayButtonHandler, self).__init__(query)
        num = int(query.data[3:])
        markup = None
        if query.message.chat.type == 'private':
            id = query.from_user.id
        else:
            id = query.message.chat.id
        if num == -1:
            markup = kb.weekday_kb(0, True)
            text = 'На какой день недели?'
        elif num == -2:
            markup = kb.weekday_kb(dm.now().weekday(), False)
            text = 'На какой день недели?'
        elif num == -4:
            text = sm.get_week_scl(dm.now(), id)
        elif num == -5:
            text = sm.get_week_scl(date_manager.get_day_over(7), id)
        else:
            text = sm.get_scl(date_manager.get_day_over(num - dm.now().weekday()), id)
        self.params['text'] = text
        self.params['kb'] = markup
        self.ready = True
