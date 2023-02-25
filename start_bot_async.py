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
    name_admin = ''
    settings = SettingUser(namedb=name_file_settings)
    admin_User = User(id=admin_client, role=Role.admin, active=True)
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

# флаг режима администратора
flag_admin = False

# кнопки главного режима для администратора
button_main_admin = [
    [Button.text("/help"),
     Button.text("/admin"),
     Button.text("/settings")]
]

# кнопки главного режима для обычного пользователя
button_main_user = [
    [Button.text("/help"),
     Button.text("/admin")]
]

# кнопки для режима администратора
button_admin = [
    [Button.text("/AddUser"),
     Button.text("/DelUser"),
     Button.text("/InfoUser"),
     Button.text("/ExitAdmin")]
]

# кнопки для режима настроек пользователя
button_settings = [
    [Button.text("/TypeResult"),
     Button.text("/QualityResult"),
     Button.text("/ExitSettings")]
]

# выбор типа результирующего файла
button_typeresult = [
    [
        Button.text("/TypeResultSound"),
        Button.text("/TypeResultVideo"),
        Button.text("/ExitTypeResult"),
    ]
]

# выбор качества результирующего файла
button_qualityresult = [
    [
        Button.text("/HighResult"),
        Button.text("/MediumResult"),
        Button.text("/LowResult"),
        Button.text("/ExitQualityResult"),
    ]
]

db_user_bot = "db_user_allow.txt"
rexp_http_url = r"https?:\/\/(www\.)?[-a-zA-Z0-9@:%._\+~#=]{2,256}\.[a-z]{2,6}\b([-a-zA-Z0-9@:%_\+.~#?&//=]*)"


# ---- END Начальные данные ----

# ----- Вспомогательные функции

def get_help(filename='help.txt'):
    """
        получаем текст для помощи о командах бота
    """
    help_text = ""
    with open(filename, "r") as f:
        help_text = f.read()
    return help_text


# проверка на разрешенного пользователя
def is_allow_user(iduser, allow_users):
    for user in allow_users:
        if user.id == iduser:
            return True
    return False


# добавляем пользователя в БД пользователей которые имеют доступ к боту
# возвращает True 
def add_new_user(id, settings):
    new_user = User(id=id)
    settings.add_user(new_user)
    return True


# возвращает список пользователей которые имеют доступ к боту
def read_user_db(settings):
    result = []
    clients = settings.get_all_user()
    for cl in clients:
        result.append(cl.__str__())
    return result


async def get_name_user(client, user_id):
    """
        получаем информацию о пользователе телеграмма по его user_id (user_id тип int)
    """
    try:
        new_name_user = await client.get_entity(user_id)
        new_name_user = new_name_user.first_name
    except ValueError as err:
        print('Ошибка получения информации о пользователе по id: ', err)
        new_name_user = ''
    return new_name_user


async def check_name_user_empty(client, sender_id, db):
    """
        проверим есть ли у этого пользователя имя пользователя в нашей БД настроек
        возвращает имя пользователя
    """
    user_name = db.get_user(sender_id)
    # print(f'Имя пользователя в БД {user_name}')
    user_name_tlg = await get_name_user(client, sender_id)
    # print(f'Имя пользователя в Телеграмме {user_name_tlg}')
    if len(user_name.name) == 0:
        user_name.name = user_name_tlg
        db.update_user(user_name)
    return user_name


# ----- END Вспомогательные функции


@bot.on(events.CallbackQuery)
async def handler(event):
    await event.answer('You clicked {}!'.format(event.data))


@bot.on(events.NewMessage(pattern='/start'))
async def start_cmd(event):
    sender = await event.get_sender()
    # проверка на право доступа к боту
    sender_id = sender.id

    if not is_allow_user(sender_id, settings.get_all_user()):
        await event.respond(f"Доступ запрещен. Обратитесь к администратору" \
                            f" чтобы добавил ваш ID в белый список. Ваш ID {sender_id}")
        return
    # END проверка на право доступа к боту

    user_name = await check_name_user_empty(event.client, sender_id, settings)

    if user_name.role == Role.admin:
        buttons = button_main_admin
    else:
        buttons = button_main_user

    await event.respond(f"Привет, {user_name.name}! Я рад видеть тебя!\n" \
                        "Пришли мне ссылку на клип ютуба, обратно получите его аудио дорожку.",
                        buttons=buttons
                        )
    raise events.StopPropagation


