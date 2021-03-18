"""
модуль для работы с sqlite в качестве хранилища настройки бота

БД настроек состоит из следцющих таблиц
    1) таблица пользователей USERS
    2) таблица ролей (прав доступа к боту)
    3) настроек по результату выгрузки для каждого пользователя
"""

import os
import sqlite3
from enum import Enum


# доступные роли пользователя
class Role(Enum):
    admin = 1
    user = 2


# типы результата работы
class TypeResult(Enum):
    video = 1
    sound = 2


class QualityResult(Enum):
    low = 1
    medium = 2
    high = 3


# данные конкретного пользователя
class User:

    def __init__(self, id=-1):
        self._id = id
        self._name = ''
        self._active = False
        self._role = Role.user
        self._typeresult = TypeResult.sound
        self._qualityresult = QualityResult.medium

    @property
    def id(self):
        return self._id

    @id.setter
    def id(self, my_id):
        self._id = my_id

    @property
    def name(self):
        return self._name

    @name.setter
    def name(self, new_name):
        self._name = new_name

    @property
    def active(self):
        return self._active

    @active.setter
    def active(self, flag):
        if flag == 0:
            self._active = False
        else:
            self._active = True

    @property
    def role(self):
        return self._role

    @role.setter
    def role(self, new_role):
        # проверить соответствует ли new_role классу Role
        self._role = new_role

    @property
    def typeresult(self):
        return self._typeresult

    @typeresult.setter
    def typeresult(self, new_type):
        # проверить соответствует ли new_type классу TypeResult
        self._typeresult = new_type

    @property
    def qualityresult(self):
        # проверить соответствует ли new_type классу QualityResult
        return self._qualityresult

    @qualityresult.setter
    def qualityresult(self, quality):
        # проверить соответствует ли new_type классу QualityResult
        self._qualityresult = quality

    def __str__(self):
        return f"User -> id: {self.id}\n\tname: {self.name}\n\tactive: {self.active}\n\t" \
               f"role: {self._role}\n\ttyperesult: {self._typeresult}\n\tqualityresult: {self._qualityresult} "


class SettingUser:

    def __init__(self, namedb='settings.db', force=False):
        """
            нициализация БД настроек бота
                namedb - название БД
                force  - если True, то даже если БД существует, оно перезапишет его
        """
        self.db = namedb  # имя БД настроек бота
        # проверим есть ли вообще БД
        self.__createnewdb(force)

    def __createnewdb(self, force=False):
        """
            создание БД настроек бота
            возращает True, если операция создания успешно.
        """
        try:
            if os.path.exists(self.db):
                if force:
                    # print('Файл существует')
                    os.remove(self.db)
            else:
                return True

            conn = sqlite3.connect(self.db)
            cursor = conn.cursor()

            """
                Создание таблицы USER - информация о пользователях
                поля: 
                    id - id пользователя из телеграмма
                    name - имя пользователя
                    active - если 0, пользователь неактивный, иначе пользователь активный
            """
            cursor.execute("""CREATE TABLE user 
                      (id INTEGER, name text, active INTEGER)
                   """)

            """
                Создание таблицы settings  - информация о настройках бота
                поля:
                    id - id пользователя из телеграмма (связана с полем id таблицы USER 
                    role - роль пользователя: admin - администратор бота, user - обычный пользователь бота
                    typeresult - результат работы бота: видео со звуком или только звук
                    qualityresult - качество видео или звука
            """
            cursor.execute("""CREATE TABLE settings 
                      (id INTEGER, role text, typeresult text, qualityresult text)
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
    new_user = User()
    print(new_user)
    new_user.id = 458999
    new_user.name = 'TestUser'
    new_user.active = False
    print(new_user)
    # sUser = SettingUser('settings_test.db', False)
