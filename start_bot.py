from telegram.ext import Updater, CommandHandler, CallbackQueryHandler, ConversationHandler, MessageHandler, Filters
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from config import Config
import logging
import subprocess
import io

ABOUT = range(1)

allow_users = [{"username":"Oilnur","id":"3608708"}]

# проверка на разрешенного пользователя
def is_allow_user(func):
    def wrapped(*args, **kwargs):
        nameuser = args[2].message.from_user.username
        print("Имя пользователя: ", nameuser)
        for user in allow_users:
            if user["username"]==nameuser:
                return func(*args, **kwargs)
        args[2].message.reply_text(text="Доступ запрещен. Обратитесь к администратору.")
        return False
    return wrapped


class iTelegramBot:
    def __init__(self, token=None,level_loggining=logging.INFO):
        logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            level=level_loggining)
        self.bot = Updater(token)

        mp3_handler = MessageHandler(filters = Filters.text, callback=self.get_mp3_from_youtube)
        self.bot.dispatcher.add_handler(mp3_handler)

        # регистрация обработчика используя паттерн срабатывания
        # self.bot.dispatcher.add_handler(CallbackQueryHandler(self.about2,pattern="^about_bot$")) 
        # регистрация команд     
        self.reg_handler("start",self.start)
        self.reg_handler("about",self.about)

    def reg_handler(self, command=None,hand=None):
        """ регистрация команд которые обрабатывает бот """
        if (command is None) or (hand is None):
            return
        self.bot.dispatcher.add_handler(CommandHandler(command, hand))
        
    def about(self, bot, update):
        """ сообщает какие есть возможности у бота """
        update.message.reply_text("Я конвертирую youtube клип в mp3.")
    
    @is_allow_user
    def start(self, bot, update):
        update.message.reply_text('Привет! {}! Я рад видеть тебя!\nПришли мне ссылку на клип ютуба, обратно получите его аудио дорожку.'.format(update.message.from_user.first_name))
        
    def run(self):
        """ запуск бота """   
        logging.debug("Start telegram bot")  
        self.bot.start_polling()
        self.bot.idle()

    @is_allow_user
    def get_mp3_from_youtube(self, bot, update):
        update.message.reply_text("Начало конвертации ютуб клипа в mp3...")
        #  youtube-dl --extract-audio --audio-format mp3 <video URL>
        url_youtube = update.message.text
        print("УРЛ: {}".format(url_youtube))
        cmds = ['youtube-dl','--extract-audio','--audio-format', 'mp3', '--output', r"mp3/%(title)s.%(ext)s" , url_youtube]

        with subprocess.Popen(cmds, stdout=subprocess.PIPE) as proc:
            result = proc.stdout.read()

        result = result.decode("utf-8")
        str_result = result.split("\n")
        str_search = "[ffmpeg] Destination:"
        file_mp3 = ""
        for s in str_result:
            if str_search in s:
                file_mp3 = s[len(str_search):].strip()
                break

        bot.send_audio(chat_id=update.message.chat_id, audio = open(file_mp3, 'rb'))
        update.message.reply_text("Конец конвертации!")


cfg = Config("config.ini")
tgbot = iTelegramBot(cfg.token,logging.DEBUG)
tgbot.run()