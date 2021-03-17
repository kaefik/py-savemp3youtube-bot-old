"""
модуль для работы с sqlite в качестве хранилища настройки бота

БД настроек состоит из следцющих таблиц
    1) таблица пользователей USERS
    2) таблица ролей (прав доступа к боту)
    3) настроек по результату выгрузки для каждого пользователя
"""

import os
import sqlite3


def createnewdb(namedb='settings.db', force=False):
    """
        создание БД настроек бота
            namedb - название БД
            force  - если True, то даже если БД существует, оно перезапишет его
        возращает True, если операция создания успешно.
    """
    try:
        if os.path.exists(namedb) and force:
            # print('Файл существует')
            os.remove(namedb)

        conn = sqlite3.connect(namedb)
        cursor = conn.cursor()

        """
            Создание таблицы USER - информация о пользователях
            поля: 
                id - id пользователя из телеграмма
                name - имя пользователя
        """
        cursor.execute("""CREATE TABLE user 
                          (id INTEGER, name text)
                       """)

        """
            Создание таблицы settings  - информация о настройках бота
            поля:
                id - id пользователя из телеграмма (связана с полем id таблицы USER 
                active - если 0, пользователь неактивный, иначе пользователь активный
                role - роль пользователя: admin - администратор бота, user - обычный пользователь бота
                typeresult - результат работы бота: видео со звуком или только звук
                qualityresult - качество видео или звука
        """
        cursor.execute("""CREATE TABLE settings 
                          (id INTEGER, active INTEGER, role text, typeresult text, qualityresult text)
                   """)
    except sqlite3.Error as error:
        print("Ошибка при подключении к sqlite", error)
        return False
    finally:
        if (conn):
            conn.close()
            # print("Соединение с SQLite закрыто")
    return True


if __name__ == '__main__':
    createnewdb('settings_test.db', True)
