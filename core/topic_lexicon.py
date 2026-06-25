import random
from typing import List, Dict, Optional

_TOPICS: Dict[str, Dict[str, List[str]]] = {
    "dinosaurs": {
        "ru": ["динозавр", "яйцо", "след", "вулкан", "джунгли", "кость", "хвост",
               "зуб", "лапа", "папоротник", "пещера", "река", "окаменелость", "гнездо",
               "динозаврик", "трицератопс", "тираннозавр", "стегозавр", "птеродактиль"],
        "uk": ["динозавр", "яйце", "слід", "вулкан", "джунглі", "кістка", "хвіст",
               "зуб", "лапа", "папороть", "печера", "річка", "скам'янілість", "гніздо",
               "динозаврик", "трицератопс", "тиранозавр", "стегозавр", "птеродактиль"],
        "en": ["dinosaur", "egg", "footprint", "volcano", "jungle", "bone", "tail",
               "tooth", "paw", "fern", "cave", "river", "fossil", "nest",
               "triceratops", "t-rex", "stegosaurus", "pterodactyl"],
    },
    "space": {
        "ru": ["ракета", "планета", "звезда", "космонавт", "луна", "спутник", "комета",
               "солнце", "метеорит", "галактика", "орбита", "звездопад", "телескоп",
               "инопланетянин", "марс", "юпитер", "сатурн", "астероид"],
        "uk": ["ракета", "планета", "зірка", "космонавт", "місяць", "супутник", "комета",
               "сонце", "метеорит", "галактика", "орбіта", "зорепад", "телескоп",
               "інопланетянин", "марс", "юпітер", "сатурн", "астероїд"],
        "en": ["rocket", "planet", "star", "astronaut", "moon", "satellite", "comet",
               "sun", "meteor", "galaxy", "orbit", "shooting star", "telescope",
               "alien", "mars", "jupiter", "saturn", "asteroid"],
    },
    "animals": {
        "ru": ["зверь", "лес", "лапа", "шерсть", "нора", "берлога", "хвост",
               "медведь", "заяц", "волк", "лиса", "ёж", "белка", "лось", "олень",
               "след", "охота", "зима", "природа"],
        "uk": ["звір", "ліс", "лапа", "шерсть", "нора", "барліг", "хвіст",
               "ведмідь", "заєць", "вовк", "лисиця", "їжак", "білка", "лось", "олень",
               "слід", "полювання", "зима", "природа"],
        "en": ["animal", "forest", "paw", "fur", "den", "lair", "tail",
               "bear", "hare", "wolf", "fox", "hedgehog", "squirrel", "elk", "deer",
               "track", "hunt", "winter", "nature"],
    },
    "cats": {
        "ru": ["кот", "кошка", "котёнок", "лапа", "усы", "хвост", "клубок",
               "миска", "молоко", "рыба", "мышь", "мяу", "шерсть", "лежанка"],
        "uk": ["кіт", "кішка", "кошеня", "лапа", "вуса", "хвіст", "клубок",
               "миска", "молоко", "риба", "миша", "няв", "шерсть", "лежанка"],
        "en": ["cat", "kitten", "paw", "whiskers", "tail", "yarn",
               "bowl", "milk", "fish", "mouse", "meow", "fur", "bed"],
    },
    "dogs": {
        "ru": ["собака", "пёс", "щенок", "лапа", "кость", "хвост", "ошейник",
               "будка", "гав", "поводок", "мяч", "нос", "уши"],
        "uk": ["собака", "пес", "цуценя", "лапа", "кістка", "хвіст", "нашийник",
               "буда", "гав", "повідець", "м'яч", "ніс", "вуха"],
        "en": ["dog", "puppy", "paw", "bone", "tail", "collar",
               "kennel", "woof", "leash", "ball", "nose", "ears"],
    },
    "cars": {
        "ru": ["машина", "колесо", "руль", "мотор", "дорога", "гараж", "фары",
               "скорость", "гонка", "шина", "капот", "дверца", "сигнал", "трасса"],
        "uk": ["машина", "колесо", "кермо", "мотор", "дорога", "гараж", "фари",
               "швидкість", "гонка", "шина", "капот", "дверцята", "сигнал", "траса"],
        "en": ["car", "wheel", "steering wheel", "engine", "road", "garage", "headlight",
               "speed", "race", "tire", "hood", "door", "horn", "track"],
    },
    "football": {
        "ru": ["футбол", "мяч", "гол", "вратарь", "стадион", "команда", "тренер",
               "матч", "победа", "кубок", "бутсы", "поле", "защитник", "нападающий"],
        "uk": ["футбол", "м'яч", "гол", "воротар", "стадіон", "команда", "тренер",
               "матч", "перемога", "кубок", "бутси", "поле", "захисник", "нападник"],
        "en": ["football", "ball", "goal", "goalkeeper", "stadium", "team", "coach",
               "match", "victory", "cup", "boots", "field", "defender", "forward"],
    },
    "princesses": {
        "ru": ["принцесса", "замок", "корона", "дракон", "принц", "бал", "карета",
               "туфелька", "трон", "королевство", "рыцарь", "единорог", "радуга"],
        "uk": ["принцеса", "замок", "корона", "дракон", "принц", "бал", "карета",
               "туфелька", "трон", "королівство", "лицар", "єдиноріг", "веселка"],
        "en": ["princess", "castle", "crown", "dragon", "prince", "ball", "carriage",
               "slipper", "throne", "kingdom", "knight", "unicorn", "rainbow"],
    },
    "pirates": {
        "ru": ["пират", "корабль", "сокровище", "остров", "карта", "меч", "флаг",
               "якорь", "штурвал", "компас", "золото", "бочка", "парус", "капитан"],
        "uk": ["пірат", "корабель", "скарб", "острів", "карта", "меч", "прапор",
               "якір", "штурвал", "компас", "золото", "бочка", "вітрило", "капітан"],
        "en": ["pirate", "ship", "treasure", "island", "map", "sword", "flag",
               "anchor", "wheel", "compass", "gold", "barrel", "sail", "captain"],
    },
    "superheroes_generic": {
        "ru": ["герой", "маска", "плащ", "сила", "спасение", "город", "злодей",
               "молния", "битва", "штаб", "гаджет", "тайна", "крылья"],
        "uk": ["герой", "маска", "плащ", "сила", "порятунок", "місто", "лиходій",
               "блискавка", "битва", "штаб", "гаджет", "таємниця", "крила"],
        "en": ["hero", "mask", "cape", "power", "rescue", "city", "villain",
               "lightning", "battle", "headquarters", "gadget", "secret", "wings"],
    },
    "pixel_world": {
        "ru": ["пиксель", "куб", "мир", "блок", "постройка", "квадрат", "моб",
               "приключение", "крафт", "ресурс", "инструмент", "кирка", "меч"],
        "uk": ["піксель", "куб", "світ", "блок", "побудова", "квадрат", "моб",
               "пригода", "крафт", "ресурс", "інструмент", "кирка", "меч"],
        "en": ["pixel", "cube", "world", "block", "build", "square", "mob",
               "adventure", "craft", "resource", "tool", "pickaxe", "sword"],
    },
    "underwater": {
        "ru": ["море", "океан", "рыба", "волна", "ракушка", "водоросль", "коралл",
               "дельфин", "кит", "акула", "медуза", "осьминог", "звезда", "дно", "глубина"],
        "uk": ["море", "океан", "риба", "хвиля", "мушля", "водорість", "корал",
               "дельфін", "кит", "акула", "медуза", "восьминіг", "зірка", "дно", "глибина"],
        "en": ["sea", "ocean", "fish", "wave", "shell", "seaweed", "coral",
               "dolphin", "whale", "shark", "jellyfish", "octopus", "starfish", "deep"],
    },
    "travel": {
        "ru": ["путешествие", "чемодан", "билет", "поезд", "самолёт", "отель", "карта",
               "багаж", "паспорт", "море", "гора", "парк", "музей", "фото", "сувенир"],
        "uk": ["подорож", "валіза", "квиток", "поїзд", "літак", "готель", "карта",
               "багаж", "паспорт", "море", "гора", "парк", "музей", "фото", "сувенір"],
        "en": ["travel", "suitcase", "ticket", "train", "plane", "hotel", "map",
               "luggage", "passport", "sea", "mountain", "park", "museum", "photo", "souvenir"],
    },
    "robots": {
        "ru": ["робот", "механизм", "железо", "шестерня", "провод", "батарея", "микросхема",
               "трансформер", "металл", "антенна", "кнопка", "экран", "двигатель", "лазер"],
        "uk": ["робот", "механізм", "залізо", "шестерня", "провід", "батарея", "мікросхема",
               "трансформер", "метал", "антена", "кнопка", "екран", "двигун", "лазер"],
        "en": ["robot", "mechanism", "iron", "gear", "wire", "battery", "chip",
               "transformer", "metal", "antenna", "button", "screen", "engine", "laser"],
    },
    "magic_forest": {
        "ru": ["лес", "дерево", "гриб", "поляна", "ручей", "трава", "цветок",
               "ягода", "фея", "гном", "эльф", "волшебство", "свет", "тень", "тропа"],
        "uk": ["ліс", "дерево", "гриб", "галявина", "струмок", "трава", "квітка",
               "ягода", "фея", "гном", "ельф", "чарівництво", "світло", "тінь", "стежка"],
        "en": ["forest", "tree", "mushroom", "clearing", "stream", "grass", "flower",
               "berry", "fairy", "gnome", "elf", "magic", "light", "shadow", "path"],
    },
    "sport": {
        "ru": ["спорт", "мяч", "соревнование", "победа", "команда", "медаль", "рекорд",
               "бег", "прыжок", "бассейн", "велосипед", "лыжи", "коньки", "теннис"],
        "uk": ["спорт", "м'яч", "змагання", "перемога", "команда", "медаль", "рекорд",
               "біг", "стрибок", "басейн", "велосипед", "лижі", "ковзани", "теніс"],
        "en": ["sport", "ball", "competition", "victory", "team", "medal", "record",
               "run", "jump", "pool", "bike", "skis", "skates", "tennis"],
    },
    "cooking": {
        "ru": ["кухня", "кастрюля", "сковорода", "рецепт", "суп", "салат", "пирог",
               "тесто", "овощи", "фрукты", "нож", "ложка", "плита", "духовка"],
        "uk": ["кухня", "каструля", "сковорода", "рецепт", "суп", "салат", "пиріг",
               "тісто", "овочі", "фрукти", "ніж", "ложка", "плита", "духовка"],
        "en": ["kitchen", "pot", "pan", "recipe", "soup", "salad", "pie",
               "dough", "vegetables", "fruit", "knife", "spoon", "stove", "oven"],
    },
    "farm": {
        "ru": ["ферма", "корова", "свинья", "курица", "петух", "лошадь", "коза",
               "овца", "утка", "сарай", "забор", "поле", "сеновал", "амбар", "трактор"],
        "uk": ["ферма", "корова", "свиня", "курка", "півень", "кінь", "коза",
               "вівця", "качка", "хлів", "паркан", "поле", "сіновал", "комора", "трактор"],
        "en": ["farm", "cow", "pig", "chicken", "rooster", "horse", "goat",
               "sheep", "duck", "barn", "fence", "field", "hayloft", "shed", "tractor"],
    },
    "zoo": {
        "ru": ["зоопарк", "зверь", "клетка", "слон", "жираф", "обезьяна", "тигр",
               "лев", "зебра", "бегемот", "носорог", "крокодил", "попугай", "черепаха"],
        "uk": ["зоопарк", "звір", "клітка", "слон", "жираф", "мавпа", "тигр",
               "лев", "зебра", "бегемот", "носоріг", "крокодил", "папуга", "черепаха"],
        "en": ["zoo", "animal", "cage", "elephant", "giraffe", "monkey", "tiger",
               "lion", "zebra", "hippo", "rhino", "crocodile", "parrot", "turtle"],
    },
}