@bot.on(events.NewMessage(pattern='/about'))
async def about_cmd(event):
    sender = await event.get_sender()
    # проверка на право доступа к боту
    sender_id = sender.id
    if not is_allow_user(sender_id, settings.get_all_user()):
        await event.respond(f"Доступ запрещен. Обратитесь к администратору"
                            f" чтобы добавил ваш ID в белый список. Ваш ID {sender_id}")
        return
    # END проверка на право доступа к боту

    await event.respond("Я конвертирую youtube клип в mp3.")


@bot.on(events.NewMessage(pattern='/delfiles'))
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
async def help_cmd(event):
    sender = await event.get_sender()
    # проверка на право доступа к боту
    sender_id = sender.id
    if not is_allow_user(sender_id, settings.get_all_user()):
        await event.respond(f"Доступ запрещен. Обратитесь к администратору" \
                            f" чтобы добавил ваш ID в белый список. Ваш ID {sender_id}")
        return
    # END проверка на право доступа к боту

    await event.respond(get_help('help.txt'))


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
    sender_id = sender.id

    current_user = settings.get_user(sender_id)

    # buttons = await event.get_buttons()
    # print(sender.id)
    user_folder = str(sender.id)
    # print(event.raw_text)
    # выделение урл из общей массы сообщения
    match = re.search(rexp_http_url, event.raw_text)
    url_youtube = match.group()
    print(url_youtube)

    if current_user.typeresult == TypeResult.sound:

        await event.respond("Начало конвертации ютуб клипа в mp3...")
        # print("get_mp3_from_youtube start subprocess begin")
        cmds = f'/home/oilnur/prj/prj-py/py-savemp3youtube-bot/yt-dlp_linux --extract-audio --audio-format mp3 ' \
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
        str_search = "[ExtractAudio] Destination:"
        print("str_search = ", str_search)
        file_mp3 = ""
        for s in str_result:
            if str_search in s:
                file_mp3 = s[len(str_search):].strip()
                break

        # если уже был сконвертирован mp3 файл
        if file_mp3 == "":
            str_search = "[ExtractAudio] Not converting audio"
            print("str_search = ", str_search)
            file_mp3 = ""
            for s in str_result:
                if str_search in s:
                    file_mp3 = s[len(str_search):].strip()
                    break
            file_mp3 = file_mp3.split(";")[0]

        await event.respond("mp3 файл скачан...будем делить на части")
        # деление mp3 файла на части, если нужно с помощью команды mp3splt
        timesplit = "59.0"  # длительность каждой части формат: минуты.секунда
        cmds2 = f'mp3splt -t {timesplit} "{file_mp3}"'

        print(cmds2)

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
            await event.respond("Внутренняя ошибка: или урл не доступен, "
                                "или конвертация невозможна.\n"
                                "Попробуйте позже или другую ссылку.")
        except Exception as err:
            # print("!!!! Внутренняя ошибка: ", err)
            await event.respond(f"!!!! Внутренняя ошибка: {err}")
        # END сделать конвертирование в mp3
        await event.respond("Конец конвертации!")

    elif current_user.typeresult == TypeResult.video:  # качаем видео
        await event.respond("Начало конвертации ютуб клипа в видео...")

        quality_video = 360

        if current_user.qualityresult == QualityResult.high:
            quality_video = 720
        elif current_user.qualityresult == QualityResult.medium:
            quality_video = 360
        elif current_user.qualityresult == QualityResult.low:
            quality_video = 244

        await event.respond(f"Качество видео {quality_video}p")

        cmds = f'youtube-dl -f "bestvideo[height<={quality_video}]+bestaudio/best[height<={quality_video}]"' \
               f' --output "{path_mp3}/{user_folder}/%(title)s.%(ext)s" "{url_youtube}"'
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

        str_search_already_begin = '[download]'
        str_search_already_back = 'has already been downloaded and merged'
        str_search = "[ffmpeg] Merging formats into"
        file_video = ""

        if result.find(str_search_already_back) > -1:
            # видео уже есть
            for s in str_result:
                if str_search_already_begin in s:
                    file_video = s[len(str_search_already_begin):-len(str_search_already_back)].strip()
                    break
            file_video = file_video.replace('"', '')
            print(file_video)
            await event.respond("Это видео уже было получено ранее.")

        elif result.find(str_search) > -1:

            for s in str_result:
                if str_search in s:
                    file_video = s[len(str_search):].strip()
                    break
            file_video = file_video.replace('"', '')
            print(file_video)

        if (os.path.getsize(file_video) / 1048576) <= 60:  # размер файла (Мб)
            try:
                await event.respond(f"Результат конвертации:")
                await event.respond(file=file_video)

            except FileNotFoundError:
                await event.respond(f"Вывод результат команды {cmds}:\n {result}")
                await event.respond("Внутренняя ошибка: или урл не доступен, "
                                    "или конвертация невозможна.\n"
                                    "Попробуйте позже или другую ссылку.")
            except Exception as err:
                # print("!!!! Внутренняя ошибка: ", err)
                await event.respond(f"!!!! Внутренняя ошибка: {err}")

            await event.respond("Конец конвертации!")
            return

        await event.respond("видео файл скачан...будем делить на части")
        # деление видео файла на части, если нужно с помощью команды ffmpeg
        timesplit = "3600"  # длительность каждой части формат: секунда
        filename, file_extension = os.path.splitext(file_video)
        cmds2 = f'ffmpeg -i "{file_video}" -acodec copy -f segment -segment_time {timesplit} -vcodec copy -reset_timestamps 1 ' \
                f'-map 0 "{filename}_%03d{file_extension}"'

        print(cmds2)

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
        else:
            result2 = result2 + error2
            # удаляем исходный файл
            os.remove(file_video)

        result2 = result2.decode("utf-8")
        str_result2 = result2.split("\n")

        # print(result2)

        # определяем имена файлов которые получились при разделении файлов
        str_search_split_begin = 'Opening'
        str_search_split_end = 'for writing'
        files_video = []
        for s in str_result2:
            if str_search_split_begin in s:
                f_video = s[s.index(str_search_split_begin) + 7:-len(str_search_split_end)].strip()
                f_video = f_video.replace("'", '')
                # print(f_video)
                files_video.append(f_video)

        try:
            await event.respond(f"Результат конвертации:")
            for el in files_video:
                await event.respond(file=el)

        except FileNotFoundError:
            await event.respond(f"Вывод результат команды {cmds}:\n {result}")
            await event.respond("Внутренняя ошибка: или урл не доступен, "
                                "или конвертация невозможна.\n"
                                "Попробуйте позже или другую ссылку.")
        except Exception as err:
            # print("!!!! Внутренняя ошибка: ", err)
            await event.respond(f"!!!! Внутренняя ошибка: {err}")

        await event.respond("Конец конвертации!")

    else:
        await event.respond("Я пока не поддерживаю такой тип результата ", current_user.typeresult)


