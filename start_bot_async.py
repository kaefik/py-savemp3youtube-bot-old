"""
 Версия телеграмм бота с использованием библиотеки Telethon

"""

import os
# pip3 install python-dotenv
from dotenv import load_dotenv
# pip3 install Telethon
from telethon import TelegramClient, events, connection, sync
import asyncio
import subprocess
from pprint import pprint
import logging

from i_utils import run_cmd


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
proxy_port = int(os.getenv("TLG_PROXY_PORT"))
proxy_key = os.getenv("TLG_PROXY_KEY")
# клиент с правами администратора
admin_client = int(os.getenv("TLG_ADMIN_ID_CLIENT"))
clients = [] # обычные пользователи TODO: сделать загрузку пользователей из файла конфигурации
clients.append(admin_client)

if proxy_server is None or proxy_port is None or proxy_key is None:
    print("Нет настроек MTProto прокси сервера телеграмма.\n"\
        "Попытка подключения клиента без прокси.")
    bot = TelegramClient(app_name, app_api_id, app_api_hash).start(
                bot_token=bot_token
            )
else:
    proxy = (proxy_server, proxy_port, proxy_key)
    bot = TelegramClient(app_name, app_api_id, app_api_hash, 
        connection=connection.ConnectionTcpMTProxyRandomizedIntermediate,
        proxy=proxy).start(bot_token=bot_token)

# получаем текст для помощи о командах бота
help_text = ""
with open("help.txt", "r") as f:
    help_text = f.read()

# ---- END Начальные данные ----

#----- Вспомогательные функции
# проверка на разрешенного пользователя
def is_allow_user(iduser, allow_users):
    for user in allow_users:                
        if user==iduser:
            return True    
    return False        
#----- END Вспомогательные функции



@bot.on(events.NewMessage(pattern='/start'))
async def start(event):
    sender = await event.get_sender() 
    # проверка на право доступа к боту
    sender_id = sender.id       
    if not is_allow_user(sender_id, clients):
        await event.respond(f"Доступ запрещен. Обратитесь к администратору"\
            f" чтобы добавил ваш ID в белый список. Ваш ID {sender_id}")
        return
    # END проверка на право доступа к боту
    await event.respond(f"Привет, {sender.first_name}! Я рад видеть тебя!\n"\
        "Пришли мне ссылку на клип ютуба, обратно получите его аудио дорожку.")
    raise events.StopPropagation

@bot.on(events.NewMessage(pattern='/about'))
async def about(event):
    sender = await event.get_sender()
    # проверка на право доступа к боту
    sender_id = sender.id       
    if not is_allow_user(sender_id, clients):
        await event.respond(f"Доступ запрещен. Обратитесь к администратору"\
            f" чтобы добавил ваш ID в белый список. Ваш ID {sender_id}")
        return
    # END проверка на право доступа к боту
    await event.respond("Я конвертирую youtube клип в mp3.")

@bot.on(events.NewMessage(pattern='/delmp3'))
async def clear_all_mp3(event):
    sender = await event.get_sender()       
    # проверка на право доступа к боту
    sender_id = sender.id       
    if not is_allow_user(sender_id, clients):
        await event.respond(f"Доступ запрещен. Обратитесь к администратору"\
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
    result, error, code =  done.pop().result()

    if code!=0:
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

    result, error, code =  done.pop().result()

    if code!=0:
        await event.respond(error.decode("utf8"))

    result = result.decode("utf8")
    # print("result = ", result)
    await event.respond(result)

    await event.respond("Очистка завершена.")

@bot.on(events.NewMessage(pattern='/help'))
async def help(event):
    sender = await event.get_sender() 
    # проверка на право доступа к боту
    sender_id = sender.id
    if not is_allow_user(sender_id, clients):
        await event.respond(f"Доступ запрещен. Обратитесь к администратору"\
            f" чтобы добавил ваш ID в белый список. Ваш ID {sender_id}")
        return
    # END проверка на право доступа к боту
    await event.respond(help_text)

# получение урл
@bot.on(events.NewMessage(
    pattern=r"https?:\/\/(www\.)?[-a-zA-Z0-9@:%._\+~#=]{2,256}\.[a-z]{2,6}\b([-a-zA-Z0-9@:%_\+.~#?&//=]*)")
    )
async def get_mp3_from_youtube(event):
    sender = await event.get_sender() 
    # проверка на право доступа к боту
    sender_id = sender.id       
    if not is_allow_user(sender_id, clients):
        await event.respond(f"Доступ запрещен. Обратитесь к администратору"\
            f" чтобы добавил ваш ID в белый список. Ваш ID {sender_id}")
        return
    # END проверка на право доступа к боту
    
    # chat = await event.get_input_chat()
    sender = await event.get_sender()
    # buttons = await event.get_buttons()
    # print(sender.id)
    user_folder = str(sender.id)
    # print(event.raw_text)
    url_youtube = event.raw_text        
    await event.respond("Начало конвертации ютуб клипа в mp3...")
    # TODO: сделать конвертирование в mp3
    # print("get_mp3_from_youtube start subprocess begin")        
    cmds = f'youtube-dl --extract-audio --audio-format mp3 '\
        f'--output "{path_mp3}/{user_folder}/%(title)s.%(ext)s" {url_youtube}'
    # print(cmds)

    done, _ = await asyncio.wait([
        run_cmd(cmds)
    ])

    # result - результат выполнения команды cmds
    # error - ошибка, если команда cmds завершилась с ошибкой
    # code - код работы команды, если 0 , то команда прошла без ошибок
    result, error, code =  done.pop().result()
    """
    print("result = ", result)
    print("code = ", code)
    print("error = ", error)
    """
    if code!=0:
        await event.respond(f"!!!! код: {code} \n"\
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
    
    try:
        # print("filename = ", file_mp3)
        await event.respond(f"Попытка отправить вам файл: {file_mp3}")
        await event.respond(file={file_mp3})            
        
    except FileNotFoundError:
        await event.respond(f"Вывод результат команды {cmds}:\n {result}")
        await event.respond("Внутреняя ошибка: или урл не доступен, "\
            "или конвертация невозможна.\n"\
            "Попробуйте позже или другую ссылку.")
    except Exception as err:
        # print("!!!! Внутреняя ошибка: ", err)
        await event.respond(f"!!!! Внутреняя ошибка: {err}")
    # END сделать конвертирование в mp3
    await event.respond("Конец конвертации!")

def main():    
    bot.run_until_disconnected()

if __name__ == '__main__':
    main()