# -*- coding: utf-8 -*-
import logging
import sqlite3
import const

logging.basicConfig(filename=const.root_path + '/log.txt', level=logging.INFO,
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')


def users_list(conn):
    return conn.cursor().execute(
        "SELECT u.user_id, u.username, r.role_name FROM users u JOIN roles r ON u.role = r.role_id ").fetchall()


def get_user(conn, tg_user_id):
    return conn.cursor().execute("SELECT users.username, users.tg_user_id, users.role FROM users WHERE users.tg_user_id=(?)",
                                 (tg_user_id, )).fetchone()


def add_or_update_user(conn, username, tg_user_id, role, group_id):
    try:
        username = unicode(username, 'utf8')
        conn.cursor().execute("INSERT OR REPLACE INTO users (username, tg_user_id, role, group_id) VALUES (?, ?, ?, ?)",
                              (username, tg_user_id, role, group_id))
    except sqlite3.DatabaseError as err:
        logging.error(err)
        conn.rollback()
    else:
        conn.commit()


def delete_user(conn, id):
    try:
        conn.cursor().execute("DELETE FROM users WHERE user_id = (?)", (id,))
    except sqlite3.DatabaseError as err:
        logging.error(err)
        conn.rollback()
    else:
        conn.commit()


def get_lecturers():
    conn = sqlite3.connect(const.assets_dir + '/data.sqlite', check_same_thread = False)
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
    conn = sqlite3.connect(const.assets_dir + '/data.sqlite', check_same_thread = False)
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


def get_subscribers(conn):
    return conn.cursor().execute("SELECT chat_id FROM subscribers").fetchall()


def get_subscriber(conn, chat_id):
    return conn.cursor().execute("SELECT chat_id FROM subscribers WHERE chat_id = (?)", (chat_id, )).fetchone()


def add_subscriber(conn, chat_id, tg_user_id):
    try:
        conn.cursor().execute("INSERT INTO subscribers (chat_id, tg_user_id) VALUES (?, ?)", (chat_id, tg_user_id))
    except sqlite3.DatabaseError as err:
        logging.error(err)
        conn.rollback()
    else:
        conn.commit()


def delete_subscriber(conn, chat_id):
    try:
        conn.cursor().execute("DELETE FROM subscribers WHERE chat_id = (?)", (chat_id, ))
    except sqlite3.DatabaseError as err:
        logging.error(err)
        conn.rollback()
    else:
        conn.commit()


def get_meta(conn):
    return conn.cursor().execute("SELECT group_name, start_date, session_date FROM meta").fetchone()


def get_groups(conn):
    return conn.cursor().execute("SELECT groups.group_id, groups.group_name FROM groups").fetchall()

def set_group(conn, gp_id, user_id):
    try:
        conn.cursor().execute('UPDATE users SET group_id = (?) WHERE users.tg_user_id = (?)', (gp_id, user_id))
    except sqlite3.DatabaseError as err:
        logging.error(err)
        conn.rollback()
    else:
        conn.commit()


#conn = sqlite3.connect(const.assets_dir + '/data.sqlite')
#user = get_user(conn, '115694888')
#gs = get_groups(conn)
#print(gs[0][1])
    

#print(user)
