import random
from typing import List
from core.cards.base import CardResult, CardTemplate
from core.deterministic_generators.maze_generator import MazeGenerator
from core.language_layer import get as ll, instruction as lli
from core.topic_lexicon import get_words, random_word, random_n_words, get_generic


def _topic_q(text: str, tw: str) -> str:
    return text.replace("{t}", tw).replace("{topic}", tw)


def _creative_ans(lang: str) -> str:
    if lang == "en":
        return "Checked by adult"
    elif lang in ("uk", "uk+en"):
        return "Перевіряється дорослим"
    else:
        return "Проверяется взрослым"


def gen_story_read(tmpl, count, topic, seed, lang):
    tw = random_word(topic, lang) if topic and topic not in ("general", "custom") else ""
    stories_ru = [
        ("Солнечный день", f"Наступило теплое утро. Солнце осветило лес. Птицы запели. {tw.capitalize()} выбежал на поляну." if tw else "Зайчик выбежал на поляну.", ["Что наступило?", "Кто выбежал?"], ["утро", "зайчик"]),
        ("Помощник", "Саша помогал маме. Он полил цветы и вытер пыль. Мама похвалила его.", ["Как звали мальчика?", "Что он сделал?"], ["Саша", "полил цветы"]),
        ("В лесу", "В лесу было тихо и красиво. Птицы пели, а белка прыгала с ветки на ветку.", ["Где было тихо?", "Кто прыгал?"], ["в лесу", "белка"]),
        ("На реке", "Дети купались в реке. Вода была тёплая и чистая. Все смеялись.", ["Где купались дети?", "Какая была вода?"], ["в реке", "тёплая"]),
    ]
    stories_uk = [
        ("Сонячний день", f"Настав теплий ранок. Сонце освітило ліс. Пташки заспівали. {tw.capitalize()} вибіг на галявину." if tw else "Зайчик вибіг на галявину.", ["Яка пора дня?", "Хто вибіг?"], ["ранок", "зайчик"]),
        ("Помічник", "Марійка допомагала мамі. Вона полила квіти.", ["Як звали дівчинку?", "Що вона зробила?"], ["Марійка", "полила квіти"]),
        ("У лісі", f"У лісі було тихо та гарно. {tw.capitalize()} стрибав по галявині." if tw else "Білка стрибала по гілках.", ["Де було тихо?", "Хто стрибав?"], ["у лісі", "білка"]),
    ]
    stories_en = [
        ("Sunny Day", f"The sun was bright. Birds were singing. A {tw or 'bunny'} ran into the meadow.", ["What was bright?", "Who ran?"], ["sun", tw or "bunny"]),
        ("Helper", "Lily helped her mom. She watered the flowers.", ["Who helped mom?", "What did she do?"], ["Lily", "watered flowers"]),
    ]
    if lang == "en":
        pool = stories_en
    elif lang in ("uk", "uk+en"):
        pool = stories_uk
    else:
        pool = stories_ru
    return [CardResult(card_type=tmpl.id, question=f"{pool[(seed+i)%len(pool)][0]}: {pool[(seed+i)%len(pool)][1]}", answer=pool[(seed+i)%len(pool)][3][0]) for i in range(count)]


def gen_question_answer(tmpl, count, topic, seed, lang):
    tw = random_word(topic, lang) if topic and topic not in ("general", "custom") else (get_generic(lang)[0] if get_generic(lang) else "?")
    ru_qa = [(f"Сколько? {tw.capitalize()}", "ответ"), (f"Где живёт {tw}?", "дома"), (f"Что любит {tw}?", "играть")]
    uk_qa = [(f"Скільки? {tw.capitalize()}", "відповідь"), (f"Де живе {tw}?", "вдома"), (f"Що любить {tw}?", "грати")]
    en_qa = [(f"How many? {tw.capitalize()}", "answer"), (f"Where does {tw} live?", "home"), (f"What does {tw} like?", "play")]
    pool = uk_qa if lang in ("uk", "uk+en") else (en_qa if lang == "en" else ru_qa)
    return [CardResult(card_type=tmpl.id, question=pool[(seed+i)%len(pool)][0], answer=pool[(seed+i)%len(pool)][1]) for i in range(count)]


