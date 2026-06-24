import os
import logging
from datetime import datetime
from typing import Dict, Any, Optional

from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, PageBreak,
    ListFlowable, ListItem, Table, TableStyle
)
from reportlab.lib.colors import HexColor, black, white
from reportlab.lib import colors

from core.models import StudyPack

logger = logging.getLogger(__name__)

PAGE_WIDTH, PAGE_HEIGHT = A4
MARGIN = 20 * mm


def _get_styles():
    styles = getSampleStyleSheet()

    styles.add(ParagraphStyle(
        name='CoverTitle', fontName='Helvetica-Bold', fontSize=28,
        leading=34, alignment=TA_CENTER, spaceAfter=12 * mm
    ))
    styles.add(ParagraphStyle(
        name='CoverSubtitle', fontName='Helvetica', fontSize=16,
        leading=22, alignment=TA_CENTER, spaceAfter=6 * mm, textColor=HexColor('#555555')
    ))
    styles.add(ParagraphStyle(
        name='CoverDetail', fontName='Helvetica', fontSize=12,
        leading=16, alignment=TA_CENTER, textColor=HexColor('#777777')
    ))
    styles.add(ParagraphStyle(
        name='PageTitle', fontName='Helvetica-Bold', fontSize=18,
        leading=24, spaceAfter=6 * mm
    ))
    styles.add(ParagraphStyle(
        name='Instruction', fontName='Helvetica', fontSize=12,
        leading=16, spaceAfter=4 * mm, textColor=HexColor('#333333')
    ))
    styles.add(ParagraphStyle(
        name='TaskQuestion', fontName='Helvetica', fontSize=12,
        leading=16, spaceAfter=2 * mm, leftIndent=5 * mm
    ))
    styles.add(ParagraphStyle(
        name='AnswerLine', fontName='Helvetica', fontSize=12,
        leading=16, spaceBefore=4 * mm, spaceAfter=8 * mm,
        textColor=HexColor('#333333')
    ))
    styles.add(ParagraphStyle(
        name='Footer', fontName='Helvetica', fontSize=9,
        alignment=TA_CENTER, textColor=HexColor('#999999')
    ))
    styles.add(ParagraphStyle(
        name='AnswerBlock', fontName='Helvetica', fontSize=11,
        leading=15, leftIndent=5 * mm, spaceAfter=2 * mm
    ))
    styles.add(ParagraphStyle(
        name='FinalMessage', fontName='Helvetica-Bold', fontSize=24,
        leading=30, alignment=TA_CENTER, spaceAfter=10 * mm
    ))

    return styles


def _add_page_number(canvas, doc):
    canvas.saveState()
    canvas.setFont('Helvetica', 9)
    canvas.setFillColor(HexColor('#999999'))
    if doc.page > 1:
        canvas.drawCentredString(PAGE_WIDTH / 2, 10 * mm, f"— {doc.page} —")
    canvas.restoreState()


