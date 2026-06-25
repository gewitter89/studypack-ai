import random
import re
from typing import Dict, List, Optional
from core.language_layer import get as ll_get
from core.topic_lexicon import random_word

_INSTRUCTION_POOLS: Dict[str, Dict[str, List[str]]] = {
    "math_addition": {
        "ru": [
            "Посчитай и запиши ответ.",
            "Сложи числа и запиши результат.",
            "Реши примеры на сложение.",
            "Найди сумму чисел.",
            "Сколько будет? Запиши ответ.",
        ],
        "uk": [
            "Порахуй і запиши відповідь.",
            "Додай числа та запиши результат.",
            "Розв'яжи приклади на додавання.",
            "Знайди суму чисел.",
            "Скільки буде? Запиши відповідь.",
        ],
        "en": [
            "Add the numbers and write the answer.",
            "Find the sum of the numbers.",
            "Solve the addition problems.",
            "What is the total? Write it down.",
        ],
    },
    "math_subtraction": {
        "ru": [
            "Вычти и запиши ответ.",
            "Реши примеры на вычитание.",
            "Найди разность чисел.",
            "Сколько осталось? Запиши.",
        ],
        "uk": [
            "Відніми та запиши відповідь.",
            "Розв'яжи приклади на віднімання.",
            "Знайди різницю чисел.",
            "Скільки залишилося? Запиши.",
        ],
        "en": [
            "Subtract and write the answer.",
            "Solve the subtraction problems.",
            "Find the difference.",
            "How many are left? Write it down.",
        ],
    },
    "math_compare": {
        "ru": ["Поставь знак >, < или =.", "Сравни числа.", "Какой знак пропущен?"],
        "uk": ["Постав знак >, < або =.", "Порівняй числа.", "Який знак пропущено?"],
        "en": ["Put the sign >, < or =.", "Compare the numbers.", "Which sign is missing?"],
    },
    "math_multiplication": {
        "ru": ["Реши примеры на умножение.", "Умножь числа.", "Найди произведение.", "Вычисли произведение чисел.", "Таблица умножения: вставь ответ."],
        "uk": ["Розв'яжи приклади на множення.", "Помнож числа.", "Знайди добуток.", "Обчисли добуток чисел.", "Таблиця множення: встав відповідь."],
        "en": ["Solve the multiplication problems.", "Multiply the numbers.", "Find the product.", "Calculate the product.", "Multiplication table: fill in the answer."],
    },
    "math_division": {
        "ru": ["Реши примеры на деление.", "Раздели числа.", "Найди частное.", "Выполни деление.", "Подели и запиши ответ."],
        "uk": ["Розв'яжи приклади на ділення.", "Поділи числа.", "Знайди частку.", "Виконай ділення.", "Поділи та запиши відповідь."],
        "en": ["Solve the division problems.", "Divide the numbers.", "Find the quotient.", "Complete the division.", "Divide and write the answer."],
    },
    "missing_number": {
        "ru": ["Вставь пропущенное число.", "Какое число пропущено?", "Найди неизвестное число."],
        "uk": ["Встав пропущене число.", "Яке число пропущено?", "Знайди невідоме число."],
        "en": ["Fill in the missing number.", "What number is missing?", "Find the unknown number."],
    },
    "math_word": {
        "ru": ["Реши задачу.", "Прочитай условие и ответь.", "Какой ответ в задаче?"],
        "uk": ["Розв'яжи задачу.", "Прочитай умову та дай відповідь.", "Яка відповідь у задачі?"],
        "en": ["Solve the problem.", "Read the story and answer.", "What is the answer?"],
    },
    "math_scheme": {
        "ru": ["Запиши выражение.", "Составь пример по схеме.", "Заполни пропуски."],
        "uk": ["Запиши вираз.", "Склади приклад за схемою.", "Заповни пропуски."],
        "en": ["Write the expression.", "Make a problem from the scheme.", "Fill in the blanks."],
    },
    "story_read": {
        "ru": ["Прочитай текст.", "Прочитай небольшой рассказ.", "Прочитай историю.", "Прочитай внимательно."],
        "uk": ["Прочитай текст.", "Прочитай невелику розповідь.", "Прочитай історію.", "Прочитай уважно."],
        "en": ["Read the text.", "Read the short story.", "Read the story carefully."],
    },
    "question_answer": {
        "ru": ["Ответь на вопросы по тексту.", "Что ты узнал из текста?", "Проверь себя."],
        "uk": ["Дай відповіді на запитання.", "Що ти дізнався з тексту?", "Перевір себе."],
        "en": ["Answer the questions about the text.", "What did you learn?", "Check yourself."],
    },
    "character_guess": {
        "ru": ["Угадай героя по описанию.", "Кто это? Прочитай и угадай.", "Из какой сказки герой?"],
        "uk": ["Відгадай героя за описом.", "Хто це? Прочитай та відгадай.", "З якої казки герой?"],
        "en": ["Guess the character from the description.", "Who is it? Read and guess."],
    },
    "main_idea": {
        "ru": ["Какая главная мысль?", "О чём этот текст?", "Что хотел сказать автор?"],
        "uk": ["Яка головна думка?", "Про що цей текст?", "Що хотів сказати автор?"],
        "en": ["What is the main idea?", "What is this text about?", "What did the author mean?"],
    },
    "find_word": {
        "ru": ["Найди слово в тексте.", "Найди и обведи слово.", "Где спряталось слово?"],
        "uk": ["Знайди слово в тексті.", "Знайди та обведи слово.", "Де сховалося слово?"],
        "en": ["Find the word in the text.", "Find and circle the word.", "Where is the word hidden?"],
    },
    "pattern": {
        "ru": ["Продолжи ряд.", "Найди закономерность.", "Какое число следующее?"],
        "uk": ["Продовж ряд.", "Знайди закономірність.", "Яке число наступне?"],
        "en": ["Continue the pattern.", "Find the rule.", "What comes next?"],
    },
    "odd_one_out": {
        "ru": ["Что лишнее? Найди и объясни.", "Какой предмет лишний?", "Найди лишнее слово."],
        "uk": ["Що зайве? Знайди та поясни.", "Який предмет зайвий?", "Знайди зайве слово."],
        "en": ["What is odd? Find and explain.", "Which item is different?", "Find the odd one out."],
    },
    "sequence": {
        "ru": ["Расставь по порядку.", "Что было сначала, что потом?", "Восстанови последовательность."],
        "uk": ["Розстав по порядку.", "Що було спочатку, що потім?", "Віднови послідовність."],
        "en": ["Put in order.", "What happened first, what next?", "Restore the sequence."],
    },
    "maze": {
        "ru": ["Пройди лабиринт.", "Найди выход из лабиринта.", "Помоги найти путь."],
        "uk": ["Пройди лабіринт.", "Знайди вихід з лабіринту.", "Допоможи знайти шлях."],
        "en": ["Go through the maze.", "Find the exit.", "Help find the way."],
    },
    "analogy": {
        "ru": ["Найди аналогию.", "Подбери пару по смыслу.", "Что подходит по аналогии?"],
        "uk": ["Знайди аналогію.", "Добери пару за змістом.", "Що підходить за аналогією?"],
        "en": ["Find the analogy.", "Match the pair.", "What fits by analogy?"],
    },
    "sudoku": {
        "ru": ["Заполни судоку.", "Вставь пропущенные цифры.", "Реши судоку."],
        "uk": ["Заповни судоку.", "Встав пропущені цифри.", "Розв'яжи судоку."],
        "en": ["Fill in the sudoku.", "Fill in the missing numbers.", "Solve the sudoku."],
    },
    "crossword": {
        "ru": ["Разгадай кроссворд.", "Заполни клетки.", "Отгадай слова по вопросам."],
        "uk": ["Розгадай кросворд.", "Заповни клітинки.", "Відгадай слова за запитаннями."],
        "en": ["Complete the crossword.", "Fill in the cells.", "Guess the words."],
    },
    "detective": {
        "ru": ["Реши детективную задачу.", "Кто это сделал? Расследуй.", "Найди улики и сделай вывод."],
        "uk": ["Розв'яжи детективну задачу.", "Хто це зробив? Розслідуй.", "Знайди докази та зроби висновок."],
        "en": ["Solve the detective case.", "Who did it? Investigate.", "Find clues and draw a conclusion."],
    },
    "deduction": {
        "ru": ["Сделай вывод из фактов.", "Что из этого следует?", "Используй логику."],
        "uk": ["Зроби висновок з фактів.", "Що з цього випливає?", "Використай логіку."],
        "en": ["Draw a conclusion from the facts.", "What follows from this?", "Use logic."],
    },
    "table_fill": {
        "ru": ["Заполни таблицу.", "Вставь данные в таблицу.", "Дополни таблицу."],
        "uk": ["Заповни таблицю.", "Встав дані в таблицю.", "Доповни таблицю."],
        "en": ["Fill in the table.", "Complete the table.", "Add data to the table."],
    },
    "puzzle_lines": {
        "ru": ["Соедини по точкам.", "Проведи линии правильно.", "Соедини линиями."],
        "uk": ["З'єднай по точках.", "Проведи лінії правильно.", "З'єднай лініями."],
        "en": ["Connect the dots.", "Draw the lines correctly.", "Match with lines."],
    },
    "count_trace": {
        "ru": ["Посчитай предметы.", "Сколько здесь?", "Обведи правильное число."],
        "uk": ["Порахуй предмети.", "Скільки тут?", "Обведи правильне число."],
        "en": ["Count the objects.", "How many are there?", "Circle the correct number."],
    },
    "letter_trace": {
        "ru": ["Обведи букву по точкам.", "Напиши букву.", "Обведи и запомни букву."],
        "uk": ["Обведи букву за точками.", "Напиши букву.", "Обведи та запам'ятай букву."],
        "en": ["Trace the letter.", "Write the letter.", "Trace and remember the letter."],
    },
    "shape_find": {
        "ru": ["Найди фигуру.", "Какая это фигура?", "Найди и обведи фигуру."],
        "uk": ["Знайди фігуру.", "Яка це фігура?", "Знайди та обведи фігуру."],
        "en": ["Find the shape.", "What shape is this?", "Find and circle the shape."],
    },
    "same_shape": {
        "ru": ["Найди такую же фигуру.", "Где такая же?", "Соедини одинаковые."],
        "uk": ["Знайди таку ж фігуру.", "Де така сама?", "З'єднай однакові."],
        "en": ["Find the same shape.", "Where is the matching one?", "Match the same ones."],
    },
    "coloring": {
        "ru": ["Раскрась картинку.", "Какого цвета?", "Раскрась по цифрам."],
        "uk": ["Розфарбуй малюнок.", "Якого кольору?", "Розфарбуй за цифрами."],
        "en": ["Colour the picture.", "What colour is it?", "Colour by numbers."],
    },
    "color_find": {
        "ru": ["Какого цвета?", "Найди цвет.", "Покажи правильный цвет."],
        "uk": ["Якого кольору?", "Знайди колір.", "Покажи правильний колір."],
        "en": ["What colour is it?", "Find the colour.", "Show the correct colour."],
    },
    "color_find_en": {
        "ru": ["Найди цвет.", "Какого цвета?", "Покажи цвет по-английски."],
        "uk": ["Знайди колір.", "Якого кольору?", "Покажи колір англійською."],
        "en": ["Find the colour.", "What colour is it?", "Find the colour in English."],
    },
    "count_en": {
        "ru": ["Посчитай по-английски.", "Сколько? Напиши число.", "How many?"],
        "uk": ["Порахуй англійською.", "Скільки? Напиши число.", "How many?"],
        "en": ["Count in English.", "How many? Write the number.", "How many are there?"],
    },
    "word_picture": {
        "ru": ["Соедини слово и картинку.", "Какое слово подходит?", "Найди пару."],
        "uk": ["З'єднай слово та малюнок.", "Яке слово підходить?", "Знайди пару."],
        "en": ["Match the word and picture.", "Which word fits?", "Find the pair."],
    },
    "fill_gap_en": {
        "ru": ["Вставь пропущенное слово.", "Заполни пропуск.", "Какое слово пропущено?", "Дополни предложение.", "Выбери верный вариант."],
        "uk": ["Встав пропущене слово.", "Заповни пропуск.", "Яке слово пропущено?", "Доповни речення.", "Обери вірний варіант."],
        "en": ["Fill in the missing word.", "Complete the gap.", "Which word is missing?", "Complete the sentence.", "Choose the correct option."],
    },
    "correct_form_en": {
        "ru": ["Выбери правильную форму.", "Какое слово правильное?", "Исправь ошибку.", "Поставь глагол в нужную форму.", "Какая форма верная?"],
        "uk": ["Обери правильну форму.", "Яке слово правильне?", "Виправ помилку.", "Постав дієслово у потрібну форму.", "Яка форма вірна?"],
        "en": ["Choose the correct form.", "Which word is correct?", "Fix the mistake.", "Put the verb in the right form.", "Which form is correct?"],
    },
    "sentence_build": {
        "ru": ["Составь предложение из слов.", "Поставь слова в правильном порядке.", "Напиши предложение."],
        "uk": ["Склади речення зі слів.", "Постав слова у правильному порядку.", "Напиши речення."],
        "en": ["Make a sentence from the words.", "Put the words in order.", "Write the sentence."],
    },
    "match_pairs_en": {
        "ru": ["Соедини пары.", "Найди соответствия.", "Подбери перевод."],
        "uk": ["З'єднай пари.", "Знайди відповідності.", "Добери переклад."],
        "en": ["Match the pairs.", "Find the matches.", "Match the translation."],
    },
    "question_answer_en": {
        "ru": ["Ответь на вопросы по-английски.", "Прочитай и ответь.", "Answer the questions."],
        "uk": ["Дай відповіді на запитання англійською.", "Прочитай та дай відповідь.", "Answer the questions."],
        "en": ["Answer the questions in English.", "Read and answer.", "Answer the questions."],
    },
    "abc_match": {
        "ru": ["Соедини букву и картинку.", "Какая буква? Найди пару.", "Алфавит: найди пару."],
        "uk": ["З'єднай букву та малюнок.", "Яка буква? Знайди пару.", "Абетка: знайди пару."],
        "en": ["Match the letter and picture.", "What letter? Find the pair.", "Alphabet: find the pair."],
    },
    "color_match": {
        "ru": ["Какой цвет? Соедини.", "Найди пару по цвету.", "Соедини одинаковые цвета."],
        "uk": ["Який колір? З'єднай.", "Знайди пару за кольором.", "З'єднай однакові кольори."],
        "en": ["What colour? Match.", "Find the colour pair.", "Match the same colours."],
    },
    "fallback": {
        "ru": ["Выполни задание.", "Сделай упражнение.", "Попробуй решить."],
        "uk": ["Виконай завдання.", "Зроби вправу.", "Спробуй розв'язати."],
        "en": ["Do the task.", "Complete the exercise.", "Try to solve it."],
    },
}

