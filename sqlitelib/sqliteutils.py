"""
модуль для работы с sqlite в качестве хранилища настройки бота

БД настроек состоит из следцющих таблиц
    1) таблица пользователей USERS
    2) таблица ролей (прав доступа к боту)
    3) настроек по результату выгрузки для каждого пользователя
"""

import os
import sqlite3


# import shutil


def createnewdb(namedb='settings.db', force=False):
    """
        создание БД настроек бота
            namedb - название БД
            force  - если True, то даже если БД существует, оно перезапишет его
    """

    if os.path.exists(namedb) and force:
        # print('Файл существует')
        os.remove(namedb)

    conn = sqlite3.connect(namedb)
    cursor = conn.cursor()

    # Создание таблицы USER - информация о пользователях
    cursor.execute("""CREATE TABLE user 
                      (id INTEGER, name text)
                   """)

    # Создание таблицы settings  - информация о настройках бота
    cursor.execute("""CREATE TABLE settings 
                      (id INTEGER, role text, typeresult text, qualityresult text)
                   """)
    return True


if __name__ == '__main__':
    createnewdb('settings_test.db', True)
