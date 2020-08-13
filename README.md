О проекте

[py-savemp3youtube-bot](https://github.com/kaefik/py-savemp3youtube-bot) - телеграмм бот получает ссылку на видео ютуба и возвращает звуковую дорожку видео.

## Реализованные возможности:

1. получение ссылки на видео ютуба -> на выходе пользователю возвращается звуковая дорожка видео (файлы в формате mp3)

2. mp3 файл делятся на несколько каждый длительностью 60 минут

3. администратор бота только один пользователь

4. администратор может выполнять следующие действия: добавить пользователя по id, удалить пользователя из доступа к данному боту, информация о тех пользователях кто имеет доступ

5. каждый пользователь может удалить все mp3 файлы которые хранятся на сервере где работает бот


## Настройка проекта для запуска

### Библиотеки:

* ```bash
  pip3 install python-dotenv	
  pip3 install Telethon
  pip3 install requests
  ```

  или просто выполняем 

  ```bash
  pip install -r requirements.txt
  ```

* установить программы для работы

  1. [youtube-dl](https://www.youtube-dl.org/) - кроссплатформенный свободный проект с открытым исходным кодом на Python - для работы с видео ютуба. Для ознакомления можно прочитать [статью](https://habr.com/ru/post/369853/).

     Для установки на убунту: 

     ```bash
     apt install youtube-dl
     ```

  2. [mp3splt](http://mp3splt.sourceforge.net/mp3splt_page/home.php) - для разбивания аудофайлов различных форматов без декодинга.

     Для установки на убунту: 

     ```bash
     apt install mp3splt
     ```

     

### Конфигурационные файлы проекта:

* **.env** 

  ```
  TLG_APP_API_ID=123456 # APP API ID get from https://my.telegram.org
  TLG_APP_API_HASH=fdgdfgdgdfgdfgd # APP API HASH get from https://my.telegram.org
  TLG_APP_NAME=app  # APP NAME get from https://my.telegram.org
  I_BOT_TOKEN=12345:fdgdfgdfgdfdfgdfg    # TOKEN Bot drom BotFather
  TLG_ADMIN_ID_CLIENT=12568999  # id administarator bot
  TLG_PROXY_SERVER = server # адрес MTProxy Telegram
  TLG_PROXY_PORT = 555 # порт  MTProxy Telegram
  TLG_PROXY_KEY=sf23231231  # secret key  MTProxy Telegram
  ```

* **db_user_allow.txt** - текстовый файл в котором указываются id пользователей которые имеют доступ к боту (за исключением администратора бота)

### Запуск проекта:

```bash
python start_bot_async.py
```

### Команды которые используются ботом для основного функционала:

#### 1. How to download an MP3 track from a YouTube video

```bash
youtube-dl --extract-audio --audio-format mp3 <video URL>
```

#### 2. Разбить аудиофайл на части продолжительностью 60 минут:

```bash
mp3splt -t 59.0 -d имя_папки_для_выходного_файла имя_входного_файла
```

### Полезные ссылки

   * https://github.com/python-telegram-bot/python-telegram-bot/wiki/Extensions-%E2%80%93-Your-first-Bot
* https://github.com/python-telegram-bot/python-telegram-bot/wiki/Code-snippets

* [https://api.telegram.org/botТОКЕН/sendMessage?chat_id=ЧАТ_ID&text=HelloBot](https://api.telegram.org/botТОКЕН/sendMessage?chat_id=ЧАТ_ID&text=HelloBot) 