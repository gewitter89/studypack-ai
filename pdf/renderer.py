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

TOPIC_ICONS = {}

# ─── Motivational messages (per-page footer) ─────────────────────────────────

MOTIVATIONAL_UK = [
    "Ти молодець! Продовжуй!",
    "Чудово! Так тримати!",
    "Кожне завдання — це перемога!",
    "Ти зростаєш з кожним завданням!",
    "Старання — це вже успіх!",
    "Неймовірно! Ти впораєшся!",
    "Крок за кроком до знань!",
    "Ти — справжня зірка! ★",
]

MOTIVATIONAL_RU = [
    "Ты молодец! Продолжай!",
    "Отлично! Так держать!",
    "Каждое задание — это победа!",
    "Ты растёшь с каждым заданием!",
    "Стараться — это уже успех!",
    "Невероятно! У тебя получится!",
    "Шаг за шагом к знаниям!",
    "Ты — настоящая звезда! ★",
]

# ─── Difficulty stars ─────────────────────────────────────────────────────────

DIFFICULTY_BADGES = {
    "easy": "⭐",
    "medium": "⭐⭐",
    "hard": "⭐⭐⭐",
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

            # ── Name + Date field (top of page) ──
            name_label = "Ім'я" if uk else "Имя"
            date_label = "Дата" if uk else "Дата"
            name_val = self.child_name if self.child_name else "____________________"
            c.setFont(FONT, 9)
            c.setFillColor(HexColor('#AAAAAA'))
            c.drawString(MARGIN, PAGE_HEIGHT - 14 * mm,
                         f"{name_label}: {name_val}     {date_label}: __________")

            # ── Difficulty badge (top right) ──
            badge = DIFFICULTY_BADGES.get(self.difficulty, "")
            if badge:
                c.setFont(FONT, 10)
                c.drawRightString(PAGE_WIDTH - MARGIN, PAGE_HEIGHT - 14 * mm, badge)

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

    # Topic icon (big centered emoji)
    try:
        from core.topic_lexicon import resolve_topic, get_display_name
        resolved_topic = resolve_topic(topic, lang)
        display_topic = get_display_name(topic, lang)
    except ImportError:
        resolved_topic = topic
        display_topic = topic
    icon = ""

    # Cover layout
    elements.append(Spacer(1, 20 * mm))

    # Safe decoration instead of emoji
    icon_style = ParagraphStyle(
        'CoverIcon', fontName=FONT, fontSize=24, textColor=t["cover_stripe"],
        leading=28, alignment=TA_CENTER, spaceAfter=8 * mm
    )
    elements.append(Paragraph("★ ★ ★", icon_style))

    # Title
    elements.append(Paragraph(title, styles['CoverTitle']))
    elements.append(Spacer(1, 2 * mm))

    if subtitle:
        elements.append(Paragraph(subtitle, styles['CoverSubtitle']))
    elements.append(Spacer(1, 8 * mm))

    # Colored stripe separator
    stripe = Table([[""]], colWidths=[CONTENT_WIDTH], rowHeights=[3])
    stripe.setStyle(TableStyle([('BACKGROUND', (0, 0), (-1, -1), t["cover_stripe"])]))
    elements.append(stripe)
    elements.append(Spacer(1, 6 * mm))

    # Cover info table (2 columns: label + value)
    cover_rows = []
    if age:
        label_a = "Вік" if uk else "Возраст"
        val_a = f"{age} {'років' if uk else 'лет'}"
        cover_rows.append([f"{label_a}:", val_a])
    if grade:
        label_g = "Клас" if uk else "Класс"
        cover_rows.append([f"{label_g}:", grade])
    if display_topic:
        label_t = "Тема" if uk else "Тема"
        cover_rows.append([f"{label_t}:", display_topic])
    if difficulty:
        label_d = "Складність" if uk else "Сложность"
        badge = DIFFICULTY_BADGES.get(difficulty, difficulty)
        cover_rows.append([f"{label_d}:", badge])

    exercise_count = len([p for p in pages_data if p.get("page_type") != "answers"])
    label_p = "Сторінок" if uk else "Страниц"
    cover_rows.append([f"{label_p}:", str(exercise_count)])

    if cover_rows:
        info_table = Table(cover_rows, colWidths=[50 * mm, 80 * mm])
        info_table.setStyle(TableStyle([
            ('FONTNAME', (0, 0), (0, -1), FONT_BOLD),
            ('FONTNAME', (1, 0), (1, -1), FONT),
            ('FONTSIZE', (0, 0), (-1, -1), 11),
            ('TEXTCOLOR', (0, 0), (0, -1), t["dark_gray"]),
            ('TEXTCOLOR', (1, 0), (1, -1), t["accent"]),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('TOPPADDING', (0, 0), (-1, -1), 2),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 2),
        ]))
        elements.append(info_table)

    # ── What's Inside list ──
    inside_items = []
    seen_titles = set()
    for page in pages_data:
        p_type = page.get("page_type", "exercise")
        if p_type in ("answers", "instruction"):
            continue
        p_title = page.get("title", "")
        if ":" in p_title:
            p_title = p_title.split(":")[-1].strip()
        p_title_lower = p_title.lower()
        if p_title_lower and p_title_lower not in seen_titles:
            seen_titles.add(p_title_lower)
            inside_items.append(p_title)
            
    if pack_data.get("include_answers", True) or pack_data.get("answers"):
        inside_items.append("відповіді для дорослого" if uk else "ответы для взрослого")

    if inside_items:
        elements.append(Spacer(1, 4 * mm))
        inside_title = "Усередині:" if uk else "Внутри:"
        inside_style_title = ParagraphStyle(
            'CoverInsideTitle', fontName=FONT_BOLD, fontSize=11,
            leading=14, spaceAfter=2 * mm, textColor=t["dark_gray"]
        )
        elements.append(Paragraph(inside_title, inside_style_title))
        
        inside_style_item = ParagraphStyle(
            'CoverInsideItem', fontName=FONT, fontSize=10,
            leading=13, textColor=t["accent"]
        )
        for item in inside_items[:5]:  # limit to 5 items to avoid overflow
            elements.append(Paragraph(f"✓ {item.lower()}", inside_style_item))

    elements.append(Spacer(1, 6 * mm))

    desc = (
        "Навчальний набір для домашніх занять"
        if uk else "Учебный набор для домашних занятий"
    )
    elements.append(Paragraph(desc, styles['CoverDetail']))

    if brand:
        elements.append(Spacer(1, 5 * mm))
        elements.append(Paragraph(brand, styles['CoverBrand']))

    elements.append(Spacer(1, 6 * mm))
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

            elements.append(Paragraph(f"<b>{j + 1}. {q}</b>", styles['TaskQuestion']))
            if opts:
                for i, opt in enumerate(opts):
                    letter = chr(65 + i) if i < 26 else str(i + 1)
                    elements.append(Paragraph(
                        f"&nbsp;&nbsp;&nbsp;{letter}) {opt}",
                        styles['TaskOption']
                    ))
            if has_space:
                elements.append(Spacer(1, 5 * mm))
                line_data = [["____________________________________________"]]
                line_t = Table(line_data, colWidths=[CONTENT_WIDTH - 12 * mm])
                line_t.setStyle(TableStyle([
                    ('TEXTCOLOR', (0, 0), (-1, -1), t["line_color"]),
                    ('FONTSIZE', (0, 0), (-1, -1), 10),
                ]))
                elements.append(line_t)
            elements.append(Spacer(1, 2 * mm))

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
    done_label = "✓" if uk else "✓"

    header = [day_label, "☆"]
    rows = [header]
    for i in range(num_exercises):
        page_title = exercise_pages[i].get("title", f"{day_label} {i+1}")
        short_title = page_title[:30] if len(page_title) > 30 else page_title
        rows.append([short_title, "☐"])

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
    msg = "Молодець! Ти чудово впорався! ★" if uk else "Молодец! Ты отлично справился! ★"
    elements.append(Paragraph(msg, styles['FinalMessage']))
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

    stars = "⭐ ⭐ ⭐ ⭐ ⭐"
    star_style = ParagraphStyle(
        'CertStars', fontName=FONT, fontSize=24,
        leading=30, alignment=TA_CENTER, spaceAfter=8 * mm
    )
    elements.append(Spacer(1, 4 * mm))
    elements.append(Paragraph(stars, star_style))

    date_str = datetime.now().strftime("%d.%m.%Y")
    date_text = f"{'Дата' if uk else 'Дата'}: {date_str}"
    elements.append(Paragraph(date_text, styles['CertBody']))

    elements.append(Spacer(1, 8 * mm))
    elements.append(stripe)
    elements.append(PageBreak())


