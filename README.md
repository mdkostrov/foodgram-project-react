# FOODGRAM. «Продуктовый помощник»

![Workflow repository status](https://github.com/mdkostrov/foodgram-project-react/actions/workflows/foodgram_workflow.yml/badge.svg)

<details>
<summary>
>>>Для ревьюера<<<
</summary>
##### АДРЕС ПРОЕКТА НА ВМ ДЛЯ РЕВЬЮ:
http://51.250.78.62/
</details>


### Описание проекта.

Проект представляет собой сервис для публикации рецептов.
Foodgram («Продуктовый помощник») позволяет любому пользователю зарегистрироваться и публиковать рецепты, подписываться на авторов других рецептов, добавлять рецепты в избранное, создавать список продуктов, которые нужно купить для приготовления выбранных блюд.

##### Технологии.

В проекте использованы следующие технологии:
Python 3.7, Django 3.2, Django REST Framework 3.12.4, Djoser 2.1.0, Gunicorn 20.1.0, nginx 1.21.3-alpine, PostgreSQL 13.0-alpine.

<details>
<summary>
Деплой проекта на удаленном сервере.
</summary>
для Linux-систем все команды необходимо выполнять от имени администратора
- Склонировать репозиторий
```bash
git clone https://github.com/mdkostrov/foodgram-project-react.git
```
- Выполнить вход на удаленный сервер
- Обновить пакеты
- Установить docker на сервер:
```bash
sudo apt install docker.io
```
- Установить docker-compose на сервер:
```bash
sudo apt install docker-compose
```
- Локально отредактировать файл infra/nginx.conf, обязательно в строке server_name вписать IP-адрес сервера
- Скопировать файлы docker-compose.yml и nginx.conf из директории infra на сервер:
```bash
scp docker-compose.yml <username>@<host>:/home/<username>/docker-compose.yml
scp nginx.conf <username>@<host>:/home/<username>/nginx.conf
```
- Создать .env файл по предлагаемому шаблону.
- Для работы с Workflow добавить в Secrets GitHub переменные окружения:
    ```
    DB_ENGINE=<django.db.backends.postgresql>
    DB_NAME=<имя базы данных postgres>
    DB_USER=<пользователь бд>
    DB_PASSWORD=<пароль>
    DB_HOST=<db>
    DB_PORT=<5432>

    DOCKER_PASSWORD=<пароль от DockerHub>
    DOCKER_USERNAME=<имя пользователя>

    SECRET_KEY=<секретный ключ проекта django>

    USER=<username для подключения к серверу>
    HOST=<IP сервера>
    PASSPHRASE=<пароль для сервера, если он установлен>
    SSH_KEY=<ваш SSH ключ (для получения команда: cat ~/.ssh/id_rsa)>

    TELEGRAM_TO=<ID чата, в который придет сообщение>
    TELEGRAM_TOKEN=<токен вашего бота>
    ```
    Workflow состоит из четырёх шагов:
     - Проверка кода на соответствие PEP8
     - Сборка и публикация образа бекенда на DockerHub.
     - Автоматический деплой на удаленный сервер.
     - Отправка уведомления в телеграм-чат.
- собрать и запустить контейнеры на сервере:
```bash
docker-compose up -d --build
```
- После успешной сборки выполнить следующие действия (только при первом деплое):
    * провести миграции внутри контейнеров:
    ```bash
    docker-compose exec web python manage.py migrate

    * Заполнить БД:
    ```bash
    docker-compose exec web python manage.py loaddata dump.json
</details>
<br />
<br />

### Как запустить проект локально на dev-сервере

Клонировать репозиторий и перейти в него в командной строке:

```bash
git clone https://github.com/mdkostrov/foodgram-project-react.git
```

```bash
cd foodgram-project-react
```

Cоздать и активировать виртуальное окружение (для Windows):

```bash
python -m venv venv
```

```bash
source venv/scripts/activate
```

Обновить установщик пакетов pip:

```bash
python -m pip install --upgrade pip
```

Установить зависимости из файла requirements.txt:

```bash
pip install -r requirements.txt
```

Перейти в директорию с manage.py:

```bash
cd foodgram
```

Создать (при необходимости) и выполнить миграции:

```bash
python manage.py makemigrations
```

```bash
python manage.py migrate
```

Команда для заполнения базы данных:

```bash
python manage.py loaddata dump.json
```

Запуск локального сервера:

```bash
python manage.py runserver
```

### Шаблон наполнения файла .env с переменными окружения (infra/.env)

```bash
DB_ENGINE=django.db.backends.postgresql
DB_NAME=postgres
POSTGRES_USER=postgres
POSTGRES_PASSWORD=postgres
DB_HOST=db
DB_PORT=5432
```

### Документация
Документация с доступными для запросов эндпоинтами после запуска DEV-сервера проекта доступна по адресу:

```bash
http://127.0.0.1/api/docs/
```

### Об авторе

Над проектом работал:

**Костров Михаил**
[GitHub](https://github.com/mdkostrov/)

Студент курса "Разработчик Python" (45-47 когорта). 2023 год.
