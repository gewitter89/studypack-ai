"""
Premium PDF renderer for StudyPack AI.
Generates print-ready, commercial-grade A4 workbooks with:
  - Professional cover with topic emoji icons
  - Name + date field on every page
  - Difficulty star badges
  - Motivational footer messages
  - Parent score box per page
  - Certificate of completion (final page)
  - Progress tracker / sticker chart page
  - Visual answer key
  - Page X of N numbering
  - Commercial/demo watermark modes
"""
import os
import random
import logging
from datetime import datetime
from typing import Dict, Any, Optional, List

from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT, TA_JUSTIFY
from reportlab.lib.colors import HexColor, black, white, Color
from reportlab.lib import colors
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, PageBreak,
    Table, TableStyle, Frame, PageTemplate, BaseDocTemplate,
    KeepTogether
)
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfgen import canvas

from core.models import StudyPack

logger = logging.getLogger(__name__)

# ─── Font registration ───────────────────────────────────────────────────────

_FONT_DIR = os.path.join(os.environ.get("WINDIR", r"C:\Windows"), "Fonts")
_fonts_registered = False


def _register_fonts():
    global _fonts_registered
    if _fonts_registered:
        return
    for name, file in [
        ("Arial", "arial.ttf"),
        ("Arial-Bold", "arialbd.ttf"),
        ("Arial-Italic", "ariali.ttf"),
        ("Arial-BoldItalic", "arialbi.ttf"),
    ]:
        path = os.path.join(_FONT_DIR, file)
        if os.path.exists(path):
            try:
                pdfmetrics.registerFont(TTFont(name, path))
            except Exception:
                pass
    _fonts_registered = True


_register_fonts()

FONT = "Arial"
FONT_BOLD = "Arial-Bold"
FONT_ITALIC = "Arial-Italic"

PAGE_WIDTH, PAGE_HEIGHT = A4
MARGIN = 22 * mm
CONTENT_WIDTH = PAGE_WIDTH - 2 * MARGIN

# ─── Topic emoji icons (Unicode safe — no images needed) ─────────────────────

TOPIC_ICONS = {
    "dinosaurs": "🦕",
    "dino": "🦕",
    "space": "🚀",
    "animals": "🐾",
    "cats": "🐱",
    "dogs": "🐶",
    "farm": "🐄",
    "underwater": "🐟",
    "ocean": "🐠",
    "sea": "🐙",
    "pirates": "🏴‍☠️",
    "superheroes": "🦸",
    "superhero": "🦸",
    "fairytale": "🧚",
    "magic": "✨",
    "robots": "🤖",
    "robot": "🤖",
    "transport": "🚗",
    "cars": "🚗",
    "princess": "👸",
    "forest": "🌲",
    "nature": "🌿",
    "sports": "⚽",
    "sport": "⚽",
    "food": "🍎",
    "pizza": "🍕",
    "music": "🎵",
    "winter": "❄️",
    "summer": "☀️",
    "spring": "🌸",
    "autumn": "🍂",
    "general": "📚",
    "reading": "📖",
    "math": "🔢",
    "logic": "🧩",
    "writing": "✏️",
    "english": "🔤",
    "alphabet": "🔤",
}

SUBJECT_THEMES = {
    "math": "academic",
    "reading": "minimal",
    "logic": "fun",
    "preschool": "fun",
    "mixed_week": "print_bw",
    "english": "minimal",
    "ukrainian": "academic",
}

# ─── Motivational messages (per-page footer) ─────────────────────────────────
MOTIVATIONAL_UK = [
    "Ти молодець! Продовжуй!",
    "Чудово! Так тримати!",
    "Кожне завдання — це перемога!",
    "Ти зростаєш з кожним завданням!",
    "Старання — це вже успіх!",
    "Неймовірно! Ти впораєшся!",
    "Крок за кроком до знань!",
    "Ти — справжній талант!",
]

MOTIVATIONAL_RU = [
    "Ты молодец! Продолжай!",
    "Отлично! Так держать!",
    "Каждое задание — это победа!",
    "Ты растёшь с каждым заданием!",
    "Стараться — это уже успех!",
    "Невероятно! У тебя получится!",
    "Шаг за шагом к знаниям!",
    "Ты — настоящий талант!",
]

# ─── Difficulty names ─────────────────────────────────────────────────────────

DIFFICULTY_NAMES_UK = {
    "easy": "легка",
    "medium": "середня",
    "hard": "складна",
}

DIFFICULTY_NAMES_RU = {
    "easy": "легкая",
    "medium": "средняя",
    "hard": "сложная",
}

# ─── Themes ───────────────────────────────────────────────────────────────────

THEMES = {
    "print_bw": {
        "name": "Чёрно-белый для печати",
        "brand": HexColor('#2E5090'),
        "light_gray": HexColor('#F0F0F0'),
        "med_gray": HexColor('#CCCCCC'),
        "dark_gray": HexColor('#444444'),
        "accent": HexColor('#3A7BD5'),
        "sep_color": HexColor('#E0E0E0'),
        "line_color": HexColor('#BBBBBB'),
        "title_color": HexColor('#2E5090'),
        "use_ink_save": True,
        "cover_bg": HexColor('#FFFFFF'),
        "cover_stripe": HexColor('#2E5090'),
    },
    "minimal": {
        "name": "Минималистичный",
        "brand": HexColor('#1A365D'),
        "light_gray": HexColor('#F7FAFC'),
        "med_gray": HexColor('#CBD5E0'),
        "dark_gray": HexColor('#2D3748'),
        "accent": HexColor('#3182CE'),
        "sep_color": HexColor('#E2E8F0'),
        "line_color": HexColor('#A0AEC0'),
        "title_color": HexColor('#1A365D'),
        "use_ink_save": False,
        "cover_bg": HexColor('#F7FAFC'),
        "cover_stripe": HexColor('#3182CE'),
    },
    "fun": {
        "name": "Весёлый",
        "brand": HexColor('#D53F8C'),
        "light_gray": HexColor('#FFF5F7'),
        "med_gray": HexColor('#FBB6CE'),
        "dark_gray": HexColor('#702459'),
        "accent": HexColor('#DD6B20'),
        "sep_color": HexColor('#FED7D7'),
        "line_color": HexColor('#E53E3E'),
        "title_color": HexColor('#D53F8C'),
        "use_ink_save": False,
        "cover_bg": HexColor('#FFF5F7'),
        "cover_stripe": HexColor('#D53F8C'),
    },
    "academic": {
        "name": "Учебный",
        "brand": HexColor('#22543D'),
        "light_gray": HexColor('#F0FFF4'),
        "med_gray": HexColor('#C6F6D5'),
        "dark_gray": HexColor('#22543D'),
        "accent": HexColor('#2F855A'),
        "sep_color": HexColor('#C6F6D5'),
        "line_color": HexColor('#68D391'),
        "title_color": HexColor('#22543D'),
        "use_ink_save": False,
        "cover_bg": HexColor('#F0FFF4'),
        "cover_stripe": HexColor('#2F855A'),
    },
}

DISCLAIMER_TEXT_UK = (
    "Матеріал є додатковим навчальним ресурсом і не замінює "
    "консультацію педагога, логопеда, психолога або лікаря."
)
DISCLAIMER_TEXT_RU = (
    "Материал является дополнительным учебным ресурсом и не заменяет "
    "консультацию педагога, логопеда, психолога или врача."
)


def _get_theme(theme_id: str = "print_bw") -> dict:
    return THEMES.get(theme_id, THEMES["print_bw"])


