# Internet Shop API

REST API интернет-магазина.

## Что делает проект

Проект предоставляет API для интернет-магазина. Реализованы:

- Регистрация и авторизация через JWT
- Профиль пользователя с пополнением баланса
- Просмотр товаров для пользователя и редактирование для администратора
- Добавление товаров, удаление, изменение количества, просмотр из корзины
- Создание заказа из корзины с проверкой остатков на складе и баланса пользователя, списание баланса и товаров, очистка корзины
- Логирование успешных заказов в файл и в консоль
- Документация API через Swagger

## Запуск через Docker

1. Клонируйте репозиторий:
   git clone github.com/nikitosiky/wbshop
   cd wbshop

2. Создайте файл .env из шаблона:
   cp .env.example .env

3. Запустите проект:
   docker compose up --build

4. Примените миграции:
   docker compose exec web python manage.py migrate

5. Создайте администратора:
   docker compose exec web python manage.py createsuperuser

После запуска проект доступен по адресам:
- Документация API: http://localhost:8000/api/docs/
- Админка: http://localhost:8000/admin/

## Тесты

docker compose exec web python manage.py test