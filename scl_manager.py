# coding=utf-8
from openpyxl import load_workbook
from datetime import datetime

wb = load_workbook(filename='schedule.xlsx')
ws = wb.worksheets[0]

now = datetime.now()

scl_time = {
    0: "9:00-10:30",
    1: "10:40-12:10",
    2: "13:00-14:30",
    3: "14:40-16:10",
    4: "16:20-17:50",
    5: "18:00-19:30"
}


# Возвращает следующий символ в алфавите для инкременты столбца таблицы
# TODO добавить логику при привышении количества букв в алфавите
def inc_col_name(col_name):
    return chr(ord(col_name) + 1)


def schedule_time(num):
    return scl_time[num]


def get_with(time):
    time = time.replace(hour=0, minute=0, second=0, microsecond=0)
    result = []
    loaded_cells = 0
    date_is_find = False

    for column in ws.iter_cols(min_col=1):

        for cell in column:

            if cell.value:

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
                        task_name += "  " + ws[cell_name].value

                    result.append(task_name)

    return result
