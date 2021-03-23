"""
 Версия телеграмм бота с использованием библиотеки Telethon

"""

import os
# pip3 install python-dotenv
from dotenv import load_dotenv
# pip3 install Telethon
from telethon import TelegramClient, events, connection, Button
import asyncio
import logging
import re

from i_utils import run_cmd
from sqlitelib.sqliteutils import User, SettingUser, Role, TypeResult, QualityResult

# ---- Начальные данные ----
path_mp3 = "mp3"
"""
level=logging.CRITICAL  # won't show errors (same as disabled)
level=logging.ERROR     # will only show errors that you didn't handle
level=logging.WARNING   # will also show messages with medium severity, 
                        # such as internal Telegram issues
level=logging.INFO      # will also show informational messages, 
                        # such as connection or disconnections
level=logging.DEBUG     # will show a lot of output to help debugging 
                        # issues in the library
"""

logging.basicConfig(format='[%(levelname) 5s/%(asctime)s] %(name)s: %(message)s',
                    level=logging.WARNING)
logging.getLogger('asyncio').setLevel(logging.ERROR)

dotenv_path = os.path.join(os.path.dirname(__file__), ".env")
# print((dotenv_path))
if os.path.exists(dotenv_path):
    load_dotenv(dotenv_path)
app_api_id = os.getenv("TLG_APP_API_ID")
app_api_hash = os.getenv("TLG_APP_API_HASH")
app_name = os.getenv("TLG_APP_NAME")
bot_token = os.getenv("I_BOT_TOKEN")
proxy_server = os.getenv("TLG_PROXY_SERVER")
proxy_port = os.getenv("TLG_PROXY_PORT")
proxy_key = os.getenv("TLG_PROXY_KEY")
# клиент с правами администратора
admin_client = int(os.getenv("TLG_ADMIN_ID_CLIENT"))

print(admin_client)

# настройки бота
name_file_settings = 'settings.db'
if not os.path.exists(name_file_settings):
    print('нет файла настроек')
    name_admin = 'User1'  # TODO: сделать получение имени пользователя
    settings = SettingUser(namedb=name_file_settings)
    admin_User = User(id=admin_client, role=Role.admin)
    settings.add_user(admin_User)
else:
    print('есть файл настроек')
    settings = SettingUser(namedb=name_file_settings)

# получение всех пользователей из БД
# clients = settings.get_all_user()  # список всех клиентов
admin_client = settings.get_user_type(Role.admin)  # список администраторов бота
# END настройки бота


if proxy_server is None or proxy_port is None or proxy_key is None:
    print("Нет настроек MTProto прокси сервера телеграмма.\n" \
          "Попытка подключения клиента без прокси.")
    bot = TelegramClient(app_name, app_api_id, app_api_hash).start(
        bot_token=bot_token
    )
else:
    proxy = (proxy_server, int(proxy_port), proxy_key)
    bot = TelegramClient(app_name, app_api_id, app_api_hash,
                         connection=connection.ConnectionTcpMTProxyRandomizedIntermediate,
                         proxy=proxy).start(bot_token=bot_token)

# получаем текст для помощи о командах бота
help_text = ""
with open("help.txt", "r") as f:
    help_text = f.read()

# флаг режима администратора
flag_admin = False

button_main = [
    [Button.text("/help"), Button.text("/admin")]
]

button_admin = [
    [Button.text("/AddUser"),
     Button.text("/DelUser"),
     Button.text("/InfoUser"),
     Button.text("/ExitAdmin")]
]

db_user_bot = "db_user_allow.txt"
rexp_http_url = r"https?:\/\/(www\.)?[-a-zA-Z0-9@:%._\+~#=]{2,256}\.[a-z]{2,6}\b([-a-zA-Z0-9@:%_\+.~#?&//=]*)"


# ---- END Начальные данные ----

# ----- Вспомогательные функции
# проверка на разрешенного пользователя
def is_allow_user(iduser, allow_users):
    for user in allow_users:
        if user.id == iduser:
            return True
    return False


# добавляем пользователя в БД пользователей которые имеют доступ к боту
# возвращает True 
def add_new_user(id, settings):
    name = 'New User'  # # TODO: сделать получение имени пользователя
    new_user = User(id=id, name=name)
    settings.add_user(new_user)
    return True


