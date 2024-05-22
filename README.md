# Foodgram.

![foodgram workflow](https://github.com/NikolayModenov/foodgram-project-react/actions/workflows/main.yml/badge.svg)

### Автор

1. Николай Моденов  
   - Аккаунт GitHub: [NikolayModenov](https://github.com/NikolayModenov)

## Описание

Проект foodgram представляет собой платформу на которой каждый может поделиться своим рецептом, просматривать рецепты других пользователей, подписаться под разными авторами и разными рецептами, создать список покупок продуктов тех рецептов которые заинтересовали.

Просматривать рецепты и страницы пользователей могут любые посетители. 

Подписываться на рецепты и авторов, а так же добавлять свои рецепты могут только зарегистрированные посетители.

### Техническое описание проекта

Проект kittygram запущен в docker-контейнерах на удалённом сервере.
Настроено автоматическое тестирование проекта и деплой на удалённый сервер при внесении изменений в существующий проект.

### Запуск проекта на новом сервере

1. Форкните проект [foodgram-project-react](https://github.com/NikolayModenov/foodgram-project-react/) на свой аккаунт Git Hub и склонируйте на свой локальный компьютер. 

-```git clone git@github.com:<ваше_имя_пользователя_на_GitHub>/foodgram-project-react.git```

2. Создайте виртуальное окружение и подключитель к нему.

- ```python -m venv venv``` - создание окружения
- ```source venv/Scripts/activate``` - подключение к созданному окружению

3. Получите и сохраните новый Secret key, для этого перейдите в директорию с файлом manage.py и поочерёдно введите команды:

- ```python manage.py shell```
- ```from django.core.management.utils import get_random_secret_key```
- ```get_random_secret_key()```

4. Подключитесь к удалённому серверу.

5. Установите docker на ваш сервер.

6. Создайте на сервере директорию с проектом и скопируйте в созданную директорию файл docker-compose.yml.

7. Создайте в корневой директории проекта файл .env и внесите в него переменные:

- SECRET_KEY = (полученный ранее Secret key)
- ALLOWED_HOSTS = (ip адресс вашего сервера), 127.0.0.1, localhost, food-gram.ru
- POSTGRES_USER = (имя пользователя базы данных postgres)
- POSTGRES_PASSWORD = (пароль базы данных postgres)
- POSTGRES_DB = (название базы данных postgres)
- DB_HOST = (название хоста)
- DB_PORT = (порт сервера для подключения базы данных postgres)

8. На сайте Git Hub перейдите в настройках форкнутого репозитория проекта создайте следующие секреты:

- DOCKER_PASSWORD - пароль от сайта Docker Hub, где хранятся ваши образы данного проекта.
- DOCKER_USERNAME - имя пользователя от сайта Docker Hub, где хранятся ваши образы данного проекта.
- HOST - IP-адрес вашего сервера.
- USER - ваше имя пользователя на сервере.
- SSH_KEY - содержимое текстового файла с закрытым SSH-ключом.
- SSH_PASSPHRASE - passphrase для SSH_KEY.
- TELEGRAM_TO - ID вашего телеграм-аккаунта.
- TELEGRAM_TOKEN - токен вашего бота.

9. На своём локальном компьютере в корневой папке проекта создайте новые папки и файл согласно указанному пути:

*.github\workflows\main.yml*

10. В ранее созданный файл main.yml перенесите код из файла foodgram_workflow.yml.

11. Запушьте в локальный проект на Git Hub.

### Локальный запуск проекта

1. Склонируйте проект на свой локальный компьютер. 

-```git clone git@github.com:NikolayModenov/foodgram-project-react.git```

2. Перейдите в директорию с проектом foodgram-project-react.

- ```cd foodgram-project-react/```

3. Создайте виртуальное окружение и подключитель к нему.

- ```python -m venv venv``` - создание окружения
- ```source venv/Scripts/activate``` - подключение к созданному окружению

4. Создайте в корневой директории проекта файл .env и внесите в него переменные:

- SECRET_KEY = (полученный ранее Secret key)
- ALLOWED_HOSTS = (ip адресс вашего сервера), 127.0.0.1, localhost, food-gram.ru
- POSTGRES_USER = (имя пользователя базы данных postgres)
- POSTGRES_PASSWORD = (пароль базы данных postgres)
- POSTGRES_DB = (название базы данных postgres)
- DB_HOST = (название хоста)
- DB_PORT = (порт сервера для подключения базы данных postgres)

5. Перейдите в директорию backend, где располагается файл manage.py:

- ```cd backend/```

6. Запустите backend сервер:

- ```python manage.py migrate``` - запуск миграций в базе данных.
- ```python manage.py runserver``` - локальный запуск backend сервера.
- ```python manage.py loaddata data/tags.json``` - наполнение базы данных тэгами.
- ```python manage.py loaddata data/ingredients.json``` - наполнение базы данных ингредиентами.

### Команды для наполнения баы данных на сервере

на удалённом сервере перейдите в папку с файлом docker-compose.yml и введите следующие комманды

```docker compose exec backend python manage.py loaddata data/tags.json``` - наполнение базы данных тэгами

```docker compose exec backend python manage.py loaddata data/ingredients.json``` - наполнение базы данных ингредиентами

## Список приложений используемых для разработки проекта

Бэкенд проекта реализован на базе django rest framework, фронтенд на базе Node.js.
Аутентификация осуществляется при помощи djoser.
Для автоматизации развёртывания применяется docker.
Взаимосвязь контёнеров docker осуществляется при помощи прокси сервера nginx.
Wsgi server - gunicorn, осуществляет взаимодействие nginx и django rest framework.
