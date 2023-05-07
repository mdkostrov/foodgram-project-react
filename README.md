# FOODGRAM. «Продуктовый помощник»

![Workflow repository status](https://github.com/mdkostrov/foodgram-project-react/actions/workflows/foodgram_workflow.yml/badge.svg)

<details>
<summary>
>>>Для ревьюера<<<
</summary>
АДРЕС ПРОЕКТА НА ВМ ДЛЯ РЕВЬЮ:
http://51.250.78.62/

Суперпользователь (админ):
логин: admin@admin.io
пароль: admin

Обычный пользователь:
логин: tester@test.io
пароль: testing31923test
</details>

### Описание проекта.

Проект представляет собой сервис для публикации рецептов.
Foodgram («Продуктовый помощник») позволяет любому пользователю зарегистрироваться и публиковать рецепты, подписываться на авторов других рецептов, добавлять рецепты в избранное, создавать список продуктов, которые нужно купить для приготовления выбранных блюд.

##### Технологии.

В проекте использованы следующие технологии:
Python 3.7, Django 3.2, Django REST Framework 3.12.4, Djoser 2.1.0, Gunicorn 20.1.0, nginx 1.21.3-alpine, PostgreSQL 13.0-alpine.

### Деплой проекта на удаленном сервере

- Склонировать репозиторий

```bash
git clone https://github.com/mdkostrov/foodgram-project-react.git
```

- Выполнить вход на удаленный сервер

```bash
ssh <username>@<host>
```

- Обновить пакеты

```bash
sudo apt update
```

```bash
sudo apt upgrade
```

- Установить docker на сервер

```bash
sudo apt install docker.io
```

- Установить docker-compose на сервер:

```bash
sudo apt install docker-compose
```

- Локально отредактировать файл infra/nginx.conf, в строке server_name вписать IP-адрес сервера
- Скопировать файлы docker-compose.yml и nginx.conf из директории infra на сервер,
- предварительно создав там директорию nginx

```bash
mkdir nginx
```

```bash
scp docker-compose.yml <username>@<host>:/home/<username>/docker-compose.yml
scp nginx.conf <username>@<host>:/home/<username>/nginx/nginx.conf
```

- Создать .env файл по предлагаемому шаблону.
- Для работы с Workflow добавить в Secrets GitHub переменные окружения:

```bash
DB_ENGINE=<django.db.backends.postgresql>
DB_NAME=<имя бд postgres>
POSTGRES_USER=<пользователь бд>
POSTGRES_PASSWORD=<пароль>
DB_HOST=<db>
DB_PORT=<5432>

DOCKER_PASSWORD=<пароль от DockerHub>
DOCKER_USERNAME=<имя пользователя>

SECRET_KEY=<секретный ключ проекта django>

USER=<username для подключения к серверу>
HOST=<IP сервера>
PASSPHRASE=<пароль для сервера, если он установлен>
SSH_KEY=<ваш SSH ключ>

TELEGRAM_TO=<ID чата, в который придет сообщение>
TELEGRAM_TOKEN=<токен вашего бота>
```

```bash
docker-compose up -d --build
```

- После успешной сборки выполнить следующие действия (только при первом деплое):
  - провести миграции внутри контейнеров

    ```bash
    docker-compose exec backend python manage.py migrate
    ```

  - Заполнить БД

    ```bash
    docker-compose exec backend python manage.py loaddata dump.json
    ```

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
http://localhost/api/docs/
```

### Об авторе

Над проектом работал:

**Костров Михаил**
[GitHub](https://github.com/mdkostrov/)

Студент курса "Разработчик Python" (45-47 когорта). 2023 год.