_AGE_SHORT = {
    "ru": {
        4: ["Посмотри и посчитай.", "Найди и покажи.", "Попробуй ещё раз."],
        5: ["Посчитай предметы.", "Найди правильный ответ.", "Проверь себя."],
    },
    "uk": {
        4: ["Подивись та порахуй.", "Знайди та покажи.", "Спробуй ще раз."],
        5: ["Порахуй предмети.", "Знайди правильну відповідь.", "Перевір себе."],
    },
    "en": {
        4: ["Look and count.", "Find and show.", "Try again."],
        5: ["Count the objects.", "Find the right answer.", "Check yourself."],
    },
}

_TOPIC_TEMPLATES = {
    "ru": [
        "Реши примеры про {topic}.",
        "Помоги {topic} выполнить задания.",
        "Приключения {topic}: выполни задания.",
        "Посчитай вместе с {topic}.",
        "Найди ответы и помоги {topic}.",
    ],
    "uk": [
        "Розв'яжи приклади про {topic}.",
        "Допоможи {topic} виконати завдання.",
        "Пригоди {topic}: виконай завдання.",
        "Порахуй разом з {topic}.",
        "Знайди відповіді та допоможи {topic}.",
    ],
    "en": [
        "Solve problems about {topic}.",
        "Help {topic} do the tasks.",
        "Adventures of {topic}: complete the tasks.",
        "Count together with {topic}.",
        "Find the answers and help {topic}.",
    ],
}