# ─── Answers section ─────────────────────────────────────────────────────────

def _build_answers(elements, answers_data, styles, t, lang):
    uk = _is_uk(lang)
    if not answers_data:
        return

    ans_title = "Відповіді" if uk else "Ответы"
    elements.append(Paragraph(ans_title, styles['PageTitle']))
    elements.append(Spacer(1, 3 * mm))
    disp = (
        "Відповіді призначені тільки для перевірки дорослим."
        if uk else "Ответы предназначены только для проверки взрослым."
    )
    elements.append(Paragraph(disp, styles['Instruction']))
    elements.append(Spacer(1, 2 * mm))

    for block in answers_data:
        an = block.get("page_number", "")
        answers_list = block.get("answers", [])
        label_s = "Сторінка" if uk else "Страница"
        elements.append(Paragraph(
            f"<b>{label_s} {an}:</b>", styles['AnswerBlock']
        ))

        # Build answer rows as a small table (visual answer key)
        if answers_list:
            ans_rows = []
            for k, a in enumerate(answers_list):
                ans_rows.append([f"{k + 1}.", str(a) if a else "—"])
            ans_table = Table(ans_rows, colWidths=[8 * mm, CONTENT_WIDTH - 20 * mm])
            ans_table.setStyle(TableStyle([
                ('FONTNAME', (0, 0), (0, -1), FONT_BOLD),
                ('FONTNAME', (1, 0), (1, -1), FONT),
                ('FONTSIZE', (0, 0), (-1, -1), 10),
                ('TEXTCOLOR', (0, 0), (0, -1), t["accent"]),
                ('TEXTCOLOR', (1, 0), (1, -1), t["dark_gray"]),
                ('TOPPADDING', (0, 0), (-1, -1), 1),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 1),
                ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ]))
            elements.append(ans_table)

        elements.append(Spacer(1, 2 * mm))

    elements.append(_separator(t))
    elements.append(Spacer(1, 2 * mm))

    disclaimer = DISCLAIMER_TEXT_UK if uk else DISCLAIMER_TEXT_RU
    elements.append(Paragraph(disclaimer, styles['Disclaimer']))


# ─── Main render function ────────────────────────────────────────────────────

def render_pdf(pack_data: Dict[str, Any], output_path: str,
               watermark: str = "", is_commercial: bool = False,
               brand: str = "", theme: str = "print_bw") -> str:
    """Render a complete premium PDF workbook from pack_data dict."""
    theme_id = theme or pack_data.get("style", "print_bw")
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

    # Estimate total pages for "page X of N" footer
    total_pages = (
        1  # cover
        + (1 if parent_instruction else 0)  # parent instruction
        + len([p for p in pages_data if p.get("page_type") != "answers"])  # exercises
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

    # 4. Progress tracker
    _build_tracker_page(elements, pages_data, styles, t, lang)

    # 5. Final "well done" page
    _build_final_page(elements, styles, t, lang)

    # 6. Certificate of completion
    _build_certificate(elements, pack_data, styles, t, lang, child_name)

    # 7. Answers
    _build_answers(elements, answers_data, styles, t, lang)

    doc.build(elements)
    logger.info(f"PDF saved: {output_path} ({os.path.getsize(output_path)} bytes)")
    return output_path