# возвращает список пользователей которые имеют доступ к боту
def read_user_db(settings):
    result = []
    clients = settings.get_all_user()
    for cl in clients:
        result.append(cl.id)
    return result


# ----- END Вспомогательные функции

@bot.on(events.CallbackQuery)
async def handler(event):
    await event.answer('You clicked {}!'.format(event.data))


@bot.on(events.NewMessage(pattern='/start'))
async def start(event):
    sender = await event.get_sender()
    # проверка на право доступа к боту
    sender_id = sender.id
    if not is_allow_user(sender_id, settings.get_all_user()):
        await event.respond(f"Доступ запрещен. Обратитесь к администратору" \
                            f" чтобы добавил ваш ID в белый список. Ваш ID {sender_id}")
        return
    # END проверка на право доступа к боту
    await event.respond(f"Привет, {sender.first_name}! Я рад видеть тебя!\n" \
                        "Пришли мне ссылку на клип ютуба, обратно получите его аудио дорожку.",
                        buttons=[[Button.text("/help"), Button.text("/admin")]]
                        )
    raise events.StopPropagation


@bot.on(events.NewMessage(pattern='/about'))
async def about(event):
    sender = await event.get_sender()
    # проверка на право доступа к боту
    sender_id = sender.id
    if not is_allow_user(sender_id, settings.get_all_user()):
        await event.respond(f"Доступ запрещен. Обратитесь к администратору" \
                            f" чтобы добавил ваш ID в белый список. Ваш ID {sender_id}")
        return
    # END проверка на право доступа к боту
    await event.respond("Я конвертирую youtube клип в mp3.")


@bot.on(events.NewMessage(pattern='/delmp3'))
async def clear_all_mp3(event):
    sender = await event.get_sender()
    # проверка на право доступа к боту
    sender_id = sender.id
    if not is_allow_user(sender_id, settings.get_all_user()):
        await event.respond(f"Доступ запрещен. Обратитесь к администратору" \
                            f" чтобы добавил ваш ID в белый список. Ваш ID {sender_id}")
        return
    # END проверка на право доступа к боту
    await event.respond("Очистка папки mp3 от файлов...")
    # TODO: сделать удаление файлов
    user_folder = str(sender.id)
    folder_mp3 = f"{path_mp3}/{user_folder}"

    done, pending = await asyncio.wait([
        run_cmd(f"ls {folder_mp3}")
    ])

    # result - результат выполнения команды cmds
    # error - ошибка, если команда cmds завершилась с ошибкой
    # code - код работы команды, если 0 , то команда прошла без ошибок
    result, error, code = done.pop().result()

    if code != 0:
        await event.respond(error.decode("utf8"))

    result = result.decode("utf8")
    if len(result) == 0:
        await event.respond("Файлов на удаления нет.")
        return
    # print("RESULT LS = ", result)
    # print("result = ", result)
    await event.respond(result)

    done, pending = await asyncio.wait([
        run_cmd(f"rm -f {folder_mp3}/*")
    ])

    result, error, code = done.pop().result()

    if code != 0:
        await event.respond(error.decode("utf8"))

    result = result.decode("utf8")
    # print("result = ", result)
    # await event.respond(result)

    await event.respond("Очистка завершена.")


@bot.on(events.NewMessage(pattern='/help'))
async def help(event):
    sender = await event.get_sender()
    # проверка на право доступа к боту
    sender_id = sender.id
    if not is_allow_user(sender_id, settings.get_all_user()):
        await event.respond(f"Доступ запрещен. Обратитесь к администратору" \
                            f" чтобы добавил ваш ID в белый список. Ваш ID {sender_id}")
        return
    # END проверка на право доступа к боту
    await event.respond(help_text)


