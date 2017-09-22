# coding=utf-8
import logging
import sqlite3

logging.basicConfig(filename='log.txt', level=logging.INFO,
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')


def users_list(conn):
    res = u"Список пользователей: \n"

    for row in conn.cursor().execute(
            "SELECT u.id, u.username, r.role_name FROM users u JOIN roles r ON u.role = r.id ").fetchall():
        res += '{}: {} (role: {})\n'.format(row[0], row[1], row[2])

    return res


def get_user(conn, tg_user_id):
    return conn.cursor().execute("SELECT id, username, tg_user_id, role FROM users WHERE tg_user_id = ?",
                                 (tg_user_id,)).fetchone()


def add_user(conn, username, tg_user_id, role):
    try:
        username = unicode(username, 'utf8')
        conn.cursor().execute("INSERT INTO users (username, tg_user_id, role) VALUES (?, ?, ?)",
                              (username, tg_user_id, role))
    except sqlite3.DatabaseError as err:
        logging.error(err)
        conn.rollback()
    else:
        conn.commit()


def delete_user(conn, id):
    try:
        conn.cursor().execute("DELETE FROM users WHERE id = (?)", (id,))
    except sqlite3.DatabaseError as err:
        logging.error(err)
        conn.rollback()
    else:
        conn.commit()


def get_lecturers(conn):
    result = u'Список преподавателей:\n\n'
    lecturers = conn.cursor().execute("""SELECT group_concat(s.name) AS subject_name,
         (SELECT l1.name
          FROM lecturer l1
            WHERE l1.id = l.id) AS lect
          FROM subjects s
          JOIN lecturer l ON s.lecture = l.id
          GROUP BY l.id""").fetchall()

    for lecturer in lecturers:
        result += lecturer[1] + ':\n'
        subjects = lecturer[0].split(",")
        for subject in subjects:
            result += subject + '\n'
        result += '\n'
    return result


def get_academy_plan(conn):
    cursor = conn.cursor()
    res = ""

    exams = cursor.execute("SELECT name FROM subjects s WHERE s.exam = 'true'").fetchall()
    res += u"Экзамены: \n"
    i = 1
    for exam in exams:
        res += str(i) + ": " + exam[0] + '\n'
        i += 1

    res += u"Всего экзаменов: " + str(i - 1) + '\n'

    res += '\n'
    credits = cursor.execute("SELECT name FROM subjects s WHERE s.exam = 'false'").fetchall()
    res += u"Зачеты: \n"
    i = 1
    for credit in credits:
        res += str(i) + ": " + credit[0] + '\n'
        i += 1

    res += u"Всего зачетов: " + str(i - 1) + '\n'

    return res
