# CI/CD для проекта API YAMDB

Сайт доступен по следующему адресу: http://158.160.68.239/

[![GITHUB-BADGE](https://github.com/Myxadin07/foodgram-project-react/actions/workflows/foodgram_workflow.yml/badge.svg)](https://github.com/Myxadin07/foodgram-project-react/actions/workflows/foodgram_workflow.yml)

## Технологический стек
[![Python](https://img.shields.io/badge/-Python-464646?style=flat&logo=Python&logoColor=FFD700&color=8B008B)](https://www.python.org/)
[![Django](https://img.shields.io/badge/-Django-464646?style=flat&logo=Django&logoColor=FFD700&color=8B008B)](https://www.djangoproject.com/)
[![Django REST Framework](https://img.shields.io/badge/-Django%20REST%20Framework-464646?style=flat&logo=Django%20REST%20Framework&logoColor=FFD700&color=8B008B)](https://www.django-rest-framework.org/)
[![PostgreSQL](https://img.shields.io/badge/-PostgreSQL-464646?style=flat&logo=PostgreSQL&logoColor=FFD700&color=8B008B)](https://www.postgresql.org/)
[![JWT](https://img.shields.io/badge/-JWT-464646?style=flat&color=8B008B)](https://jwt.io/)
[![Nginx](https://img.shields.io/badge/-NGINX-464646?style=flat&logo=NGINX&logoColor=FFD700&color=8B008B)](https://nginx.org/ru/)
[![gunicorn](https://img.shields.io/badge/-gunicorn-464646?style=flat&logo=gunicorn&logoColor=FFD700&color=8B008B)](https://gunicorn.org/)
[![Docker](https://img.shields.io/badge/-Docker-464646?style=flat&logo=Docker&logoColor=FFD700&color=8B008B)](https://www.docker.com/)
[![Docker-compose](https://img.shields.io/badge/-Docker%20compose-464646?style=flat&logo=Docker&logoColor=FFD700&color=8B008B)](https://www.docker.com/)
[![Docker Hub](https://img.shields.io/badge/-Docker%20Hub-464646?style=flat&logo=Docker&logoColor=FFD700&color=8B008B)](https://www.docker.com/products/docker-hub)
[![GitHub%20Actions](https://img.shields.io/badge/-GitHub%20Actions-464646?style=flat&logo=GitHub%20actions&logoColor=FFD700&color=8B008B)](https://github.com/features/actions)
[![Yandex.Cloud](https://img.shields.io/badge/-Yandex.Cloud-464646?style=flat&logo=Yandex.Cloud&logoColor=FFD700&color=8B008B)](https://cloud.yandex.ru/)


Админка: 
login - mmm@gmail.com  
password - Myxadin402613

## Проект "Продуктовый помошник" (Foodgram) предоставляет пользователям следующие возможности:

* регистрироваться
* создавать свои рецепты и управлять ими (корректировать\удалять)
* просматривать рецепты других пользователей
* добавлять рецепты других пользователей в "Избранное" и в "Корзину"
* подписываться на других пользователей
* скачать список ингредиентов для рецептов, добавленных в "Корзину"

## Workflow
* tests - Проверка кода на соответствие стандарту PEP8 и запуск pytest. При неудачном прохождении, на телеграм приходит уведомление о том, что тест не пройден. Все дальнейшие дествия прерываются. 

* build_and_push_to_docker_hub - Сборка и доставка докер-образов на Docker Hub. При неудачном прохождении, на телеграм приходит уведомление о том, что тест не пройден. Все дальнейшие дествия прерываются. 

* deploy - Автоматический деплой проекта на боевой сервер. Выполняется копирование файлов из репозитория на сервер:

* send_message - Отправка уведомления в Telegram

### Подготовка для запуска workflow
Создайте и активируйте виртуальное окружение, обновите pip:
```
python3 -m venv venv
 venv/bin/activate
python3 -m pip install --upgrade pip
```
Запустите автотесты:
```
pytest
```
Отредактируйте файл `nginx/default.conf` и в строке `server_name` впишите IP виртуальной машины (сервера).  
Скопируйте подготовленные файлы `docker-compose.yaml` и `nginx/default.conf` из вашего проекта на сервер:


В репозитории на Гитхабе добавьте данные в `https://github.com/<Owner>/<Repository>/settings/secrets/actions`:
```
DOCKER_USERNAME - имя пользователя в DockerHub
DOCKER_PASSWORD - пароль пользователя в DockerHub
HOST - ip-адрес сервера
USER - пользователь
SSH_KEY - приватный ssh-ключ (публичный должен быть на сервере)
PASSPHRASE - кодовая фраза для ssh-ключа
DB_ENGINE - django.db.backends.postgresql
DB_HOST - db
DB_PORT - 5432
SECRET_KEY - секретный ключ приложения django
ALLOWED_HOSTS - список разрешённых адресов
TELEGRAM_TO - id своего телеграм-аккаунта (можно узнать у @userinfobot, команда /start)
TELEGRAM_TOKEN - токен бота (получить токен можно у @BotFather, /token, имя бота)
DB_NAME - postgres (по умолчанию)
POSTGRES_USER - postgres (по умолчанию)
POSTGRES_PASSWORD - postgres (по умолчанию)
```

## Для запуска проекта на сервере:


Установите Docker и Docker-compose:
```
sudo apt install docker.io

sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-composelocal/bin/docker-compose

sudo chmod +x /usr/local/bin/docker-compose
```
Проверьте корректность установки Docker-compose:
```
sudo  docker-compose --version  -- должен выдать: Docker Compose version v2.18.1
```

## Контакты

[![telegram](https://img.shields.io/badge/-telegram-464646?style=flat&logo=telegram&logoColor=FFD700&color=8B008B)](https://t.me/mukhadin07)