# получение урл
@bot.on(events.NewMessage(
    pattern=r".*\n*" + rexp_http_url)
)
async def get_mp3_from_youtube(event):
    print("get_mp3_from_youtube start subprocess begin")
    sender = await event.get_sender()
    # проверка на право доступа к боту
    sender_id = sender.id
    if not is_allow_user(sender_id, settings.get_all_user()):
        await event.respond(f"Доступ запрещен. Обратитесь к администратору" \
                            f" чтобы добавил ваш ID в белый список. Ваш ID {sender_id}")
        return
    # END проверка на право доступа к боту

    # chat = await event.get_input_chat()
    sender = await event.get_sender()
    # buttons = await event.get_buttons()
    # print(sender.id)
    user_folder = str(sender.id)
    # print(event.raw_text)
    # выделение урл из общей массы сообщения
    match = re.search(rexp_http_url, event.raw_text)
    url_youtube = match.group()
    print(url_youtube)
    await event.respond("Начало конвертации ютуб клипа в mp3...")
    # print("get_mp3_from_youtube start subprocess begin")
    cmds = f'youtube-dl --extract-audio --audio-format mp3 ' \
           f'--output "{path_mp3}/{user_folder}/%(title)s.%(ext)s" {url_youtube}'
    # print(cmds)

    done, _ = await asyncio.wait([
        run_cmd(cmds)
    ])

    # result - результат выполнения команды cmds
    # error - ошибка, если команда cmds завершилась с ошибкой
    # code - код работы команды, если 0 , то команда прошла без ошибок
    result, error, code = done.pop().result()

    if code != 0:
        await event.respond(f"!!!! код: {code} \n" \
                            f"Внутреняя ошибка: {error}")
        return

    result = result.decode("utf-8")
    str_result = result.split("\n")
    str_search = "[ffmpeg] Destination:"
    file_mp3 = ""
    for s in str_result:
        if str_search in s:
            file_mp3 = s[len(str_search):].strip()
            break

    await event.respond("mp3 файл скачан...будем делить на части")
    # деление mp3 файла на части, если нужно с помощью команды mp3splt
    timesplit = "59.0"  # длительность каждой части формат: минуты.секунда
    cmds2 = f'mp3splt -t {timesplit} "{file_mp3}"'

    # print(cmds)

    done2, _ = await asyncio.wait([
        run_cmd(cmds2)
    ])

    # result - результат выполнения команды cmds
    # error - ошибка, если команда cmds завершилась с ошибкой
    # code - код работы команды, если 0 , то команда прошла без ошибок
    result2, error2, code2 = done2.pop().result()

    if code2 != 0:
        await event.respond(f"!!!! код: {code2} \n" \
                            f"Внутреняя ошибка: {error2}")
        return

    result2 = result2.decode("utf-8")
    str_result2 = result2.split("\n")
    str_search2 = "File"
    files_mp3 = []
    for s in str_result2:
        if str_search2 in s:
            ss = s[s.index('"') + 1:]
            files_mp3.append(ss[:ss.index('"')].strip())

    try:
        await event.respond(f"Результат конвертации:")
        for el in files_mp3:
            await event.respond(file=el)

    except FileNotFoundError:
        await event.respond(f"Вывод результат команды {cmds}:\n {result}")
        await event.respond("Внутреняя ошибка: или урл не доступен, " \
                            "или конвертация невозможна.\n" \
                            "Попробуйте позже или другую ссылку.")
    except Exception as err:
        # print("!!!! Внутреняя ошибка: ", err)
        await event.respond(f"!!!! Внутреняя ошибка: {err}")
    # END сделать конвертирование в mp3
    await event.respond("Конец конвертации!")


@bot.on(events.NewMessage(pattern='/admin'))
async def admin(event):
    sender = await event.get_sender()
    # проверка на право доступа к боту
    sender_id = sender.id
    if not is_allow_user(sender_id, admin_client):
        await event.respond(f"Доступ запрещен. Обратитесь к администратору" \
                            f" чтобы добавил ваш ID в белый список. Ваш ID {sender_id}")
        return
    # END проверка на право доступа к боту
    flag_admin = True
    await event.respond("Вы вошли в режим администратора",
                        buttons=button_admin
                        )


