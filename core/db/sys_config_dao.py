#!/usr/bin/python3
# -*- coding: UTF-8 -*-

import sqlite3

import os

_DB_NAME = str(__file__[:-3]) + '.db'


def init_db():
    if not os.path.exists(_DB_NAME):
        print('create db')
        conn = sqlite3.connect(_DB_NAME)
        # 创建一个Cursor:
        cursor = conn.cursor()
        # 执行一条SQL语句，创建user表:
        cursor.execute('CREATE TABLE SYS_CONFIG (KEY VARCHAR(50) PRIMARY KEY, VALUE TEXT)')

        # 继续执行一条SQL语句，插入一条记录:
        cursor.execute('INSERT INTO SYS_CONFIG (key, value) VALUES (\'update_store\', \'True\')')
        cursor.execute('INSERT INTO SYS_CONFIG (key, value) VALUES (\'update_script\', \'True\')')
        cursor.execute('INSERT INTO SYS_CONFIG (key, value) VALUES (\'notifications\', \'True\')')

        # 关闭Cursor:
        cursor.close()
        # 提交事务:
        conn.commit()
        # 关闭Connection:
        conn.close()


def load_config(key=''):
    if key == '':
        return ''

    init_db()

    conn = sqlite3.connect(_DB_NAME)
    cursor = conn.cursor()
    # 执行查询语句:
    cursor.execute('SELECT VALUE FROM SYS_CONFIG WHERE key=?', (key,))

    # 获得查询结果集:
    try:
        value = cursor.fetchall()[0][0]
    except (IOError, IndexError) as e:
        value = ''

    cursor.close()
    conn.close()

    return value


def setter(key='', value='true'):
    if key == '':
        return ''

    init_db()

    conn = sqlite3.connect(_DB_NAME)
    cursor = conn.cursor()
    # 执行查询语句:
    cursor.execute('UPDATE SYS_CONFIG SET VALUE= ? WHERE key=?', (value, key))

    cursor.close()
    conn.commit()
    conn.close()


if __name__ == '__main__':
    init_db()