def _is_uk(lang: str) -> bool:
    return lang in ("uk", "uk+en")


# ─── Styles ───────────────────────────────────────────────────────────────────

def _get_styles(theme_id: str = "print_bw"):
    styles = getSampleStyleSheet()
    t = _get_theme(theme_id)

    styles.add(ParagraphStyle(
        name='CoverTitle', fontName=FONT_BOLD, fontSize=30,
        leading=38, alignment=TA_CENTER, spaceAfter=8 * mm,
        textColor=t["brand"]
    ))
    styles.add(ParagraphStyle(
        name='CoverSubtitle', fontName=FONT, fontSize=16,
        leading=22, alignment=TA_CENTER, spaceAfter=4 * mm,
        textColor=t["dark_gray"]
    ))
    styles.add(ParagraphStyle(
        name='CoverDetail', fontName=FONT, fontSize=11,
        leading=15, alignment=TA_CENTER, textColor=t["dark_gray"],
        spaceAfter=1.5 * mm
    ))
    styles.add(ParagraphStyle(
        name='CoverBrand', fontName=FONT_BOLD, fontSize=10,
        leading=14, alignment=TA_CENTER, textColor=t["med_gray"],
        spaceBefore=10 * mm
    ))
    styles.add(ParagraphStyle(
        name='PageTitle', fontName=FONT_BOLD, fontSize=20,
        leading=26, spaceBefore=2 * mm, spaceAfter=4 * mm,
        textColor=t["title_color"]
    ))
    styles.add(ParagraphStyle(
        name='Instruction', fontName=FONT, fontSize=11,
        leading=15, spaceAfter=3 * mm, textColor=t["dark_gray"],
        leftIndent=3 * mm
    ))
    styles.add(ParagraphStyle(
        name='TaskQuestion', fontName=FONT, fontSize=12,
        leading=17, spaceAfter=1 * mm, leftIndent=6 * mm,
        textColor=black
    ))
    styles.add(ParagraphStyle(
        name='TaskOption', fontName=FONT, fontSize=11,
        leading=15, leftIndent=10 * mm, textColor=t["dark_gray"],
        spaceAfter=0.5 * mm
    ))
    styles.add(ParagraphStyle(
        name='TaskAnswer', fontName=FONT, fontSize=11,
        leading=15, leftIndent=6 * mm, textColor=t["accent"],
        spaceBefore=2 * mm, spaceAfter=4 * mm
    ))
    styles.add(ParagraphStyle(
        name='Footer', fontName=FONT, fontSize=8,
        alignment=TA_CENTER, textColor=t["med_gray"]
    ))
    styles.add(ParagraphStyle(
        name='AnswerBlockTitle', fontName=FONT_BOLD, fontSize=14,
        leading=18, spaceBefore=4 * mm, spaceAfter=3 * mm,
        textColor=t["title_color"]
    ))
    styles.add(ParagraphStyle(
        name='AnswerBlock', fontName=FONT, fontSize=11,
        leading=16, leftIndent=6 * mm, spaceAfter=1.5 * mm
    ))
    styles.add(ParagraphStyle(
        name='FinalMessage', fontName=FONT_BOLD, fontSize=26,
        leading=34, alignment=TA_CENTER, spaceAfter=6 * mm,
        textColor=t["brand"]
    ))
    styles.add(ParagraphStyle(
        name='Disclaimer', fontName=FONT_ITALIC, fontSize=8,
        leading=11, alignment=TA_CENTER, textColor=t["med_gray"],
        spaceBefore=3 * mm
    ))
    styles.add(ParagraphStyle(
        name='SectionRule', fontName=FONT_BOLD, fontSize=13,
        leading=17, spaceBefore=3 * mm, spaceAfter=2 * mm,
        textColor=t["dark_gray"]
    ))
    styles.add(ParagraphStyle(
        name='ParentInst', fontName=FONT, fontSize=11,
        leading=16, leftIndent=4 * mm, spaceAfter=2 * mm,
        textColor=t["dark_gray"]
    ))
    styles.add(ParagraphStyle(
        name='MotivFooter', fontName=FONT_ITALIC, fontSize=8,
        leading=11, alignment=TA_CENTER, textColor=t["accent"],
        spaceBefore=2 * mm
    ))
    styles.add(ParagraphStyle(
        name='NameField', fontName=FONT, fontSize=10,
        leading=14, textColor=t["dark_gray"]
    ))
    styles.add(ParagraphStyle(
        name='ScoreBox', fontName=FONT, fontSize=9,
        leading=12, textColor=t["med_gray"], alignment=TA_RIGHT
    ))
    styles.add(ParagraphStyle(
        name='CertTitle', fontName=FONT_BOLD, fontSize=28,
        leading=36, alignment=TA_CENTER, textColor=t["brand"],
        spaceAfter=6 * mm
    ))
    styles.add(ParagraphStyle(
        name='CertBody', fontName=FONT, fontSize=14,
        leading=20, alignment=TA_CENTER, textColor=t["dark_gray"],
        spaceAfter=3 * mm
    ))
    styles.add(ParagraphStyle(
        name='CertName', fontName=FONT_BOLD, fontSize=22,
        leading=30, alignment=TA_CENTER, textColor=t["brand"],
        spaceAfter=4 * mm
    ))
    styles.add(ParagraphStyle(
        name='TrackerTitle', fontName=FONT_BOLD, fontSize=16,
        leading=22, alignment=TA_CENTER, textColor=t["title_color"],
        spaceAfter=4 * mm
    ))
    return styles


# ─── Watermark canvas (page decorations drawn on every page) ──────────────────

class _WatermarkCanvas:
    def __init__(self, watermark: str = "", is_commercial: bool = False,
                 brand: str = "", total_pages: int = 0, lang: str = "uk",
                 child_name: str = "", difficulty: str = "easy",
                 topic: str = "general"):
        self.watermark = watermark
        self.is_commercial = is_commercial
        self.brand = brand
        self.total_pages = total_pages
        self.lang = lang
        self.child_name = child_name
        self.difficulty = difficulty
        self.topic = topic

    def _draw_page_decorations(self, c: canvas.Canvas, doc):
        c.saveState()
        page_num = doc.page

        # Watermark (demo mode only)
        if not self.is_commercial and self.watermark and self.watermark.lower() == "internal_demo":
            c.setFont(FONT, 36)
            c.setFillColor(HexColor('#E0E0E0'))
            c.saveState()
            c.translate(PAGE_WIDTH / 2, PAGE_HEIGHT / 2)
            c.rotate(45)
            c.drawCentredString(0, 0, self.watermark)
            c.restoreState()

        # Skip decorations on cover page (page 1)
        if page_num > 1:
            uk = _is_uk(self.lang)

            # ── Demo watermark footer (left side, pages > 1) ──
            if not self.is_commercial and self.watermark and self.watermark.lower() != "internal_demo":
                c.setFont(FONT, 6)
                c.setFillColor(HexColor('#CCCCCC'))
                footer_text = "StudyPack AI — демо-сторінка" if uk else "StudyPack AI — демо-версия"
                c.drawString(MARGIN, 8 * mm, footer_text)

            # ── Page X of N (bottom center) ──
            if self.total_pages > 0:
                label = f"Сторінка {page_num} з {self.total_pages}" if uk else f"Страница {page_num} из {self.total_pages}"
            else:
                label = f"— {page_num} —"
            c.setFont(FONT, 7)
            c.setFillColor(HexColor('#BBBBBB'))
            c.drawCentredString(PAGE_WIDTH / 2, 8 * mm, label)

                    # ── Brand footer (right side) ──
            if self.brand:
                c.setFont(FONT, 6)
                c.setFillColor(HexColor('#CCCCCC'))
                c.drawRightString(PAGE_WIDTH - MARGIN, 8 * mm, self.brand)
                # Brand in top-right corner too
                c.setFont(FONT, 7)
                c.setFillColor(HexColor('#DDDDDD'))
                c.drawRightString(PAGE_WIDTH - MARGIN, PAGE_HEIGHT - 10 * mm, self.brand)

            # ── Name + Date field (top of page) ──
            name_label = "Ім'я" if uk else "Имя"
            date_label = "Дата" if uk else "Дата"
            name_val = self.child_name if self.child_name else "____________________"
            c.setFont(FONT, 9)
            c.setFillColor(HexColor('#AAAAAA'))
            c.drawString(MARGIN, PAGE_HEIGHT - 14 * mm,
                         f"{name_label}: {name_val}     {date_label}: __________")

            # ── Difficulty badge (top right) ──
            diff_dict = DIFFICULTY_NAMES_UK if uk else DIFFICULTY_NAMES_RU
            badge = diff_dict.get(self.difficulty, self.difficulty)
            if badge:
                c.setFont(FONT, 10)
                diff_label = "Складність: " if uk else "Сложность: "
                c.drawRightString(PAGE_WIDTH - MARGIN, PAGE_HEIGHT - 14 * mm, diff_label + badge)

        c.restoreState()

    def first_page(self, c: canvas.Canvas, doc):
        self._draw_page_decorations(c, doc)

    def later_pages(self, c: canvas.Canvas, doc):
        self._draw_page_decorations(c, doc)