@bot.on(events.NewMessage(pattern='/admin'))
async def admin_cmd(event):
    sender = await event.get_sender()
    # проверка на право доступа к боту
    sender_id = sender.id
    if not is_allow_user(sender_id, admin_client):
        await event.respond(f"Доступ запрещен. Обратитесь к администратору"
                            f" чтобы добавил ваш ID в белый список. Ваш ID {sender_id}")
        return
    # END проверка на право доступа к боту
    await event.respond("Вы вошли в режим администратора",
                        buttons=button_admin)


@bot.on(events.NewMessage(pattern='/AddUser'))
async def add_user_admin(event):
    sender = await event.get_sender()
    # проверка на право доступа к боту
    sender_id = sender.id
    if not is_allow_user(sender_id, admin_client):
        await event.respond(f"Доступ запрещен. Обратитесь к администратору"
                            f" чтобы добавил ваш ID в белый список. Ваш ID {sender_id}")
        return
    # END проверка на право доступа к боту
    await event.respond("Выполняется команда /AddUSer")
    # диалог с запросом информации нужной для работы команды /AddUser
    chat_id = event.chat_id
    async with bot.conversation(chat_id) as conv:
        # response = conv.wait_event(events.NewMessage(incoming=True))
        await conv.send_message("Привет! Введите номер id пользователя"
                                "который нужно добавить для доступа к боту:")
        id_new_user = await conv.get_response()
        id_new_user = id_new_user.message
        # print("id_new_user ", id_new_user)
        while not all(x.isdigit() for x in id_new_user):
            await conv.send_message("ID нового пользователя - это число. Попробуйте еще раз.")
            id_new_user = await conv.get_response()
            id_new_user = id_new_user.message
        # print("id_new_user ", id_new_user)

        new_name_user = await get_name_user(event.client, int(id_new_user))

        print('Имя нового пользователя', new_name_user)
        add_new_user(id_new_user, settings)
        await conv.send_message(f"Добавили нового пользователя с ID: {id_new_user} с именем {new_name_user}")