class InstructionProvider:
    def __init__(self, language: str, card_type: str, age: int, topic: str):
        self.language = language
        self.card_type = card_type
        self.age = age
        self.topic = topic
        self._used: List[str] = []
        self._pool = _INSTRUCTION_POOLS.get(card_type, _INSTRUCTION_POOLS["fallback"])
        self._lang_pool = self._pool.get(language, self._pool.get("ru", []))
        self._templates = _TOPIC_TEMPLATES.get(language, _TOPIC_TEMPLATES["ru"])
        self._age_short_map = _AGE_SHORT.get(language, _AGE_SHORT["ru"])

    def get(self) -> str:
        pool = list(self._lang_pool)
        random.shuffle(pool)
        # prefer unused
        for instr in pool:
            if instr not in self._used:
                self._used.append(instr)
                return self._with_topic(instr)
        # all used — cycle
        instr = random.choice(pool)
        self._used = [instr]
        return self._with_topic(instr)

    def _with_topic(self, instr: str) -> str:
        if self.topic and self.topic not in ("general", "custom", ""):
            topic_word = random_word(self.topic, self.language)
            if topic_word and topic_word != "?":
                return instr.replace("{topic}", topic_word)
        instr = instr.replace("{topic}", "")
        instr = re.sub(r'\s+', ' ', instr).strip()
        return instr

    def age_short(self) -> str:
        pool = self._age_short_map.get(self.age, self._age_short_map.get(max(k for k in self._age_short_map.keys() if k <= self.age), ["Выполни задание."]))
        return random.choice(pool)


def get_pool_for_card(card_type: str, language: str = "ru") -> List[str]:
    pool = _INSTRUCTION_POOLS.get(card_type, _INSTRUCTION_POOLS["fallback"])
    return pool.get(language, pool.get("ru", []))


def available_card_types() -> List[str]:
    return list(_INSTRUCTION_POOLS.keys())