# ─── Helper: separator line ──────────────────────────────────────────────────

def _separator(t, width=None):
    w = width or CONTENT_WIDTH
    sep = Table([[""]], colWidths=[w], rowHeights=[0.5])
    sep.setStyle(TableStyle([('BACKGROUND', (0, 0), (-1, -1), t["med_gray"])]))
    return sep


def _thin_separator(t, width=None):
    w = width or CONTENT_WIDTH
    sep = Table([[""]], colWidths=[w], rowHeights=[0.3])
    sep.setStyle(TableStyle([('BACKGROUND', (0, 0), (-1, -1), t["light_gray"])]))
    return sep


# ─── Cover page ───────────────────────────────────────────────────────────────

def _build_cover(elements, pack_data, styles, t, is_commercial, watermark, brand, lang):
    uk = _is_uk(lang)
    title = pack_data.get("title", "StudyPack")
    subtitle = pack_data.get("subtitle", "")
    age = pack_data.get("age", "")
    grade = pack_data.get("grade", "")
    topic = pack_data.get("topic", "")
    pages_data = pack_data.get("pages", [])
    difficulty = pack_data.get("difficulty", "easy")

    try:
        from core.topic_lexicon import resolve_topic, get_display_name
        resolved_topic = resolve_topic(topic, lang)
        display_topic = get_display_name(topic, lang)
    except ImportError:
        resolved_topic = topic
        display_topic = topic
    icon = TOPIC_ICONS.get(topic.lower(), TOPIC_ICONS.get("general", "📚"))
    icon_display = f"<font size='48'>{icon}</font>"

    mascot = pack_data.get("_mascot")
    mascot_greeting = pack_data.get("_mascot_greeting", "")

    # ── Top Color Banner ──
    banner = Table([[""]], colWidths=[PAGE_WIDTH], rowHeights=[30 * mm])
    banner.setStyle(TableStyle([('BACKGROUND', (0, 0), (-1, -1), t["cover_stripe"])]))
    elements.append(banner)
    elements.append(Spacer(1, 15 * mm))

    # ── Decorative Top ──
    try:
        from pdf.vector_drawings import draw_star
        star_deco = draw_star(size=12*mm, color=t["accent"])
        elements.append(star_deco)
        elements.append(Spacer(1, 4*mm))
    except ImportError:
        pass

    icon_style = ParagraphStyle('CoverIcon', fontName=FONT, fontSize=48, alignment=TA_CENTER, spaceAfter=4*mm)
    elements.append(Paragraph(icon_display, icon_style))
    elements.append(Spacer(1, 4 * mm))

    if mascot:
        mascot_emoji = mascot.get("emoji", "")
        mascot_name_uk = mascot.get("name_uk", "")
        mascot_name_ru = mascot.get("name_ru", "")
        mascot_display = mascot_name_uk if uk else mascot_name_ru
        mascot_style = ParagraphStyle(
            'CoverMascot', fontName=FONT_BOLD, fontSize=14,
            leading=20, alignment=TA_CENTER, textColor=t["dark_gray"]
        )
        elements.append(Paragraph(f"{mascot_emoji} {mascot_display}", mascot_style))
        elements.append(Spacer(1, 2 * mm))

    if mascot_greeting:
        greet_style = ParagraphStyle(
            'CoverGreeting', fontName=FONT_ITALIC, fontSize=12,
            leading=17, alignment=TA_CENTER, textColor=t["accent"]
        )
        elements.append(Paragraph(mascot_greeting, greet_style))
        elements.append(Spacer(1, 4 * mm))

    elements.append(Paragraph(title, styles['CoverTitle']))
    elements.append(Spacer(1, 5 * mm))

    if subtitle:
        elements.append(Paragraph(subtitle, styles['CoverSubtitle']))
    elements.append(Spacer(1, 15 * mm))

    # Info Blocks (Rich Cards)
    # Block 1: Для кого підходить
    target_title = "Для кого підходить:" if uk else "Для кого подходит:"
    target_style = ParagraphStyle(
        'CoverInsideTitle', fontName=FONT_BOLD, fontSize=14,
        leading=18, spaceAfter=4 * mm, textColor=t["dark_gray"]
    )
    elements.append(Paragraph(target_title, target_style))
    
    target_info = []
    if age:
        target_info.append(f"Вік: {age} років" if uk else f"Возраст: {age} лет")
    if grade:
        target_info.append(f"Клас: {grade}" if uk else f"Класс: {grade}")
    if difficulty:
        diff_dict = DIFFICULTY_NAMES_UK if uk else DIFFICULTY_NAMES_RU
        target_info.append(f"Складність: {diff_dict.get(difficulty, difficulty)}" if uk else f"Сложность: {diff_dict.get(difficulty, difficulty)}")
        
    inside_style_item = ParagraphStyle(
        'CoverInsideItem', fontName=FONT, fontSize=12,
        leading=16, textColor=t["dark_gray"]
    )
        
    target_str = " • ".join(target_info)
    target_card = Table([[Paragraph(target_str, inside_style_item)]], colWidths=[CONTENT_WIDTH])
    target_card.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), t.get("light_gray", "#f0f0f0")),
        ('BOX', (0,0), (-1,-1), 1, t.get("accent", "#cccccc")),
        ('TOPPADDING', (0,0), (-1,-1), 8),
        ('BOTTOMPADDING', (0,0), (-1,-1), 8),
    ]))
    elements.append(target_card)
    elements.append(Spacer(1, 10 * mm))

    # Block 2: Що тренуємо (Тематика)
    if display_topic:
        topic_title = "Що тренуємо:" if uk else "Что тренируем:"
        elements.append(Paragraph(topic_title, target_style))
        topic_card = Table([[Paragraph(display_topic, inside_style_item)]], colWidths=[CONTENT_WIDTH])
        topic_card.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,-1), t.get("light_gray", "#f0f0f0")),
            ('BOX', (0,0), (-1,-1), 1, t.get("accent", "#cccccc")),
            ('TOPPADDING', (0,0), (-1,-1), 8),
            ('BOTTOMPADDING', (0,0), (-1,-1), 8),
        ]))
        elements.append(topic_card)
        elements.append(Spacer(1, 10 * mm))

    # ── What's Inside list ──
    # Group by task types instead of raw page titles
    category_counts = {}
    for page in pages_data:
        p_type = page.get("page_type", "exercise")
        if p_type in ("answers", "instruction"):
            continue
        tasks = page.get("tasks", [])
        for tsk in tasks:
            t_type = tsk.get("type", "logic")
            if "math" in t_type or "count" in t_type:
                category_counts["math"] = category_counts.get("math", 0) + 1
            elif "logic" in t_type or "maze" in t_type or "sudoku" in t_type:
                category_counts["logic"] = category_counts.get("logic", 0) + 1
            elif "reading" in t_type:
                category_counts["reading"] = category_counts.get("reading", 0) + 1
            elif "writing" in t_type:
                category_counts["writing"] = category_counts.get("writing", 0) + 1
            elif "creative" in t_type or "coloring" in t_type or "drawing" in t_type:
                category_counts["creative"] = category_counts.get("creative", 0) + 1
            else:
                category_counts["logic"] = category_counts.get("logic", 0) + 1

    inside_items = []
    if category_counts.get("math"):
        inside_items.append("Математика та лічба" if uk else "Математика и счет")
    if category_counts.get("logic"):
        inside_items.append("Логіка та мислення" if uk else "Логика и мышление")
    if category_counts.get("reading"):
        inside_items.append("Читання" if uk else "Чтение")
    if category_counts.get("writing"):
        inside_items.append("Письмо та граматика" if uk else "Письмо и грамматика")
    if category_counts.get("creative"):
        inside_items.append("Творчість (розмальовки)" if uk else "Творчество (раскраски)")

    if pack_data.get("include_answers", True) or pack_data.get("answers"):
        inside_items.append("Відповіді для дорослого" if uk else "Ответы для взрослого")

    # If it's still empty for some reason, fallback
    if not inside_items:
        inside_items = ["Цікаві завдання" if uk else "Интересные задания", "Відповіді" if uk else "Ответы"]

    if inside_items:
        inside_title = "Що всередині:" if uk else "Что внутри:"
        inside_style_title = ParagraphStyle(
            'CoverInsideTitle', fontName=FONT_BOLD, fontSize=14,
            leading=18, spaceAfter=4 * mm, textColor=t["dark_gray"]
        )
        elements.append(Paragraph(inside_title, inside_style_title))
        
        inside_style_item = ParagraphStyle(
            'CoverInsideItem', fontName=FONT, fontSize=12,
            leading=16, textColor=t["accent"]
        )
        
        try:
            from pdf.vector_drawings import draw_checkbox
            box_icon = draw_checkbox(size=6*mm, checked=True, color=t["accent"])
        except ImportError:
            box_icon = "✓"
            
        inside_rows = []
        for item in inside_items:
            inside_rows.append([box_icon, Paragraph(item, inside_style_item)])
            
        if inside_rows:
            inside_t = Table(inside_rows, colWidths=[10*mm, CONTENT_WIDTH - 10*mm])
            inside_t.setStyle([('VALIGN', (0,0), (-1,-1), 'MIDDLE')])
            elements.append(inside_t)

    elements.append(Spacer(1, 15 * mm))

    # Format block
    format_title = "Формат:" if uk else "Формат:"
    elements.append(Paragraph(format_title, inside_style_title))
    format_1 = "PDF для друку A4" if uk else "PDF для печати A4"
    format_2 = "10-20 хвилин на день" if uk else "10-20 минут в день"
    
    format_rows = [
        [box_icon, Paragraph(format_1, inside_style_item)],
        [box_icon, Paragraph(format_2, inside_style_item)]
    ]
    format_t = Table(format_rows, colWidths=[10*mm, CONTENT_WIDTH - 10*mm])
    format_t.setStyle([('VALIGN', (0,0), (-1,-1), 'MIDDLE')])
    elements.append(format_t)
    
    elements.append(Spacer(1, 10 * mm))

    if brand:
        # Brand box with colored background
        brand_label = "Викладач:" if uk else "Преподаватель:"
        brand_style = ParagraphStyle(
            'CoverBrandLabel', fontName=FONT_BOLD, fontSize=11,
            leading=15, alignment=TA_CENTER, textColor=t["accent"],
            spaceAfter=2*mm
        )
        elements.append(Paragraph(brand_label, brand_style))
        brand_card = Table([[Paragraph(brand, styles['CoverBrand'])]], colWidths=[CONTENT_WIDTH*0.7])
        brand_card.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,-1), t.get("light_gray", "#f0f0f0")),
            ('BOX', (0,0), (-1,-1), 1.5, t.get("accent", "#cccccc")),
            ('TOPPADDING', (0,0), (-1,-1), 6),
            ('BOTTOMPADDING', (0,0), (-1,-1), 6),
            ('ALIGN', (0,0), (-1,-1), 'CENTER'),
        ]))
        elements.append(brand_card)
        elements.append(Spacer(1, 5 * mm))

    # Colored stripe separator at bottom
    stripe = Table([[""]], colWidths=[CONTENT_WIDTH], rowHeights=[3])
    stripe.setStyle(TableStyle([('BACKGROUND', (0, 0), (-1, -1), t["cover_stripe"])]))
    elements.append(stripe)

    if not is_commercial and watermark:
        demo_note = (
            "ДЕМО-ВЕРСІЯ | Для комерційного використання звертайтеся до автора"
            if uk
            else "ДЕМО-ВЕРСИЯ | Для коммерческого использования обратитесь к автору"
        )
        elements.append(Spacer(1, 3 * mm))
        elements.append(Paragraph(demo_note, styles['CoverBrand']))

    elements.append(PageBreak())