def gen_find_word(tmpl, count, topic, seed, lang):
    words = get_words(topic, lang) if topic and topic not in ("general", "custom") else [ll("find", lang).upper(), "МАМА", "КНИГА", "ЛІС", "СОНЦЕ"]
    if not words:
        words = ["КНИГА", "ШКОЛА", "СОНЦЕ", "ЛІС"]
    return [CardResult(card_type=tmpl.id, question=f"{lli('find', lang)} слово '{words[(seed+i)%len(words)]}'", answer=words[(seed+i)%len(words)]) for i in range(count)]


def gen_main_idea(tmpl, count, topic, seed, lang):
    if lang == "en":
        return [CardResult(card_type=tmpl.id, question="What is the main idea of this text?", answer=_creative_ans(lang)) for _ in range(count)]
    q = "Яка головна думка тексту?" if lang in ("uk", "uk+en") else "Какая главная мысль текста?"
    return [CardResult(card_type=tmpl.id, question=q, answer=_creative_ans(lang)) for _ in range(count)]


def gen_character_guess(tmpl, count, topic, seed, lang):
    tw = random_word(topic, lang) if topic and topic not in ("general", "custom") else ""
    default_ru = tw.capitalize() if tw else "Колобок"
    default_uk = tw.capitalize() if tw else "Колобок"
    default_en = tw.capitalize() if tw else "Gingerbread Man"
    ru_chars = [(default_ru, f"круглый, убежал от бабушки"), ("Репка", "тянули всей семьёй"), ("Золушка", "потеряла туфельку")]
    uk_chars = [(default_uk, f"круглий, втік від бабусі"), ("Ріпка", "тягнули всією сім'єю"), ("Попелюшка", "загубила туфельку")]
    en_chars = [(default_en, f"round, ran away from grandma"), ("Cinderella", "lost her slipper"), ("Turnip", "the whole family pulled it")]
    pool = uk_chars if lang in ("uk", "uk+en") else (en_chars if lang == "en" else ru_chars)
    prefix = ll("guess", lang)
    return [CardResult(card_type=tmpl.id, question=f"{prefix}: {pool[(seed+i)%len(pool)][1]}", answer=pool[(seed+i)%len(pool)][0]) for i in range(count)]



def gen_sequence(tmpl, count, topic, seed, lang):
    tw = random_word(topic, lang) if topic and topic not in ("general", "custom") else ""
    template = "Розстав по порядку: {a}, {b}, {d}..." if lang in ("uk", "uk+en") else ("Put in order: {a}, {b}, {d}..." if lang == "en" else "Разложи по порядку: {a}, {b}, {d}...")
    if tw:
        template = f"{template} ({tw})"
    return [CardResult(card_type=tmpl.id, question=template.format(a=seed+i, b=seed+i+1, d=seed+i+3), answer=str(seed+i+4)) for i in range(count)]


def gen_retelling(tmpl, count, topic, seed, lang):
    prompt = f"Перекажи текст у 3 реченнях ({topic})" if lang in ("uk", "uk+en") else (f"Retell in 3 sentences ({topic})" if lang == "en" else f"Перескажи текст в 3 предложениях ({topic})")
    return [CardResult(card_type=tmpl.id, question=prompt, answer=_creative_ans(lang)) for _ in range(count)]


def gen_make_plan(tmpl, count, topic, seed, lang):
    prompt = "Склади план: що було на початку, потім, в кінці" if lang in ("uk", "uk+en") else ("Make a plan: beginning, middle, end" if lang == "en" else "Составь план: что было в начале, потом, в конце")
    return [CardResult(card_type=tmpl.id, question=prompt, answer=_creative_ans(lang)) for _ in range(count)]


