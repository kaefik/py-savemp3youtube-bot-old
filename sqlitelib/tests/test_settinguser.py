import unittest

from sqlitelib.sqliteutils import User, SettingUser, Role, TypeResult, QualityResult


class TestSettingUser(unittest.TestCase):
    """
        Тесты для проверки работы настроек пользователя испольуя объект SettingUser
    """

    @classmethod
    def setUpClass(cls) -> None:
        pass

    @classmethod
    def tearDownClass(cls):
        pass

    def setUp(self) -> None:
        self.usr = SettingUser(force=True)  # перед каждым тестом создаем заново

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


if __name__ == '__main__':
    unittest.main()