# ─── Parent instruction page ─────────────────────────────────────────────────

def _build_parent_page(elements, pack_data, styles, t, lang):
    uk = _is_uk(lang)
    parent_instruction = pack_data.get("parent_instruction", "")

    inst_title = "Інструкція для батьків" if uk else "Инструкция для родителей"
    elements.append(Paragraph(inst_title, styles['PageTitle']))
    elements.append(Spacer(1, 2 * mm))

    bullets = [
        "Займайтеся 10–20 хвилин на день." if uk else "Занимайтесь 10–20 минут в день.",
        "Не сваріть дитину за помилки — хваліть за спробу." if uk else "Не ругайте ребёнка за ошибки — хвалите за попытку.",
        "Робіть перерви, якщо дитина втомилася." if uk else "Делайте перерывы, если ребёнок устал.",
        "Використовуйте завдання як гру, а не як іспит." if uk else "Используйте задания как игру, а не как экзамен.",
        "Відповіді в кінці — тільки для перевірки дорослим." if uk else "Ответы в конце — только для проверки взрослым.",
    ]
    for b in bullets:
        elements.append(Paragraph(f"•  {b}", styles['ParentInst']))
        elements.append(Spacer(1, 1 * mm))

    disclaimer = DISCLAIMER_TEXT_UK if uk else DISCLAIMER_TEXT_RU
    elements.append(Spacer(1, 4 * mm))
    elements.append(_thin_separator(t))
    elements.append(Spacer(1, 2 * mm))
    elements.append(Paragraph(disclaimer, styles['Disclaimer']))
    elements.append(PageBreak())


# ─── Exercise pages ──────────────────────────────────────────────────────────

