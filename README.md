# StudyPack AI

Генератор PDF-наборов учебных заданий для детей 4–10 лет.  
Локальная Windows-программа. Не требует сервера или базы данных.

## Как это работает

1. Вводите параметры ребёнка (возраст, класс, язык, тема, тип заданий).
2. Программа отправляет запрос в OpenRouter AI (или использует офлайн-шаблон).
3. AI генерирует структурированный набор заданий.
4. Программа проверяет математику, санирует бренды, создаёт PDF.
5. PDF готов к печати и отправке клиенту.

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

Вставьте API-ключ OpenRouter:

```
OPENROUTER_API_KEY=sk-or-v1-ваш_ключ
OPENROUTER_MODEL=openrouter/free
```

Получить ключ: https://openrouter.ai/keys

## Запуск

### GUI

```bash
python main.py
```

### CLI (AI)

```bash
python main.py --cli --age 7 --language uk --topic dinosaurs --pack mixed_week --pages 12
```

### CLI (офлайн-шаблоны, без API)

```bash
python main.py --cli --offline --age 7 --pack math --pages 12
python main.py --cli --offline --age 6 --pack logic --pages 8
python main.py --cli --offline --age 8 --pack mixed_week --pages 14
```

### CLI (собрать PDF из JSON)

```bash
python main.py --cli --from-json output/StudyPack_7_dinosaurs_2026-06-24.json
```

### CLI (проверить математику в JSON)

```bash
python main.py --cli --check-math output/StudyPack_7_dinosaurs_2026-06-24.json
```

### Демо-генерация (без API)

```bash
python generate_examples.py
```

## Новые возможности (v1.1)

| Функция | Описание |
|---------|----------|
| **Офлайн-шаблоны** | 5 встроенных шаблонов без обращения к AI |
| **Редактор JSON** | GUI: кнопка "Редактор JSON" → править → "Сохранить и собрать PDF" |
| **HTML Preview** | Визуальный предпросмотр набора перед созданием PDF |
| **Собрать PDF из JSON** | Загрузить готовый JSON и получить PDF |
| **Проверка математики** | Программа проверяет сложение/вычитание в ответах AI |
| **Блочная генерация** | 30-40 страниц разбиваются на блоки по 10 страниц |
| **Защита от >20 страниц** | Предупреждение: большой набор может быть нестабильным |
| **Корректные пути** | Работает и из исходников, и после сборки PyInstaller |

## Примеры

Готовые демо-наборы в папке `examples/`:

- `7_uk_dinosaurs_mixed.pdf` — 7 лет, украинский, динозавры, смешанный
- `6_ru_space_logic.pdf` — 6 лет, русский, космос, логика
- `8_uk_animals_math.pdf` — 8 лет, украинский, животные, математика

## Типы наборов

- Подготовка к школе (4–6 лет)
- Математика (6–10 лет)
- Чтение (6–10 лет)
- Украинский язык (6–10 лет)
- Английский для детей (5–10 лет)
- Логика и внимание (4–10 лет)
- Смешанный набор на неделю (основной коммерческий)

## Языки

- Украинский, Русский, Английский
- Украинский + английский, Русский + английский

## Сборка .exe

```bash
pip install pyinstaller
pyinstaller --onedir --windowed --name "StudyPack AI" --add-data "config;config" --add-data "prompts;prompts" main.py
```

Готовый файл: `dist/StudyPack AI/StudyPack AI.exe`

Для onefile:
```bash
pyinstaller --onefile --windowed --name "StudyPack AI" --add-data "config;config" --add-data "prompts;prompts" main.py
```

## Частые ошибки

| Ошибка | Решение |
|--------|---------|
| "API ключ не настроен" | Создайте `.env` с OPENROUTER_API_KEY |
| "Нет подключения к OpenRouter" | Проверьте интернет |
| "Недостаточно средств" | Пополните счёт OpenRouter |
| "Неверный API ключ" | Проверьте ключ в `.env` |
| "Невалидный JSON" | AI вернул мусор. Попробуйте снова или используйте офлайн-режим |

## Ограничения

- Только стиль "чёрно-белый для печати" в MVP
- Для AI-генерации требуется интернет и ключ OpenRouter
- Редактор — текстовый (JSON), графический редактор в разработке
- 30-40 страниц — блочная генерация (может быть медленнее)
