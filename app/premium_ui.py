import json
import os
import sys
import threading
import webbrowser
from datetime import datetime
from tkinter import messagebox as tkmsg
from typing import Optional

import customtkinter as ctk

from core.models import PackRequest
from core.generator import StudyPackGenerator
from core.math_checker import verify_math_in_pack
from core.templates import generate_offline
from core.card_generator import generate_from_preset
from core.preset_loader import load_preset, list_presets, find_best_preset, preset_to_request
from core.postprocess import postprocess
from core.paths import output_dir, ensure_dirs, logs_dir
from pdf.renderer import render_pdf
from pdf.preview import render_html_preview
from config.settings_loader import load_settings
from config.topics_loader import load_topics
from core.updater import VERSION

ctk.set_appearance_mode("Light")
ctk.set_default_color_theme("blue")

FONT = ("Segoe UI", 13)
FONT_BOLD = ("Segoe UI", 13, "bold")
FONT_SMALL = ("Segoe UI", 11)
FONT_TITLE = ("Segoe UI", 18, "bold")
FONT_HEADER = ("Segoe UI", 15, "bold")

COLOR_BG = "#F3F7FB"
COLOR_CARD = "#FFFFFF"
COLOR_PRIMARY = "#2563EB"
COLOR_TEXT = "#111827"
COLOR_SECONDARY = "#6B7280"
COLOR_GREEN = "#22C55E"
COLOR_RED = "#EF4444"
COLOR_BORDER = "#E5E7EB"
COLOR_ACCENT = "#FACC15"

CARD_PAD = 15
CORNER_RADIUS = 10