def _build_exercise_pages(elements, pages_data, styles, t, lang, difficulty):
    uk = _is_uk(lang)
    motiv_pool = MOTIVATIONAL_UK if uk else MOTIVATIONAL_RU

    for page in pages_data:
        if page.get("page_type") == "answers":
            continue

        title_text = page.get("title", "")
        instruction = page.get("instruction", "")
        tasks = page.get("tasks", [])

        # Page title with decorative line
        elements.append(Spacer(1, 4 * mm))  # space below name/date field
        elements.append(Paragraph(title_text, styles['PageTitle']))
        if instruction:
            elements.append(Paragraph(instruction, styles['Instruction']))

        elements.append(_thin_separator(t, CONTENT_WIDTH - 6 * mm))
        elements.append(Spacer(1, 2 * mm))

        # Tasks
        for j, task in enumerate(tasks):
            q = task.get("question", "")
            opts = task.get("options") or []
            has_space = task.get("answer_space", True)
            
            import re
            try:
                from pdf import vector_drawings
            except ImportError:
                vector_drawings = None

            try:
                from pdf import visual_renderers
            except ImportError:
                visual_renderers = None
            
            cell_flowables = []
            
            from reportlab.platypus import KeepTogether
            
            task_visual = task.get("visual_aid", "")
            if task_visual and visual_renderers:
                accent = t.get("brand", "#4A90E2")
                if q.strip():
                    cell_flowables.append(Paragraph(q.strip(), styles['TaskQuestion']))
                draw = visual_renderers.render_visual(task, lang, accent, CONTENT_WIDTH)
                cell_flowables.append(Spacer(1, 4*mm))
                cell_flowables.append(draw)
                cell_flowables.append(Spacer(1, 4*mm))
            else:
                parts = re.split(r'(\{\{(?:DRAW|SHAPE):[^}]+\}\})', q)
                for part in parts:
                    if not part:
                        continue
                    if part.startswith("{{") and part.endswith("}}"):
                        content = part[2:-2]
                        tokens = content.split(":")
                        cmd = tokens[0]
                        if vector_drawings:
                            if cmd == "DRAW" and len(tokens) >= 3:
                                icon_type = tokens[1]
                                count = int(tokens[2])
                                d = vector_drawings.draw_thematic_icon(icon_type, count)
                                cell_flowables.append(Spacer(1, 4*mm))
                                cell_flowables.append(d)
                                cell_flowables.append(Spacer(1, 4*mm))
                            elif cmd == "SHAPE" and len(tokens) >= 2:
                                shape_type = tokens[1]
                                d = vector_drawings.draw_shape(shape_type)
                                cell_flowables.append(Spacer(1, 4*mm))
                                cell_flowables.append(d)
                                cell_flowables.append(Spacer(1, 4*mm))
                        else:
                            cell_flowables.append(Paragraph(f"[VECTOR_MISSING: {content}]", styles['TaskQuestion']))
                    else:
                        if part.strip():
                            cell_flowables.append(Paragraph(part.strip(), styles['TaskQuestion']))
                        
            if opts:
                cell_flowables.append(Spacer(1, 2*mm))
                for i, opt in enumerate(opts):
                    letter = chr(65 + i) if i < 26 else str(i + 1)
                    cell_flowables.append(Paragraph(
                        f"&nbsp;&nbsp;&nbsp;<b>{letter})</b> {opt}",
                        styles['TaskOption']
                    ))
                    
            if has_space:
                cell_flowables.append(Spacer(1, 6 * mm))
                ans_box = Table([["Відповідь: " if uk else "Ответ: ", "__________________"]], colWidths=[25*mm, 50*mm])
                ans_box.setStyle(TableStyle([
                    ('FONTNAME', (0,0), (-1,-1), FONT_BOLD),
                    ('FONTSIZE', (0,0), (-1,-1), 12),
                    ('TEXTCOLOR', (0,0), (-1,-1), t["dark_gray"]),
                    ('ALIGN', (0,0), (0,-1), 'RIGHT'),
                    ('VALIGN', (0,0), (-1,-1), 'BOTTOM'),
                    ('BOTTOMPADDING', (0,0), (-1,-1), 0),
                ]))
                cell_flowables.append(ans_box)
            else:
                cell_flowables.append(Spacer(1, 2 * mm))

            # Wrap in a premium card Table (2 rows: Header, Content)
            task_header_text = f"Завдання {j + 1}" if uk else f"Задание {j + 1}"
            header_style = ParagraphStyle(
                'CardHeader', fontName=FONT_BOLD, fontSize=11, textColor=white
            )
            header_flowable = Paragraph(task_header_text, header_style)
            
            card = Table([[header_flowable], [cell_flowables]], colWidths=[CONTENT_WIDTH])
            card.setStyle(TableStyle([
                # Header row styling
                ('BACKGROUND', (0,0), (-1,0), t.get("brand", "#4A90E2")),
                ('TOPPADDING', (0,0), (-1,0), 4),
                ('BOTTOMPADDING', (0,0), (-1,0), 4),
                ('LEFTPADDING', (0,0), (-1,0), 8),
                # Content row styling
                ('BACKGROUND', (0,1), (-1,1), "#fafafa"),
                ('TOPPADDING', (0,1), (-1,1), 8*mm),
                ('BOTTOMPADDING', (0,1), (-1,1), 8*mm),
                ('LEFTPADDING', (0,1), (-1,1), 8*mm),
                ('RIGHTPADDING', (0,1), (-1,1), 8*mm),
                # Box around the whole card
                ('BOX', (0,0), (-1,-1), 1.5, t.get("brand", "#4A90E2")),
            ]))
            
            elements.append(KeepTogether(card))
            elements.append(Spacer(1, 8 * mm))

        # ── Score box (bottom of page) ──
        score_label = "Результат" if uk else "Результат"
        total = len(tasks)
        score_text = f"{score_label}: ___ / {total}     {'Дата' if uk else 'Дата'}: __________"
        elements.append(Spacer(1, 3 * mm))
        elements.append(_thin_separator(t))
        elements.append(Spacer(1, 1 * mm))
        elements.append(Paragraph(score_text, styles['ScoreBox']))

        # ── Motivational message ──
        motiv = random.choice(motiv_pool)
        elements.append(Paragraph(motiv, styles['MotivFooter']))

        elements.append(PageBreak())


# ─── Progress tracker page ───────────────────────────────────────────────────

def _build_tracker_page(elements, pages_data, styles, t, lang):
    uk = _is_uk(lang)
    elements.append(Spacer(1, 4 * mm))
    tracker_title = "Трекер прогресу" if uk else "Трекер прогресса"
    elements.append(Paragraph(tracker_title, styles['TrackerTitle']))

    desc = (
        "Відмічай кожне виконане завдання зірочкою або наклейкою!"
        if uk
        else "Отмечай каждое выполненное задание звёздочкой или наклейкой!"
    )
    elements.append(Paragraph(desc, styles['Instruction']))
    elements.append(Spacer(1, 4 * mm))

    exercise_pages = [p for p in pages_data if p.get("page_type") != "answers"]
    num_exercises = len(exercise_pages)

    # Build tracker grid (rows of 7)
    day_label = "Завдання" if uk else "Задание"
    
    try:
        from pdf.vector_drawings import draw_star, draw_checkbox
        star_icon = draw_star(size=12*mm)
        box_icon = draw_checkbox(size=10*mm)
    except ImportError:
        star_icon = "Star"
        box_icon = "Box"

    header = [day_label, star_icon]
    rows = [header]
    for i in range(num_exercises):
        page_title = exercise_pages[i].get("title", f"{day_label} {i+1}")
        short_title = page_title[:30] if len(page_title) > 30 else page_title
        rows.append([short_title, box_icon])

    col_widths = [CONTENT_WIDTH - 30 * mm, 25 * mm]
    tracker_table = Table(rows, colWidths=col_widths)
    tracker_table.setStyle(TableStyle([
        ('FONTNAME', (0, 0), (-1, 0), FONT_BOLD),
        ('FONTNAME', (0, 1), (-1, -1), FONT),
        ('FONTSIZE', (0, 0), (-1, -1), 11),
        ('TEXTCOLOR', (0, 0), (-1, 0), t["brand"]),
        ('TEXTCOLOR', (0, 1), (-1, -1), t["dark_gray"]),
        ('ALIGN', (1, 0), (1, -1), 'CENTER'),
        ('GRID', (0, 0), (-1, -1), 0.5, t["line_color"]),
        ('BACKGROUND', (0, 0), (-1, 0), t["light_gray"]),
        ('TOPPADDING', (0, 0), (-1, -1), 3),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 3),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
    ]))
    elements.append(tracker_table)
    elements.append(PageBreak())


