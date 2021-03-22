import unittest
import os
import shutil

from sqlitelib.sqliteutils import User, SettingUser, Role, TypeResult, QualityResult


class TestSettingUser(unittest.TestCase):
    """
        Тесты для проверки работы настроек пользователя испольуя объект SettingUser
    """

    @classmethod
    def setUpClass(cls) -> None:
        cls.current_dir_test = os.path.dirname(os.path.abspath(__file__))
        cls.output_dir = cls.current_dir_test + '/db/'
        try:
            os.mkdir(cls.output_dir)
        except FileExistsError:
            shutil.rmtree(cls.output_dir, ignore_errors=False, onerror=None)
            os.mkdir(cls.output_dir)

    @classmethod
    def tearDownClass(cls):
        pass

    def setUp(self) -> None:
        self.usr = SettingUser(namedb=self.output_dir + 'settings.db', force=True)  # перед каждым тестом создаем заново

        self.user1 = User()
        self.user1.name = 'User1'
        self.user1.id = 123456
        self.user1.active = True
        self.user1.role = Role.admin
        self.user1.typeresult = TypeResult.sound
        self.user1.qualityresult = QualityResult.medium

        self.user2 = User()
        self.user2.name = 'User2'
        self.user2.id = 654321
        self.user2.active = True
        self.user2.role = Role.user
        self.user2.typeresult = TypeResult.video
        self.user2.qualityresult = QualityResult.low

        self.user3 = User()
        self.user3.name = 'User3'
        self.user3.id = 7854125
        self.user3.active = True
        self.user3.role = Role.user
        self.user3.typeresult = TypeResult.sound
        self.user3.qualityresult = QualityResult.high

    def tearDown(self) -> None:
        self.usr.close()

    def test_get_user_exist_id(self):
        """
            получение пользователя который существует
        """
        self.usr.add_user(self.user1)
        self.usr.add_user(self.user2)
        result = self.usr.get_user(self.user1.id)
        self.assertEqual(self.user1, result)

    def test_get_user_no_exist_id(self):
        """
            получение пользователя который не существует
        """
        self.usr.add_user(self.user1)
        self.usr.add_user(self.user2)
        result = self.usr.get_user(idd=1)
        self.assertEqual(result, None)

    def test_is_exist_user(self):
        """
            поиск пользователя с id который есть в таблице
        """
        self.usr.add_user(self.user1)
        self.usr.add_user(self.user2)
        result = self.usr.is_exist_user(self.user1.id)
        self.assertEqual(True, result)

    def test_is_not_exist_user(self):
        """
            поиск пользователя с id которого нет в таблице
        """
        self.usr.add_user(self.user1)
        self.usr.add_user(self.user2)
        result = self.usr.is_exist_user(idd=1)
        self.assertEqual(False, result)

    def test_get_all_user(self):
        self.usr.add_user(self.user1)
        self.usr.add_user(self.user2)
        result = self.usr.get_all_user()
        self.assertEqual(self.user1, result[0])
        self.assertEqual(self.user2, result[1])

    def test_add_user_double(self):
        """
            проверка на попытке добавить пользователя который существует
        """
        self.usr.add_user(self.user1)
        self.usr.add_user(self.user2)
        self.usr.add_user(self.user1)
        result = self.usr.get_all_user()
        self.assertEqual(2, len(result))
        self.assertEqual(self.user1.id, result[0].id)
        self.assertEqual(self.user2.id, result[1].id)

    def test_get_user_type_exist(self):
        """
            проверка на получение пользователей указанного типа, если данный тип есть в БД
        """
        self.usr.add_user(self.user3)
        self.usr.add_user(self.user1)
        self.usr.add_user(self.user2)

        result = self.usr.get_user_type(Role.user)
        self.assertEqual(2, len(result))

    def test_get_user_type_no_exist(self):
        """
            проверка на получение пользователей указанного типа, если данного типа нет в БД
        """
        self.usr.add_user(self.user3)
        self.usr.add_user(self.user2)
        result = self.usr.get_user_type(Role.admin)
        self.assertEqual(0, len(result))

    def test_del_user_exist(self):
        """
            удаление пользователя по id который есть в БД
        """
        self.usr.add_user(self.user3)
        self.usr.add_user(self.user1)
        self.usr.add_user(self.user2)

        idd = self.user1.id
        self.usr.del_user(idd)
        result = self.usr.is_exist_user(idd)

        self.assertEqual(False, result)

    def test_del_user_no_exist(self):
        """
            удаление пользователя по id которого нет в БД
        """
        self.usr.add_user(self.user3)
        self.usr.add_user(self.user1)
        self.usr.add_user(self.user2)

        idd = 555555
        self.usr.del_user(idd)
        result = self.usr.get_all_user()

        self.assertEqual(3, len(result))

    def test_update_user_exist(self):
        """
            обновление информации о пользователе
        """
        self.usr.add_user(self.user3)
        self.usr.add_user(self.user1)
        self.usr.add_user(self.user2)

        user4 = User(id=self.user2.id, name='User4', active=False, role=Role.admin,
                     typeresult=TypeResult.sound, qualityresult=QualityResult.low)

        self.usr.update_user(user4)

        result = self.usr.get_all_user()
        self.assertEqual(3, len(result))

        result_user = self.usr.get_user(user4.id)
        self.assertEqual(user4, result_user)

    def test_update_user_no_exist(self):
        """
            обновление информации о пользователе которого нет, то есть добавляет нового пользователя
        """
        self.usr.add_user(self.user3)
        self.usr.add_user(self.user1)
        self.usr.add_user(self.user2)

        user4 = User(id=555555, name='User4', active=False, role=Role.admin,
                     typeresult=TypeResult.sound, qualityresult=QualityResult.low)

        self.usr.update_user(user4)

        result = self.usr.get_all_user()
        self.assertEqual(4, len(result))

        result_user = self.usr.get_user(user4.id)
        self.assertEqual(user4, result_user)


if __name__ == '__main__':
    unittest.main()