def gen_synonym_find(tmpl, count, topic, seed, lang):
    ru = [("большой", "огромный"), ("красивый", "прекрасный"), ("быстрый", "скоростной"), ("веселый", "радостный")]
    uk = [("великий", "величезний"), ("гарний", "прекрасний"), ("швидкий", "прудкий"), ("веселий", "радісний")]
    en = [("big", "large"), ("small", "little"), ("happy", "glad"), ("fast", "quick")]
    pool = uk if lang in ("uk", "uk+en") else (en if lang == "en" else ru)
    prefix = "Синонім до" if lang in ("uk", "uk+en") else ("Synonym of" if lang == "en" else "Подбери синоним к слову")
    return [CardResult(card_type=tmpl.id, question=f"{prefix} '{pool[(seed+i)%len(pool)][0]}'", answer=pool[(seed+i)%len(pool)][1]) for i in range(count)]


def gen_discussion(tmpl, count, topic, seed, lang):
    tw = random_word(topic, lang) if topic and topic not in ("general", "custom") else "це"
    if lang == "en":
        message = f"Why is {tw} important? Write 2 reasons."
    elif lang in ("uk", "uk+en"):
        message = f"Чому {tw} важливе? Напиши 2 причини."
    else:
        message = f"Почему {tw} важно? Напиши 2 причины."
    return [CardResult(card_type=tmpl.id, question=message, answer=_creative_ans(lang)) for _ in range(count)]


def gen_pattern(tmpl, count, topic, seed, lang):
    tw = random_word(topic, lang) if topic and topic not in ("general", "custom") else ""
    return [CardResult(
        card_type=tmpl.id,
        question=_pattern_q(i, seed, lang, tw),
        answer=str((seed+i)%10+7)
    ) for i in range(count)]


def _pattern_q(i, seed, lang, tw):
    if lang == "en":
        q = f"Continue the pattern: {(seed+i)%10+1}, {(seed+i)%10+3}, {(seed+i)%10+5}, ..."
    elif lang in ("uk", "uk+en"):
        q = f"Продовж ряд: {(seed+i)%10+1}, {(seed+i)%10+3}, {(seed+i)%10+5}, ..."
    else:
        q = f"Продолжи ряд: {(seed+i)%10+1}, {(seed+i)%10+3}, {(seed+i)%10+5}, ..."
    if tw:
        q = f"{q} ({tw})"
    return q


def gen_odd_one_out(tmpl, count, topic, seed, lang):
    tw = random_word(topic, lang) if topic and topic not in ("general", "custom") else ""
    topics = get_words(topic, lang)
    if topics and len(topics) >= 3:
        selected = random.sample(topics, min(4, len(topics)))
        odd_one = selected[-1]
        items = ", ".join(selected[:-1])
        odd_topic = f"{items}, ???"
        actual_odd = "???"
        sets = [(odd_topic, odd_one)]
    else:
        if lang == "en":
            sets = [("apple, pear, car, banana", "car"), ("2, 4, 7, 8", "7")]
        elif lang in ("uk", "uk+en"):
            sets = [("яблуко, груша, машина, банан", "машина"), ("2, 4, 7, 8", "7")]
        else:
            sets = [("яблоко, груша, машина, банан", "машина"), ("2, 4, 7, 8", "7")]
    prefix = ll("think", lang) if lang in ("uk", "uk+en") else ("Find the odd one" if lang == "en" else "Что лишнее?")
    return [CardResult(card_type=tmpl.id, question=f"{prefix}: {sets[(seed+i)%len(sets)][0]}", answer=sets[(seed+i)%len(sets)][1]) for i in range(count)]


def gen_analogy(tmpl, count, topic, seed, lang):
    ru_pairs = [("птица : летает = рыба : ...", "плавает"), ("утро : завтрак = вечер : ...", "ужин"), ("огонь : горячий = лёд : ...", "холодный")]
    uk_pairs = [("птах : літає = риба : ...", "плаває"), ("ранок : сніданок = вечір : ...", "вечеря"), ("вогонь : гарячий = лід : ...", "холодний")]
    en_pairs = [("bird : fly = fish : ...", "swim"), ("morning : breakfast = evening : ...", "dinner"), ("fire : hot = ice : ...", "cold")]
    pool = uk_pairs if lang in ("uk", "uk+en") else (en_pairs if lang == "en" else ru_pairs)
    return [CardResult(card_type=tmpl.id, question=pool[(seed+i)%len(pool)][0], answer=pool[(seed+i)%len(pool)][1]) for i in range(count)]