# ─── Final "well done" page ──────────────────────────────────────────────────

def _build_final_page(elements, styles, t, lang):
    uk = _is_uk(lang)
    elements.append(Spacer(1, 30 * mm))
    msg = "Молодець! Ти чудово впорався!" if uk else "Молодец! Ты отлично справился!"
    elements.append(Paragraph(msg, styles['FinalMessage']))
    
    try:
        from pdf.vector_drawings import draw_star
        elements.append(Spacer(1, 5 * mm))
        
        # We can draw 3 stars centered
        from reportlab.platypus import Table
        star = draw_star(size=15*mm)
        t_stars = Table([[star, star, star]], colWidths=[20*mm]*3)
        t_stars.setStyle([('ALIGN', (0,0), (-1,-1), 'CENTER')])
        elements.append(t_stars)
    except ImportError:
        pass
        
    elements.append(Spacer(1, 8 * mm))
    finish = (
        "Продовжуй займатися, і в тебе все вийде!"
        if uk else "Продолжай заниматься, и у тебя всё получится!"
    )
    elements.append(Paragraph(finish, styles['CoverSubtitle']))
    elements.append(PageBreak())


# ─── Certificate of completion ────────────────────────────────────────────────

def _build_certificate(elements, pack_data, styles, t, lang, child_name):
    uk = _is_uk(lang)
    elements.append(Spacer(1, 15 * mm))

    # Decorative border (top stripe)
    stripe = Table([[""]], colWidths=[CONTENT_WIDTH], rowHeights=[4])
    stripe.setStyle(TableStyle([('BACKGROUND', (0, 0), (-1, -1), t["cover_stripe"])]))
    elements.append(stripe)
    elements.append(Spacer(1, 10 * mm))

    cert_label = "СЕРТИФІКАТ" if uk else "СЕРТИФИКАТ"
    elements.append(Paragraph(cert_label, styles['CertTitle']))

    desc = (
        "Цим підтверджується, що"
        if uk else "Настоящим подтверждается, что"
    )
    elements.append(Paragraph(desc, styles['CertBody']))

    name_display = child_name if child_name else ("____________________" if uk else "____________________")
    elements.append(Paragraph(name_display, styles['CertName']))

    topic = pack_data.get("topic", "")
    try:
        from core.topic_lexicon import get_display_name
        display_topic = get_display_name(topic, lang)
    except ImportError:
        display_topic = topic

    title = pack_data.get("title", "StudyPack")
    completed_text = (
        f"успішно завершив(ла) навчальний набір «{title}»"
        if uk
        else f"успешно завершил(а) учебный набор «{title}»"
    )
    elements.append(Paragraph(completed_text, styles['CertBody']))
    elements.append(Spacer(1, 4 * mm))

    pages_count = len([p for p in pack_data.get("pages", []) if p.get("page_type") != "answers"])
    pages_text = (
        f"Виконано завдань: {pages_count} сторінок"
        if uk
        else f"Выполнено заданий: {pages_count} страниц"
    )
    elements.append(Paragraph(pages_text, styles['CertBody']))

    try:
        from pdf.vector_drawings import draw_star
        star_flowable = draw_star(size=15*mm)
        stars_row = [star_flowable] * 5
        stars_t = Table([stars_row], colWidths=[20*mm]*5)
        stars_t.setStyle([('ALIGN', (0,0), (-1,-1), 'CENTER')])
        elements.append(Spacer(1, 4 * mm))
        elements.append(stars_t)
    except ImportError:
        pass

    date_str = datetime.now().strftime("%d.%m.%Y")
    date_text = f"{'Дата' if uk else 'Дата'}: {date_str}"
    elements.append(Paragraph(date_text, styles['CertBody']))

    elements.append(Spacer(1, 8 * mm))
    elements.append(stripe)
    elements.append(PageBreak())


def _build_achievements_page(elements, pack_data, styles, t, lang):
    """Render a page showing XP progress, achievements earned, and stars collected."""
    uk = _is_uk(lang)
    gamification = pack_data.get("_gamification", {})
    if not gamification:
        return

    xp = gamification.get("xp")
    achievements = gamification.get("achievements", [])
    stars = gamification.get("stars", [])
    quote = gamification.get("motivational_quote", "")

    elements.append(Spacer(1, 4 * mm))
    
    title = "Твої досягнення" if uk else "Твои достижения"
    elements.append(Paragraph(title, styles['PageTitle']))
    elements.append(_thin_separator(t, CONTENT_WIDTH - 6 * mm))
    elements.append(Spacer(1, 3 * mm))

    if xp:
        level_label = "Рівень" if uk else "Уровень"
        xp_text = f"{level_label} {xp.level} • {xp.current_xp} / {xp.xp_to_next} XP"
        elements.append(Paragraph(xp_text, ParagraphStyle(
            'XPLevel', fontName=FONT_BOLD, fontSize=16, leading=20,
            spaceAfter=4 * mm, textColor=t["accent"], alignment=TA_CENTER
        )))
        xp_filled = int((xp.current_xp / max(xp.xp_to_next, 1)) * 20)
        progress_bar = "█" * xp_filled + "░" * (20 - xp_filled)
        elements.append(Paragraph(progress_bar, ParagraphStyle(
            'XPBar', fontName=FONT, fontSize=14, leading=18,
            spaceAfter=5 * mm, alignment=TA_CENTER, textColor=t["dark_gray"]
        )))

    if stars:
        earned = sum(1 for s in stars if s.earned)
        total = len(stars)
        star_label = "Зірки" if uk else "Звёзды"
        star_text = f"{star_label}: ⭐ {earned} / {total}"
        elements.append(Paragraph(star_text, ParagraphStyle(
            'StarsText', fontName=FONT, fontSize=14, leading=18,
            spaceAfter=5 * mm, alignment=TA_CENTER, textColor=t["dark_gray"]
        )))

    if achievements:
        ach_title = "Відзнаки" if uk else "Награды"
        elements.append(Paragraph(ach_title, ParagraphStyle(
            'AchTitle', fontName=FONT_BOLD, fontSize=13, leading=16,
            spaceAfter=3 * mm, textColor=t["dark_gray"]
        )))
        
        cols = 2
        ach_rows = []
        row = []
        for a in achievements:
            a_title = a.title.get(lang, a.title.get("uk", a.title.get("en", "")))
            cell_text = f"{a.icon} {a_title}"
            cell = Table(
                [[cell_text]],
                colWidths=[(CONTENT_WIDTH - 4 * mm) / cols],
                rowHeights=[12 * mm],
            )
            cell.setStyle(TableStyle([
                ('FONTNAME', (0, 0), (-1, -1), FONT),
                ('FONTSIZE', (0, 0), (-1, -1), 11),
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                ('BACKGROUND', (0, 0), (-1, -1), HexColor("#f0f8ff")),
                ('BOX', (0, 0), (-1, -1), 0.5, t["line_color"]),
                ('LEFTPADDING', (0, 0), (-1, -1), 4),
            ]))
            row.append(cell)
            if len(row) == cols:
                ach_rows.append(row)
                row = []
        if row:
            while len(row) < cols:
                row.append(Table([[""]], colWidths=[(CONTENT_WIDTH - 4 * mm) / cols], rowHeights=[12 * mm]))
            ach_rows.append(row)
        
        if ach_rows:
            ach_table = Table(ach_rows, colWidths=[(CONTENT_WIDTH - 4 * mm) / cols] * cols)
            ach_table.setStyle(TableStyle([
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                ('TOPPADDING', (0, 0), (-1, -1), 2 * mm),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 2 * mm),
            ]))
            elements.append(ach_table)
        elements.append(Spacer(1, 4 * mm))

    if quote:
        elements.append(Paragraph(f"«{quote}»", ParagraphStyle(
            'Quote', fontName=FONT_ITALIC, fontSize=12, leading=16,
            spaceBefore=3 * mm, spaceAfter=3 * mm, textColor=t["accent"],
            alignment=TA_CENTER
        )))
    
    elements.append(PageBreak())