@bot.on(events.NewMessage(pattern='/DelUser'))
async def del_user_admin(event):
    sender = await event.get_sender()
    # проверка на право доступа к боту
    sender_id = sender.id
    if not is_allow_user(sender_id, admin_client):
        await event.respond(f"Доступ запрещен. Обратитесь к администратору"
                            f" чтобы добавил ваш ID в белый список. Ваш ID {sender_id}")
        return
    # END проверка на право доступа к боту
    await event.respond("Выполняется команда /DelUSer")
    # диалог с запросом информации нужной для работы команды /DelUser
    chat_id = event.chat_id
    async with bot.conversation(chat_id) as conv:
        # response = conv.wait_event(events.NewMessage(incoming=True))
        await conv.send_message("Привет! Введите номер id пользователя "
                                "который нужно запретить доступ к боту")
        id_del_user = await conv.get_response()
        id_del_user = id_del_user.message
        while not any(x.isdigit() for x in id_del_user):
            await conv.send_message("ID пользователя - это число. "
                                    "Попробуйте еще раз.")
            id_del_user = await conv.get_response()
            id_del_user = id_del_user.message
        # проверяем на то если пользователь админ который захочет удалить себя это не получится
        if not is_allow_user(int(id_del_user), admin_client):
            settings.del_user(int(id_del_user))
            await conv.send_message(f"Пользователю с ID: {id_del_user} "
                                    "доступ к боту запрещен.")
        else:
            await conv.send_message("Удаление пользователя с правами администратора запрещено.")


@bot.on(events.NewMessage(pattern='/InfoUser'))
async def info_user_admin(event):
    ids = read_user_db(settings)
    ids = [str(x) for x in ids]
    strs = '\n'.join(ids)
    await event.respond(f"Пользователи которые имеют доступ:\n{strs}")


@bot.on(events.NewMessage(pattern='/ExitAdmin'))
async def exit_admin_admin(event):
    sender = await event.get_sender()
    # проверка на право доступа к боту
    sender_id = sender.id
    if not is_allow_user(sender_id, admin_client):
        await event.respond(f"Доступ запрещен. Обратитесь к администратору"
                            f" чтобы добавил ваш ID в белый список. Ваш ID {sender_id}")
        return
    # END проверка на право доступа к боту
    await event.respond(f"Вы вышли из режима администратора.",
                        buttons=button_main_admin)


# ---------------------- Команды settings


@bot.on(events.NewMessage(pattern='/settings'))
async def settings_cmd(event):
    sender = await event.get_sender()
    # проверка на право доступа к боту
    sender_id = sender.id
    if not is_allow_user(sender_id, admin_client):
        await event.respond(f"Доступ запрещен. Обратитесь к администратору"
                            f" чтобы добавил ваш ID в белый список. Ваш ID {sender_id}")
        return
    # END проверка на право доступа к боту
    await event.respond("Вы вошли в режим настроек пользователя",
                        buttons=button_settings)


