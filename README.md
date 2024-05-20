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

2. Создайте виртуальное окружение и подключитель к нему.

3. Получите и сохраните новый Secret key, для этого перейдите в директорию с файлом manage.py и поочерёдно введите команды:

- ```python manage.py shell```
- ```from django.core.management.utils import get_random_secret_key```
- ```get_random_secret_key()```

4. Подключитесь к удалённому серверу.

5. Поочерёдно выполните комманды для установки docker на ваш сервер:

- ```sudo apt update```
- ```sudo apt install curl```
- ```curl -fSL https://get.docker.com -o get-docker.sh```
- ```sudo sh ./get-docker.sh```
- ```sudo apt install docker-compose-plugin```

6. Поочерёдно выполните комманды для установки и настройки внешнего Nginx на ваш сервер:

- ```sudo apt install nginx -y``` - Далее сервер, скорее всего, попросит вас перезагрузить операционную систему — сделайте это.
- ```sudo systemctl start nginx``` - Для проверки корректности установленной программы исполните указанную комманду и введите в адресную строку браузера IP-адрес вашего удалённого сервера без указания порта. Должна открыться страница приветствия от Nginx.
- ```sudo ufw allow 'Nginx Full'```
- ```sudo ufw allow OpenSSH```
- ```sudo ufw enable``` - В терминале выведется запрос на подтверждение операции с предупреждением, что команда может оборвать SSH-соединение, подтвердите операцию.
- ```sudo ufw status``` - Проверьте внесённые изменения, файрвол ufw сообщит вам, что он «активен» и разрешает принимать запросы на порты, которые вы указали.
- ```sudo nano /etc/nginx/sites-enabled/default ``` - Удалите все настройки из файла, запишите и сохраните новые:

    server {

       server_name food-gram.ru;

       location / {
          proxy_set_header Host $http_host;
          proxy_pass http://127.0.0.1:9009;
          server_tokens off;
       }
    }


- ```sudo nginx -t``` - проверка файла конфигурации на ошибки.
- ```sudo systemctl reload nginx``` - перезагрузка конфигурации Nginx.

7. Создайте на сервере директорию с проектом и скопируйте в созданную директорию файл docker-compose.yml.

8. Создайте в корневой директории проекта файл .env и внесите в него переменные:

- SECRET_KEY = (полученный ранее Secret key)
- ALLOWED_HOSTS = (ip адресс вашего сервера), 127.0.0.1, localhost, food-gram.ru
- POSTGRES_USER = (имя пользователя базы данных postgres)
- POSTGRES_PASSWORD = (пароль базы данных postgres)
- POSTGRES_DB = (название базы данных postgres)
- DB_HOST = (название хоста)
- DB_PORT = (порт сервера для подключения базы данных postgres)

9. На сайте Git Hub перейдите в настройках форкнутого репозитория проекта создайте следующие секреты:

- DOCKER_PASSWORD - пароль от сайта Docker Hub, где хранятся ваши образы данного проекта.
- DOCKER_USERNAME - имя пользователя от сайта Docker Hub, где хранятся ваши образы данного проекта.
- HOST - IP-адрес вашего сервера.
- USER - ваше имя пользователя на сервере.
- SSH_KEY - содержимое текстового файла с закрытым SSH-ключом.
- SSH_PASSPHRASE - passphrase для SSH_KEY.
- TELEGRAM_TO - ID вашего телеграм-аккаунта.
- TELEGRAM_TOKEN - токен вашего бота.

10. На своём локальном компьютере в корневой папке проекта создайте новые папки и файл согласно указанному пути:

*.github\workflows\main.yml*

11. В ранее созданный файл main.yml перенесите код из файла foodgram_workflow.yml.

12. Запушьте в локальный проект на Git Hub.

### Команды для наполнения баы данных на сервере

на удалённом сервере перейдите в папку с файлом docker-compose.yml и введите следующие комманды

```docker compose exec backend python manage.py loaddata data/tags.json``` - наполнение базы данных тэгами

```docker compose exec backend python manage.py loaddata data/ingredients.json``` - наполнение базы данных ингредиентами

## Список приложений используемых для разработки проекта

- Python 3.9.13
- Django 3.2.3
- djangorestframework 3.12.4
- djoser 2.1.0
- PyJWT 2.1.0
- pytest 6.2.4
- pytest-django 4.4.0
- gunicorn 20.1.0
- Node.js 18 
- nginx 1.22.1