def render_pdf(pack_data: Dict[str, Any], output_path: str) -> str:
    styles = _get_styles()

    pack = StudyPack(**pack_data)

    doc = SimpleDocTemplate(
        output_path,
        pagesize=A4,
        leftMargin=MARGIN,
        rightMargin=MARGIN,
        topMargin=MARGIN,
        bottomMargin=MARGIN + 5 * mm,
    )

    elements = []

    elements.append(Spacer(1, 30 * mm))
    elements.append(Paragraph(pack.title, styles['CoverTitle']))
    elements.append(Spacer(1, 5 * mm))
    elements.append(Paragraph(pack.subtitle, styles['CoverSubtitle']))
    elements.append(Spacer(1, 10 * mm))

    details = []
    if pack.age:
        details.append(f"Возраст: {pack.age} лет" if pack.language == 'ru' else f"Вік: {pack.age} років")
    if pack.grade:
        details.append(f"Класс: {pack.grade}" if pack.language == 'ru' else f"Клас: {pack.grade}")
    if pack.topic:
        details.append(f"Тема: {pack.topic}" if pack.language == 'ru' else f"Тема: {pack.topic}")
    details.append(f"Страниц: {len([p for p in pack.pages if p.page_type != 'answers'])}" if pack.language == 'ru'
                   else f"Сторінок: {len([p for p in pack.pages if p.page_type != 'answers'])}")

    for detail in details:
        elements.append(Paragraph(detail, styles['CoverDetail']))
        elements.append(Spacer(1, 2 * mm))

    cover_desc = (
        "Набор учебных заданий для домашних занятий."
        if pack.language == 'ru'
        else "Набір навчальних завдань для домашніх занять."
    )
    elements.append(Spacer(1, 10 * mm))
    elements.append(Paragraph(cover_desc, styles['CoverDetail']))

    elements.append(PageBreak())

    if pack.parent_instruction:
        inst_title = "Инструкция для родителей" if pack.language == 'ru' else "Інструкція для батьків"
        elements.append(Paragraph(inst_title, styles['PageTitle']))
        elements.append(Spacer(1, 3 * mm))

        instructions = [
            "Занимайтесь 10–20 минут в день.",
            "Не ругайте ребёнка за ошибки — хвалите за попытку.",
            "Делайте перерывы, если ребёнок устал.",
            "Используйте задания как игру, а не как экзамен.",
            "Ответы в конце набора предназначены только для проверки взрослым.",
        ]
        if pack.language == 'uk':
            instructions = [
                "Займайтеся 10–20 хвилин на день.",
                "Не сваріть дитину за помилки — хваліть за спробу.",
                "Робіть перерви, якщо дитина втомилася.",
                "Використовуйте завдання як гру, а не як іспит.",
                "Відповіді в кінці набору призначені тільки для перевірки дорослим.",
            ]

        for inst in instructions:
            elements.append(Paragraph(f"• {inst}", styles['Instruction']))
            elements.append(Spacer(1, 2 * mm))

        elements.append(Spacer(1, 5 * mm))
        disclaimer = (
            "Важно: этот набор — учебный материал. Он не заменяет профессиональную "
            "педагогическую, логопедическую или психологическую помощь."
            if pack.language == 'ru'
            else "Важливо: цей набір — навчальний матеріал. Він не замінює професійну "
                 "педагогічну, логопедичну чи психологічну допомогу."
        )
        elements.append(Paragraph(disclaimer, styles['Instruction']))
        elements.append(PageBreak())

    for page in pack.pages:
        if page.page_type == "answers":
            continue

        elements.append(Paragraph(page.title, styles['PageTitle']))
        if page.instruction:
            elements.append(Paragraph(page.instruction, styles['Instruction']))
            elements.append(Spacer(1, 3 * mm))

        for task in page.tasks:
            q_text = task.question
            if task.options:
                for i, opt in enumerate(task.options):
                    q_text += f"<br/>{'ABCD'[i] if i < 4 else i + 1}) {opt}"
            elements.append(Paragraph(f"<b>{q_text}</b>", styles['TaskQuestion']))

            if task.answer_space:
                elements.append(Spacer(1, 8 * mm))
                line_style = styles['AnswerLine']
                elements.append(Paragraph("_" * 60, line_style))

            elements.append(Spacer(1, 3 * mm))

        elements.append(PageBreak())

    elements.append(Spacer(1, 30 * mm))
    msg = "Молодец! Ты отлично справился!" if pack.language == 'ru' else "Молодець! Ти чудово впорався!"
    elements.append(Paragraph("⭐ " + msg + " ⭐", styles['FinalMessage']))
    elements.append(Spacer(1, 10 * mm))
    finish_text = (
        "Продолжай заниматься, и у тебя всё получится!"
        if pack.language == 'ru'
        else "Продовжуй займатися, і в тебе все вийде!"
    )
    elements.append(Paragraph(finish_text, styles['CoverSubtitle']))
    elements.append(PageBreak())

    if pack.answers:
        ans_title = "Ответы" if pack.language == 'ru' else "Відповіді"
        elements.append(Paragraph(ans_title, styles['PageTitle']))
        elements.append(Spacer(1, 5 * mm))

        for block in pack.answers:
            pn = block.page_number
            elements.append(Paragraph(
                f"<b>{'Страница' if pack.language == 'ru' else 'Сторінка'} {pn}:</b>",
                styles['Instruction']
            ))
            for i, ans in enumerate(block.answers):
                elements.append(Paragraph(f"{i + 1}. {ans}", styles['AnswerBlock']))
            elements.append(Spacer(1, 3 * mm))

    doc.build(elements, onFirstPage=_add_page_number, onLaterPages=_add_page_number)
    logger.info(f"PDF saved: {output_path}")
    return output_path
