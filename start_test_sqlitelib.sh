#!/usr/bin/bash
# запуск тестов для проверки SqliteLib
# ключ -s указывает путь где находятся
python -m unittest discover -s sqlitelib/tests/ $1