def gen_maze(tmpl, count, topic, seed, lang):
    return [CardResult(card_type=tmpl.id, question=f"{ll('find', lang)} вихід ({'лабіринт' if lang in ('uk','uk+en') else ('maze' if lang=='en' else 'лабиринт')} {(seed+i)%4+5}x{(seed+i*3)%4+5})", answer="OK") for i in range(count)]


def gen_find_path(tmpl, count, topic, seed, lang):
    label = ll("connect", lang)
    return [CardResult(card_type=tmpl.id, question=f"{label} від A до B (сітка {4+i}x{4+i})" if lang in ("uk", "uk+en") else f"{label} from A to B (grid {4+i}x{4+i})", answer="OK") for i in range(count)]


def gen_puzzle_lines(tmpl, count, topic, seed, lang):
    label = ll("connect", lang)
    return [CardResult(card_type=tmpl.id, question=f"{label}: {(seed+i)%10+1} → {(seed+i*2+3)%10+1}", answer=str((seed+i)%10+1 + (seed+i*2+3)%10+1)) for i in range(count)]


def gen_table_fill(tmpl, count, topic, seed, lang):
    fill_word = "Заповни" if lang in ("uk", "uk+en") else ("Fill in" if lang == "en" else "Заполни")
    return [CardResult(card_type=tmpl.id, question=f"{fill_word} таблицю: {(seed+i)%5+1} + {(seed+i*3)%5+1} = ?" if lang in ("uk", "uk+en") else f"{fill_word} таблицу: {(seed+i)%5+1} + {(seed+i*3)%5+1} = ?", answer=str((seed+i)%5+1 + (seed+i*3)%5+1)) for i in range(count)]


def gen_crossword(tmpl, count, topic, seed, lang):
    action = "Розгадай кросворд" if lang in ("uk", "uk+en") else ("Solve the crossword" if lang == "en" else "Разгадай кроссворд")
    return [CardResult(card_type=tmpl.id, question=f"{action} ({topic})", answer=_creative_ans(lang)) for _ in range(count)]


def gen_detective(tmpl, count, topic, seed, lang):
    tw = random_word(topic, lang) if topic and topic not in ("general", "custom") else ""
    if lang == "en":
        clues = [(f"{tw.capitalize()} has 3 cookies. Gave 1 away. How many left?" if tw else "Tom has 3 cookies. He gave 1 away. How many left?", "2")]
    elif lang in ("uk", "uk+en"):
        clues = [(f"У {tw} було 3 цукерки. Віддав 1. Скільки залишилося?" if tw else "У Сашка було 3 цукерки. Віддав 1. Скільки залишилося?", "2")]
    else:
        clues = [(f"У {tw} было 3 конфеты. Отдал 1. Сколько осталось?" if tw else "У Саши было 3 конфеты. Он отдал 1. Сколько осталось?", "2")]
    return [CardResult(card_type=tmpl.id, question=clues[(seed+i)%len(clues)][0], answer=clues[(seed+i)%len(clues)][1]) for i in range(count)]


def gen_deduction(tmpl, count, topic, seed, lang):
    if lang == "en":
        return [CardResult(card_type=tmpl.id, question=f"Logical: {(seed+i)%5+2} > {(seed+i*2)%3+1}? (yes/no)", answer="yes") for _ in range(count)]
    yes = "так" if lang in ("uk", "ru") else "yes"
    return [CardResult(card_type=tmpl.id, question=f"{'Логічна задача' if lang in ('uk','uk+en') else 'Логическая задача'}: {(seed+i)%5+2} > {(seed+i*2)%3+1}? (так/ні)" if lang in ("uk", "uk+en") else f"Логическая задача: {(seed+i)%5+2} > {(seed+i*2)%3+1}? (да/нет)", answer=yes) for _ in range(count)]


