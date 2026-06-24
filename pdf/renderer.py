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
from reportlab.pdfgen import canvas

from core.models import StudyPack

logger = logging.getLogger(__name__)

PAGE_WIDTH, PAGE_HEIGHT = A4
MARGIN = 22 * mm
WATERMARK_TEXT = "Демо-набір StudyPack AI"

BRAND_COLOR = HexColor('#2E5090')
LIGHT_GRAY = HexColor('#F0F0F0')
MED_GRAY = HexColor('#CCCCCC')
DARK_GRAY = HexColor('#444444')
ANSWER_LINE_COLOR = HexColor('#BBBBBB')
ACCENT_COLOR = HexColor('#3A7BD5')

DISCLAIMER_TEXT = (
    "Матеріал є додатковим навчальним ресурсом і не замінює "
    "консультацію педагога, логопеда, психолога або лікаря."
)


def _get_styles():
    styles = getSampleStyleSheet()

    styles.add(ParagraphStyle(
        name='CoverTitle', fontName='Helvetica-Bold', fontSize=30,
        leading=38, alignment=TA_CENTER, spaceAfter=8 * mm,
        textColor=BRAND_COLOR
    ))
    styles.add(ParagraphStyle(
        name='CoverSubtitle', fontName='Helvetica', fontSize=16,
        leading=22, alignment=TA_CENTER, spaceAfter=4 * mm,
        textColor=HexColor('#555555')
    ))
    styles.add(ParagraphStyle(
        name='CoverDetail', fontName='Helvetica', fontSize=11,
        leading=15, alignment=TA_CENTER, textColor=HexColor('#777777'),
        spaceAfter=1.5 * mm
    ))
    styles.add(ParagraphStyle(
        name='CoverBrand', fontName='Helvetica-Bold', fontSize=10,
        leading=14, alignment=TA_CENTER, textColor=HexColor('#AAAAAA'),
        spaceBefore=10 * mm
    ))
    styles.add(ParagraphStyle(
        name='PageTitle', fontName='Helvetica-Bold', fontSize=20,
        leading=26, spaceBefore=2 * mm, spaceAfter=4 * mm,
        textColor=BRAND_COLOR
    ))
    styles.add(ParagraphStyle(
        name='Instruction', fontName='Helvetica', fontSize=11,
        leading=15, spaceAfter=3 * mm, textColor=HexColor('#444444'),
        leftIndent=3 * mm
    ))
    styles.add(ParagraphStyle(
        name='TaskQuestion', fontName='Helvetica', fontSize=12,
        leading=17, spaceAfter=1 * mm, leftIndent=6 * mm,
        textColor=black
    ))
    styles.add(ParagraphStyle(
        name='TaskOption', fontName='Helvetica', fontSize=11,
        leading=15, leftIndent=10 * mm, textColor=HexColor('#333333'),
        spaceAfter=0.5 * mm
    ))
    styles.add(ParagraphStyle(
        name='TaskAnswer', fontName='Helvetica', fontSize=11,
        leading=15, leftIndent=6 * mm, textColor=ACCENT_COLOR,
        spaceBefore=2 * mm, spaceAfter=4 * mm
    ))
    styles.add(ParagraphStyle(
        name='Footer', fontName='Helvetica', fontSize=8,
        alignment=TA_CENTER, textColor=HexColor('#AAAAAA')
    ))
    styles.add(ParagraphStyle(
        name='AnswerBlockTitle', fontName='Helvetica-Bold', fontSize=14,
        leading=18, spaceBefore=4 * mm, spaceAfter=3 * mm,
        textColor=BRAND_COLOR
    ))
    styles.add(ParagraphStyle(
        name='AnswerBlock', fontName='Helvetica', fontSize=11,
        leading=16, leftIndent=6 * mm, spaceAfter=1.5 * mm
    ))
    styles.add(ParagraphStyle(
        name='FinalMessage', fontName='Helvetica-Bold', fontSize=26,
        leading=34, alignment=TA_CENTER, spaceAfter=6 * mm,
        textColor=BRAND_COLOR
    ))
    styles.add(ParagraphStyle(
        name='Disclaimer', fontName='Helvetica-Oblique', fontSize=8,
        leading=11, alignment=TA_CENTER, textColor=HexColor('#AAAAAA'),
        spaceBefore=3 * mm
    ))
    styles.add(ParagraphStyle(
        name='SectionRule', fontName='Helvetica-Bold', fontSize=13,
        leading=17, spaceBefore=3 * mm, spaceAfter=2 * mm,
        textColor=HexColor('#666666')
    ))
    styles.add(ParagraphStyle(
        name='ParentInst', fontName='Helvetica', fontSize=11,
        leading=16, leftIndent=4 * mm, spaceAfter=2 * mm,
        textColor=HexColor('#333333')
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
            c.setFont('Helvetica', 36)
            c.setFillColor(HexColor('#E0E0E0'))
            c.translate(PAGE_WIDTH / 2, PAGE_HEIGHT / 2)
            c.rotate(45)
            c.drawCentredString(0, 0, self.watermark)
        if doc.page > 1:
            c.setFont('Helvetica', 7)
            c.setFillColor(HexColor('#BBBBBB'))
            c.drawCentredString(PAGE_WIDTH / 2, 8 * mm, f"— {doc.page} —")
            if self.brand and not self.is_commercial:
                c.setFont('Helvetica', 6)
                c.drawRightString(PAGE_WIDTH - MARGIN, 8 * mm, self.brand)
        c.restoreState()

    def first_page(self, c: canvas.Canvas, doc):
        self.add_watermark(c, doc)

    def later_pages(self, c: canvas.Canvas, doc):
        self.add_watermark(c, doc)


def render_pdf(pack_data: Dict[str, Any], output_path: str,
               watermark: str = "", is_commercial: bool = False,
               brand: str = "") -> str:
    styles = _get_styles()
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
    sep.setStyle(TableStyle([('BACKGROUND', (0,0), (-1,-1), MED_GRAY)]))
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
        sep2.setStyle(TableStyle([('BACKGROUND', (0,0), (-1,-1), MED_GRAY)]))
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
        sep3.setStyle(TableStyle([('BACKGROUND', (0,0), (-1,-1), LIGHT_GRAY)]))
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
                    ('TEXTCOLOR', (0,0), (-1,-1), ANSWER_LINE_COLOR),
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
        sep4.setStyle(TableStyle([('BACKGROUND', (0,0), (-1,-1), MED_GRAY)]))
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
