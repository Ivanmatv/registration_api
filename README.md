# Реферальная система
Простая реферальная система с авторизацией по номеру телефона, реализованная на Django и Django REST Framework.i

## Функциональность
🔐 Авторизация по номеру телефона с подтверждением через 4-значный код

👤 Профиль пользователя с персональным инвайт-кодом

🔗 Активация чужого инвайт-кода (один раз на пользователя)

📊 Просмотр рефералов - списка пользователей, активировавших ваш инвайт-код

📚 API документация через Swagger и ReDoc

🎨 Веб-интерфейс на Django Templates для тестирования

## Технологический стек
- Backend: Django 5.x, Django REST Framework
- База данных: PostgreSQL
- Аутентификация: JWT токены
- Документация API: drf-yasg (Swagger/ReDoc)

## Установка и запуск
1. Создание виртуального окружения
```bash
  python -m venv venv
  source venv/bin/activate  # Linux/Mac
  # или
  venv\Scripts\activate  # Windows
```
2. Установка зависимостей
```bash
  pip install -r requirements.txt
```
3. Настройка окружения
 
    Создайте файл .env в корневой директории:
```bash
  SECRET_KEY=your-secret-key-here
  DB_NAME=referral_db
  DB_USER=db_user
  DB_PASSWORD=db_password
  DB_HOST=localhost
  DB_PORT=5432
```
4. Примените миграции
```bash
  python manage.py makemigrations
  python manage.py migrate
```
5. Создайте суперпользователя (для админки)
```bash
  python manage.py createsuperuser
```
6. Запуск сервера
```bash
  python manage.py runserver
```
Приложение будет доступно по адресу: http://localhost:8000
## API Endpoints
### Аутентификация
- POST /api/users/v1/auth/request/ - Запрос кода авторизации
- POST /api/users/v1/auth/verify/ - Подтверждение кода авторизации
- POST /api/token/ - Получение JWT токена
- POST /api/token/refresh/ - Обновление JWT токена
### Профиль пользователя
- GET /api/users/v1/profile/ - Получение профиля пользователя
- POST /api/users/v1/profile/activate/ - Активация инвайт-кода
### Документация API
- Swagger UI: http://localhost:8000/swagger/
- ReDoc: http://localhost:8000/redoc/
## Примеры запросов API
1. Запрос кода авторизации

Endpoint: POST  http://localhost:8000/api/users/v1/auth/request/

Body:
```bash
{
    "phone": "+79123456789"
}
```
Response:
```bash
{
    "message": "Код отправлен",
    "debug": "Код подтверждения для +79123456789: 1234"
}
```
2. Подтверждение кода авторизации

Endpoint: POST http://localhost:8000/api/users/v1/auth/verify/

Body:
```bash
{
    "code": "1234"
}
```
Response:
```bash
{
    "message": "Успешная авторизация",
    "access": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
    "refresh": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..."
}
```
3. Получение профиля пользователя

Endpoint: GET http://localhost:8000/api/users/v1/profile/

Response:
```bash
{
    "phone": "+79123456789",
    "invite_code": "A1B2C3",
    "activated_invite_code": "X9Y8Z7",
    "referrals": ["+79987654321", "+79876543210"]
}
```
4. Активация инвайт-кода

Endpoint: POST http://localhost:8000/api/users/v1/profile/activate/

Body:
```bash
{
    "invite_code": "X9Y8Z7"
}
```

Response:
```bash
{
    "message": "Код активирован"
}
```

## Веб-интерфейс
Для удобства тестирования реализован веб-интерфейс:

- Главная страница: http://localhost:8000/
- Авторизация: http://localhost:8000/auth/phone/
- Подтверждение кода: http://localhost:8000/auth/verify/
- Профиль пользователя: http://localhost:8000/profile/
- Активация инвайт-кода: http://localhost:8000/profile/activate/