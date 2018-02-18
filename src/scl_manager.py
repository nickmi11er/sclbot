# -*- coding: utf-8 -*-
from openpyxl import load_workbook
from datetime import datetime
import const
import data_manager as dm
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
                    else:
                        task_tp = ''

                    cn = inc_col_name(cn)
                    cn = inc_col_name(cn)
                    fullnm = cn + str(daynum)
                    cl_num = ws2[fullnm].value
                    if isinstance(cl_num, long) or isinstance(cl_num, float):
                        cl_num = str(cl_num)
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


## DEPRECATED
# Получение списка предметов из exel на указанный день
def get_with(time):
    time = time.replace(hour=0, minute=0, second=0, microsecond=0)
    result = []
    loaded_cells = 0
    date_is_find = False

    for column in ws.iter_cols(min_col=1):

        for cell in column:
            # если ячейка не пустая
            if cell.value:
                # если нужная дата еще не найдена, проверяем дальше
                if not date_is_find:
                    if isinstance(cell.value, datetime):
                        if time == cell.value:
                            date_is_find = True
                            continue

                if date_is_find and loaded_cells < 6:
                    loaded_cells += 1

                    if cell.value == "-":
                        continue

                    task_name = schedule_time(loaded_cells) + "     " + cell.value

                    # Если есть номер аудитории, добавляем в строку
                    cell_name = inc_col_name(cell.column) + str(cell.row)

                    if ws[cell_name].value:
                        val = ws[cell_name].value
                        if isinstance(val, float) or isinstance(val, long):
                            val = str(val)

                        task_name += "  " + val

                    result.append(task_name)

    return result


def scl_info(conn):
    meta = dm.get_meta(conn)

    time_start = datetime.strptime(meta[1], '%d.%m.%Y')
    time_now = datetime.today()
    time_end = datetime.strptime(meta[2], '%d.%m.%Y')

    weeknum = (time_now - time_start).days / 7 + 1
    percentage = str(int((float((time_now - time_start).days) / float((time_end - time_start).days)) * 100))

    res = {
        'weeknum': weeknum,
        'days': (time_end - time_now).days,
        'percentage': percentage
    }

    return res
