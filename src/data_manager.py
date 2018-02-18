# -*- coding: utf-8 -*-
import logging
import sqlite3
import const

logging.basicConfig(filename=const.root_path + '/log.txt', level=logging.INFO,
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
DB_NAME = const._db_name


def connect():
    return sqlite3.connect(DB_NAME, check_same_thread = False)

def users_list():
    conn = connect()
    users = conn.cursor().execute(
        "SELECT u.user_id, u.username, r.role_name FROM users u JOIN roles r ON u.role = r.role_id ").fetchall()
    conn.close()
    return users


def get_user(tg_user_id):
    conn = connect()
    user = conn.cursor().execute("SELECT users.username, users.tg_user_id, users.role, groups.group_name FROM users INNER JOIN groups ON users.group_id = groups.group_id WHERE users.tg_user_id = (?)",
                                 (tg_user_id, )).fetchone()
    conn.close()
    return user


def add_or_update_user(username, tg_user_id, role, group_id):
    conn = connect()
    try:
        username = unicode(username, 'utf8')
        conn.cursor().execute("INSERT OR REPLACE INTO users (username, tg_user_id, role, group_id) VALUES (?, ?, ?, ?)",
                              (username, tg_user_id, role, group_id))
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
