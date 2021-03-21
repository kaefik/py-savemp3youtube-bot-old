import unittest

from sqlitelib.sqliteutils import User, Role, TypeResult, QualityResult


class TestUser(unittest.TestCase):
    """
        тесты для проверки работо объекта User - данных о пользователе
    """

    def setUp(self) -> None:
        self.user1 = User()
        self.user1.name = 'User1'
        self.user1.id = 123456
        self.user1.active = True
        self.user1.role = Role.admin
        self.user1.typeresult = TypeResult.sound
        self.user1.qualityresult = QualityResult.medium

        self.user1_copy = User()
        self.user1_copy.name = 'User1'
        self.user1_copy.id = 123456
        self.user1_copy.active = True
        self.user1_copy.role = Role.admin
        self.user1_copy.typeresult = TypeResult.sound
        self.user1_copy.qualityresult = QualityResult.medium

        self.user2 = User()
        self.user2.name = 'User2'
        self.user2.id = 654321
        self.user2.active = True
        self.user2.role = Role.user
        self.user2.typeresult = TypeResult.video
        self.user2.qualityresult = QualityResult.low

    def tearDown(self) -> None:
        pass

    def test_eq_user(self):
        """
            проверка на сравнение двух объектов User которые одинаковые по содержанию
        """
        self.assertEqual(self.user1, self.user1_copy)

    def test_no_eq_user(self):
        """
            проверка на сравнение двух объектов User которые разные по содержанию
        """
        self.assertNotEqual(self.user1, self.user2)

    def test_create_new(self):
        new_user = User(name='User1', id=123456, active=True, role=Role.admin,
                        typeresult=TypeResult.sound, qualityresult=QualityResult.medium)
        self.assertEqual(self.user1, new_user)

    def test_create_new_string_param_typeresult(self):
        """
            создание объекта User в котором typeresult передаются строками
        """
        new_user = User(name='User2', id=654321, active=True, role=Role.user,
                        typeresult='TypeResult.video', qualityresult=QualityResult.low)
        self.assertEqual(self.user2, new_user)

    def test_create_new_string_param_typeresult2(self):
        """
            создание объекта User в котором typeresult передаются строками
        """
        new_user = User()
        new_user.name = 'User2'
        new_user.id = 654321
        new_user.active = True
        new_user.role = Role.user
        new_user.typeresult = 'TypeResult.video'
        new_user.qualityresult = QualityResult.low
        self.assertEqual(self.user2, new_user)

    def test_create_new_string_param_qualityresult(self):
        """
            создание объекта User в котором qualityresult передаются строками
        """
        new_user = User(name='User2', id=654321, active=True, role=Role.user,
                        typeresult=TypeResult.video, qualityresult='QualityResult.low')
        self.assertEqual(self.user2, new_user)

    def test_create_new_string_param_qualityresult2(self):
        """
            создание объекта User в котором qualityresult передаются строками
        """
        new_user = User()
        new_user.name = 'User2'
        new_user.id = 654321
        new_user.active = True
        new_user.role = Role.user
        new_user.typeresult = TypeResult.video
        new_user.qualityresult = 'QualityResult.low'
        self.assertEqual(self.user2, new_user)

    def test_create_new_string_param_role(self):
        """
            создание объекта User в котором role передаются строками
        """
        new_user = User(name='User2', id=654321, active=True, role='Role.user',
                        typeresult=TypeResult.video, qualityresult=QualityResult.low)
        self.assertEqual(self.user2, new_user)

    def test_create_new_string_param_role2(self):
        """
            создание объекта User в котором role передаются строками
        """
        new_user = User()
        new_user.name = 'User2'
        new_user.id = 654321
        new_user.active = True
        new_user.role = 'Role.user'
        new_user.typeresult = TypeResult.video
        new_user.qualityresult = QualityResult.low
        self.assertEqual(self.user2, new_user)
        pass

        if __name__ == '__main__':
            unittest.main()