class PremiumStudyPackUI:
    def __init__(self):
        self.settings = load_settings()
        self.topics = load_topics()
        self.last_pdf_path: Optional[str] = None
        self.last_json_path: Optional[str] = None
        self.last_pack_data: Optional[dict] = None
        self._build_ui()
        
        self._check_first_run()
        self._check_for_updates_silently()

    def _check_first_run(self):
        user_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "user_data")
        welcome_flag = os.path.join(user_dir, ".welcome_done")
        if not os.path.exists(welcome_flag):
            self.root.after(300, self._show_welcome)

    def _show_welcome(self):
        win = ctk.CTkToplevel(self.root)
        win.title("StudyPack AI")
        win.geometry("520x400")
        win.resizable(False, False)
        win.transient(self.root)
        win.grab_set()

        frame = ctk.CTkFrame(win, fg_color=COLOR_CARD, corner_radius=12)
        frame.pack(fill="both", expand=True, padx=15, pady=15)

        ctk.CTkLabel(frame, text="StudyPack AI", font=FONT_TITLE,
                     text_color=COLOR_PRIMARY).pack(pady=(20, 4))
        ctk.CTkLabel(frame, text="Создавайте PDF-наборы заданий для детей\nза несколько минут",
                     font=FONT, text_color=COLOR_SECONDARY).pack(pady=(0, 15))

        for line in [
            "✓ Работайте в офлайн-режиме без API",
            "✓ Подключите AI через OpenRouter",
            "✓ Создавайте PDF для печати на A4",
            "✓ Используйте готовые примеры",
            "✓ Наборы на любую тему: динозавры, космос и т.д.",
        ]:
            ctk.CTkLabel(frame, text=line, font=FONT, text_color=COLOR_TEXT,
                         anchor="w").pack(padx=20, pady=1, anchor="w")

        ctk.CTkLabel(frame, text="",
                     font=FONT_SMALL, text_color=COLOR_SECONDARY).pack(pady=5)

        btn_frame = ctk.CTkFrame(frame, fg_color="transparent")
        btn_frame.pack(pady=15)

        user_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "user_data")
        os.makedirs(user_dir, exist_ok=True)

        def dismiss():
            with open(os.path.join(user_dir, ".welcome_done"), "w") as f:
                f.write("1")
            win.destroy()

        def open_examples_from_welcome():
            dismiss()
            self._open_examples_folder()

        ctk.CTkButton(btn_frame, text="Создать первый набор", command=dismiss,
                      fg_color=COLOR_PRIMARY, font=FONT_BOLD,
                      height=40, width=180).pack(side="left", padx=5)
        ctk.CTkButton(btn_frame, text="Открыть примеры", command=open_examples_from_welcome,
                      fg_color="transparent", border_width=1, border_color=COLOR_BORDER,
                      text_color=COLOR_PRIMARY, font=FONT,
                      height=40, width=150).pack(side="left", padx=5)
        ctk.CTkButton(btn_frame, text="Настроить API", command=dismiss,
                      fg_color="transparent", border_width=1, border_color=COLOR_BORDER,
                      text_color=COLOR_TEXT, font=FONT,
                      height=40, width=150).pack(side="left", padx=5)

    def _build_ui(self):
        self.root = ctk.CTk()
        self.root.title("StudyPack AI")
        self.root.geometry("1180x760")
        self.root.minsize(1100, 720)
        self.root.configure(fg_color=COLOR_BG)
        
        try:
            from PIL import Image, ImageTk
            from core.paths import logo_path
            icon_path = logo_path()
            if os.path.exists(icon_path):
                img = Image.open(icon_path)
                photo = ImageTk.PhotoImage(img)
                self.root.wm_iconphoto(True, photo)
        except Exception as e:
            logger.warning(f"Failed to set window icon: {e}")

        self.root.after(0, lambda: self.root.focus_force())

        # Top bar
        self._build_topbar()

        # Main 3-column layout
        main_row = ctk.CTkFrame(self.root, fg_color="transparent")
        main_row.pack(fill="both", expand=True, padx=10, pady=(0, 5))

        self._build_content_area(main_row)
        self._build_sidebar(main_row)
        self._build_preview_panel(main_row)

        # Bottom status
        self._build_status_bar()

    def _build_topbar(self):
        top = ctk.CTkFrame(self.root, fg_color=COLOR_CARD, height=52, corner_radius=0)
        top.pack(fill="x", padx=0, pady=(0, 0))
        top.pack_propagate(False)

        inner = ctk.CTkFrame(top, fg_color="transparent")
        inner.pack(fill="both", expand=True, padx=15)

        ctk.CTkLabel(inner, text="StudyPack AI", font=FONT_TITLE,
                     text_color=COLOR_PRIMARY).pack(side="left")
        ctk.CTkLabel(inner, text="Генератор PDF-заданий для детей",
                     font=("Segoe UI", 11), text_color=COLOR_SECONDARY).pack(side="left", padx=(8, 0))

        ctk.CTkLabel(inner, text=f"v{VERSION}", font=FONT_SMALL,
                     text_color=COLOR_SECONDARY).pack(side="right", padx=5)
        self.update_btn = ctk.CTkButton(inner, text="Проверить обновления",
                                        font=FONT_SMALL, fg_color="transparent",
                                        border_width=1, border_color=COLOR_BORDER,
                                        text_color=COLOR_SECONDARY, height=28,
                                        command=self._check_for_updates_manually)
        self.update_btn.pack(side="right", padx=5)

    def _build_sidebar(self, parent):
        side = ctk.CTkFrame(parent, fg_color=COLOR_CARD, width=200, corner_radius=CORNER_RADIUS)
        side.pack(side="left", fill="y", padx=(0, 8))
        side.pack_propagate(False)

        try:
            from PIL import Image
            from core.paths import logo_path
            img_path = logo_path()
            if os.path.exists(img_path):
                pil_img = Image.open(img_path)
                aspect = pil_img.height / pil_img.width
                h = int(160 * aspect)
                logo_img = ctk.CTkImage(light_image=pil_img, dark_image=pil_img, size=(160, h))
                logo_label = ctk.CTkLabel(side, image=logo_img, text="")
                logo_label.pack(pady=(12, 8))
            else:
                ctk.CTkLabel(side, text="StudyPack AI", font=FONT_BOLD, text_color=COLOR_TEXT).pack(pady=(12, 6))
        except Exception as e:
            logger.warning(f"Failed to load logo in sidebar: {e}")
            ctk.CTkLabel(side, text="StudyPack AI", font=FONT_BOLD, text_color=COLOR_TEXT).pack(pady=(12, 6))

        self.nav_btns = {}
        nav_items = [
            ("create", "Создать набор", "📋"),
            ("examples", "Примеры", "📂"),
            ("history", "История", "🕐"),
            ("settings", "Настройки", "⚙"),
        ]

        for key, label, icon in nav_items:
            btn = ctk.CTkButton(side, text=f"{icon}  {label}",
                                font=FONT, anchor="w",
                                fg_color="transparent",
                                text_color=COLOR_TEXT,
                                hover_color="#EEF2FF",
                                height=36,
                                command=lambda k=key: self._nav_click(k))
            btn.pack(fill="x", padx=8, pady=1)
            self.nav_btns[key] = btn

        # Sidebar bottom
        ctk.CTkLabel(side, text="", font=FONT_SMALL, text_color=COLOR_SECONDARY).pack(
            side="bottom", pady=8)

        self.side_status_label = ctk.CTkLabel(side, text="●  Готово",
                                              font=FONT_SMALL, text_color=COLOR_GREEN)
        self.side_status_label.pack(side="bottom", pady=(0, 4))

        version_frame = ctk.CTkFrame(side, fg_color="#F0F4F8", corner_radius=8)
        version_frame.pack(side="bottom", fill="x", padx=8, pady=8)
        ctk.CTkLabel(version_frame, text="StudyPack AI", font=("Segoe UI", 9, "bold"),
                     text_color=COLOR_SECONDARY).pack()
        ctk.CTkLabel(version_frame, text="v0.1.0  |  RC 0.1",
                     font=("Segoe UI", 9), text_color=COLOR_SECONDARY).pack()

        # Highlight default nav
        self._nav_click("create")

    def _nav_click(self, key):
        for k, btn in self.nav_btns.items():
            if k == key:
                btn.configure(fg_color="#EEF2FF", text_color=COLOR_PRIMARY)
            else:
                btn.configure(fg_color="transparent", text_color=COLOR_TEXT)
        self._show_page(key)

    def _show_page(self, key):
        for w in self.content_area.winfo_children():
            w.destroy()
        if key == "create":
            self._build_create_page()
        elif key == "examples":
            self._build_examples_page()
        elif key == "history":
            self._build_history_page()
        elif key == "settings":
            self._build_settings_page()

    def _build_content_area(self, parent):
        self.content_area = ctk.CTkScrollableFrame(parent, fg_color="transparent",
                                                    corner_radius=0)
        self.content_area.pack(side="left", fill="both", expand=True, padx=(0, 8))

    def _build_preview_panel(self, parent):
        preview_frame = ctk.CTkFrame(parent, fg_color=COLOR_CARD, width=280,
                                      corner_radius=CORNER_RADIUS)
        preview_frame.pack(side="right", fill="y")
        preview_frame.pack_propagate(False)
        self.preview_frame = preview_frame

        ctk.CTkLabel(preview_frame, text="Ваш набор", font=FONT_BOLD,
                     text_color=COLOR_TEXT).pack(pady=(12, 6))

        self.preview_inner = ctk.CTkFrame(preview_frame, fg_color="transparent")
        self.preview_inner.pack(fill="both", expand=True, padx=10)

        self.preview_labels = {}
        pfields = [
            ("age", "Возраст:"),
            ("grade", "Уровень:"),
            ("language", "Язык:"),
            ("pack_type", "Тип:"),
            ("topic", "Тема:"),
            ("pages", "Страниц:"),
            ("style", "Стиль:"),
            ("answers", "Ответы:"),
            ("offline", "Режим:"),
        ]
        for key, label in pfields:
            row = ctk.CTkFrame(self.preview_inner, fg_color="transparent")
            row.pack(fill="x", pady=2)
            ctk.CTkLabel(row, text=label, font=FONT_SMALL,
                         text_color=COLOR_SECONDARY, width=60, anchor="w").pack(side="left")
            lbl = ctk.CTkLabel(row, text="—", font=FONT_SMALL,
                               text_color=COLOR_TEXT, anchor="w")
            lbl.pack(side="left", padx=(4, 0))
            self.preview_labels[key] = lbl

        sep = ctk.CTkFrame(self.preview_inner, height=1, fg_color=COLOR_BORDER)
        sep.pack(fill="x", pady=8)

        self.preview_result_frame = ctk.CTkFrame(self.preview_inner, fg_color="#F0FDF4",
                                                  corner_radius=8)
        self.preview_result_frame.pack(fill="x", pady=4)
        for txt in ["PDF для печати A4", "Ответы для взрослых",
                     "Инструкция 10-20 мин"]:
            f = ctk.CTkFrame(self.preview_result_frame, fg_color="transparent")
            f.pack(fill="x", padx=8, pady=1)
            ctk.CTkLabel(f, text="✓", text_color=COLOR_GREEN, font=FONT_SMALL).pack(side="left")
            ctk.CTkLabel(f, text=txt, font=FONT_SMALL,
                         text_color="#065F46").pack(side="left", padx=(4, 0))

        ctk.CTkLabel(preview_frame, text="", font=FONT_SMALL).pack()
        ctk.CTkButton(preview_frame, text="Открыть примеры",
                       font=FONT, fg_color="transparent",
                       border_width=1, border_color=COLOR_BORDER,
                       text_color=COLOR_TEXT, height=34,
                       command=self._open_examples_folder).pack(fill="x", padx=10, pady=2)
        self.preview_open_last_btn = ctk.CTkButton(preview_frame, text="Последний PDF",
                                                    font=FONT, fg_color="transparent",
                                                    border_width=1, border_color=COLOR_BORDER,
                                                    text_color=COLOR_TEXT, height=34,
                                                    command=self._open_last_pdf,
                                                    state="disabled")
        self.preview_open_last_btn.pack(fill="x", padx=10, pady=2)
        ctk.CTkButton(preview_frame, text="Открыть папку",
                       font=FONT, fg_color="transparent",
                       border_width=1, border_color=COLOR_BORDER,
                       text_color=COLOR_TEXT, height=34,
                       command=self._open_output).pack(fill="x", padx=10, pady=2)

    def _build_status_bar(self):
        bar = ctk.CTkFrame(self.root, fg_color=COLOR_CARD, height=30, corner_radius=0)
        bar.pack(fill="x")
        bar.pack_propagate(False)

        inner = ctk.CTkFrame(bar, fg_color="transparent")
        inner.pack(fill="both", expand=True, padx=12)

        self.status_var = ctk.StringVar(value="Готов к работе")
        ctk.CTkLabel(inner, textvariable=self.status_var,
                     font=FONT_SMALL, text_color=COLOR_SECONDARY).pack(side="left")

        self.progress = ctk.CTkProgressBar(inner, height=6,
                                            fg_color=COLOR_BORDER,
                                            progress_color=COLOR_PRIMARY,
                                            width=200)
        self.progress.pack(side="right", padx=5)
        self.progress.set(0)

    # ═══════════════════════════════════════════════════════════
    # CREATE PAGE
    # ═══════════════════════════════════════════════════════════

    def _build_create_page(self):
        frame = self.content_area

        # CARD 1: Child
        card1 = ctk.CTkFrame(frame, fg_color=COLOR_CARD, corner_radius=CORNER_RADIUS)
        card1.pack(fill="x", pady=4)

        ctk.CTkLabel(card1, text="1. Параметры ребёнка", font=FONT_HEADER,
                     text_color=COLOR_TEXT).pack(anchor="w", padx=CARD_PAD, pady=(12, 2))
        ctk.CTkLabel(card1, text="Укажите возраст, уровень и язык заданий",
                     font=FONT_SMALL, text_color=COLOR_SECONDARY).pack(
            anchor="w", padx=CARD_PAD, pady=(0, 8))

        row1 = ctk.CTkFrame(card1, fg_color="transparent")
        row1.pack(fill="x", padx=CARD_PAD, pady=3)

        ctk.CTkLabel(row1, text="Возраст:", font=FONT, width=80, anchor="w",
                     text_color=COLOR_TEXT).pack(side="left")
        self.age_var = ctk.StringVar(value="7")

        age_frame = ctk.CTkFrame(row1, fg_color="transparent")
        age_frame.pack(side="left")
        ctk.CTkButton(age_frame, text="−", width=28, height=28,
                      font=("Segoe UI", 16, "bold"), fg_color=COLOR_BORDER,
                      text_color=COLOR_TEXT, hover_color="#D1D5DB",
                      command=lambda: self._adj_age(-1)).pack(side="left")
        self.age_entry = ctk.CTkEntry(age_frame, textvariable=self.age_var,
                                       width=50, height=28,
                                       font=FONT_BOLD, justify="center")
        self.age_entry.pack(side="left", padx=3)
        ctk.CTkButton(age_frame, text="+", width=28, height=28,
                      font=("Segoe UI", 16, "bold"), fg_color=COLOR_BORDER,
                      text_color=COLOR_TEXT, hover_color="#D1D5DB",
                      command=lambda: self._adj_age(1)).pack(side="left")
        self.age_var.trace_add("write", lambda *a: self._update_preview())

        ctk.CTkLabel(row1, text="Класс/уровень:", font=FONT, width=100, anchor="w",
                     text_color=COLOR_TEXT).pack(side="left", padx=(20, 0))
        self.grade_var = ctk.StringVar(value="Дошкольник")
        grades = ["Дошкольник", "1 класс", "2 класс", "3 класс", "4 класс",
                   "Не знаю, подобрать автоматически"]
        ctk.CTkComboBox(row1, variable=self.grade_var, values=grades,
                         width=200, font=FONT, state="readonly",
                         command=lambda _: self._update_preview()).pack(side="left", padx=5)

        row2 = ctk.CTkFrame(card1, fg_color="transparent")
        row2.pack(fill="x", padx=CARD_PAD, pady=3)

        ctk.CTkLabel(row2, text="Язык набора:", font=FONT, width=80, anchor="w",
                     text_color=COLOR_TEXT).pack(side="left")
        self.lang_var = ctk.StringVar(value="Русский")
        langs = ["Русский", "Украинский", "Английский",
                  "Украинский + английский", "Русский + английский"]
        ctk.CTkComboBox(row2, variable=self.lang_var, values=langs,
                         width=200, font=FONT, state="readonly",
                         command=lambda _: self._update_preview()).pack(side="left", padx=5)
        ctk.CTkLabel(card1, text="", font=FONT_SMALL).pack(pady=4)

        # CARD 2: Pack
        card2 = ctk.CTkFrame(frame, fg_color=COLOR_CARD, corner_radius=CORNER_RADIUS)
        card2.pack(fill="x", pady=4)

        ctk.CTkLabel(card2, text="2. Параметры набора", font=FONT_HEADER,
                     text_color=COLOR_TEXT).pack(anchor="w", padx=CARD_PAD, pady=(12, 2))
        ctk.CTkLabel(card2, text="Выберите тип, тему, объём и сложность",
                     font=FONT_SMALL, text_color=COLOR_SECONDARY).pack(
            anchor="w", padx=CARD_PAD, pady=(0, 8))

        r1 = ctk.CTkFrame(card2, fg_color="transparent")
        r1.pack(fill="x", padx=CARD_PAD, pady=3)
        ctk.CTkLabel(r1, text="Тип набора:", font=FONT, width=100, anchor="w",
                     text_color=COLOR_TEXT).pack(side="left")
        self.pack_var = ctk.StringVar(value="Смешанный набор на неделю")
        packs = ["Подготовка к школе", "Математика", "Чтение",
                  "Украинский язык", "Английский", "Логика",
                  "Смешанный набор на неделю"]
        ctk.CTkComboBox(r1, variable=self.pack_var, values=packs,
                         width=220, font=FONT, state="readonly",
                         command=lambda _: self._update_preview()).pack(side="left", padx=5)

        r2 = ctk.CTkFrame(card2, fg_color="transparent")
        r2.pack(fill="x", padx=CARD_PAD, pady=3)
        ctk.CTkLabel(r2, text="Тема/интерес:", font=FONT, width=100, anchor="w",
                     text_color=COLOR_TEXT).pack(side="left")

        topic_names = [t["name_ru"] for t in self.topics["topics"] if t["id"] != "custom"]
        topic_names.append("Своя тема")
        self.topic_var = ctk.StringVar(value="Динозавры")
        self.topic_combo = ctk.CTkComboBox(r2, variable=self.topic_var, values=topic_names,
                                            width=220, font=FONT, state="readonly",
                                            command=self._on_topic_change)
        self.topic_combo.pack(side="left", padx=5)

        self.custom_topic_var = ctk.StringVar(value="")
        self.custom_topic_entry = ctk.CTkEntry(r2, textvariable=self.custom_topic_var,
                                                width=220, font=FONT,
                                                placeholder_text="Введите свою тему")
        self.custom_topic_var.trace_add("write", lambda *a: self._update_preview())

        r3 = ctk.CTkFrame(card2, fg_color="transparent")
        r3.pack(fill="x", padx=CARD_PAD, pady=3)
        ctk.CTkLabel(r3, text="Кол-во страниц:", font=FONT, width=100, anchor="w",
                     text_color=COLOR_TEXT).pack(side="left")
        self.pages_var = ctk.StringVar(value="12")
        pages_menu = ctk.CTkOptionMenu(r3, variable=self.pages_var,
                                        values=["8", "12", "20", "30", "40"],
                                        font=FONT, fg_color=COLOR_CARD,
                                        button_color=COLOR_PRIMARY,
                                        command=lambda _: self._update_preview())
        pages_menu.pack(side="left", padx=5)

        self.page_warn_label = ctk.CTkLabel(r3, text="", font=FONT_SMALL, text_color=COLOR_RED)
        self.page_warn_label.pack(side="left", padx=5)
        self.pages_var.trace_add("write", self._on_pages_change)

        r4 = ctk.CTkFrame(card2, fg_color="transparent")
        r4.pack(fill="x", padx=CARD_PAD, pady=3)
        ctk.CTkLabel(r4, text="Сложность:", font=FONT, width=100, anchor="w",
                     text_color=COLOR_TEXT).pack(side="left")
        self.diff_var = ctk.StringVar(value="Подобрать автоматически по возрасту")
        diffs = ["Лёгкая", "Средняя", "Сложная", "Подобрать автоматически по возрасту"]
        ctk.CTkComboBox(r4, variable=self.diff_var, values=diffs,
                         width=220, font=FONT, state="readonly",
                         command=lambda _: self._update_preview()).pack(side="left", padx=5)

        r5 = ctk.CTkFrame(card2, fg_color="transparent")
        r5.pack(fill="x", padx=CARD_PAD, pady=3)
        ctk.CTkLabel(r5, text="Стиль:", font=FONT, width=100, anchor="w",
                     text_color=COLOR_TEXT).pack(side="left")
        self.style_var = ctk.StringVar(value="Чёрно-белый для печати")
        styles = ["Минималистичный", "Весёлый", "Учебный", "Чёрно-белый для печати"]
        ctk.CTkComboBox(r5, variable=self.style_var, values=styles,
                         width=220, font=FONT, state="readonly").pack(side="left", padx=5)
        ctk.CTkLabel(card2, text="", font=FONT_SMALL).pack(pady=4)

        # CARD 3: Extra
        card3 = ctk.CTkFrame(frame, fg_color=COLOR_CARD, corner_radius=CORNER_RADIUS)
        card3.pack(fill="x", pady=4)

        ctk.CTkLabel(card3, text="3. Дополнительно", font=FONT_HEADER,
                     text_color=COLOR_TEXT).pack(anchor="w", padx=CARD_PAD, pady=(12, 2))
        ctk.CTkLabel(card3, text="Настройте режим генерации и имя",
                     font=FONT_SMALL, text_color=COLOR_SECONDARY).pack(
            anchor="w", padx=CARD_PAD, pady=(0, 8))

        er1 = ctk.CTkFrame(card3, fg_color="transparent")
        er1.pack(fill="x", padx=CARD_PAD, pady=2)

        self.answers_var = ctk.BooleanVar(value=True)
        ctk.CTkCheckBox(er1, text="Добавить ответы", variable=self.answers_var,
                         font=FONT, text_color=COLOR_TEXT,
                         command=self._update_preview).pack(side="left", padx=(0, 20))
        self.instruction_var = ctk.BooleanVar(value=True)
        ctk.CTkCheckBox(er1, text="Инструкция для родителя", variable=self.instruction_var,
                         font=FONT, text_color=COLOR_TEXT,
                         command=self._update_preview).pack(side="left", padx=(0, 20))

        er2 = ctk.CTkFrame(card3, fg_color="transparent")
        er2.pack(fill="x", padx=CARD_PAD, pady=2)

        self.offline_var = ctk.BooleanVar(value=True)
        self.offline_cb = ctk.CTkCheckBox(er2, text="Офлайн-режим (шаблонные задания)",
                                           variable=self.offline_var,
                                           font=FONT, text_color=COLOR_TEXT,
                                           command=self._on_offline_change)
        self.offline_cb.pack(side="left")

        self.offline_status_label = ctk.CTkLabel(er2, text="",
                                                  font=FONT_SMALL, text_color=COLOR_GREEN)
        self.offline_status_label.pack(side="left", padx=8)

        self.commercial_var = ctk.BooleanVar(value=False)
        ctk.CTkCheckBox(er2, text="Коммерческий PDF (без водяного знака)",
                         variable=self.commercial_var,
                         font=FONT, text_color=COLOR_TEXT).pack(side="left", padx=(20, 0))
        self._on_offline_change()

        er3 = ctk.CTkFrame(card3, fg_color="transparent")
        er3.pack(fill="x", padx=CARD_PAD, pady=2)
        ctk.CTkLabel(er3, text="Имя ребёнка:", font=FONT, width=100,
                     anchor="w", text_color=COLOR_TEXT).pack(side="left")
        self.name_var = ctk.StringVar(value="")
        ctk.CTkEntry(er3, textvariable=self.name_var, width=180,
                      font=FONT, placeholder_text="Необязательно").pack(side="left", padx=5)
        ctk.CTkLabel(er3, text="Бренд (для коммерч.):", font=FONT, width=130,
                     anchor="w", text_color=COLOR_TEXT).pack(side="left", padx=(10, 0))
        self.brand_var = ctk.StringVar(value="")
        ctk.CTkEntry(er3, textvariable=self.brand_var, width=180,
                      font=FONT, placeholder_text="Имя исполнителя").pack(side="left", padx=5)

        er4 = ctk.CTkFrame(card3, fg_color="transparent")
        er4.pack(fill="x", padx=CARD_PAD, pady=2)
        ctk.CTkLabel(er4, text="Папка сохранения:", font=FONT, width=110,
                     anchor="w", text_color=COLOR_TEXT).pack(side="left")
        out_dir_default = output_dir()
        self.out_dir_var = ctk.StringVar(value=out_dir_default)
        ctk.CTkEntry(er4, textvariable=self.out_dir_var, width=350,
                      font=FONT).pack(side="left", padx=5)
        ctk.CTkButton(er4, text="Обзор", width=60, height=28,
                      font=FONT, fg_color=COLOR_BORDER,
                      text_color=COLOR_TEXT,
                      command=self._browse_output).pack(side="left")
        ctk.CTkLabel(card3, text="", font=FONT_SMALL).pack(pady=4)

        # Advanced tools (collapsible)
        self.adv_expanded = False
        self.adv_frame = ctk.CTkFrame(card3, fg_color="#F9FAFB", corner_radius=8)
        self.adv_frame.pack(fill="x", padx=CARD_PAD, pady=(0, 8))
        self.adv_btn = ctk.CTkButton(self.adv_frame, text="▶  Расширенные инструменты",
                                      font=FONT, fg_color="transparent",
                                      text_color=COLOR_SECONDARY, anchor="w",
                                      command=self._toggle_advanced)
        self.adv_btn.pack(fill="x", padx=5, pady=2)
        self.adv_content = ctk.CTkFrame(self.adv_frame, fg_color="transparent")

        adv_buttons = [
            ("HTML Preview", self._on_html_preview),
            ("Редактор JSON", self._on_edit_json),
            ("Собрать PDF из JSON", self._on_build_from_json),
            ("Создать по тексту", self._on_custom_text),
            ("Настройки API", self._show_api_settings),
            ("Открыть логи", self._open_logs),
            ("Проверить математику", self._check_math),
        ]
        adv_row = ctk.CTkFrame(self.adv_content, fg_color="transparent")
        adv_row.pack(fill="x", padx=5, pady=5)
        for txt, cmd in adv_buttons:
            ctk.CTkButton(adv_row, text=txt, font=FONT_SMALL,
                          fg_color="transparent", border_width=1,
                          border_color=COLOR_BORDER, text_color=COLOR_TEXT,
                          height=30, command=cmd).pack(side="left", padx=3)

        # Main generate button
        gen_row = ctk.CTkFrame(frame, fg_color="transparent")
        gen_row.pack(fill="x", pady=(8, 2))

        self.generate_btn = ctk.CTkButton(gen_row, text="Сгенерировать PDF",
                                           font=("Segoe UI", 16, "bold"),
                                           fg_color=COLOR_PRIMARY, hover_color="#1D4ED8",
                                           text_color="white", height=52,
                                           command=self._on_generate)
        self.generate_btn.pack(fill="x", padx=CARD_PAD)

        # Error block
        self.error_frame = ctk.CTkFrame(frame, fg_color="#FEF2F2",
                                         corner_radius=CORNER_RADIUS)
        self.error_label = ctk.CTkLabel(self.error_frame, text="",
                                         font=FONT, text_color=COLOR_RED,
                                         justify="left")
        self.error_label.pack(fill="x", padx=12, pady=8)
        self.error_btn = ctk.CTkButton(self.error_frame, text="",
                                        font=FONT, fg_color=COLOR_PRIMARY,
                                        height=32)
        self.error_frame.pack(fill="x", pady=4)
        self.error_frame.pack_forget()

        ctk.CTkLabel(frame, text="", font=FONT_SMALL).pack(pady=10)

    def _toggle_advanced(self):
        self.adv_expanded = not self.adv_expanded
        if self.adv_expanded:
            self.adv_btn.configure(text="▼  Расширенные инструменты")
            self.adv_content.pack(fill="x")
        else:
            self.adv_btn.configure(text="▶  Расширенные инструменты")
            self.adv_content.pack_forget()

    def _adj_age(self, delta):
        try:
            val = int(self.age_var.get()) + delta
            val = max(4, min(10, val))
            self.age_var.set(str(val))
        except ValueError:
            self.age_var.set("7")
        self._update_preview()

    def _on_topic_change(self, choice):
        if choice == "Своя тема":
            self.custom_topic_entry.pack(side="left", padx=5)
        else:
            self.custom_topic_entry.pack_forget()
        self._update_preview()

    def _on_pages_change(self, *args):
        try:
            p = int(self.pages_var.get())
            if p > 20:
                self.page_warn_label.configure(text="Большие наборы лучше генерировать по блокам")
            else:
                self.page_warn_label.configure(text="")
        except ValueError:
            pass
        self._update_preview()

    def _on_offline_change(self):
        offline = self.offline_var.get()
        if offline:
            self.offline_status_label.configure(text="Активен: используются встроенные шаблоны",
                                                 text_color=COLOR_GREEN)
            self.side_status_label.configure(text="●  Офлайн-режим", text_color="#FACC15")
        else:
            self.offline_status_label.configure(text="")
            self._check_api_key()
        self._update_preview()

    def _check_api_key(self):
        key = os.getenv("OPENROUTER_API_KEY", "")
        if not key or key == "your_key_here":
            self.side_status_label.configure(text="●  Нет API-ключа", text_color=COLOR_RED)
            self._show_api_warning()
        else:
            self.side_status_label.configure(text="●  AI готов", text_color=COLOR_PRIMARY)
            self._hide_api_warning()

    def _show_api_warning(self):
        self.error_frame.pack(fill="x", pady=4)
        self.error_label.configure(
            text="API-ключ не настроен.\n"
                 "Добавьте ключ в настройках или включите офлайн-режим."
        )
        self.error_btn.configure(text="Открыть настройки API",
                                  command=self._show_api_settings)

    def _hide_api_warning(self):
        self.error_frame.pack_forget()

    # ═══════════════════════════════════════════════════════════
    # PREVIEW UPDATE
    # ═══════════════════════════════════════════════════════════

    def _update_preview(self, *args):
        if not hasattr(self, 'preview_labels'):
            return
        lang_map = {"Русский": "ru", "Украинский": "uk", "Английский": "en",
                     "Украинский + английский": "uk+en", "Русский + английский": "ru+en"}
        pack_map = {"Подготовка к школе": "preschool", "Математика": "math",
                     "Чтение": "reading", "Украинский язык": "ukrainian",
                     "Английский": "english", "Логика": "logic",
                     "Смешанный набор на неделю": "mixed_week"}

        lang = lang_map.get(self.lang_var.get(), "ru")
        ptype = pack_map.get(self.pack_var.get(), "mixed_week")
        topic = self.topic_var.get()
        if topic == "Своя тема" and self.custom_topic_var.get().strip():
            topic = self.custom_topic_var.get().strip()
        pages = self.pages_var.get()
        offline = self.offline_var.get()
        answers = self.answers_var.get()

        self.preview_labels["age"].configure(text=self.age_var.get() + " лет")
        self.preview_labels["grade"].configure(text=self.grade_var.get())
        self.preview_labels["language"].configure(text={"ru": "Русский", "uk": "Украинский",
                                                          "en": "Английский",
                                                          "uk+en": "Укр+Англ",
                                                          "ru+en": "Рус+Англ"}.get(lang, lang))
        self.preview_labels["pack_type"].configure(text=ptype)
        self.preview_labels["topic"].configure(text=topic)
        self.preview_labels["pages"].configure(text=pages)
        self.preview_labels["style"].configure(text=self.style_var.get())
        self.preview_labels["answers"].configure(text="Да" if answers else "Нет")
        self.preview_labels["offline"].configure(text="Офлайн" if offline else "AI")

    # ═══════════════════════════════════════════════════════════
    # GENERATE
    # ═══════════════════════════════════════════════════════════

    def _on_generate(self):
        try:
            age = int(self.age_var.get())
            if age < 4 or age > 10:
                raise ValueError
        except ValueError:
            self._show_error("Возраст должен быть числом от 4 до 10.")
            return

        lang_map = {"Русский": "ru", "Украинский": "uk", "Английский": "en",
                     "Украинский + английский": "uk+en", "Русский + английский": "ru+en"}
        language = lang_map.get(self.lang_var.get(), "ru")

        pack_map = {"Подготовка к школе": "preschool", "Математика": "math",
                     "Чтение": "reading", "Украинский язык": "ukrainian",
                     "Английский": "english", "Логика": "logic",
                     "Смешанный набор на неделю": "mixed_week"}
        pack_type = pack_map.get(self.pack_var.get(), "mixed_week")

        topic_map = {t["name_ru"]: t["id"] for t in self.topics["topics"]}
        topic_id = topic_map.get(self.topic_var.get(), "custom")
        topic = self.custom_topic_var.get().strip() or topic_id
        if topic_id == "custom" and not self.custom_topic_var.get().strip():
            topic = "custom"

        pages_count = int(self.pages_var.get())

        diff_map = {"Лёгкая": "easy", "Средняя": "medium", "Сложная": "hard",
                     "Подобрать автоматически по возрасту": "auto"}
        difficulty = diff_map.get(self.diff_var.get(), "auto")

        style_map = {"Минималистичный": "minimal", "Весёлый": "fun",
                      "Учебный": "academic", "Чёрно-белый для печати": "print_bw"}
        style = style_map.get(self.style_var.get(), "print_bw")

        if pages_count > 20:
            if not self._ask_yesno("Предупреждение",
                    "Большие наборы лучше генерировать по блокам.\n\nПродолжить?"):
                return

        request = PackRequest(
            age=age, grade=self.grade_var.get(), language=language,
            pack_type=pack_type, topic=topic, pages_count=pages_count,
            difficulty=difficulty,
            include_answers=self.answers_var.get(),
            include_parent_instruction=self.instruction_var.get(),
            style=style, child_name=self.name_var.get().strip(),
            output_dir=self.out_dir_var.get().strip() or output_dir(),
            offline_mode=self.offline_var.get(),
            commercial_mode=self.commercial_var.get(),
            brand_name=self.brand_var.get().strip(),
        )

        self.generate_btn.configure(state="disabled", text="Генерация...")
        self.progress.set(0.1)
        self._set_status("Подготовка...")
        self.error_frame.pack_forget()

        thread = threading.Thread(
            target=self._generate_thread, args=(request,), daemon=True
        )
        thread.start()

    def _set_status(self, text):
        self.status_var.set(text)
        self.root.update_idletasks()

    def _generate_thread(self, request):
        try:
            offline = request.offline_mode
            if offline:
                self.root.after(0, lambda: self._set_status("Создание по шаблону (офлайн)..."))
                self.root.after(0, lambda: self.progress.set(0.3))

                # New pipeline: preset -> card_generator -> postprocess
                preset = find_best_preset(
                    age=request.age,
                    pack_type=request.pack_type,
                    difficulty=request.difficulty
                )
                if preset:
                    pdata = preset_to_request(preset)
                    pdata["age"] = request.age
                    pdata["language"] = request.language
                    pdata["topic"] = request.topic
                    pdata["pages_count"] = request.pages_count
                    pdata["include_answers"] = request.include_answers
                    pdata["include_parent_instruction"] = request.include_parent_instruction
                    if request.child_name:
                        pdata["title"] = f"{request.child_name}: задания"
                    data = generate_from_preset(pdata)
                    data = postprocess(data)
                else:
                    # Fallback to old offline
                    data = generate_offline(request)

                if data is None:
                    self.root.after(0, lambda: self._show_error(
                        "Нет шаблона для выбранного типа набора."
                    ))
                    self.root.after(0, self._reset_generate_btn)
                    return

                self.last_pack_data = data
                ensure_dirs()
                date_str = datetime.now().strftime("%Y-%m-%d")
                base = f"StudyPack_{request.age}_{request.topic}_{date_str}"
                base = "".join(c if c.isalnum() or c in "-_" else "_" for c in base)
                json_path = os.path.join(output_dir(), f"{base}.json")
                with open(json_path, "w", encoding="utf-8") as f:
                    json.dump(data, f, ensure_ascii=False, indent=2)
                self.last_json_path = json_path

                self.root.after(0, lambda: self.progress.set(0.6))
                self._build_pdf_from_data(data)
                self.root.after(0, lambda: self._set_status("Готово! PDF создан."))
                self.root.after(0, lambda: self.progress.set(1.0))
                self.root.after(0, self._reset_generate_btn)
                return

            # AI mode
            self.root.after(0, lambda: self._set_status("Генерация заданий через AI..."))
            self.root.after(0, lambda: self.progress.set(0.2))
            generator = StudyPackGenerator()
            result = generator.generate(request)

            if result.success:
                self.last_pdf_path = result.pdf_path
                self.last_json_path = result.json_path
                if result.json_path and os.path.exists(result.json_path):
                    with open(result.json_path, "r", encoding="utf-8") as f:
                        self.last_pack_data = json.load(f)

                math_issues = []
                if self.last_pack_data:
                    math_issues = verify_math_in_pack(self.last_pack_data)

                self.root.after(0, lambda: self.progress.set(1.0))
                self.root.after(0, lambda: self._show_result(
                    result.pdf_path, result.json_path, math_issues, result.warnings
                ))
                self.root.after(0, lambda: self._set_status(
                    f"PDF создан: {os.path.basename(result.pdf_path) if result.pdf_path else ''}"
                ))
            else:
                self.root.after(0, lambda: self._show_error(result.error))

        except Exception as e:
            self.root.after(0, lambda: self._show_error(f"Критическая ошибка: {e}"))
        finally:
            self.root.after(0, self._reset_generate_btn)

    def _reset_generate_btn(self):
        self.generate_btn.configure(state="normal", text="Сгенерировать PDF")

    def _build_pdf_from_data(self, data):
        out_dir = self.out_dir_var.get().strip() or output_dir()
        os.makedirs(out_dir, exist_ok=True)

        age = data.get("age", 7)
        topic = data.get("topic", "custom")
        date_str = datetime.now().strftime("%Y-%m-%d")
        base_name = f"StudyPack_{age}_{topic}_{date_str}"
        base_name = "".join(c if c.isalnum() or c in "-_" else "_" for c in base_name)

        theme_map = {"Минималистичный": "minimal", "Весёлый": "fun",
                      "Учебный": "academic", "Чёрно-белый для печати": "print_bw"}
        style_key = theme_map.get(self.style_var.get(), "print_bw")

        pdf_path = os.path.join(out_dir, f"{base_name}.pdf")
        try:
            is_commercial = self.commercial_var.get() if hasattr(self, 'commercial_var') else False
            brand = self.brand_var.get().strip() if hasattr(self, 'brand_var') else ""
            watermark = "" if is_commercial else "Демо-набір StudyPack AI"

            render_pdf(data, pdf_path, watermark=watermark,
                       is_commercial=is_commercial, brand=brand,
                       theme=style_key)
            self.last_pdf_path = pdf_path
            self.last_pack_data = data

            math_issues = verify_math_in_pack(data)
            self.root.after(0, lambda: self._show_result(
                pdf_path, None, math_issues, []
            ))
        except Exception as e:
            self.root.after(0, lambda: self._show_error(f"Не удалось создать PDF: {e}"))

    def _show_result(self, pdf_path, json_path, math_issues, warnings):
        self.last_pdf_path = pdf_path
        self.preview_open_last_btn.configure(state="normal")

        qc = (self.last_pack_data or {}).get("_quality", {})
        q_errors = qc.get("errors", [])
        q_warnings = qc.get("warnings", [])
        q_passed = qc.get("passed", True)

        win = ctk.CTkToplevel(self.root)
        title_s = "PDF готов!" if q_passed else "PDF создан (с замечаниями)"
        win.title(title_s)
        win.geometry("520x480")
        win.resizable(False, False)
        win.transient(self.root)
        win.grab_set()

        frame = ctk.CTkFrame(win, fg_color=COLOR_CARD, corner_radius=12)
        frame.pack(fill="both", expand=True, padx=15, pady=15)

        ctk.CTkLabel(frame, text=title_s, font=FONT_TITLE,
                     text_color=COLOR_GREEN if q_passed else "#F59E0B").pack(pady=(15, 2))

        pdf_name = os.path.basename(pdf_path) if pdf_path else "—"
        ctk.CTkLabel(frame, text=pdf_name, font=FONT, text_color=COLOR_SECONDARY).pack()

        sep = ctk.CTkFrame(frame, height=1, fg_color=COLOR_BORDER)
        sep.pack(fill="x", padx=15, pady=8)

        checks = [
            ("Структура проверена", True),
            ("Математика проверена", len(math_issues) == 0),
            ("Запрещённые бренды проверены", True),
            ("Редакторская проверка", q_passed),
            ("PDF сохранён", os.path.exists(pdf_path) if pdf_path else False),
        ]

        for label, ok in checks:
            row = ctk.CTkFrame(frame, fg_color="transparent")
            row.pack(fill="x", padx=20, pady=1)
            ctk.CTkLabel(row, text="✓" if ok else "✗",
                         text_color=COLOR_GREEN if ok else COLOR_RED,
                         font=FONT_BOLD).pack(side="left")
            ctk.CTkLabel(row, text=label, font=FONT,
                         text_color=COLOR_TEXT).pack(side="left", padx=5)

        if math_issues:
            ctk.CTkLabel(frame, text=f"Найдено {len(math_issues)} ошибок в математике",
                         font=FONT_SMALL, text_color=COLOR_RED).pack(pady=2)

        if q_errors:
            for e in q_errors[:3]:
                ctk.CTkLabel(frame, text=f"✗ {e}", font=FONT_SMALL,
                             text_color=COLOR_RED).pack(pady=1)
        if q_warnings:
            for w in q_warnings[:3]:
                ctk.CTkLabel(frame, text=f"⚠ {w}", font=FONT_SMALL,
                             text_color="#F59E0B").pack(pady=1)

        if warnings:
            for w in warnings[:3]:
                ctk.CTkLabel(frame, text=f"⚠ {w}", font=FONT_SMALL,
                             text_color="#F59E0B").pack(pady=1)

        btn_row = ctk.CTkFrame(frame, fg_color="transparent")
        btn_row.pack(pady=12)

        def open_pdf():
            if pdf_path and os.path.exists(pdf_path):
                os.startfile(pdf_path)
            win.destroy()

        def open_folder():
            folder = os.path.dirname(pdf_path) if pdf_path else output_dir()
            if os.path.isdir(folder):
                os.startfile(folder)
            win.destroy()

        ctk.CTkButton(btn_row, text="Открыть PDF", command=open_pdf,
                      fg_color=COLOR_PRIMARY, font=FONT_BOLD,
                      height=38, width=130).pack(side="left", padx=4)
        ctk.CTkButton(btn_row, text="Открыть папку", command=open_folder,
                      fg_color="transparent", border_width=1, border_color=COLOR_BORDER,
                      text_color=COLOR_TEXT, font=FONT,
                      height=38, width=130).pack(side="left", padx=4)
        ctk.CTkButton(btn_row, text="Создать ещё", command=win.destroy,
                      fg_color="transparent", border_width=1, border_color=COLOR_BORDER,
                      text_color=COLOR_TEXT, font=FONT,
                      height=38, width=130).pack(side="left", padx=4)

    def _show_error(self, text):
        self.error_frame.pack(fill="x", pady=4)
        self.error_label.configure(text=text)
        self.error_btn.configure(text="", command=lambda: None)
        self.error_btn.pack_forget()

    # ═══════════════════════════════════════════════════════════
    # NAV PAGES
    # ═══════════════════════════════════════════════════════════

    def _build_examples_page(self):
        frame = self.content_area
        ctk.CTkLabel(frame, text="Библиотека пресетов", font=FONT_TITLE,
                     text_color=COLOR_TEXT).pack(anchor="w", pady=(8, 2))
        ctk.CTkLabel(frame, text="Готовые шаблоны наборов — выберите и создайте PDF",
                     font=FONT, text_color=COLOR_SECONDARY).pack(anchor="w", pady=(0, 10))

        presets = list_presets()
        if not presets:
            ctk.CTkLabel(frame, text="Пресеты не найдены. Проверьте templates_library/presets/",
                         font=FONT, text_color=COLOR_RED).pack(pady=20)
            return

        lang_label = {"ru": "Русский", "uk": "Украинский", "en": "Английский",
                      "ru+en": "Рус+Англ", "uk+en": "Укр+Англ"}
        diff_label = {"easy": "Лёгкая", "medium": "Средняя", "hard": "Сложная"}
        type_label = {"preschool": "Подготовка к школе", "math": "Математика",
                      "reading": "Чтение", "logic": "Логика",
                      "english": "Английский", "mixed_week": "Смешанный"}

        # Filter row
        filter_frame = ctk.CTkFrame(frame, fg_color="transparent")
        filter_frame.pack(fill="x", pady=(0, 8))

        self.preset_filter_var = ctk.StringVar(value="Все типы")
        filters = ["Все типы", "Подготовка к школе", "Математика",
                    "Чтение", "Логика", "Английский", "Смешанный"]
        ctk.CTkComboBox(filter_frame, variable=self.preset_filter_var,
                        values=filters, width=200, font=FONT, state="readonly",
                        command=lambda _: self._rebuild_preset_list()
                        ).pack(side="left", padx=2)

        ctk.CTkLabel(filter_frame, text="", font=FONT_SMALL).pack(pady=2)

        self.presets_container = ctk.CTkFrame(frame, fg_color="transparent")
        self.presets_container.pack(fill="both", expand=True)
        self._rebuild_preset_list()

    def _rebuild_preset_list(self):
        for w in self.presets_container.winfo_children():
            w.destroy()

        raw = list_presets()
        filt = self.preset_filter_var.get()
        type_rev = {"Подготовка к школе": "preschool", "Математика": "math",
                    "Чтение": "reading", "Логика": "logic",
                    "Английский": "english", "Смешанный": "mixed_week"}

        if filt != "Все типы":
            raw = [p for p in raw if p.get("pack_type") == type_rev.get(filt)]

        lang_label = {"ru": "Русский", "uk": "Украинский", "en": "Английский",
                      "ru+en": "Рус+Англ", "uk+en": "Укр+Англ"}
        diff_label = {"easy": "Лёгкая", "medium": "Средняя", "hard": "Сложная"}
        type_label = {"preschool": "Подготовка к школе", "math": "Математика",
                      "reading": "Чтение", "logic": "Логика",
                      "english": "Английский", "mixed_week": "Смешанный"}

        examples_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "examples")

        grid = ctk.CTkFrame(self.presets_container, fg_color="transparent")
        grid.pack(fill="both", expand=True)

        row_frame = None
        for i, p in enumerate(raw):
            if i % 3 == 0:
                row_frame = ctk.CTkFrame(grid, fg_color="transparent")
                row_frame.pack(fill="x", pady=2)

            card = ctk.CTkFrame(row_frame, fg_color=COLOR_CARD, corner_radius=CORNER_RADIUS)
            card.pack(side="left", fill="both", expand=True, padx=4, pady=4)

            pid = p.get("id", "")
            title = p.get("title", pid)
            age = p.get("age", 7)
            pt = type_label.get(p.get("pack_type", ""), p.get("pack_type", ""))
            lang = lang_label.get(p.get("language", "ru"), p.get("language", "ru"))
            diff = diff_label.get(p.get("difficulty", "easy"), p.get("difficulty", "easy"))
            desc = p.get("description", "")

            ctk.CTkLabel(card, text=title, font=FONT_BOLD,
                         text_color=COLOR_TEXT).pack(anchor="w", padx=10, pady=(8, 2))

            meta = f"Возраст: {age}  |  {pt}  |  {lang}  |  {diff}"
            ctk.CTkLabel(card, text=meta, font=FONT_SMALL,
                         text_color=COLOR_SECONDARY).pack(anchor="w", padx=10, pady=1)

            if desc:
                ctk.CTkLabel(card, text=desc[:80], font=FONT_SMALL,
                             text_color=COLOR_SECONDARY).pack(anchor="w", padx=10, pady=1)

            btn_row_w = ctk.CTkFrame(card, fg_color="transparent")
            btn_row_w.pack(fill="x", padx=10, pady=6)

            # Try to find matching example PDF
            pdf_candidates = [f for f in os.listdir(examples_dir)
                              if f.endswith(".pdf") and pid in f] if os.path.isdir(examples_dir) else []
            if pdf_candidates:
                pdf_path = os.path.join(examples_dir, pdf_candidates[0])
                ctk.CTkButton(btn_row_w, text="Открыть PDF", font=FONT_SMALL,
                              fg_color=COLOR_PRIMARY, height=30,
                              command=lambda p=pdf_path: os.startfile(p)
                              ).pack(side="left", padx=2)

            ctk.CTkButton(btn_row_w, text="Использовать",
                          font=FONT_SMALL, fg_color="transparent",
                          border_width=1, border_color=COLOR_BORDER,
                          text_color=COLOR_TEXT, height=30,
                          command=lambda pa=p, pd=pid: self._use_preset(pa)
                          ).pack(side="left", padx=2)

    def _use_preset(self, preset_data):
        pdata = preset_to_request(preset_data)
        self.age_var.set(str(pdata["age"]))

        type_rev = {"preschool": "Подготовка к школе", "math": "Математика",
                    "reading": "Чтение", "logic": "Логика",
                    "english": "Английский", "mixed_week": "Смешанный набор на неделю"}
        pt = type_rev.get(pdata.get("pack_type", ""), "Смешанный набор на неделю")
        self.pack_var.set(pt)

        lang_rev = {"ru": "Русский", "uk": "Украинский", "en": "Английский",
                    "uk+en": "Украинский + английский", "ru+en": "Русский + английский"}
        l = lang_rev.get(pdata.get("language", "ru"), "Русский")
        self.lang_var.set(l)

        diff_rev = {"easy": "Лёгкая", "medium": "Средняя", "hard": "Сложная"}
        d = diff_rev.get(pdata.get("difficulty", "medium"), "Средняя")
        self.diff_var.set(d)

        self.pages_var.set(str(pdata.get("pages_count", 10)))

        topic_str = pdata.get("topic", "")
        if topic_str:
            topics_vals = self.topic_combo.cget("values")
            for tv in topics_vals:
                if topic_str.lower() in tv.lower():
                    self.topic_var.set(tv)
                    break

        self._nav_click("create")

    def _build_history_page(self):
        frame = self.content_area
        ctk.CTkLabel(frame, text="История генераций", font=FONT_TITLE,
                     text_color=COLOR_TEXT).pack(anchor="w", pady=(8, 2))
        ctk.CTkLabel(frame, text="Последние созданные наборы",
                     font=FONT, text_color=COLOR_SECONDARY).pack(anchor="w", pady=(0, 10))

        history_path = os.path.join(os.path.dirname(os.path.dirname(__file__)),
                                     "user_data", "history.json")
        items = []
        if os.path.exists(history_path):
            with open(history_path, "r", encoding="utf-8") as f:
                items = json.load(f)

        if not items:
            ctk.CTkLabel(frame, text="История пуста.\nСоздайте первый PDF-набор!",
                         font=FONT, text_color=COLOR_SECONDARY,
                         justify="center").pack(expand=True, pady=40)
            return

        for h in items[-20:][::-1]:
            card = ctk.CTkFrame(frame, fg_color=COLOR_CARD, corner_radius=8)
            card.pack(fill="x", pady=2)
            inner = ctk.CTkFrame(card, fg_color="transparent")
            inner.pack(fill="x", padx=10, pady=5)

            ctk.CTkLabel(inner, text=f"{h.get('date','')} — {h.get('title','')}",
                         font=FONT_BOLD, text_color=COLOR_TEXT).pack(anchor="w")
            ctk.CTkLabel(inner,
                         text=f"{h.get('age','')} лет | {h.get('language','')} | {h.get('type','')} | {h.get('mode','')}",
                         font=FONT_SMALL, text_color=COLOR_SECONDARY).pack(anchor="w")

            btn_r = ctk.CTkFrame(inner, fg_color="transparent")
            btn_r.pack(fill="x", pady=2)

            pdf_p = h.get("pdf_path", "")
            if pdf_p and os.path.exists(pdf_p):
                ctk.CTkButton(btn_r, text="Открыть PDF", font=FONT_SMALL,
                              fg_color="transparent", border_width=1, border_color=COLOR_BORDER,
                              text_color=COLOR_TEXT, height=28,
                              command=lambda p=pdf_p: os.startfile(p)).pack(side="left", padx=2)

            ctk.CTkButton(btn_r, text="Повторить", font=FONT_SMALL,
                          fg_color="transparent", border_width=1, border_color=COLOR_BORDER,
                          text_color=COLOR_TEXT, height=28,
                          command=lambda: None).pack(side="left", padx=2)

    def _build_settings_page(self):
        frame = self.content_area

        sec1 = ctk.CTkFrame(frame, fg_color=COLOR_CARD, corner_radius=CORNER_RADIUS)
        sec1.pack(fill="x", pady=4)
        ctk.CTkLabel(sec1, text="AI-настройки", font=FONT_HEADER,
                     text_color=COLOR_TEXT).pack(anchor="w", padx=15, pady=(10, 4))

        from core.paths import env_file_path
        from dotenv import load_dotenv, set_key
        load_dotenv(env_file_path())

        r1 = ctk.CTkFrame(sec1, fg_color="transparent")
        r1.pack(fill="x", padx=15, pady=3)
        ctk.CTkLabel(r1, text="API-ключ OpenRouter:", font=FONT, width=160, anchor="w",
                     text_color=COLOR_TEXT).pack(side="left")
        self.api_key_var = ctk.StringVar(value=os.getenv("OPENROUTER_API_KEY", ""))
        ctk.CTkEntry(r1, textvariable=self.api_key_var, width=350, font=FONT,
                      show="*").pack(side="left", padx=5)

        r2 = ctk.CTkFrame(sec1, fg_color="transparent")
        r2.pack(fill="x", padx=15, pady=3)
        ctk.CTkLabel(r2, text="Модель:", font=FONT, width=160, anchor="w",
                     text_color=COLOR_TEXT).pack(side="left")
        self.api_model_var = ctk.StringVar(value=os.getenv("OPENROUTER_MODEL", "openrouter/free"))
        ctk.CTkEntry(r2, textvariable=self.api_model_var, width=350,
                      font=FONT).pack(side="left", padx=5)

        def save_api():
            env_path = env_file_path()
            try:
                set_key(env_path, "OPENROUTER_API_KEY", self.api_key_var.get())
                set_key(env_path, "OPENROUTER_MODEL", self.api_model_var.get())
            except Exception:
                with open(env_path, "w") as f:
                    f.write(f"OPENROUTER_API_KEY={self.api_key_var.get()}\n")
                    f.write(f"OPENROUTER_MODEL={self.api_model_var.get()}\n")
            os.environ["OPENROUTER_API_KEY"] = self.api_key_var.get()
            os.environ["OPENROUTER_MODEL"] = self.api_model_var.get()
            self._show_notification("Настройки API сохранены")

        ctk.CTkButton(sec1, text="Сохранить", command=save_api,
                      fg_color=COLOR_PRIMARY, font=FONT_BOLD,
                      height=34, width=120).pack(anchor="w", padx=15, pady=8)

        sec2 = ctk.CTkFrame(frame, fg_color=COLOR_CARD, corner_radius=CORNER_RADIUS)
        sec2.pack(fill="x", pady=4)
        ctk.CTkLabel(sec2, text="Интерфейс", font=FONT_HEADER,
                     text_color=COLOR_TEXT).pack(anchor="w", padx=15, pady=(10, 4))

        r3 = ctk.CTkFrame(sec2, fg_color="transparent")
        r3.pack(fill="x", padx=15, pady=3)
        ctk.CTkLabel(r3, text="Тема:", font=FONT, width=100, anchor="w",
                     text_color=COLOR_TEXT).pack(side="left")
        theme_var = ctk.StringVar(value="Светлая")
        ctk.CTkComboBox(r3, variable=theme_var, values=["Светлая", "Тёмная"],
                         width=150, font=FONT, state="readonly",
                         command=lambda c: ctk.set_appearance_mode("Dark" if c == "Тёмная" else "Light")
                         ).pack(side="left", padx=5)

        r4 = ctk.CTkFrame(sec2, fg_color="transparent")
        r4.pack(fill="x", padx=15, pady=3)
        ctk.CTkLabel(r4, text="Масштаб:", font=FONT, width=100, anchor="w",
                     text_color=COLOR_TEXT).pack(side="left")
        ctk.CTkComboBox(r4, variable=ctk.StringVar(value="100%"),
                         values=["90%", "100%", "110%"],
                         width=150, font=FONT, state="readonly").pack(side="left", padx=5)
        ctk.CTkLabel(sec2, text="", font=FONT_SMALL).pack(pady=4)

        ctk.CTkLabel(frame, text="", font=FONT_SMALL).pack(pady=10)

    # ═══════════════════════════════════════════════════════════
    # HELPERS
    # ═══════════════════════════════════════════════════════════

    def _show_notification(self, text):
        self.status_var.set(text)
        self.root.after(3000, lambda: self.status_var.set("Готов к работе"))

    def _ask_yesno(self, title, message):
        return tkmsg.askyesno(title=title, message=message, parent=self.root)

    def _browse_output(self):
        from tkinter import filedialog
        path = filedialog.askdirectory(title="Выберите папку сохранения")
        if path:
            self.out_dir_var.set(path)

    def _open_output(self):
        path = self.out_dir_var.get().strip() or output_dir()
        if os.path.isdir(path):
            os.startfile(path)

    def _open_last_pdf(self):
        if self.last_pdf_path and os.path.exists(self.last_pdf_path):
            os.startfile(self.last_pdf_path)

    def _open_examples_folder(self):
        ex_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "examples")
        if os.path.isdir(ex_path):
            os.startfile(ex_path)

    def _open_logs(self):
        log_dir = logs_dir()
        if os.path.isdir(log_dir):
            os.startfile(log_dir)

    def _on_html_preview(self):
        if not self.last_pack_data:
            self._show_error("Сначала сгенерируйте набор.")
            return
        ensure_dirs()
        html_path = os.path.join(output_dir(), "_preview.html")
        render_html_preview(self.last_pack_data, html_path)
        os.startfile(html_path)

    def _on_edit_json(self):
        if not self.last_json_path or not os.path.exists(self.last_json_path):
            if self.last_pack_data:
                ensure_dirs()
                self.last_json_path = os.path.join(output_dir(), "_edit_data.json")
                with open(self.last_json_path, "w", encoding="utf-8") as f:
                    json.dump(self.last_pack_data, f, ensure_ascii=False, indent=2)
            else:
                self._show_error("Сначала сгенерируйте набор.")
                return

        win = ctk.CTkToplevel(self.root)
        win.title("Редактор JSON")
        win.geometry("700x500")
        win.transient(self.root)

        text_area = ctk.CTkTextbox(win, font=("Consolas", 11))
        text_area.pack(fill="both", expand=True, padx=8, pady=8)

        with open(self.last_json_path, "r", encoding="utf-8") as f:
            text_area.insert("1.0", f.read())

        def save_and_rebuild():
            content = text_area.get("1.0", "end-1c")
            try:
                data = json.loads(content)
            except json.JSONDecodeError as e:
                self._show_error(f"Невалидный JSON: {e}")
                return
            with open(self.last_json_path, "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            self.last_pack_data = data
            math_issues = verify_math_in_pack(data)
            msg = "JSON сохранён."
            if math_issues:
                msg += f"\nFound {len(math_issues)} math issues."
            self._show_notification(msg)
            win.destroy()

        ctk.CTkButton(win, text="Сохранить и собрать PDF",
                      command=save_and_rebuild,
                      fg_color=COLOR_PRIMARY, font=FONT_BOLD,
                      height=36).pack(pady=5)

    def _on_build_from_json(self):
        from tkinter import filedialog
        path = filedialog.askopenfilename(
            title="Выберите JSON-файл",
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")]
        )
        if not path:
            return
        try:
            with open(path, "r", encoding="utf-8") as f:
                data = json.load(f)
        except (json.JSONDecodeError, IOError) as e:
            self._show_error(f"Не удалось прочитать JSON: {e}")
            return
        self.last_pack_data = data
        self._build_pdf_from_data(data)

    def _on_custom_text(self):
        win = ctk.CTkToplevel(self.root)
        win.title("Создать по своему тексту")
        win.geometry("700x600")
        win.transient(self.root)
        win.grab_set()

        main_f = ctk.CTkFrame(win, fg_color=COLOR_CARD, corner_radius=12)
        main_f.pack(fill="both", expand=True, padx=12, pady=12)

        ctk.CTkLabel(main_f, text="Вставьте текст ребёнка или тему",
                     font=FONT_HEADER, text_color=COLOR_TEXT).pack(anchor="w", padx=10, pady=(10, 2))
        ctk.CTkLabel(main_f, text="На основе текста создадим задания (математика, чтение, логика, раскраски)",
                     font=FONT_SMALL, text_color=COLOR_SECONDARY).pack(anchor="w", padx=10, pady=(0, 6))

        textbox = ctk.CTkTextbox(main_f, font=("Segoe UI", 12), height=160)
        textbox.pack(fill="x", padx=10, pady=4)
        textbox.insert("1.0", "Например: космос, ракета, планеты, звёзды, инопланетяне")

        params_f = ctk.CTkFrame(main_f, fg_color="transparent")
        params_f.pack(fill="x", padx=10, pady=6)

        ctk.CTkLabel(params_f, text="Возраст:", font=FONT).pack(side="left")
        ct_age = ctk.CTkEntry(params_f, width=50, font=FONT)
        ct_age.insert(0, "7")
        ct_age.pack(side="left", padx=5)

        ctk.CTkLabel(params_f, text="Тип:", font=FONT).pack(side="left", padx=(15, 0))
        ct_type = ctk.CTkComboBox(params_f, values=["Смешанный", "Математика", "Чтение", "Логика"],
                                  width=150, font=FONT, state="readonly")
        ct_type.set("Смешанный")
        ct_type.pack(side="left", padx=5)

        ctk.CTkLabel(params_f, text="Язык:", font=FONT).pack(side="left", padx=(15, 0))
        ct_lang = ctk.CTkComboBox(params_f, values=["Русский", "Украинский", "Английский"],
                                  width=120, font=FONT, state="readonly")
        ct_lang.set("Русский")
        ct_lang.pack(side="left", padx=5)

        ctk.CTkLabel(params_f, text="Стр.:", font=FONT).pack(side="left", padx=(15, 0))
        ct_pages = ctk.CTkEntry(params_f, width=50, font=FONT)
        ct_pages.insert(0, "6")
        ct_pages.pack(side="left", padx=5)

        ctk.CTkLabel(params_f, text="Сложность:", font=FONT).pack(side="left", padx=(15, 0))
        ct_diff = ctk.CTkComboBox(params_f, values=["Лёгкая", "Средняя", "Сложная"],
                                  width=100, font=FONT, state="readonly")
        ct_diff.set("Средняя")
        ct_diff.pack(side="left", padx=5)

        def do_generate():
            text = textbox.get("1.0", "end-1c").strip()
            if not text or len(text) < 3:
                self._show_error("Введите текст минимум 3 символа")
                return

            diff_map = {"Лёгкая": "easy", "Средняя": "medium", "Сложная": "hard"}
            type_map = {"Смешанный": "mixed_week", "Математика": "math",
                        "Чтение": "reading", "Логика": "logic"}
            lang_map = {"Русский": "ru", "Украинский": "uk", "Английский": "en"}

            age = int(ct_age.get())
            pages = int(ct_pages.get())

            preset = find_best_preset(
                age=age,
                pack_type=type_map.get(ct_type.get(), "mixed_week"),
                difficulty=diff_map.get(ct_diff.get(), "medium")
            )
            if not preset:
                self._show_error("Нет подходящего пресета")
                return

            pdata = preset_to_request(preset)
            pdata["age"] = age
            pdata["language"] = lang_map.get(ct_lang.get(), "ru")
            pdata["topic"] = text[:60]
            pdata["pages_count"] = pages
            pdata["include_answers"] = True
            pdata["include_parent_instruction"] = True
            data = generate_from_preset(pdata)
            data = postprocess(data)

            self.last_pack_data = data
            ensure_dirs()
            date_s = datetime.now().strftime("%Y-%m-%d")
            base = f"StudyPack_custom_{date_s}"
            jpath = os.path.join(output_dir(), f"{base}.json")
            with open(jpath, "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            self.last_json_path = jpath

            self._build_pdf_from_data(data)
            win.destroy()

        ctk.CTkButton(main_f, text="Создать PDF по тексту",
                      command=do_generate,
                      fg_color=COLOR_PRIMARY, font=FONT_BOLD,
                      height=42).pack(pady=10)

    def _show_api_settings(self):
        self._nav_click("settings")

    def _check_math(self):
        if not self.last_pack_data:
            self._show_error("Сначала сгенерируйте набор.")
            return
        issues = verify_math_in_pack(self.last_pack_data)
        if not issues:
            self._show_notification("Математика проверена: ошибок нет.")
        else:
            msg = "\n".join([f"Стр.{i['page']}: {i['question']} -> '{i['given_answer']}'"
                            for i in issues[:10]])
            self._show_error(f"Найдено {len(issues)} ошибок:\n{msg}")

    def _check_for_updates_silently(self):
        def worker():
            from core.updater import check_for_update
            update_info = check_for_update(VERSION)
            if update_info:
                self.root.after(0, lambda: self._prompt_update(update_info))
        threading.Thread(target=worker, daemon=True).start()

    def _check_for_updates_manually(self):
        self.update_btn.configure(text="Проверка...", state="disabled")
        def worker():
            from core.updater import check_for_update
            update_info = check_for_update(VERSION)
            if update_info:
                self.root.after(0, lambda: self.update_btn.configure(text="Обновить!", fg_color=COLOR_PRIMARY, text_color="#FFFFFF", state="normal"))
                self.root.after(0, lambda: self._prompt_update(update_info))
            else:
                self.root.after(0, lambda: self.update_btn.configure(text="Проверить обновления", state="normal"))
                self.root.after(0, lambda: tkmsg.showinfo("Обновление", f"У вас установлена последняя версия v{VERSION}."))
        threading.Thread(target=worker, daemon=True).start()

    def _prompt_update(self, update_info):
        self.update_btn.configure(
            text=f"Обновить до v{update_info['version']}",
            fg_color=COLOR_PRIMARY,
            text_color="#FFFFFF"
        )
        changelog = update_info.get("changelog", "Нет описания изменений.")
        msg = f"Доступна новая версия v{update_info['version']}!\n\nЧто нового:\n{changelog}\n\nХотите обновить программу сейчас?"
        if tkmsg.askyesno("Доступно обновление", msg):
            self._start_update_process(update_info)

    def _start_update_process(self, update_info):
        from core.updater import download_update, verify_sha256, apply_update, get_current_exe_path
        
        win = ctk.CTkToplevel(self.root)
        win.title("Обновление StudyPack AI")
        win.geometry("420x200")
        win.resizable(False, False)
        win.transient(self.root)
        win.grab_set()
        
        frame = ctk.CTkFrame(win, fg_color=COLOR_CARD, corner_radius=12)
        frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        lbl = ctk.CTkLabel(frame, text=f"Загрузка обновления v{update_info['version']}...", font=FONT_BOLD, text_color=COLOR_TEXT)
        lbl.pack(pady=(20, 10))
        
        progress = ctk.CTkProgressBar(frame, width=320)
        progress.set(0)
        progress.pack(pady=10)
        
        status_lbl = ctk.CTkLabel(frame, text="0%", font=FONT_SMALL, text_color=COLOR_SECONDARY)
        status_lbl.pack()
        
        def progress_callback(fraction):
            self.root.after(0, lambda: progress.set(fraction))
            self.root.after(0, lambda: status_lbl.configure(text=f"{int(fraction * 100)}%"))
            
        def download_worker():
            import tempfile
            temp_dir = os.path.join(tempfile.gettempdir(), "StudyPackAIUpdate")
            new_exe_name = "StudyPack_AI_new.exe"
            new_exe_path = os.path.join(temp_dir, new_exe_name)
            
            # Download file
            success = download_update(update_info["download_url"], new_exe_path, progress_callback)
            if not success:
                self.root.after(0, lambda: tkmsg.showerror("Ошибка", "Не удалось скачать обновление. Проверьте интернет."))
                self.root.after(0, win.destroy)
                return
                
            # Verify SHA-256
            self.root.after(0, lambda: lbl.configure(text="Проверка целостности файла..."))
            if not verify_sha256(new_exe_path, update_info["sha256"]):
                self.root.after(0, lambda: tkmsg.showerror("Ошибка", "Проверка хэша SHA-256 не удалась. Файл повреждён."))
                self.root.after(0, win.destroy)
                return
                
            # Apply update
            self.root.after(0, lambda: lbl.configure(text="Применение обновления, перезапуск..."))
            self.root.after(800, lambda: apply_update(new_exe_path, get_current_exe_path()))
            
        threading.Thread(target=download_worker, daemon=True).start()

    def run(self):
        self.root.mainloop()
