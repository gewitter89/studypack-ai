# StudyPack AI

Генератор PDF-наборов учебных заданий для детей 4–10 лет.

Локальная Windows-программа. Не требует сервера или базы данных.

## Как это работает

1. Вводите параметры ребёнка (возраст, класс, язык, тема, тип заданий).
2. Программа отправляет запрос в OpenRouter AI.
3. AI генерирует структурированный набор заданий.
4. Программа создаёт PDF с обложкой, заданиями и ответами.

## Установка

### 1. Установите Python 3.11+

### 2. Установите зависимости

```bash
pip install -r requirements.txt
```

### 3. Создайте `.env`

```bash
copy .env.example .env
```

Откройте `.env` и вставьте ваш API-ключ OpenRouter:

```
OPENROUTER_API_KEY=sk-or-v1-ваш_ключ
OPENROUTER_MODEL=openrouter/free
```

Получить ключ: https://openrouter.ai/keys

## Запуск

### GUI-режим

```bash
python main.py
```

### CLI-режим

```bash
python main.py --cli --age 7 --language uk --topic dinosaurs --pack mixed_week --pages 12
```

Другие примеры:

```bash
python main.py --cli --age 6 --language ru --topic space --pack logic --pages 8 --difficulty easy
python main.py --cli --age 8 --language uk --topic animals --pack math --pages 20 --difficulty medium
```

## Структура выходных файлов

```
output/
  StudyPack_7_dinosaurs_2026-06-24.pdf   # PDF-набор
  StudyPack_7_dinosaurs_2026-06-24.json  # Исходная структура (для редактирования)
```

## Сборка .exe

```bash
pip install pyinstaller
pyinstaller --onefile --windowed --name "StudyPack AI" main.py
```

Готовый файл: `dist/StudyPack AI.exe`

## Типы наборов

- Подготовка к школе (4–6 лет)
- Математика (6–10 лет)
- Чтение (6–10 лет)
- Украинский язык (6–10 лет)
- Английский для детей (5–10 лет)
- Логика и внимание (4–10 лет)
- Смешанный набор на неделю (основной коммерческий)

## Языки

- Украинский
- Русский
- Английский
- Украинский + английский
- Русский + английский

## Ограничения MVP

- Только стиль "чёрно-белый для печати"
- Количество страниц: 8, 12, 20
- Требуется интернет для генерации через OpenRouter
- Не включает редактор перед сохранением

## Частые ошибки

**"API ключ не настроен"** — создайте `.env` и укажите ключ.

**"Нет подключения к OpenRouter"** — проверьте интернет.

**"Недостаточно средств"** — пополните счёт OpenRouter.

**"Неверный API ключ"** — проверьте ключ в `.env`.
