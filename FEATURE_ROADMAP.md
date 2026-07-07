# StudyPack AI — Feature Roadmap

> Исследовано 2026-07-07 на базе Kumon, Логля, Умназия, Skysmart, Развивай-ка, Фабрика Заданий, K5 Learning.

---

## ✅ Сделано

### Phase 1: Визуальные задания (интегрировано 2026-07-07)

| Тип | Генератор | Рендеринг | Тесты |
|-----|-----------|-----------|-------|
| Color by Number | `ColorByNumberGenerator` | SVG-style сетка с легендой | ✅ |
| Sudoku (4x4) | `SudokuGenerator` | сетка с пустыми клетками | ✅ |
| Connect the Dots | `ConnectDotsGenerator` | пронумерованные точки | ✅ |
| Graphic Dictation | `GraphicDictationGenerator` | инструкции по клеткам | ✅ |

### Phase 2: Сложные визуальные типы (интегрировано 2026-07-07)

| Тип | Генератор | Рендеринг | Тесты |
|-----|-----------|-----------|-------|
| Find the Differences | `FindDifferencesGenerator` (4x4, 4-6 diffs) | две параллельные сетки | ✅ |
| Maze | `MazeGenerator` (с ответами) | walls/paths grid | ✅ |
| Crossword | `CrosswordGenerator` (с пересечениями) | клетки с номерами и подсказками | ✅ |

### Phase 3: Маскоты и бонусные страницы (интегрировано ранее)

- 5 маскотов: медведь (narrator), панда (creative), ёжик (math), слон (reading), птичка (logic)
- Бонус-страницы: наклейки-награды, surprise bonus, секретный код
- Вставлены автоматически в каждый PDF

### Phase 4: Геймификация — XP, достижения, звёзды (интегрировано 2026-07-07)

| Компонент | Описание | Статус |
|-----------|----------|--------|
| `XPProgress` | 10 XP за задачу, 1.3x scale per level | ✅ |
| 10 Achievements | first_pack, math_master, logic_king, reader_star, creative_soul, full_completion, speed_demon, perfect_score, explorer, persistence | ✅ |
| `StarReward` | ⭐ за каждую визуальную/творческую страницу | ✅ |
| Мотивационные цитаты | 6 цитат × 3 языка, ротация | ✅ |
| Рендеринг страницы достижений | XP-level, progress bar, звёзды, бейджи, цитата | ✅ |
| Интеграция в generator.py | `_gamification` dict в pack_data | ✅ |
| 22 unit теста | XP, achievements, stars, quotes, multilang | ✅ |

### Итого

- **179/179 тестов проходят**
- **End-to-end PDF: 166KB**, все 7 визуальных типов + gamification
- GitHub Pages: https://gewitter89.github.io/studypack-ai/

---

## 🔮 Следующие фазы

### Phase 5: AI-Personalization (интегрировано 2026-07-07)

| Компонент | Описание | Статус |
|-----------|----------|--------|
| `adaptive_difficulty.py` | 5 возрастных групп (3-4, 5-6, 7-8, 9-10, 11-12) с параметрами для всех типов | ✅ |
| `adaptive_math_range` | Математика масштабируется: 4yo→1-5, 10yo→10-50 | ✅ |
| `recommended_card_mix` | Автоматический подбор типов карточек по возрасту | ✅ |
| `THEME_CHAINS` | 5 цепочек тем для сериалов: animals, nature, adventure и т.д. | ✅ |
| `generate_story_opening` | Персонализированное начало рассказа с именем ребёнка (uk/ru/en) | ✅ |
| `adaptive_card_params` | Размер сеток, количество отличий/слов для каждого типа | ✅ |
| Интеграция в `card_generator.py` | Автоматическое применение adaptive params к templates | ✅ |
| 37 unit тестов | `test_adaptive_difficulty.py` | ✅ |

### Phase 6: Аналитика для родителей (интегрировано 2026-07-07)

