# -*- coding: utf-8 -*-
import logging
import sqlite3
from const import DB_PATH, SCHEMA_PATH, LOG_PATH
import os.path
import os
from cache_manager import Cache

def dict_factory(cursor, row):
    d = {}
    for idx, col in enumerate(cursor.description):
        d[col[0]] = row[idx]
    return d

logging.basicConfig(filename=LOG_PATH, level=logging.INFO,
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
if not os.path.isfile(DB_PATH): 
    open(DB_PATH, 'a')
    os.system('sqlite3 ' + DB_PATH + ' < ' + SCHEMA_PATH)


def connect():
    conn = sqlite3.connect(DB_PATH, check_same_thread = False)
    conn.row_factory = dict_factory
    return conn
        

def users_list():
    conn = connect()
    users = conn.cursor().execute(
        "SELECT users.username, users.tg_user_id, users.role, groups.group_name, groups.group_id FROM users INNER JOIN groups ON users.group_id = groups.group_id").fetchall()
    conn.close()
    return users


def get_user(tg_user_id, flush=False):
    conn = connect()
    user = conn.cursor().execute("SELECT users.username, users.tg_user_id, users.role, groups.group_name, groups.group_id FROM users INNER JOIN groups ON users.group_id = groups.group_id WHERE users.tg_user_id = (?)",
                                 (tg_user_id, )).fetchone()
    conn.close()
    return user


def add_or_update_user(username, tg_user_id, role, group_id, show_lecturer):
    conn = connect()
    try:
        try:
            username = unicode(username, 'utf8')
        except TypeError:
            pass
        conn.cursor().execute("INSERT OR REPLACE INTO users (username, tg_user_id, role, group_id, show_lecturer) VALUES (?, ?, ?, ?, ?)",
                              (username, tg_user_id, role, group_id, show_lecturer))
    except sqlite3.DatabaseError as err:
        logging.error(err)
        conn.rollback()
    else:
        conn.commit()
    conn.close()


def delete_user(id):
    conn = connect()
    try:
        conn.cursor().execute("DELETE FROM users WHERE user_id = (?)", (id,))
    except sqlite3.DatabaseError as err:
        logging.error(err)
        conn.rollback()
    else:
        conn.commit()
    conn.close()


def get_lecturers():
    conn = connect()
    result = u'Список преподавателей:\n\n'
    lecturers = conn.cursor().execute("""SELECT group_concat(s.subj_name) AS subject_name,
                                             (SELECT l1.lecturer_name
                                              FROM lecturer l1
                                                WHERE l1.lecturer_id = l.lecturer_id) AS lect
                                              FROM subjects s
                                              JOIN lecturer l ON s.lecture = l.lecturer_id
                                              GROUP BY l.lecturer_id""").fetchall()

    for lecturer in lecturers:
        result += lecturer[1] + ':\n'
        subjects = lecturer[0].split(",")
        for subject in subjects:
            result += subject + '\n'
        result += '\n'
    conn.close()
    return result


def get_academy_plan():
    conn = connect()
    cursor = conn.cursor()
    res = ""

    exams = cursor.execute("SELECT subj_name FROM subjects s WHERE s.exam = 'true'").fetchall()
    res += u"Экзамены: \n"
    i = 1
    for exam in exams:
        res += str(i) + ": " + exam[0] + '\n'
        i += 1

    res += u"Всего экзаменов: " + str(i - 1) + '\n'

    res += '\n'
    credits = cursor.execute("SELECT subj_name FROM subjects s WHERE s.exam = 'false'").fetchall()
    res += u"Зачеты: \n"
    i = 1
    for credit in credits:
        res += str(i) + ": " + credit[0] + '\n'
        i += 1

    res += u"Всего зачетов: " + str(i - 1) + '\n'
    conn.close()
    return res


def get_subscribers():
    conn = connect()
    subs = conn.cursor().execute("SELECT chat_id, tg_user_id FROM subscribers").fetchall()
    conn.close()
    return subs


def get_subscriber(chat_id):
    conn = connect()
    sub = conn.cursor().execute("SELECT chat_id FROM subscribers WHERE chat_id = (?)", (chat_id, )).fetchone()
    conn.close()
    return sub


def add_subscriber(chat_id, tg_user_id):
    conn = connect()
    try:
        conn.cursor().execute("INSERT INTO subscribers (chat_id, tg_user_id) VALUES (?, ?)", (chat_id, tg_user_id))
    except sqlite3.DatabaseError as err:
        logging.error(err)
        conn.rollback()
    else:
        conn.commit()
    conn.close()


def delete_subscriber(chat_id):
    conn = connect()
    try:
        conn.cursor().execute("DELETE FROM subscribers WHERE chat_id = (?)", (chat_id, ))
    except sqlite3.DatabaseError as err:
        logging.error(err)
        conn.rollback()
    else:
        conn.commit()
    conn.close()


def get_meta():
    conn = connect()
    meta = conn.cursor().execute("SELECT group_name, start_date, session_date FROM meta").fetchone()
    conn.close()
    return meta


def get_groups():
    conn = connect()
    gps = conn.cursor().execute("SELECT groups.group_id, groups.group_name FROM groups").fetchall()
    conn.close()
    return gps


def set_group(gp_id, user_id):
    conn = connect()
    try:
        conn.cursor().execute('UPDATE users SET group_id = (?) WHERE users.tg_user_id = (?)', (gp_id, user_id))
    except sqlite3.DatabaseError as err:
        logging.error(err)
        conn.rollback()
    else:
        conn.commit()
    conn.close()


def get_group_by_id(gp_id):
    conn = connect()
    gp = conn.cursor().execute("SELECT groups.group_id, groups.group_name FROM groups WHERE group_id = (?)", (gp_id, )).fetchone()
    conn.close()
    return gp

def get_group_by_name(gp_name):
    conn = connect()
    gp = conn.cursor().execute("SELECT groups.group_id, groups.group_name FROM groups WHERE group_name = (?)", (gp_name, )).fetchone()
    conn.close()
    return gp

def add_group(gp_name):
    conn = connect()
    gp_id = None
    try:
        cursor = conn.cursor()
        cursor.execute("INSERT INTO groups (group_name) VALUES (?)", (gp_name, ))
        gp_id = cursor.lastrowid
    except sqlite3.DatabaseError as err:
        logging.error(err)
        conn.rollback()
    else:
        conn.commit()
    conn.close()
    return gp_id

def _add_poll(cursor, p_id, question, answeres):
    cursor.execute("INSERT INTO polls (poll_id, question) VALUES (?, ?)", (p_id, question))
    poll_id = cursor.lastrowid
    inc = 1
    for answer in answeres:
        ans_id = poll_id + inc
        inc += 1
        cursor.execute("INSERT INTO poll_answeres (answer_id, poll_id, answer) VALUES (?, ?, ?)", (ans_id, poll_id, answer))
    return poll_id

def add_poll(p_id, question, answeres):
    conn = connect()
    poll_id = None
    try:
        cursor = conn.cursor()
        _add_poll(cursor, p_id, question, answeres)
    except sqlite3.DatabaseError as err:
        logging.error(err)
        conn.rollback()
    else:
        conn.commit()
    conn.close()
    return poll_id

def add_throne_pretender(user_id, p_id):
    conn = connect()
    try:
        cursor = conn.cursor()
        poll_id = _add_poll(cursor, p_id, 'Сделать ' + user_id + ' мастером группы', ['Да', 'Нет'])
        cursor.execute("INSERT INTO throne_pretenders (tg_user_id, poll_id) VALUES (?, ?)", (user_id, poll_id))
    except sqlite3.DatabaseError as err:
        logging.error(err)
        conn.rollback()
    else:
        conn.commit()
    conn.close()

def increment_poll_count(user_id, poll_id, answer_id, message_id):
    conn = connect()
    participants = []
    is_participate = False
    try:
        cursor = conn.cursor()
        participants = cursor.execute("SELECT user_id, answer_id FROM poll_participants WHERE poll_id = (?)", (poll_id, )).fetchall()
        for participant in participants:
            if user_id == participant['user_id']:
                is_participate = True
        if not is_participate:
            cursor.execute("UPDATE poll_answeres SET count = count + 1 WHERE answer_id = (?)", (answer_id, ))
            cursor.execute("INSERT INTO poll_participants (poll_id, user_id, answer_id, message_id) VALUES (?, ?, ?, ?)", (poll_id, user_id, answer_id, message_id))
    except sqlite3.DatabaseError as err:
        logging.error(err)
        conn.rollback()
    else:
        conn.commit()
    conn.close()
    if not is_participate:
        return participants
    else:
         return None

def get_classmates_ids(user_id):
    conn = connect()
    ids = conn.cursor().execute("SELECT ").fetchall()

    return ids

# print(increment_poll_count("363242536", 3, 6, "14532345"))


# def scl_info(conn):
#     meta = dm.get_meta(conn)

#     time_start = datetime.strptime(meta[1], '%d.%m.%Y')
#     time_now = datetime.today()
#     time_end = datetime.strptime(meta[2], '%d.%m.%Y')

#     weeknum = (time_now - time_start).days / 7 + 1
#     percentage = str(int((float((time_now - time_start).days) / float((time_end - time_start).days)) * 100))

#     res = {
#         'weeknum': weeknum,
#         'days': (time_end - time_now).days,
#         'percentage': percentage
#     }

#     return res

q = """
SELECT subjects.subj_name 
FROM   (WITH recursive list( element, remainder ) AS 
       ( 
              SELECT NULL AS element, 
                     ( 
                            SELECT wt.subj_ids
                            FROM   work_type AS wt 
                            WHERE  w_type = 2 and group_id = 1) AS remainder 
              UNION ALL 
              SELECT 
                     CASE 
                            WHEN instr( remainder, ',' )>0 THEN substr( remainder, 0, instr( remainder, ',' ) )
                            ELSE remainder 
                     END AS element, 
                     CASE 
                            WHEN instr( remainder, ',' )>0 THEN substr( remainder, instr( remainder, ',' )+1 )
                            ELSE NULL 
                     END AS remainder 
              FROM   list 
              WHERE  remainder IS NOT NULL )SELECT element 
FROM   list 
WHERE  element IS NOT NULL) AS sjs 
JOIN   subjects 
ON     sjs.element = subjects.subject_id"""