_NEUTRAL_WORDS = {
    "ru": ["предмет", "число", "фигура", "слово", "буква", "цифра", "знак",
           "картинка", "линия", "круг", "квадрат", "треугольник"],
    "uk": ["предмет", "число", "фігура", "слово", "буква", "цифра", "знак",
           "картинка", "лінія", "коло", "квадрат", "трикутник"],
    "en": ["object", "number", "shape", "word", "letter", "digit", "sign",
           "picture", "line", "circle", "square", "triangle"],
}

_GENERIC_ITEMS = {
    "ru": ["яблоко", "груша", "банан", "книга", "ручка", "стол", "стул"],
    "uk": ["яблуко", "груша", "банан", "книга", "ручка", "стіл", "стілець"],
    "en": ["apple", "pear", "banana", "book", "pen", "table", "chair"],
}


def get_words(topic: str, language: str = "ru") -> List[str]:
    topic = topic.lower().replace(" ", "_")
    if topic in _TOPICS:
        return _TOPICS[topic].get(language, _TOPICS[topic].get("ru", []))
    return []


def get_neutral(language: str = "ru") -> List[str]:
    return _NEUTRAL_WORDS.get(language, _NEUTRAL_WORDS["ru"])


def get_generic(language: str = "ru") -> List[str]:
    return _GENERIC_ITEMS.get(language, _GENERIC_ITEMS["ru"])


