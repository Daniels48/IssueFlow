
# IssueFlow 🐛

IssueFlow — веб-приложение для управления проектами, задачами и командной работой.

Приложение позволяет создавать проекты, управлять задачами (Issues), назначать исполнителей, отслеживать статусы и приоритеты, а также взаимодействовать с задачами через комментарии.

## Возможности

- Регистрация и аутентификация пользователей
- JWT-аутентификация (Access и Refresh токены)
- Управление пользовательскими сессиями
- Подтверждение электронной почты
- Восстановление пароля
- Drag & Drop для управления задачами
- Redis для хранения пользовательских сессий
- RabbitMQ для обмена событиями между сервисами
- Event-driven обработка фоновых событий
- WebSocket для работы с событиями в реальном времени
- Outbox pattern для надёжной публикации событий
- RBAC (Admin / Owner / Member)
- Alembic-миграции
- Backend-тесты
- Структурированное JSON-логирование

## Технологии

- Python
- FastAPI
- PostgreSQL
- SQLAlchemy
- Alembic
- Redis
- RabbitMQ
- JWT
- WebSocket
- HTML / CSS / JavaScript
- Docker / Docker Compose
- Pytest

## 🚀 Запуск проекта

### 1️⃣ Клонировать репозиторий

```bash
git clone https://github.com/Daniels48/IssueFlow.git
```
```bash
cd IssueFlow
```


### 2️⃣ Создать файл `.env`

Скопируйте `.env.example` и переименуйте его в `.env`:

```bash
cp .env.example .env
```

После этого при необходимости измените значения переменных в файле `.env`.

### 3️⃣ Запустить контейнеры

**Linux / macOS:**

```bash
make up
```

**Windows:**
```bash
docker compose up -d --build
```

### 4️⃣ Применить миграции

**Linux / macOS:**

```bash
make upgrade
```

**Windows :**

```bash
docker compose exec api alembic -c app/infrastructure/db/alembic.ini upgrade head
```

### 5️⃣ Загрузить тестовые данные

**Linux / macOS:**

```bash
make seed
```

**Windows:**

```bash
docker compose exec api python -m scripts.seed
```

### 6️⃣ Открыть приложение

```text
http://localhost:8000
```

### 7️⃣ API документация

```text
http://localhost:8000/docs
```


## 🧪 Тесты

Запустить все backend-тесты:

```bash
docker compose exec api pytest -v
```

## Тестовые пользователи

Пароль для всех пользователей:

```text
password123
```

| Email | Роль | Статус |
|---|---|---|
| `admin@example.com` | Admin | Подтверждён |
| `owner@example.com` | Владелец досок | Подтверждён |
| `editor@example.com` | Editor | Подтверждён |
| `viewer@example.com` | Viewer | Подтверждён |
| `unverified@example.com` | User | Не подтверждён |