import os
import logging
from datetime import datetime
from typing import Dict, Any, Optional

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

logger = logging.getLogger(__name__)

PAGE_WIDTH, PAGE_HEIGHT = A4
MARGIN = 22 * mm
WATERMARK_TEXT = "Демо-набір StudyPack AI"

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
    },
}

DISCLAIMER_TEXT = (
    "Матеріал є додатковим навчальним ресурсом і не замінює "
    "консультацію педагога, логопеда, психолога або лікаря."
)


def _get_theme(theme_id: str = "print_bw") -> dict:
    return THEMES.get(theme_id, THEMES["print_bw"])


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
    return styles


class _WatermarkCanvas:
    def __init__(self, watermark: str = "", is_commercial: bool = False,
                 brand: str = ""):
        self.watermark = watermark
        self.is_commercial = is_commercial
        self.brand = brand

    def add_watermark(self, c: canvas.Canvas, doc):
        c.saveState()
        if not self.is_commercial and self.watermark:
            c.setFont(FONT, 36)
            c.setFillColor(HexColor('#E0E0E0'))
            c.translate(PAGE_WIDTH / 2, PAGE_HEIGHT / 2)
            c.rotate(45)
            c.drawCentredString(0, 0, self.watermark)
        if doc.page > 1:
            c.setFont(FONT, 7)
            c.setFillColor(HexColor('#BBBBBB'))
            c.drawCentredString(PAGE_WIDTH / 2, 8 * mm, f"— {doc.page} —")
            if self.brand and not self.is_commercial:
                c.setFont(FONT, 6)
                c.drawRightString(PAGE_WIDTH - MARGIN, 8 * mm, self.brand)
        c.restoreState()

    def first_page(self, c: canvas.Canvas, doc):
        self.add_watermark(c, doc)

    def later_pages(self, c: canvas.Canvas, doc):
        self.add_watermark(c, doc)