def gen_count_trace(tmpl, count, topic, seed, lang):
    tw = random_word(topic, lang) if topic and topic not in ("general", "custom") else "★"
    emoji_char = tw[0] if len(tw) > 0 else "★"
    count_label = ll("count", lang)
    return [CardResult(card_type=tmpl.id, question=f"{count_label}: {emoji_char*((seed+i)%9+1)}", answer=str((seed+i)%9+1)) for i in range(count)]


def gen_shape_find(tmpl, count, topic, seed, lang):
    ru_shapes = [("круг", "круг"), ("квадрат", "квадрат"), ("треугольник", "треугольник")]
    uk_shapes = [("коло", "коло"), ("квадрат", "квадрат"), ("трикутник", "трикутник")]
    en_shapes = [("circle", "circle"), ("square", "square"), ("triangle", "triangle")]
    pool = uk_shapes if lang in ("uk", "uk+en") else (en_shapes if lang == "en" else ru_shapes)
    prefix = ll("find", lang)
    if lang in ("uk", "uk+en"):
        post = "серед фігур: ○ □ △ ☆ ◇"
    elif lang == "en":
        post = "among shapes: ○ □ △ ☆ ◇"
    else:
        post = "среди фигур: ○ □ △ ☆ ◇"
    tw = random_word(topic, lang) if topic and topic not in ("general", "custom") else ""
    if tw:
        post = f"{post} ({tw})"
    return [CardResult(card_type=tmpl.id, question=f"{prefix} {pool[(seed+i)%len(pool)][0]} {post}", answer=pool[(seed+i)%len(pool)][1]) for i in range(count)]


def gen_letter_trace(tmpl, count, topic, seed, lang):
    if lang == "en":
        letters = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
    elif lang in ("uk", "uk+en"):
        letters = "АБВГДЕЄЖЗИІЇЙКЛМНОПРСТУФХЦЧШЩЬЮЯ"
    else:
        letters = "АБВГДЕЁЖЗИКЛМНОПРСТУФХЦЧШЩЪЫЬЭЮЯ"
    if topic and topic not in ("general", "custom"):
        tw = random_word(topic, lang)
        if tw:
            visible = tw[0].upper() if tw[0].upper() in letters else letters[(seed)%len(letters)]
        else:
            visible = letters[(seed)%len(letters)]
    else:
        visible = letters[(seed)%len(letters)]
    circle_word = ll("circle", lang)
    return [CardResult(card_type=tmpl.id, question=f"{circle_word} букву {visible} за точками" if lang in ("uk", "uk+en") else f"{circle_word} букву {visible} по точкам", answer=f"літера {visible}" if lang in ("uk", "uk+en") else f"буква {visible}") for i in range(count)]


def gen_same_shape(tmpl, count, topic, seed, lang):
    shapes = ["○", "□", "△", "☆", "◇"]
    s = shapes[(seed)%len(shapes)]
    tw = random_word(topic, lang) if topic and topic not in ("general", "custom") else ""
    
    shape_names_ru = {"○": "круг", "□": "квадрат", "△": "треугольник", "☆": "звезда", "◇": "ромб"}
    shape_names_uk = {"○": "коло", "□": "квадрат", "△": "трикутник", "☆": "зірка", "◇": "ромб"}
    shape_names_en = {"○": "circle", "□": "square", "△": "triangle", "☆": "star", "◇": "diamond"}
    
    if lang in ("uk", "uk+en"):
        ans = shape_names_uk.get(s, s)
        prefix = "Знайди таку ж:"
        base = f"{prefix} {s} | {' '.join(shapes)}"
    elif lang == "en":
        ans = shape_names_en.get(s, s)
        base = f"Find the same: {s} | {' '.join(shapes)}"
    else:
        ans = shape_names_ru.get(s, s)
        prefix = "Найди такую же:"
        base = f"{prefix} {s} | {' '.join(shapes)}"
        
    if tw:
        base = f"{base} ({tw})"
    return [CardResult(card_type=tmpl.id, question=base, answer=ans) for _ in range(count)]