def _build_parent_report_page(elements, pack_data, styles, t, lang):
    """Render parent analytics report page with category breakdown and recommendations."""
    uk = _is_uk(lang)
    
    try:
        from core.analytics import generate_report, format_report_text
    except ImportError:
        return
    
    pages_data = pack_data.get("pages", [])
    if not pages_data:
        return
    
    report = generate_report(pages_data, lang)
    if report.total_tasks == 0:
        return
    
    report_lines = format_report_text(report, lang)
    
    elements.append(Spacer(1, 4 * mm))
    
    title = "Звіт для батьків" if uk else "Отчёт для родителей"
    elements.append(Paragraph(title, styles['PageTitle']))
    elements.append(_thin_separator(t, CONTENT_WIDTH - 6 * mm))
    elements.append(Spacer(1, 3 * mm))
    
    series_info = pack_data.get("_series", {})
    if series_info:
        idx = series_info.get("pack_index", 1)
        total = series_info.get("total_packs", 1)
        series_name = series_info.get("name", "")
        series_text = f"{series_name} #{idx}/{total}" if uk else f"{series_name} №{idx}/{total}"
        elements.append(Paragraph(series_text, ParagraphStyle(
            'SeriesInfo', fontName=FONT_ITALIC, fontSize=10, leading=14,
            spaceAfter=2 * mm, textColor=t["dark_gray"], alignment=TA_RIGHT
        )))
    
    line_style = ParagraphStyle(
        'ReportLine', fontName=FONT, fontSize=11, leading=15,
        spaceAfter=2 * mm, textColor=t["dark_gray"]
    )
    line_bold = ParagraphStyle(
        'ReportLineBold', fontName=FONT_BOLD, fontSize=11, leading=15,
        spaceAfter=2 * mm, textColor=t["dark_gray"]
    )
    
    for line in report_lines:
        if not line:
            elements.append(Spacer(1, 2 * mm))
            continue
        style = line_bold if line.strip().startswith(("Сильні", "Сильные", "Підтягнути", "Подтянуть", "Розподіл", "Распределение", "Рекомендації", "Рекомендации")) else line_style
        elements.append(Paragraph(line, style))
    
    if report.category_breakdown:
        elements.append(Spacer(1, 3 * mm))
        
        bar_data = [["Категорія" if uk else "Категория", "%"]]
        total = max(report.total_tasks, 1)
        for cat, count in sorted(report.category_breakdown.items(), key=lambda x: -x[1]):
            from core.analytics import TYPE_LABELS
            cat_label = TYPE_LABELS.get(lang, TYPE_LABELS["uk"]).get(cat, cat)
            pct = int(count / total * 100)
            bar_data.append([cat_label, f"{pct}%"])
        
        if len(bar_data) > 1:
            cat_table = Table(bar_data, colWidths=[80 * mm, 20 * mm])
            cat_table.setStyle(TableStyle([
                ('FONTNAME', (0, 0), (-1, 0), FONT_BOLD),
                ('FONTNAME', (0, 1), (-1, -1), FONT),
                ('FONTSIZE', (0, 0), (-1, -1), 10),
                ('TEXTCOLOR', (0, 0), (-1, 0), white),
                ('BACKGROUND', (0, 0), (-1, 0), t["brand"]),
                ('GRID', (0, 0), (-1, -1), 0.5, t["line_color"]),
                ('ALIGN', (1, 0), (1, -1), 'CENTER'),
                ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                ('TOPPADDING', (0, 0), (-1, -1), 3),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 3),
            ]))
            elements.append(cat_table)
    
    elements.append(PageBreak())







# ─── Bonus pages (stickers, coloring, etc) ─────────────────────────────────

def _build_bonus_pages(elements, pack_data, styles, t, lang):
    uk = _is_uk(lang)
    bonus_pages = pack_data.get("_bonus_pages", [])
    if not bonus_pages:
        return

    for bp in bonus_pages:
        bp_type = bp.get("page_type", "")
        bp_title = bp.get("title", "")
        bp_instruction = bp.get("instruction", "")
        bp_tasks = bp.get("tasks", [])

        elements.append(Spacer(1, 4 * mm))
        elements.append(Paragraph(bp_title, styles['PageTitle']))
        if bp_instruction:
            elements.append(Paragraph(bp_instruction, styles['Instruction']))
        elements.append(_thin_separator(t, CONTENT_WIDTH - 6 * mm))
        elements.append(Spacer(1, 2 * mm))

        if bp_type == "sticker_rewards":
            grid_cols = 4
            cells = []
            row = []
            for i in range(len(bp_tasks)):
                cell = Table(
                    [[f"⭐ {i + 1}"]],
                    colWidths=[(CONTENT_WIDTH - 4 * mm) / grid_cols],
                    rowHeights=[25 * mm],
                )
                cell.setStyle(TableStyle([
                    ('FONTNAME', (0, 0), (-1, -1), FONT),
                    ('FONTSIZE', (0, 0), (-1, -1), 16),
                    ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                    ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                    ('BOX', (0, 0), (-1, -1), 1, t["line_color"]),
                    ('BACKGROUND', (0, 0), (-1, -1), t["light_gray"]),
                ]))
                row.append(cell)
                if len(row) == grid_cols:
                    cells.append(row)
                    row = []
            if row:
                while len(row) < grid_cols:
                    row.append("")
                cells.append(row)
            if cells:
                sticker_table = Table(cells, colWidths=[(CONTENT_WIDTH - 4 * mm) / grid_cols] * grid_cols)
                sticker_table.setStyle(TableStyle([
                    ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                    ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                    ('GRID', (0, 0), (-1, -1), 0.5, t["line_color"]),
                    ('TOPPADDING', (0, 0), (-1, -1), 2 * mm),
                    ('BOTTOMPADDING', (0, 0), (-1, -1), 2 * mm),
                ]))
                elements.append(sticker_table)
        else:
            for j, task in enumerate(bp_tasks):
                q = task.get("question", "")
                answer_style = ParagraphStyle(
                    'BonusTask', fontName=FONT, fontSize=12,
                    leading=17, spaceAfter=8 * mm, leftIndent=6 * mm,
                    textColor=black
                )
                elements.append(Paragraph(q, answer_style))
                if task.get("answer_space"):
                    ans_box = Table([[""]], colWidths=[CONTENT_WIDTH * 0.8], rowHeights=[20 * mm])
                    ans_box.setStyle(TableStyle([
                        ('BOX', (0, 0), (-1, -1), 1, t["line_color"]),
                        ('BACKGROUND', (0, 0), (-1, -1), "#fafafa"),
                    ]))
                    elements.append(ans_box)
                elements.append(Spacer(1, 6 * mm))

        elements.append(PageBreak())


