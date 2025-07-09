Flask-Twitter
========
REST API для сервиса микроблогов на Flask с PostgreSQL базой данных.
# 📌 Основные функции
- Аутентификация пользователей по API-ключу
- Создание и управление твитами
- Система подписок на пользователей
- Лайки твитов
- Загрузка медиафайлов (изображения)
- Полноценное API с документацией Swagger

## 🛠 Технологии
- Python 3.8+
- Flask
- Flask-RESTX (Swagger документация)
- SQLAlchemy (ORM)
- PostgreSQL (база данных)
- Docker (контейнеризация)

## 🚀 Быстрый старт
1. Установка с Docker (рекомендуемый способ)
```bash
# Клонировать репозиторий
git clone https://github.com/ninja152play/Flask-Twitter.git
cd Flask-Twitter

# Собрать и запустить контейнеры
docker-compose up --build
```
После запуска API будет доступно на http://localhost:5000

Документация Swagger: http://localhost:5000/docs/

2. Локальная установка (без Docker)
 1. Установите PostgreSQL и создайте БД:
```bash
sudo -u postgres psql -c "CREATE USER admin WITH PASSWORD 'admin';"
sudo -u postgres psql -c "CREATE DATABASE twitter_db OWNER admin;"
```
Установите зависимости:

```bash
pip install -r requirements.txt
```
Запустите приложение:

```bash
python main.py
```

## 🐳 Docker конфигурация
Проект использует два сервиса:
Web (Flask приложение)

- Порт: 5000
- Зависит от готовности БД
- Автоматически подключается к PostgreSQL

DB (PostgreSQL 13)

- Порт: 5432
- Настроены healthcheck-и
- Данные сохраняются в volumes
- Предустановленные учетные данные:
- Пользователь: admin
- Пароль: admin
- БД: twitter_db

## 📊 Структура проекта
```text
Flask-Twitter/
├── app/                      # Основное приложение
│   ├── migrations/
│   ├── __init__.py
│   ├── alembic.ini       
│   ├── prod-requirements.txt # Зависимости Python для production
│   ├── models.py             # Модели БД
│   ├── utils.py              # Вспомогательные функции
│   └── app.py                # Конфигурация Flask
├── db/
│   ├── postgresql.conf       # Конфигурация PostgreSQL
│   └── Dockerfile            # Конфигурация Docker PostgreSQL
├── docker-compose.yml        # Конфигурация сервисов
├── dev-requirements.txt      # Зависимости Python для разработки
├── Dockerfile                # Конфигурация Docker app
└── main.py                   # Точка входа
```
## Аутентификация
Все запросы (кроме документации) требуют API-ключа в заголовке:

```text
Api-Key: ваш-api-ключ
При первом обращении с новым ключом система автоматически создаст нового пользователя.
```
## 🌐 API Endpoints
- POST /api/tweets/ - Создать твит
- GET /api/tweets/ - Получить твиты
- DELETE /api/tweets/<id> - Удалить твит
- POST /api/medias/ - Загрузить медиа
- POST /api/users/<id>/follow - Подписаться на пользователя
- DELETE /api/users/<id>/follow - Отписаться от пользователя
- POST /api/tweets/<id>/likes - Лайкнуть твит
- DELETE /api/tweets/<id>/likes - Убрать лайк с твита
- GET /api/users/me - Получить свой профиль
- GET /api/users/<id> -Получить профиль другого пользователя

Полная документация доступна в Swagger UI.

## ⚠️ Важно
- Для production использования замените стандартные учетные данные
- Настройте правильные права доступа к volumes в Docker
- Добавьте HTTPS и другие меры безопасности