def gen_coloring(tmpl, count, topic, seed, lang):
    tw = random_word(topic, lang) if topic and topic not in ("general", "custom") else ""
    ru_items = [f"{tw}" if tw else "солнышко", f"{tw}" if tw else "цветок", f"{tw}" if tw else "мячик"]
    uk_items = [f"{tw}" if tw else "сонечко", f"{tw}" if tw else "квітку", f"{tw}" if tw else "м'ячик"]
    en_items = [f"{tw}" if tw else "sun", f"{tw}" if tw else "flower", f"{tw}" if tw else "ball"]
    # deduplicate
    ru_items = list(dict.fromkeys(ru_items))
    uk_items = list(dict.fromkeys(uk_items))
    en_items = list(dict.fromkeys(en_items))
    pool = uk_items if lang in ("uk", "uk+en") else (en_items if lang == "en" else ru_items)
    if len(pool) <= 1:
        pool = pool * 3
    color_word = "Розфарбуй" if lang in ("uk", "uk+en") else ("Colour" if lang == "en" else "Раскрась")
    return [CardResult(card_type=tmpl.id, question=f"{color_word} {pool[(seed+i)%len(pool)]}", answer=_creative_ans(lang)) for i in range(count)]


def gen_color_find(tmpl, count, topic, seed, lang):
    ru = [("красный", "🔴"), ("синий", "🔵"), ("зелёный", "🟢"), ("жёлтый", "🟡")]
    uk = [("червоний", "🔴"), ("синій", "🔵"), ("зелений", "🟢"), ("жовтий", "🟡")]
    en = [("red", "🔴"), ("blue", "🔵"), ("green", "🟢"), ("yellow", "🟡")]
    pool = uk if lang in ("uk", "uk+en") else (en if lang == "en" else ru)
    prefix = ll("find", lang)
    return [CardResult(card_type=tmpl.id, question=f"{prefix} {pool[(seed+i)%len(pool)][0]} колір: 🔴 🔵 🟢 🟡 🟣" if lang in ("uk", "uk+en") else f"{prefix} {pool[(seed+i)%len(pool)][0]} цвет: 🔴 🔵 🟢 🟡 🟣", answer=pool[(seed+i)%len(pool)][1]) for i in range(count)]


def gen_find_shadow(tmpl, count, topic, seed, lang):
    tw = random_word(topic, lang) if topic and topic not in ("general", "custom") else (get_generic(lang)[0] if get_generic(lang) else "?")
    prefix = "Знайди тінь" if lang in ("uk", "uk+en") else ("Find shadow of" if lang == "en" else "Найди тень")
    return [CardResult(card_type=tmpl.id, question=f"{prefix} {tw}", answer=tw) for i in range(count)]


def gen_sound_letter(tmpl, count, topic, seed, lang):
    tw = random_word(topic, lang) if topic and topic not in ("general", "custom") else ""
    source = get_words(topic, lang) if topic and topic not in ("general", "custom") else (get_generic(lang) if lang in ("uk", "uk+en") else ["сонце", "книга", "ліс", "вода", "кіт"])
    if not source or len(source) < 2:
        source = ["сонце", "книга", "ліс"]
    word = source[(seed+i)%len(source)]
    if lang == "en":
        return [CardResult(card_type=tmpl.id, question=f"First letter of '{word}'?", answer=word[0].upper()) for i in range(count)]
    return [CardResult(card_type=tmpl.id, question=f"З якої букви починається '{word}'?", answer=word[0].upper()) for i in range(count)]


# === ENGLISH generators remain but with topic support ===
def gen_letter_trace_en(tmpl, count, topic, seed, lang):
    letters = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
    return [CardResult(card_type=tmpl.id, question=f"Trace letter {letters[(seed+i)%26]}. Write it three times.", answer=letters[(seed+i)%26]) for i in range(count)]


def gen_abc_match(tmpl, count, topic, seed, lang):
    tw = random_word(topic, "en") if topic and topic not in ("general", "custom") else ""
    pairs = [("A", "Apple"), ("B", "Ball"), ("C", "Cat"), ("D", "Dog"), ("E", f"{tw.capitalize() if tw else 'Egg'}")]
    return [CardResult(card_type=tmpl.id, question=f"Match: {pairs[(seed+i)%len(pairs)][0]} → ?", answer=pairs[(seed+i)%len(pairs)][1]) for i in range(count)]


