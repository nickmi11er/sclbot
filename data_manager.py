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


conn = sqlite3.connect('data.sqlite')
print(users_list(conn))
