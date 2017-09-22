# coding=utf-8
from openpyxl import load_workbook
from datetime import datetime

wb = load_workbook(filename='schedule.xlsx')
ws = wb.worksheets[0]

scl_time = {
    1: "09:00-10:30",
    2: "10:40-12:10",
    3: "13:00-14:30",
    4: "14:40-16:10",
    5: "16:20-17:50",
    6: "18:00-19:30"
}


# Возвращает следующий символ в алфавите для инкременты столбца таблицы
# TODO добавить логику при привышении количества букв в алфавите
def inc_col_name(col_name):
    return chr(ord(col_name) + 1)


def schedule_time(num):
    return scl_time[num]


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
                        if isinstance(val, float):
                            val = str(val)

                        task_name += "  " + val

                    result.append(task_name)

    return result
