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
     sudo -H pip3 install --upgrade youtube-dl
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


### Добавление в автозапуск программы при загрузке сервера Ubuntu

в папке /etc/systemd/system/ создадим файл start-youtube-audio.service

Содержимое файла:
```bash
[Unit]
Description=Youtube video to audio
After=network.target

[Service]
ExecStart=путь до скрипта запуска программы

[Install]
WantedBy=default.target
```

выполним команды
```bash
systemctl daemon-reload
systemctl enable start-youtube-audio.service
systemctl start start-youtube-audio.service
```

## Запуск docker контейнера с программой

1. скопировать всю программу в папку на компьютере например в папку *tlg-youtube2audio/app*:

2. сохранить файл *Dockerfile* в папке *tlg-youtube2audio*:

   ENV TZ=Europe/Moscow
   RUN apt-get update && apt-get install -y python3 && apt-get install -y python3-pip 
   RUN DEBIAN_FRONTEND=noninteractive apt-get install -y youtube-dl && apt-get install -y mp3splt
   RUN pip3 install python-dotenv && pip3 install Telethon && pip3 install requests
   WORKDIR /home/app
   #VOLUME /home/app
   COPY app /home/app
   CMD ["python3", "start_bot_async.py"]

3. в папку *tlg-youtube2audio/cfg* файлы конфигурации проекта:
   1. *.env*
   2. *db_user_allow.txt*

4. Создание образа контейнера

`docker build --tag=tlgyoutube2audio .`

5. Запуск docker контейнера (после завершения работы контейнера)

 `docker run -it --rm  -v "/полный_путь_до_проекта/tlg-youtube2audio/cfg/.env:/home/app/.env" -v "/полный_путь_до_проекта/tlg-youtube2audio/cfg/d`
`b_user_allow.txt:/home/app/db_user_allow.txt" tlgyoutube2audio`

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