| Компонент | Описание | Статус |
|-----------|----------|--------|
| `analytics.py` | Генерация отчёта с breakdown по категориям (math/logic/reading/creative) | ✅ |
| `ParentReport` | total_tasks, accuracy, strengths, areas_to_work, recommendations, category_breakdown | ✅ |
| `format_report_text` | Текстовый вывод отчёта (uk/ru/en) с процентами и рекомендациями | ✅ |
| `CATEGORY_MAP` | Маппинг card_type → категория (math, logic, reading, creative) | ✅ |
| `TYPE_LABELS` | Локализованные названия типов заданий (3 языка) | ✅ |
| Страница отчёта в PDF | `_build_parent_report_page` — таблица категорий + текст | ✅ |
| 17 unit тестов | `test_analytics.py` | ✅ |

### Phase 7: Серии PDF и мультимедиа (интегрировано 2026-07-07)

| Компонент | Описание | Статус |
|-----------|----------|--------|
| `series_generator.py` | Генерация серии связанных паков с прогрессивной сложностью | ✅ |
| `SeriesConfig` | name, theme_chain, total_packs, difficulty_start, difficulty_progress | ✅ |
| `build_series_presets` | Создание preset-ов для каждого пака в серии | ✅ |
| `generate_series` | Полный цикл: presets → pack_data + `_series` метаданные | ✅ |
| `get_difficulty_for_pack` | Прогрессия easy→medium→hard по индексу пака | ✅ |
| `multimedia.py` | TTS-хуки (gTTS optional), QR-коды для аудио | ✅ |
| `generate_tts_for_instructions` | Аудиофайлы для каждой страницы (when gTTS installed) | ✅ |
| `create_qr_codes_for_audio` | QR-коды с ссылками на аудио | ✅ |
| 12 unit тестов | `test_series_generator.py` + `test_multimedia.py` (13) | ✅ |
| End-to-end серия | 3 PDF (153KB → 166KB → 170KB), easy→medium→hard | ✅ |

### Итого

- **259/259 тестов проходят**
- **End-to-end серия: 3 PDF с прогрессивной сложностью**
- **Родительский отчёт рендерится в каждом PDF**
- GitHub Pages: https://gewitter89.github.io/studypack-ai/

---

## 🔮 Следующие фазы (Roadmap v2)

### Phase 8: LLM-интеграция и адаптивный контент

- [ ] AI-генерация задач через OpenAI / Groq API с fallback cascade
- [ ] Динамические рассказы с учётом интересов ребёнка
- [ ] AI-проверка ответов в свободной форме
- [ ] Персонализация на основе истории ответов

### Phase 9: Платформа и монетизация

- [ ] Telegram-бот для заказа паков через чат
- [ ] Подписочная модель (месяц/год)
- [ ] Stripe / Telegram Stars оплата
- [ ] CRM: родительский кабинет с историей и прогрессом

### Phase 10: Мультимедиа v2

- [ ] Полноценные TTS-инструкции в каждом PDF (при наличии API key)
- [ ] AR-раскраски через камеру
- [ ] Интерактивные онлайн-задания (web-версия)
- [ ] Совместная работа (родитель-ребёнок через app)

---

## Архитектурные решения (принятые)

1. **Deterministic generators** — для визуальных типов (без LLM)
2. **Quality Gate exemption** — визуальные типы не требуют question
3. **Visual dispatcher** — `visual_renderers.py` маршрутизирует по card_type
4. **Gamification layer** — вычисления отдельно от генерации, рендеринг опциональный
5. **Adaptive difficulty** — параметры масштабируются по возрасту, не hardcoded
6. **Analytics from pack_data** — отчёт строится из данных, которые уже есть в pack_data
7. **Series as presets** — серия = набор preset-ов с прогрессивными параметрами
8. **Multimedia hooks** — TTS/QR optional (graceful degradation если зависимости не установлены)

---

## Ссылки

- Kumon: https://www.kumon.com/
- Умназия: https://umnazia.ru/
- Логля: https://logly.ru/
- Skysmart: https://skysmart.ru/
