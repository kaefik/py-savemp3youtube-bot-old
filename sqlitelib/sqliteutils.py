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
        self.connect = self.__createnewdb(force)  # конект в БД

    def open(self):
        """
            открыть файл настроек
        """
        try:
            conn = sqlite3.connect(self.db)
        except sqlite3.Error as error:
            print("Ошибка при подключении к sqlite", error)
            return False
        finally:
            return True

    def close(self):
        """
            закрытие коннекта к БД
        """
        if not (self.connect is None):
            self.connect.close()

    def __createnewdb(self, force=False):
        """
            создание БД настроек бота
            возвращает True, если операция создания успешно.
        """
        try:
            if os.path.exists(self.db):
                if force:
                    # print('Файл существует')
                    os.remove(self.db)
                else:
                    connect = sqlite3.connect(self.db)
                    return connect

            connect = sqlite3.connect(self.db)
            cursor = connect.cursor()

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

        return connect

    def add_user(self, new_user):
        """
            добавление нового пользователя new_user (тип User)

        """
        cursor = self.connect.cursor()
        sqlite_insert_query_user = f"""INSERT INTO user
                                  (id, name, active)
                                  VALUES
                                  ({new_user.id}, '{new_user.name}', {new_user.active});"""
        cursor.execute(sqlite_insert_query_user)

        sqlite_insert_query_settings = f"""INSERT INTO settings
                                          (id, role, typeresult, qualityresult)
                                          VALUES
                                          ({new_user.id}, '{new_user.role}', '{new_user.typeresult}', '{new_user.qualityresult}');"""
        cursor.execute(sqlite_insert_query_settings)
        self.connect.commit()
        cursor.close()
        return True

    def del_user(self, id):
        """
            удаление пользователя с id
        """
        pass

    def update_user(self, new_user):
        """
            обновить данные пользователя  User, если такого пользователя нет, то добавляется новый пользователь
        """
        pass

    def get_user(self, id):
        """
            получить информацию о пользователе по id
        """
        pass

    def get_all_user(self):
        """
            получить всех пользователей
        """
        pass

    def get_user_type(self, type_user):
        """
            получение всех пользователей с типом type_user (тип Role)
        """
        pass


if __name__ == '__main__':
    new_user = User()
    print(new_user)
    new_user.id = 458999
    new_user.name = 'TestUser'
    new_user.active = True
    print(new_user)

    usr = SettingUser()
    usr.add_user(new_user)
    usr.close()