def random_word(topic: str, language: str = "ru") -> str:
    # Handle compound language codes like "uk+en" or "ru+en"
    simple_lang = language.split("+")[0].split("-")[0]
    words = get_words(topic, simple_lang)
    if not words:
        simple_lang = "en" if language.startswith("uk") else "ru"
        words = get_words(topic, simple_lang)
    if not words:
        words = get_neutral(simple_lang)
    return random.choice(words) if words else "?"


def random_n_words(topic: str, language: str = "ru", n: int = 3) -> List[str]:
    words = get_words(topic, language)
    if not words:
        words = get_neutral(language)
    return random.sample(words, min(n, len(words)))


def has_topic_words(text: str, topic: str, language: str = "ru") -> bool:
    words = get_words(topic, language)
    text_lower = text.lower()
    return any(w.lower() in text_lower for w in words)


def topic_word_ratio(text_pages: List[str], topic: str, language: str = "ru") -> float:
    words = get_words(topic, language)
    if not words or not text_pages:
        return 0.0
    matched = 0
    for page_text in text_pages:
        text_lower = page_text.lower()
        if any(w.lower() in text_lower for w in words):
            matched += 1
    return matched / len(text_pages)


def available_topics() -> List[str]:
    return list(_TOPICS.keys())


def make_story(topic_word: str, language: str = "ru") -> str:
    templates = {
        "ru": [
            f"Однажды {topic_word} отправился в путешествие.",
            f"Встретили {topic_word} на поляне.",
            f"Маленький {topic_word} нашёл новый друг.",
        ],
        "uk": [
            f"Одного разу {topic_word} вирушив у подорож.",
            f"Зустріли {topic_word} на галявині.",
            f"Маленький {topic_word} знайшов нового друга.",
        ],
        "en": [
            f"Once upon a time, {topic_word} went on a journey.",
            f"They met a {topic_word} in the clearing.",
            f"A little {topic_word} found a new friend.",
        ],
    }
    templates_list = templates.get(language, templates["ru"])
    return random.choice(templates_list)