def gen_word_picture(tmpl, count, topic, seed, lang):
    tw_en = random_word(topic, "en") if topic and topic not in ("general", "custom") else ""
    words = [("cat", "🐱"), ("dog", "🐶"), ("sun", "☀"), (tw_en if tw_en else "book", "📖"), ("fish", "🐟")]
    return [CardResult(card_type=tmpl.id, question=f"Match word: {words[(seed+i)%len(words)][1]} = ? (cat, dog, sun, book, fish)", answer=words[(seed+i)%len(words)][0]) for i in range(count)]


def gen_color_find_en(tmpl, count, topic, seed, lang):
    colors = [("red", "🔴"), ("blue", "🔵"), ("green", "🟢"), ("yellow", "🟡")]
    tw_en = random_word(topic, "en") if topic and topic not in ("general", "custom") else ""
    base = "Find color: {c} 🔴 🔵 🟢 🟡"
    if tw_en:
        base = f"{base} ({tw_en})"
    return [CardResult(card_type=tmpl.id, question=base.format(c=colors[(seed+i)%len(colors)][0]), answer=colors[(seed+i)%len(colors)][1]) for i in range(count)]


def gen_count_en(tmpl, count, topic, seed, lang):
    tw_en = random_word(topic, "en") if topic and topic not in ("general", "custom") else ""
    stars = "{s}"
    if tw_en:
        lbl = f" ({tw_en})"
    else:
        lbl = ""
    return [CardResult(card_type=tmpl.id, question=f"How many? {stars.format(s='★'*((seed+i)%9+1))}{lbl}", answer=str((seed+i)%9+1)) for i in range(count)]


def gen_match_pairs_en(tmpl, count, topic, seed, lang):
    tw_en = random_word(topic, "en") if topic and topic not in ("general", "custom") else ""
    a, b = (seed+1)%20+1, (seed*2)%15+1
    if tw_en:
        return [CardResult(card_type=tmpl.id, question=f"{a} {tw_en}", answer=str(a+b)) for _ in range(count)]
    return [CardResult(card_type=tmpl.id, question=f"{a} + {b}", answer=str(a+b)) for _ in range(count)]


def gen_read_short_en(tmpl, count, topic, seed, lang):
    tw_en = random_word(topic, "en") if topic and topic not in ("general", "custom") else ""
    texts = [(f"The {tw_en or 'cat'} sat on the mat.", f"Where did the {tw_en or 'cat'} sit?", "mat"),
             ("A dog likes to run.", "What does the dog like?", "run"),
             ("The sun is hot.", "Is the sun hot?", "yes")]
    return [CardResult(card_type=tmpl.id, question=f"Read: '{texts[(seed+i)%len(texts)][0]}' {texts[(seed+i)%len(texts)][1]}", answer=texts[(seed+i)%len(texts)][2]) for i in range(count)]


def gen_question_answer_en(tmpl, count, topic, seed, lang):
    tw_en = random_word(topic, "en") if topic and topic not in ("general", "custom") else ""
    qa = [("What color is the sky?", "blue"), ("How many legs does a cat have?", "4"), (f"What does a {tw_en or 'dog'} like?" if tw_en else "What do you drink?", tw_en or "water")]
    return [CardResult(card_type=tmpl.id, question=qa[(seed+i)%len(qa)][0], answer=qa[(seed+i)%len(qa)][1]) for i in range(count)]


def gen_fill_gap_en(tmpl, count, topic, seed, lang):
    tw_en = random_word(topic, "en") if topic and topic not in ("general", "custom") else ""
    gaps = [("I ___ a student.", "am"), ("She ___ a teacher.", "is"), (f"The {tw_en or 'cat'} ___ happy.", "is"),
            (f"{tw_en.capitalize() if tw_en else 'They'} ___ friends.", "are") if tw_en else ("We ___ happy.", "are")]
    return [CardResult(card_type=tmpl.id, question=gaps[(seed+i)%len(gaps)][0], answer=gaps[(seed+i)%len(gaps)][1]) for i in range(count)]


