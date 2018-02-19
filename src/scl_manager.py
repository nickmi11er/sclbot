# -*- coding: utf-8 -*-
from openpyxl import load_workbook
from datetime import datetime
import const
import data_manager as dm
import date_manager
import re
import subprocess

pt = re.compile(r'(?:\s*([0-9]+(?:,[0-9]+)*)+\s*(н|ч)+\s*)?\s*(.+)', re.UNICODE)
wb2 = load_workbook(filename=const.assets_dir + '/scl.xlsx')
ws2 = wb2.worksheets[0]

start_dt = datetime.strptime('05.02.2018', '%d.%m.%Y')

scl_time = {
    1: "09:00-10:30",
    2: "10:40-12:10",
    3: "13:00-14:30",
    4: "14:40-16:10",
    5: "16:20-17:50",
    6: "18:00-19:30"
}

def updscl():
    subprocess.call('sh ../assets/dlscl.sh', shell=True)
    wb2 = load_workbook(filename=const.assets_dir + '/scl.xlsx')
    ws2 = wb2.worksheets[0]


# Возвращает следующий символ в алфавите для инкременты столбца таблицы
# TODO добавить логику при привышении количества букв в алфавите
def inc_col_name(col_name):
    if col_name == 'Z':
        return 'AA'
    elif len(col_name) > 1:
        return 'A' + inc_col_name(col_name[1])
    else:
        return chr(ord(col_name) + 1)


# Разбивает строку на три составляющие: 
# 1 группа - номера недель, в которых стоит предмет 
# 3 группа - название самого предмета 
# На основании переданного номера недели, возвращает название предмета
def choose_task(entity, wleft):
    entity = entity.encode('utf-8')
    res = pt.match(entity)
    if res is not None and res.group(1) is not None:
        num_weeks = re.split(r',', res.group(1))
        for num in num_weeks:
            if int(num) == int(wleft):
                return res.group(3)
    else:
        return 'kostil'
            

def _get_scl(gp_nm, date):
    date = date.replace(hour=0, minute=0, second=0, microsecond=0)
    result = []
    loaded_tasks = 0
    wleft = ((date - start_dt).days + 1) / 7 + 1    # номер текущей недели

    wdoffset = 3    # отступ по ячейкам
    # если запрашиваемый день не понедельник, добавляем смещение
    if date.weekday() != 0:
        wdoffset = wdoffset + date.weekday() * 12

    findall = False
    # перебираем учебные группы 
    for col in ws2.iter_cols(min_col=1):
        if findall:
            break
        for cell in col:
            cv = cell.value
            if cv and int(cell.row) == 2:
                if isinstance(cv, basestring):
                    cv = cv.replace(' ', '')
            # нашли нужную группу
            if cv == gp_nm:
                cc = cell.column
                # парсим расписание на запрошенный день
                # перебираем следующие 12 ячеек с шагом 2 с учетом четности недели
                for i in range(wdoffset + 1, wdoffset + 13, 2):
                    loaded_tasks += 1
                    daynum = i
                    if wleft % 2 == 0:
                        daynum = daynum + 1

                    val = ws2[cc + str(daynum)].value
                    if val is None:
                        continue
                    
                    # парсим время пары, тип занятий и аудиторию
                    time = scl_time[loaded_tasks]

                    cn = inc_col_name(cell.column)
                    fullnm = cn + str(daynum)
                    task_tp = ws2[fullnm].value
                    # если тип занятия - практика, добавляем символ восклицательного знака
                    if task_tp.encode('utf-8') == 'пр':
                        task_tp = ' ❗'
                    elif task_tp.encode('utf-8') == 'лр':
                        task_tp = ' 👩‍🔬'
                    else:
                        task_tp = ''

                    cn = inc_col_name(cn)
                    cn = inc_col_name(cn)
                    fullnm = cn + str(daynum)
                    cl_num = ws2[fullnm].value
                    if isinstance(cl_num, long) or isinstance(cl_num, float):
                        cl_num = str(int(cl_num))
                    else:
                        cl_num = cl_num.encode('utf-8')

                    # проверяем существует ли вариативность пар на один и тот же промежуток времени
                    ent = re.split(r'\n', val)
                    if len(ent) == 1:
                        res = choose_task(ent[0], wleft)
                        if res is not None:
                            if res == 'kostil':
                                res = ent[0].encode('utf-8')
                            result.append('{} {} ({}){}'.format(time, res, cl_num, task_tp))
                    # если существует вариативность, выбираем необходимый предмет
                    elif len(ent) > 1:
                        ch_flag = 0
                        for i in ent:
                            res = choose_task(i, wleft)
                            if res is not None:
                                cl_nums = re.split(r'\n', cl_num)
                                if len(cl_nums) == 2:
                                    cl_num = cl_nums[ch_flag]
                                result.append('{} {} ({}){}'.format(time, res, cl_num, task_tp))
                                break
                            ch_flag += 1
                findall = True
                break
    return result                   


def get_scl_with(dt, id):
    date = datetime.now()
    user = dm.get_user(id)
    gp_name = user[3]
    if dt is not None:
        date = dt

    if date < start_dt:
        return u'Учеба еще на началась'

    out = "Расписание пар на " + date_manager.rus_week_day[date.weekday()] + ": \n\n"
    res = _get_scl(gp_name, date)

    if res:
        for r in res:
            out = out + r + "\n"
    else:
        out = u"Пар нет. Отдыхай!"

    return out