def _build_answers(elements, answers_data, styles, t, lang, pack_data=None):
    uk = _is_uk(lang)
    if not answers_data:
        return

    mascot = (pack_data or {}).get("_mascot")
    child_name = (pack_data or {}).get("child_name", "")

    if mascot:
        try:
            from core.mascot import get_answers_heading
            heading = get_answers_heading(mascot, child_name, lang)
            heading_style = ParagraphStyle(
                'MascotAnswerHeading', fontName=FONT_BOLD, fontSize=13,
                leading=18, spaceAfter=3 * mm, textColor=t["accent"]
            )
            elements.append(Paragraph(heading, heading_style))
        except ImportError:
            pass

    ans_title = "Відповіді" if uk else "Ответы"
    elements.append(Paragraph(ans_title, styles['PageTitle']))
    elements.append(Spacer(1, 3 * mm))
    disp = (
        "Відповіді призначені тільки для перевірки дорослим."
        if uk else "Ответы предназначены только для проверки взрослым."
    )
    elements.append(Paragraph(disp, styles['Instruction']))
    elements.append(Spacer(1, 4 * mm))

    # Build a unified table
    table_data = []
    
    # Header row
    h1 = "Сторінка" if uk else "Страница"
    h2 = "Завдання" if uk else "Задание"
    h3 = "Відповідь" if uk else "Ответ"
    table_data.append([h1, h2, h3])

    has_rows = False
    for block in answers_data:
        an = block.get("page_number", "")
        answers_list = block.get("answers", [])
        if answers_list:
            for k, a in enumerate(answers_list):
                has_rows = True
                table_data.append([str(an), str(k + 1), str(a) if a else "—"])

    if has_rows:
        ans_table = Table(table_data, colWidths=[25 * mm, 25 * mm, CONTENT_WIDTH - 50 * mm])
        ans_table.setStyle(TableStyle([
            ('FONTNAME', (0, 0), (-1, 0), FONT_BOLD),
            ('FONTNAME', (0, 1), (-1, -1), FONT),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('TEXTCOLOR', (0, 0), (-1, 0), white),
            ('BACKGROUND', (0, 0), (-1, 0), t["brand"]),
            ('TEXTCOLOR', (0, 1), (-1, -1), t["dark_gray"]),
            ('GRID', (0, 0), (-1, -1), 0.5, t["line_color"]),
            ('ALIGN', (0, 0), (1, -1), 'CENTER'),
            ('ALIGN', (2, 0), (2, -1), 'LEFT'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('TOPPADDING', (0, 0), (-1, -1), 3),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 3),
        ]))
        elements.append(ans_table)

    elements.append(Spacer(1, 4 * mm))
    elements.append(Spacer(1, 2 * mm))

    disclaimer = DISCLAIMER_TEXT_UK if uk else DISCLAIMER_TEXT_RU
    elements.append(Paragraph(disclaimer, styles['Disclaimer']))


# ─── Main render function ────────────────────────────────────────────────────

def render_pdf(pack_data: Dict[str, Any], output_path: str,
               watermark: str = "", is_commercial: bool = False,
               brand: str = "", theme: str = "") -> str:
    """Render a complete premium PDF workbook from pack_data dict."""
    theme_id = theme or pack_data.get("style", "")
    if not theme_id or theme_id not in THEMES:
        pack_type = pack_data.get("pack_type", "")
        theme_id = SUBJECT_THEMES.get(pack_type, "print_bw")
    if theme_id not in THEMES:
        theme_id = "print_bw"
    styles = _get_styles(theme_id)
    t = _get_theme(theme_id)

    try:
        pack = StudyPack(**pack_data)
    except Exception as e:
        logger.warning(f"Pydantic validation failed: {e}, using raw dict")
        pack = None

    lang = pack_data.get("language", "uk")
    child_name = pack_data.get("child_name", "")
    difficulty = pack_data.get("difficulty", "easy")
    topic = pack_data.get("topic", "general")
    pages_data = pack_data.get("pages", [])
    answers_data = pack_data.get("answers", [])
    parent_instruction = pack_data.get("parent_instruction", "")

    bonus_pages_list = pack_data.get("_bonus_pages", [])
    gamification = pack_data.get("_gamification", {})
    total_pages = (
        1  # cover
        + (1 if parent_instruction else 0)  # parent instruction
        + len([p for p in pages_data if p.get("page_type") != "answers"])  # exercises
        + len(bonus_pages_list)  # bonus pages
        + (1 if gamification else 0)  # achievements page
        + 1  # tracker
        + 1  # final / well done
        + 1  # certificate
        + (1 if answers_data else 0)  # answers
    )

    wc = _WatermarkCanvas(
        watermark=watermark or ("" if is_commercial else "Демо-набір StudyPack AI"),
        is_commercial=is_commercial,
        brand=brand,
        total_pages=total_pages,
        lang=lang,
        child_name=child_name,
        difficulty=difficulty,
        topic=topic,
    )

    doc = BaseDocTemplate(
        output_path,
        pagesize=A4,
        leftMargin=MARGIN,
        rightMargin=MARGIN,
        topMargin=MARGIN,
        bottomMargin=MARGIN + 8 * mm,
    )

    frame = Frame(
        MARGIN, MARGIN + 8 * mm,
        CONTENT_WIDTH,
        PAGE_HEIGHT - 2 * MARGIN - 8 * mm,
        id='normal'
    )

    doc.addPageTemplates([
        PageTemplate(id='First', frames=frame, onPage=wc.first_page),
        PageTemplate(id='Later', frames=frame, onPage=wc.later_pages),
    ])

    elements = []

    # 1. Cover
    _build_cover(elements, pack_data, styles, t, is_commercial, watermark, brand, lang)

    # 2. Parent instruction
    if parent_instruction:
        _build_parent_page(elements, pack_data, styles, t, lang)

    # 3. Exercise pages
    _build_exercise_pages(elements, pages_data, styles, t, lang, difficulty)

    # 4. Bonus pages (sticker rewards, coloring, maze, secret code)
    _build_bonus_pages(elements, pack_data, styles, t, lang)
    
    # 5. Achievements page (XP, stars, badges)
    _build_achievements_page(elements, pack_data, styles, t, lang)

    # 6. Progress tracker
    _build_tracker_page(elements, pages_data, styles, t, lang)

    # 7. Final "well done" page
    _build_final_page(elements, styles, t, lang)

    # 8. Certificate of completion
    _build_certificate(elements, pack_data, styles, t, lang, child_name)

    # 9. Answers
    _build_answers(elements, answers_data, styles, t, lang, pack_data)

    # 10. Parent analytics report
    _build_parent_report_page(elements, pack_data, styles, t, lang)

    doc.build(elements)
    logger.info(f"PDF saved: {output_path} ({os.path.getsize(output_path)} bytes)")
    return output_path
