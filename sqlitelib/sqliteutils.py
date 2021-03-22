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

    def __init__(self, id=-1, name='', active=False, role=Role.user, typeresult=TypeResult.sound,
                 qualityresult=QualityResult.medium):
        self._id = id
        self._name = name
        if active == 0:
            self._active = False
        else:
            self._active = True

        # TODO: понять как из строки перевести в тип enum без бесконечных if
        if type(role) is Role:
            self._role = role
        elif type(role) is str:
            if role == 'Role.admin':
                self._role = Role.admin
            elif role == 'Role.user':
                self._role = Role.user
        else:
            self._role = Role.user

        # TODO: понять как из строки перевести в тип enum без бесконечных if
        if typeresult == 'TypeResult.video':
            self._typeresult = TypeResult.video
        elif typeresult == 'TypeResult.sound':
            self._typeresult = TypeResult.sound
        elif type(typeresult) is TypeResult:
            self._typeresult = typeresult
        else:
            self._typeresult = TypeResult.sound

        # TODO: понять как из строки перевести в тип enum без бесконечных if
        if type(qualityresult) is QualityResult:
            self._qualityresult = qualityresult
        elif qualityresult == 'QualityResult.low':
            self._qualityresult = QualityResult.low
        elif qualityresult == 'QualityResult.medium':
            self._qualityresult = QualityResult.medium
        elif qualityresult == 'QualityResult.high':
            self._qualityresult = QualityResult.high
        else:
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
        if type(new_role) is Role:
            self._role = new_role
        elif type(new_role) is str:
            if new_role == 'Role.admin':
                self._role = Role.admin
            elif new_role == 'Role.user':
                self._role = Role.user

    @property
    def typeresult(self):
        return self._typeresult

    @typeresult.setter
    def typeresult(self, new_type):
        # проверить соответствует ли new_type классу TypeResult
        if type(new_type) is TypeResult:
            self._typeresult = new_type
        if type(new_type) is str:
            if new_type == 'TypeResult.video':
                self._typeresult = TypeResult.video
            elif new_type == 'TypeResult.sound':
                self.new_type = TypeResult.sound
            else:
                self.new_type = TypeResult.sound

    @property
    def qualityresult(self):
        # проверить соответствует ли new_type классу QualityResult
        return self._qualityresult

    @qualityresult.setter
    def qualityresult(self, quality):
        # проверить соответствует ли new_type классу QualityResult

        if type(quality) is QualityResult:
            self._qualityresult = quality
        elif type(quality) is str:
            if quality == 'QualityResult.low':
                self._qualityresult = QualityResult.low
            elif quality == 'QualityResult.medium':
                self._qualityresult = QualityResult.medium
            elif quality == 'QualityResult.high':
                self._qualityresult = QualityResult.high

    def __str__(self):
        return f"User -> id: {self.id}\t{type(self.id)}\n\tname: {self.name}\t{type(self.name)}\n\t" \
               f"active: {self.active}\t{type(self.active)}\n\t" \
               f"role: {self.role}\t{type(self.role)}\n\t" \
               f"typeresult: {self.typeresult}\t{type(self.typeresult)}\n\t" \
               f"qualityresult: {self.qualityresult}\t{type(self.qualityresult)}\n "

    def __eq__(self, other):
        if (self.id == other.id) and (self.name == other.name) and (self.active == other.active) \
                and (self.role is other.role) and (self.typeresult is other.typeresult) \
                and (self.qualityresult is other.qualityresult):
            return True
        return False


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
            возвращает: True - операция добавления пользователя удалась, False - ошибка при добавлении или пользователь существует
            тест: есть
        """
        cursor = self.connect.cursor()

        id_exist = self.is_exist_user(new_user.id)

        if id_exist:  # проверка на то что пользователь с данным id есть пользователь
            return False

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

    def is_exist_user(self, idd):
        """
            проверить есть ли БД пользователь с id
            тест: есть
        """
        result = self.get_user(idd=idd)
        if result is not None:
            return True
        else:
            return False

    def del_user(self, idd):
        """
            удаление пользователя с id
            тест: есть
        """
        cursor = self.connect.cursor()

        sqlite_delete_user = f"""DELETE from user where id = {idd}"""
        cursor.execute(sqlite_delete_user)

        sqlite_delete_setting = f"""DELETE from settings where id = {idd}"""
        cursor.execute(sqlite_delete_setting)

        self.connect.commit()
        cursor.close()
        return True

    def update_user(self, new_user):
        """
            обновить данные пользователя  User, если такого пользователя нет, то добавляется новый пользователь
            тест: есть
        """
        # """Update sqlitedb_developers set salary = 10000 where id = 4"""

        if not self.is_exist_user(new_user.id):
            self.add_user(new_user)

        cursor = self.connect.cursor()



        sqlite_update_user = f"""UPDATE user SET name ='{new_user.name}',  
                                active = {new_user.active}
                                WHERE id={new_user.id}"""
        cursor.execute(sqlite_update_user)

        sqlite_update_settings = f"""UPDATE settings SET role = '{new_user.role}',  
                                typeresult = '{new_user.typeresult}', qualityresult = '{new_user.qualityresult}'
                                WHERE id={new_user.id}"""
        cursor.execute(sqlite_update_settings)

        self.connect.commit()
        cursor.close()
        return True

    def get_user(self, idd):
        """
            получить информацию о пользователе по id
            тест: есть
        """
        result = None

        cursor = self.connect.cursor()
        sqlite_query_user = f"""SELECT * FROM user WHERE id={idd}"""
        cursor.execute(sqlite_query_user)
        result_user = cursor.fetchone()

        if result_user is None:
            return result

        sqlite_query_user = f"""SELECT * FROM settings WHERE id={idd}"""
        cursor.execute(sqlite_query_user)
        result_settings = cursor.fetchone()

        if result_settings is None:
            return result

        result = User(id=result_user[0], name=result_user[1], active=result_user[2],
                      role=result_settings[1], typeresult=result_settings[2],
                      qualityresult=result_settings[3])
        return result

    def get_all_user(self):
        """
            получить всех пользователей
            тест: есть
        """
        cursor = self.connect.cursor()
        sqlite_query_user = """SELECT * from user"""
        cursor.execute(sqlite_query_user)
        result_user = cursor.fetchall()

        sqlite_query_user = """SELECT * from settings"""
        cursor.execute(sqlite_query_user)
        result_settings = cursor.fetchall()

        result = []

        for row in result_user:
            result.append(User(id=row[0], name=row[1], active=row[2]))

        for i in range(0, len(result)):
            for row in result_settings:
                if result[i].id == row[0]:
                    result[i].role = row[1]
                    result[i].typeresult = row[2]
                    result[i].qualityresult = row[3]

        return result

    def get_user_type(self, type_user):
        """
            получение всех пользователей с типом type_user (тип Role)
            возвращает: массив пользователей, если пользователей нет, то пустой массив
            тест: есть
        """
        result = []

        cursor = self.connect.cursor()
        sqlite_query_settings = f"""SELECT * FROM settings WHERE role='{type_user}'"""
        cursor.execute(sqlite_query_settings)
        result_setting = cursor.fetchall()

        if len(result_setting) == 0:
            return result

        for row in result_setting:
            idd = row[0]

            sqlite_query_user = f"""SELECT * FROM user WHERE id={idd}"""
            cursor.execute(sqlite_query_user)
            result_user = cursor.fetchone()

            if len(result_user) == 0:
                continue

            result.append(User(id=result_user[0], name=result_user[1], active=result_user[2],
                               role=row[1], typeresult=row[2], qualityresult=row[3]))

        return result

    def fix_settings(self):
        """
            починка БД настроек пользователя,
            например каким-то образом информация о пользователе есть только в одной таблице
             User или Settings
        """
        pass


if __name__ == '__main__':
    # user1 = User()
    # user1.name = 'User1'
    # user1.id = 123456
    # user1.active = True
    # user1.role = Role.admin
    # user1.typeresult = TypeResult.sound
    # user1.qualityresult = QualityResult.medium
    #
    # user2 = User()
    # user2.name = 'User1'
    # user2.id = 123456
    # user2.active = True
    # user2.role = Role.admin
    # user2.typeresult = TypeResult.sound
    # user2.qualityresult = QualityResult.medium
    # print(user1 == user2)
    #
    # print(ord(user2.typeresult))

    # for name, member in TypeResult.__members__.items():
    #     print(name, member)

    pass
