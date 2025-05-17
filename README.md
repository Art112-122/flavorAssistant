# Flavor Assistant 🤖☕️

**Flavor Assistant** — Telegram-бот для підбору фільмів, книг або пісень під ваш смак.

## 🔧 Можливості

- Використання aioMySQL
- Вибір фільмів
- Зручне використання
- Обробка вподобань користувача
- Можливість налаштування бота під себе
- Підтримка FMS
- Використання публічного api від cohere

## 📦 Встановлення та запуск

1. Клонуйте репозиторій:

```bash
git clone https://github.com/Art112-122/flavorAssistant.git
cd flavorAssistant
```

2. Встановіть залежності:

```bash
pip install -r requirements.txt
```

3. Створіть файл `.env` та додайте токен вашого бота та ключ до апі cohere та налаштування mysql:

```env
BOT_TOKEN=ваш_токен_бота
API_KEY=ваш_ключ
MYSQL_DB=ваша_база_данних
MYSQL_HOST="127.0.0.1"
MYSQL_PORT=3306
MYSQL_USER="root"
MYSQL_PASSWORD=ваш_пароль
```

4. Запустіть бота:

```bash
python main.py
```

## 🗂 Структура проєкту

```
flavorAssistant/
├── app/
│   ├── command/       # Команди
│   ├── connection/      # Інлайн та Reply-клавіатури
│   ├── state/         # FSM-стани
|   ├── .env/          # Приклад конфігураційного файлу
│   └── /         
├── main.py             # Точка входу
├── requirements.txt    # Залежності      
```

## 🛠 Використані технології

- Python 3.12+
- [aiogram](https://github.com/aiogram/aiogram)
- python-dotenv
- MYSQL (AIO)
- Структурована FSM
