import json
import os
from typing import Dict, Any


def render_html_preview(pack_data: Dict[str, Any], output_path: str) -> str:
    title = pack_data.get("title", "StudyPack")
    subtitle = pack_data.get("subtitle", "")
    pages = pack_data.get("pages", [])
    answers = pack_data.get("answers", [])
    has_answers = any(a.get("answers") for a in answers)

    html = """<!DOCTYPE html>
<html lang="ru">
<head>
<meta charset="UTF-8">
<title>StudyPack AI - Preview</title>
<style>
* { margin: 0; padding: 0; box-sizing: border-box; }
body { font-family: 'Segoe UI', Arial, sans-serif; background: #f5f5f5; padding: 20px; color: #222; }
.pack { max-width: 800px; margin: 0 auto; }
.page { background: white; border-radius: 8px; box-shadow: 0 2px 8px rgba(0,0,0,0.1); margin-bottom: 20px; padding: 24px; }
.page-header { font-size: 20px; font-weight: 700; color: #1a1a2e; margin-bottom: 8px; }
.page-number { font-size: 12px; color: #999; margin-bottom: 4px; }
.instruction { font-size: 14px; color: #555; margin-bottom: 16px; font-style: italic; }
.task { background: #fafafa; border-left: 3px solid #4CAF50; padding: 12px; margin-bottom: 10px; border-radius: 0 4px 4px 0; }
.task-question { font-size: 14px; margin-bottom: 6px; }
.task-options { font-size: 13px; color: #666; margin-bottom: 4px; }
.task-answer { font-size: 13px; color: #2e7d32; font-weight: 600; margin-top: 4px; }
.answer-space { border-bottom: 1px dashed #ccc; height: 24px; margin-top: 8px; width: 60%; }
.tag { display: inline-block; font-size: 11px; padding: 2px 8px; border-radius: 10px; color: white; margin-right: 6px; }
.tag-math { background: #2196F3; }
.tag-reading { background: #9C27B0; }
.tag-writing { background: #FF9800; }
.tag-logic { background: #4CAF50; }
.tag-english { background: #E91E63; }
.tag-creative { background: #009688; }
.tag-quiz { background: #607D8B; }
.answers-section { background: #fffde7; border: 1px solid #f9e64b; }
.answers-title { font-size: 18px; font-weight: 700; margin-bottom: 12px; }
.answer-block { margin-bottom: 8px; }
.answer-page { font-weight: 600; }
.header { text-align: center; margin-bottom: 20px; }
.header h1 { font-size: 28px; color: #1a1a2e; }
.header p { color: #666; }
</style>
</head>
<body>
<div class="pack">
<div class="header">
<h1>""" + _esc(title) + """</h1>
<p>""" + _esc(subtitle) + """</p>
<p style="font-size:12px;color:#999;margin-top:8px;">""" + _meta(pack_data) + """</p>
</div>
"""

    for page in pages:
        pt = page.get("page_type", "")
        if pt == "answers":
            continue
        pn = page.get("page_number", "")
        html += '<div class="page">'
        html += f'<div class="page-number">Страница {pn}</div>'
        html += f'<div class="page-header">{_esc(page.get("title", ""))}</div>'
        if page.get("instruction"):
            html += f'<div class="instruction">{_esc(page["instruction"])}</div>'
        for task in page.get("tasks", []):
            ttype = task.get("type", "")
            html += '<div class="task">'
            html += f'<span class="tag tag-{ttype}">{ttype}</span>'
            html += f'<div class="task-question">{_esc(task.get("question", ""))}</div>'
            if task.get("options"):
                html += f'<div class="task-options">Варианты: {", ".join(task["options"])}</div>'
            if task.get("answer_space"):
                html += '<div class="answer-space"></div>'
            if task.get("answer"):
                html += f'<div class="task-answer">✓ {_esc(task["answer"])}</div>'
            html += '</div>'
        html += '</div>'

    if has_answers:
        html += '<div class="page answers-section"><div class="answers-title">Ответы</div>'
        for block in answers:
            if block.get("answers"):
                html += f'<div class="answer-block"><span class="answer-page">Страница {block["page_number"]}:</span> '
                html += ', '.join(_esc(a) for a in block["answers"])
                html += '</div>'
        html += '</div>'

    html += "</div></body></html>"

    with open(output_path, "w", encoding="utf-8") as f:
        f.write(html)

    return output_path


def _esc(text: str) -> str:
    return text.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def _meta(pack: dict) -> str:
    parts = []
    if pack.get("age"):
        parts.append(f"Возраст: {pack['age']} лет")
    if pack.get("grade"):
        parts.append(f"Класс: {pack['grade']}")
    if pack.get("language"):
        parts.append(f"Язык: {pack['language']}")
    if pack.get("pages"):
        parts.append(f"Страниц: {len(pack['pages'])}")
    return " | ".join(parts)