@bot.on(events.NewMessage(pattern='/ExitSettings|/ExitTypeResult|/ExitQualityResult'))
async def exit_settings_cmd(event):
    sender = await event.get_sender()
    # # проверка на право доступа к боту
    sender_id = sender.id
    if not is_allow_user(sender_id, admin_client):
        await event.respond(f"Доступ запрещен. Обратитесь к администратору"
                            f" чтобы добавил ваш ID в белый список. Ваш ID {sender_id}")
        return
    # END проверка на право доступа к боту
    user_name = await check_name_user_empty(event.client, sender_id, settings)

    if user_name.role == Role.admin:
        buttons = button_main_admin
    else:
        buttons = button_main_user

    await event.respond("Вы вышли из режима настроек пользователя.", buttons=buttons)


@bot.on(events.NewMessage(pattern='/TypeResult|/QualityResult'))
async def typeresult_cmd(event):
    sender = await event.get_sender()
    # проверка на право доступа к боту
    sender_id = sender.id
    if not is_allow_user(sender_id, admin_client):
        await event.respond(f"Доступ запрещен. Обратитесь к администратору"
                            f" чтобы добавил ваш ID в белый список. Ваш ID {sender_id}")
        return
    # END проверка на право доступа к боту

    message = event.raw_text

    new_message = ''

    if message == '/TypeResult':
        new_message = 'Выберите тип результирующего файла.'
        button = button_typeresult
    elif message == '/QualityResult':
        new_message = 'Выберите качество результирующего файла.'
        button = button_qualityresult

    await event.respond(new_message, buttons=button)


@bot.on(events.NewMessage(pattern='/TypeResultSound|/TypeResultVideo'))
async def typeresult_cmd(event):
    sender = await event.get_sender()
    # проверка на право доступа к боту
    sender_id = sender.id
    if not is_allow_user(sender_id, admin_client):
        await event.respond(f"Доступ запрещен. Обратитесь к администратору"
                            f" чтобы добавил ваш ID в белый список. Ваш ID {sender_id}")
        return
    # END проверка на право доступа к боту
    message = event.raw_text  # сырой текст который ввёл пользователь

    current_user = settings.get_user(sender_id)

    if message == '/TypeResultSound':
        new_message = 'Для текущего пользователя выбрали результатом работы бота только звук.'
        current_user.typeresult = TypeResult.sound

    elif message == '/TypeResultVideo':
        new_message = 'Для текущего пользователя выбрали результатом работы бота видео со звуком.'
        current_user.typeresult = TypeResult.video

    settings.update_user(current_user)
    await event.respond(new_message, buttons=button_settings)


@bot.on(events.NewMessage(pattern='/HighResult|/MediumResult|/LowResult'))
async def qualityresult_cmd(event):
    sender = await event.get_sender()
    # проверка на право доступа к боту
    sender_id = sender.id
    if not is_allow_user(sender_id, admin_client):
        await event.respond(f"Доступ запрещен. Обратитесь к администратору"
                            f" чтобы добавил ваш ID в белый список. Ваш ID {sender_id}")
        return
    # END проверка на право доступа к боту
    message = event.raw_text  # сырой текст который ввёл пользователь

    current_user = settings.get_user(sender_id)

    if message == '/HighResult':
        new_message = 'Для текущего пользователя выбрали высокое качество.'
        current_user.qualityresult = QualityResult.high

    elif message == '/MediumResult':
        new_message = 'Для текущего пользователя выбрали среднее качество.'
        current_user.qualityresult = QualityResult.medium

    elif message == '/LowResult':
        new_message = 'Для текущего пользователя выбрали низкое качество.'
        current_user.qualityresult = QualityResult.low

    settings.update_user(current_user)
    await event.respond(new_message, buttons=button_settings)


# ---------------------- END Команды settings

def main():
    bot.run_until_disconnected()


if __name__ == '__main__':
    main()