@bot.on(events.NewMessage(pattern='/AddUser'))
async def adduser_admin(event):
    """
    if not flag_admin:
        await event.respond("Войдите в режим администратора.")
        return
    """
    sender = await event.get_sender()
    # проверка на право доступа к боту
    sender_id = sender.id
    if not is_allow_user(sender_id, admin_client):
        await event.respond(f"Доступ запрещен. Обратитесь к администратору" \
                            f" чтобы добавил ваш ID в белый список. Ваш ID {sender_id}")
        return
    # END проверка на право доступа к боту
    await event.respond("Выполняется команда /AddUSer")
    # диалог с запросом информации нужной для работы команды /AddUser
    chat_id = event.chat_id
    async with bot.conversation(chat_id) as conv:
        # response = conv.wait_event(events.NewMessage(incoming=True))
        await conv.send_message("Привет! Введите номер id пользователя" \
                                "который нужно добавить для доступа к боту:")
        id_new_user = await conv.get_response()
        id_new_user = id_new_user.message
        # print("id_new_user ", id_new_user)
        while not all(x.isdigit() for x in id_new_user):
            await conv.send_message("ID нового пользователя - это число. Попробуйте еще раз.")
            id_new_user = await conv.get_response()
            id_new_user = id_new_user.message
        # print("id_new_user ", id_new_user)

        # получаем информацию о пользователе
        try:
            new_nameuser = await event.client.get_entity(int(id_new_user))
            new_nameuser = new_nameuser.username
        except ValueError as err:
            print('Ошибка получения информации о пользователе по id: ', err)
            new_nameuser = ''

        print('Имя нового пользователя', new_nameuser)
        add_new_user(id_new_user, settings)
        await conv.send_message(f"Добавили нового пользователя с ID: {id_new_user} с именем {new_nameuser}")


@bot.on(events.NewMessage(pattern='/DelUser'))
async def deluser_admin(event):
    """
    if not flag_admin:
        await event.respond("Войдите в режим администратора.")
        return
    """
    sender = await event.get_sender()
    # проверка на право доступа к боту
    sender_id = sender.id
    if not is_allow_user(sender_id, admin_client):
        await event.respond(f"Доступ запрещен. Обратитесь к администратору" \
                            f" чтобы добавил ваш ID в белый список. Ваш ID {sender_id}")
        return
    # END проверка на право доступа к боту
    await event.respond("Выполняется команда /DelUSer")
    # диалог с запросом информации нужной для работы команды /DelUser
    chat_id = event.chat_id
    async with bot.conversation(chat_id) as conv:
        # response = conv.wait_event(events.NewMessage(incoming=True))
        await conv.send_message("Привет! Введите номер id пользователя " \
                                "который нужно запретить доступ к боту")
        id_del_user = await conv.get_response()
        id_del_user = id_del_user.message
        while not any(x.isdigit() for x in id_del_user):
            await conv.send_message("ID пользователя - это число. " \
                                    "Попробуйте еще раз.")
            id_del_user = await conv.get_response()
            id_del_user = id_del_user.message
        # проверяем на то если пользователь админ который захочет удалить себя это не получится
        if not is_allow_user(int(id_del_user), admin_client):
            settings.del_user(int(id_del_user))
            await conv.send_message(f"Пользователю с ID: {id_del_user} " \
                                    "доступ к боту запрещен.")
        else:
            await conv.send_message("Удаление пользователя с правами администратора запрещено.")


@bot.on(events.NewMessage(pattern='/InfoUser'))
async def infouser_admin(event):
    ids = read_user_db(settings)
    ids = [str(x) for x in ids]
    strs = ", ".join(ids)
    await event.respond(f"Пользователи которые имеют доступ:\n{strs}")


@bot.on(events.NewMessage(pattern='/ExitAdmin'))
async def exitadmin_admin(event):
    sender = await event.get_sender()
    # проверка на право доступа к боту
    sender_id = sender.id
    if not is_allow_user(sender_id, admin_client):
        await event.respond(f"Доступ запрещен. Обратитесь к администратору" \
                            f" чтобы добавил ваш ID в белый список. Ваш ID {sender_id}")
        return
    # END проверка на право доступа к боту
    flag_admin = False
    await event.respond(f"Вы вышли из режима администратора.",
                        buttons=button_main
                        )


def main():
    bot.run_until_disconnected()


if __name__ == '__main__':
    main()