def gen_correct_form_en(tmpl, count, topic, seed, lang):
    tw_en = random_word(topic, "en") if topic and topic not in ("general", "custom") else ""
    forms = [("He (go/goes) to school.", "goes"), ("She (have/has) a cat.", "has"), (f"They (play/plays) with {tw_en or 'toys'}.", "play")]
    return [CardResult(card_type=tmpl.id, question=forms[(seed+i)%len(forms)][0], answer=forms[(seed+i)%len(forms)][1]) for i in range(count)]


def gen_sentence_build(tmpl, count, topic, seed, lang):
    tw_en = random_word(topic, "en") if topic and topic not in ("general", "custom") else ""
    sents = [("cat / the / sleeping / is", f"The {tw_en or 'cat'} is sleeping" if tw_en else "The cat is sleeping"),
             ("like / I / apples", "I like apples"),
             ("go / let's / park / the / to", "Let's go to the park")]
    return [CardResult(card_type=tmpl.id, question=f"Make a sentence: {sents[(seed+i)%len(sents)][0]}", answer=sents[(seed+i)%len(sents)][1]) for i in range(count)]


def gen_true_false_en(tmpl, count, topic, seed, lang):
    tw_en = random_word(topic, "en") if topic and topic not in ("general", "custom") else ""
    qs = [("The sky is green.", "False"), (f"{tw_en.capitalize() if tw_en else 'Cats'} can fly.", "False"), ("Water is wet.", "True"), ("Fish live in water.", "True")]
    return [CardResult(card_type=tmpl.id, question=qs[(seed+i)%len(qs)][0] + " (True/False)", answer=qs[(seed+i)%len(qs)][1]) for i in range(count)]


def gen_vocab_match(tmpl, count, topic, seed, lang):
    en_pairs = [("big", "large"), ("small", "little"), ("happy", "glad"), ("fast", "quick")]
    return [CardResult(card_type=tmpl.id, question=f"Synonym of '{en_pairs[(seed+i)%len(en_pairs)][0]}'", answer=en_pairs[(seed+i)%len(en_pairs)][1]) for i in range(count)]


GENERATORS = {
    "story_read": gen_story_read,
    "question_answer": gen_question_answer,
    "find_word": gen_find_word,
    "main_idea": gen_main_idea,
    "character_guess": gen_character_guess,
    "sequence": gen_sequence,
    "retelling": gen_retelling,
    "make_plan": gen_make_plan,
    "synonym_find": gen_synonym_find,
    "discussion": gen_discussion,
    "pattern": gen_pattern,
    "odd_one_out": gen_odd_one_out,
    "analogy": gen_analogy,
    "maze": gen_maze,
    "labyrinth": gen_maze,
    "find_path": gen_find_path,
    "puzzle_lines": gen_puzzle_lines,
    "table_fill": gen_table_fill,
    "crossword": gen_crossword,
    "detective": gen_detective,
    "deduction": gen_deduction,
    "count_trace": gen_count_trace,
    "shape_find": gen_shape_find,
    "letter_trace": gen_letter_trace,
    "same_shape": gen_same_shape,
    "coloring": gen_coloring,
    "color_find": gen_color_find,
    "find_shadow": gen_find_shadow,
    "sound_letter": gen_sound_letter,
    "letter_trace_en": gen_letter_trace_en,
    "abc_match": gen_abc_match,
    "word_picture": gen_word_picture,
    "color_find_en": gen_color_find_en,
    "count_en": gen_count_en,
    "match_pairs_en": gen_match_pairs_en,
    "read_short_en": gen_read_short_en,
    "question_answer_en": gen_question_answer_en,
    "fill_gap_en": gen_fill_gap_en,
    "correct_form_en": gen_correct_form_en,
    "sentence_build": gen_sentence_build,
    "true_false_en": gen_true_false_en,
    "vocab_match": gen_vocab_match,
}