def render_pdf(pack_data: Dict[str, Any], output_path: str,
               watermark: str = "", is_commercial: bool = False,
               brand: str = "", theme: str = "print_bw") -> str:
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

    wc = _WatermarkCanvas(watermark or WATERMARK_TEXT, is_commercial, brand)

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
        PAGE_WIDTH - 2 * MARGIN,
        PAGE_HEIGHT - 2 * MARGIN - 8 * mm,
        id='normal'
    )

    doc.addPageTemplates([
        PageTemplate(id='First', frames=frame, onPage=wc.first_page),
        PageTemplate(id='Later', frames=frame, onPage=wc.later_pages),
    ])

    elements = []

    title = pack_data.get("title", "StudyPack")
    subtitle = pack_data.get("subtitle", "")
    lang = pack_data.get("language", "uk")
    age = pack_data.get("age", "")
    grade = pack_data.get("grade", "")
    topic = pack_data.get("topic", "")
    pack_type = pack_data.get("pack_type", "")
    pages_data = pack_data.get("pages", [])
    answers_data = pack_data.get("answers", [])
    parent_instruction = pack_data.get("parent_instruction", "")

    elements.append(Spacer(1, 25 * mm))
    elements.append(Paragraph(title, styles['CoverTitle']))
    elements.append(Spacer(1, 3 * mm))
    if subtitle:
        elements.append(Paragraph(subtitle, styles['CoverSubtitle']))
    elements.append(Spacer(1, 10 * mm))

    cover_lines = []
    if age:
        label_a = "Вік" if lang in ("uk", "uk+en") else "Возраст"
        cover_lines.append(f"{label_a}: {age} {('років' if lang in ('uk','uk+en') else 'лет')}")
    if grade:
        label_g = "Клас" if lang in ("uk", "uk+en") else "Класс"
        cover_lines.append(f"{label_g}: {grade}")
    if topic:
        label_t = "Тема" if lang in ("uk", "uk+en") else "Тема"
        cover_lines.append(f"{label_t}: {topic}")
    label_p = "Сторінок" if lang in ("uk", "uk+en") else "Страниц"
    exercise_count = len([p for p in pages_data if p.get("page_type") != "answers"])
    cover_lines.append(f"{label_p}: {exercise_count}")

    for line in cover_lines:
        elements.append(Paragraph(line, styles['CoverDetail']))

    elements.append(Spacer(1, 8 * mm))
    desc = (
        "Навчальний набір для домашніх занять"
        if lang in ("uk", "uk+en")
        else "Учебный набор для домашних занятий"
    )
    elements.append(Paragraph(desc, styles['CoverDetail']))

    if brand:
        elements.append(Spacer(1, 5 * mm))
        elements.append(Paragraph(brand, styles['CoverBrand']))

    sep =Table([[""]],colWidths=[PAGE_WIDTH - 2 * MARGIN],rowHeights=[0.5])
    sep.setStyle(TableStyle([('BACKGROUND', (0,0), (-1,-1), t["med_gray"])]))
    elements.append(Spacer(1, 8 * mm))
    elements.append(sep)

    if not is_commercial and watermark:
        demo_note = (
            "ДЕМО-ВЕРСІЯ | Для комерційного використання звертайтеся до автора"
            if lang in ("uk", "uk+en")
            else "ДЕМО-ВЕРСИЯ | Для коммерческого использования обратитесь к автору"
        )
        elements.append(Spacer(1, 3 * mm))
        elements.append(Paragraph(demo_note, styles['CoverBrand']))

    elements.append(PageBreak())

    if parent_instruction:
        inst_title = "Інструкція для батьків" if lang in ("uk", "uk+en") else "Инструкция для родителей"
        elements.append(Paragraph(inst_title, styles['PageTitle']))
        elements.append(Spacer(1, 2 * mm))

        bullets = [
            ("Займайтеся 10–20 хвилин на день." if lang in ("uk", "uk+en") else "Занимайтесь 10–20 минут в день."),
            ("Не сваріть дитину за помилки — хваліть за спробу." if lang in ("uk", "uk+en") else "Не ругайте ребёнка за ошибки — хвалите за попытку."),
            ("Робіть перерви, якщо дитина втомилася." if lang in ("uk", "uk+en") else "Делайте перерывы, если ребёнок устал."),
            ("Використовуйте завдання як гру, а не як іспит." if lang in ("uk", "uk+en") else "Используйте задания как игру, а не как экзамен."),
            ("Відповіді в кінці — тільки для перевірки дорослим." if lang in ("uk", "uk+en") else "Ответы в конце — только для проверки взрослым."),
        ]
        for b in bullets:
            elements.append(Paragraph(f"•  {b}", styles['ParentInst']))
            elements.append(Spacer(1, 1 * mm))

        disclaimer = (
            DISCLAIMER_TEXT if lang in ("uk", "uk+en")
            else "Материал является дополнительным учебным ресурсом и не заменяет "
                 "консультацию педагога, логопеда, психолога или врача."
        )
        elements.append(Spacer(1, 4 * mm))
        sep2 = Table([[""]], colWidths=[PAGE_WIDTH - 2 * MARGIN], rowHeights=[0.3])
        sep2.setStyle(TableStyle([('BACKGROUND', (0,0), (-1,-1), t["med_gray"])]))
        elements.append(sep2)
        elements.append(Spacer(1, 2 * mm))
        elements.append(Paragraph(disclaimer, styles['Disclaimer']))
        elements.append(PageBreak())

    # Exercise pages
    for page in pages_data:
        if page.get("page_type") == "answers":
            continue
        pn = page.get("page_number", "")
        title_text = page.get("title", "")
        instruction = page.get("instruction", "")
        tasks = page.get("tasks", [])

        elements.append(Paragraph(title_text, styles['PageTitle']))
        if instruction:
            elements.append(Paragraph(instruction, styles['Instruction']))

        # Decorative separator
        sep3 = Table([[""]], colWidths=[PAGE_WIDTH - 2 * MARGIN - 6 * mm], rowHeights=[0.3])
        sep3.setStyle(TableStyle([('BACKGROUND', (0,0), (-1,-1), t["light_gray"])]))
        elements.append(sep3)
        elements.append(Spacer(1, 2 * mm))

        for j, task in enumerate(tasks):
            q = task.get("question", "")
            opts = task.get("options") or []
            ans = task.get("answer", "")
            has_space = task.get("answer_space", True)
            ttype = task.get("type", "")

            elements.append(Paragraph(f"<b>{j + 1}. {q}</b>", styles['TaskQuestion']))
            if opts:
                for i, opt in enumerate(opts):
                    letter = chr(65 + i) if i < 26 else str(i + 1)
                    elements.append(Paragraph(
                        f"&nbsp;&nbsp;&nbsp;{letter}) {opt}",
                        styles['TaskOption']
                    ))
            if has_space:
                elements.append(Spacer(1, 7 * mm))
                line_data = [["____________________________________________"]]
                line_t = Table(line_data, colWidths=[PAGE_WIDTH - 2 * MARGIN - 12 * mm])
                line_t.setStyle(TableStyle([
                    ('TEXTCOLOR', (0,0), (-1,-1), t["line_color"]),
                    ('FONTSIZE', (0,0), (-1,-1), 10),
                ]))
                elements.append(line_t)
            elements.append(Spacer(1, 2 * mm))

        elements.append(PageBreak())

    # Final page
    elements.append(Spacer(1, 30 * mm))
    msg = (
        "Молодець! Ти чудово впорався! \u2605"
        if lang in ("uk", "uk+en")
        else "Молодец! Ты отлично справился! \u2605"
    )
    elements.append(Paragraph(msg, styles['FinalMessage']))
    elements.append(Spacer(1, 8 * mm))
    finish = (
        "Продовжуй займатися, і в тебе все вийде!"
        if lang in ("uk", "uk+en")
        else "Продолжай заниматься, и у тебя всё получится!"
    )
    elements.append(Paragraph(finish, styles['CoverSubtitle']))
    elements.append(PageBreak())

    # Answers
    if answers_data:
        ans_title = "Відповіді" if lang in ("uk", "uk+en") else "Ответы"
        elements.append(Paragraph(ans_title, styles['PageTitle']))
        elements.append(Spacer(1, 3 * mm))
        disp = (
            "Відповіді призначені тільки для перевірки дорослим."
            if lang in ("uk", "uk+en")
            else "Ответы предназначены только для проверки взрослым."
        )
        elements.append(Paragraph(disp, styles['Instruction']))
        elements.append(Spacer(1, 2 * mm))

        for block in answers_data:
            an = block.get("page_number", "")
            answers_list = block.get("answers", [])
            label_s = "Сторінка" if lang in ("uk", "uk+en") else "Страница"
            elements.append(Paragraph(
                f"<b>{label_s} {an}:</b>", styles['AnswerBlock']
            ))
            for k, a in enumerate(answers_list):
                elements.append(Paragraph(
                    f"{k + 1}. {a}", styles['AnswerBlock']
                ))
            elements.append(Spacer(1, 1.5 * mm))

        sep4 = Table([[""]], colWidths=[PAGE_WIDTH - 2 * MARGIN], rowHeights=[0.3])
        sep4.setStyle(TableStyle([('BACKGROUND', (0,0), (-1,-1), t["med_gray"])]))
        elements.append(sep4)
        elements.append(Spacer(1, 2 * mm))

    disclaimer_text = (
        DISCLAIMER_TEXT if lang in ("uk", "uk+en")
        else "Материал является дополнительным учебным ресурсом и не заменяет "
             "консультацию педагога, логопеда, психолога или врача."
    )
    elements.append(Paragraph(disclaimer_text, styles['Disclaimer']))

    doc.build(elements)
    logger.info(f"PDF saved: {output_path} ({os.path.getsize(output_path)} bytes)")
    return output_path
