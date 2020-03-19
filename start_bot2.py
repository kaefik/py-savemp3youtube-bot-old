"""
 Версия телеграмм бота с использованием библиотеки Telethon

"""

import os
from dotenv import load_dotenv  # pip3 install python-dotenv
from telethon import TelegramClient, events, connection  # pip3 install Telethon
import asyncio
import subprocess

dotenv_path = os.path.join(os.path.dirname(__file__), ".env")
print((dotenv_path))
if os.path.exists(dotenv_path):
    load_dotenv(dotenv_path)
app_api_id = os.getenv("TLG_APP_API_ID")
app_api_hash = os.getenv("TLG_APP_API_HASH")
app_name = os.getenv("TLG_APP_NAME")
bot_token = os.getenv("I_BOT_TOKEN")
client = os.getenv("TLG_CLIENT")
proxy_server = os.getenv("TLG_PROXY_SERVER")
proxy_port = int(os.getenv("TLG_PROXY_PORT"))
proxy_key = os.getenv("TLG_PROXY_KEY")
proxy = (proxy_server, proxy_port, proxy_key)

bot = TelegramClient(app_name, app_api_id, app_api_hash, 
    connection=connection.ConnectionTcpMTProxyRandomizedIntermediate,
    proxy=proxy).start(bot_token=bot_token)
client = [] # клиент


async def run_cmd(cmd):
    proc = await asyncio.create_subprocess_shell(
        cmd,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE)

    stdout, stderr = await proc.communicate()

    print(f'[{cmd!r} exited with {proc.returncode}]')
    if stdout:
        print(f'[stdout]\n{stdout.decode()}')        
    if stderr:
        print(f'[stderr]\n{stderr.decode()}')

@bot.on(events.NewMessage(pattern='/start'))
async def start(event):
    """Send a message when the command /start is issued."""
    sender = await event.get_sender()    
    await event.respond(f"Привет, {sender.first_name}! Я рад видеть тебя!\nПришли мне ссылку на клип ютуба, обратно получите его аудио дорожку.")
    raise events.StopPropagation

@bot.on(events.NewMessage(pattern='/about'))
async def about(event):
    await event.respond("Я конвертирую youtube клип в mp3.")

@bot.on(events.NewMessage(pattern='/delmp3'))
async def clear_all_mp3(event):
    await event.respond("Очистка папки mp3 от файлов...")
    # TODO: сделать удаление файлов
    await event.respond("Очистка завершена.")

@bot.on(events.NewMessage(pattern='/help'))
async def help(event):
        str1 = "/start - подружиться с ботом."
        str2 = "/about - описания бота."
        str3 = "/delmp3 - очистить папку сохраненных mp3 файлов из сервера."
        str4 = "Пришлите ссылку youtube чтобы получить mp3 файл в ответ."
        str5 = "/admin - переключиться в режим администратора."        
        await event.respond(f"Список команд:\n{str1}\n{str2}\n{str3}\n{str5}\n{str4}\n")

# получение урл
@bot.on(events.NewMessage(pattern=r"https?:\/\/(www\.)?[-a-zA-Z0-9@:%._\+~#=]{2,256}\.[a-z]{2,6}\b([-a-zA-Z0-9@:%_\+.~#?&//=]*)"))
async def get_mp3_from_youtube(event):
    chat = await event.get_input_chat()
    sender = await event.get_sender()
    buttons = await event.get_buttons()
    print(sender.id)
    user_folder = sender.id
    print(event.raw_text)
    url_youtube = event.raw_text
    cmds = ['youtube-dl','--extract-audio','--audio-format', 'mp3', '--output', r"mp3/"+user_folder+r"/%(title)s.%(ext)s" , url_youtube]
    await event.respond("Начало конвертации ютуб клипа в mp3...")
    # TODO: сделать конвертирование в mp3
    print("get_mp3_from_youtube start subprocess begin")
    with subprocess.Popen(cmds, stdout=subprocess.PIPE) as proc:
        result = proc.stdout.read()

    print("get_mp3_from_youtube start subprocess end")
    print("result = ", result)       

    result = result.decode("utf-8")
    str_result = result.split("\n")
    str_search = "[ffmpeg] Destination:"
    file_mp3 = ""
    for s in str_result:
        if str_search in s:
            file_mp3 = s[len(str_search):].strip()
            break
    try:
        print("filename = ", file_mp3)
        event.respond(f"Попытка отправить вам файл: {file_mp3}")
        # bot.send_audio(chat_id=update.message.chat_id, audio = open(file_mp3, 'rb'), timeout=1000)
    except FileNotFoundError:
        event.respond(f"Вывод результат команды {cmds}:\n {result}")
        event.respond("Внутреняя ошибка: или урл не доступен, или конвертация невозможна.\nПопробуйте позже или другую ссылку.")
    except Exception as err:
        print("------!!!! Внутреняя ошибка: ", err)
        event.respond(f"------!!!! Внутреняя ошибка: {err}")
    # END сделать конвертирование в mp3

    await event.respond("Конец конвертации!")

def main():
    """Start the bot."""
    bot.run_until_disconnected()

if __name__ == '__main__':
    main()