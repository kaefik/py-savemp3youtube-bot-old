"""
 Версия телеграмм бота с использованием библиотеки Telethon

"""

import os
from dotenv import load_dotenv  # pip3 install python-dotenv
from telethon import TelegramClient, events, connection  # pip3 install Telethon

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
    await event.respond("Начало конвертации ютуб клипа в mp3...")
    # TODO: сделать конвертирование в mp3
    await event.respond("Конец конвертации!")

def main():
    """Start the bot."""
    bot.run_until_disconnected()

if __name__ == '__main__':
    main()