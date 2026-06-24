import os
import sys
import threading
import webbrowser
from tkinter import (
    Tk, Frame, Label, Button, Entry, OptionMenu, StringVar,
    IntVar, Checkbutton, messagebox, filedialog, scrolledtext,
    Toplevel
)
from tkinter.ttk import Progressbar

from core.models import PackRequest
from core.generator import StudyPackGenerator
from config.settings_loader import load_settings
from config.topics_loader import load_topics


class StudyPackGUI:
    def __init__(self):
        self.root = Tk()
        self.root.title("StudyPack AI")
        self.root.geometry("700x780")
        self.root.resizable(False, False)

        self.settings = load_settings()
        self.topics = load_topics()

        self.last_pdf_path = None
        self._build_ui()

    def _build_ui(self):
        main_frame = Frame(self.root, padx=15, pady=10)
        main_frame.pack(fill="both", expand=True)

        Label(main_frame, text="StudyPack AI", font=("Arial", 18, "bold")).pack(pady=(0, 5))
        Label(main_frame, text="Генератор PDF-наборов заданий для детей",
              font=("Arial", 10)).pack(pady=(0, 15))

        # Block 1: Child parameters
        self._add_section_title(main_frame, "Параметры ребёнка")

        age_frame = Frame(main_frame)
        age_frame.pack(fill="x", pady=2)
        Label(age_frame, text="Возраст (4-10):", width=20, anchor="w").pack(side="left")
        self.age_var = StringVar(value="7")
        Entry(age_frame, textvariable=self.age_var, width=8).pack(side="left")

        grade_frame = Frame(main_frame)
        grade_frame.pack(fill="x", pady=2)
        Label(grade_frame, text="Класс/уровень:", width=20, anchor="w").pack(side="left")
        self.grade_var = StringVar(value="Дошкольник")
        grades = ["Дошкольник", "1 класс", "2 класс", "3 класс", "4 класс",
                   "Не знаю, подобрать автоматически"]
        OptionMenu(grade_frame, self.grade_var, *grades).pack(side="left", fill="x", expand=True)

        lang_frame = Frame(main_frame)
        lang_frame.pack(fill="x", pady=2)
        Label(lang_frame, text="Язык набора:", width=20, anchor="w").pack(side="left")
        self.lang_var = StringVar(value="Русский")
        langs = ["Русский", "Украинский", "Английский",
                  "Украинский + английский", "Русский + английский"]
        OptionMenu(lang_frame, self.lang_var, *langs).pack(side="left", fill="x", expand=True)

        # Block 2: Pack parameters
        self._add_section_title(main_frame, "Параметры набора")

        pack_frame = Frame(main_frame)
        pack_frame.pack(fill="x", pady=2)
        Label(pack_frame, text="Тип набора:", width=20, anchor="w").pack(side="left")
        self.pack_var = StringVar(value="Смешанный набор на неделю")
        packs = ["Подготовка к школе", "Математика", "Чтение",
                  "Украинский язык", "Английский", "Логика",
                  "Смешанный набор на неделю"]
        OptionMenu(pack_frame, self.pack_var, *packs).pack(side="left", fill="x", expand=True)

        topic_frame = Frame(main_frame)
        topic_frame.pack(fill="x", pady=2)
        Label(topic_frame, text="Тема/интерес:", width=20, anchor="w").pack(side="left")
        topic_names = [t["name_ru"] for t in self.topics["topics"] if t["id"] != "custom"]
        topic_names.append("Своя тема")
        self.topic_var = StringVar(value="Динозавры")
        self.topic_menu = OptionMenu(topic_frame, self.topic_var, *topic_names)
        self.topic_menu.pack(side="left", fill="x", expand=True)

        custom_frame = Frame(main_frame)
        custom_frame.pack(fill="x", pady=2)
        Label(custom_frame, text="Своя тема:", width=20, anchor="w").pack(side="left")
        self.custom_topic_var = StringVar()
        Entry(custom_frame, textvariable=self.custom_topic_var, width=30).pack(side="left")

        pages_frame = Frame(main_frame)
        pages_frame.pack(fill="x", pady=2)
        Label(pages_frame, text="Количество страниц:", width=20, anchor="w").pack(side="left")
        self.pages_var = StringVar(value="12")
        OptionMenu(pages_frame, self.pages_var, "8", "12", "20", "30", "40").pack(side="left")

        diff_frame = Frame(main_frame)
        diff_frame.pack(fill="x", pady=2)
        Label(diff_frame, text="Сложность:", width=20, anchor="w").pack(side="left")
        self.diff_var = StringVar(value="Подобрать автоматически по возрасту")
        diffs = ["Лёгкая", "Средняя", "Сложная", "Подобрать автоматически по возрасту"]
        OptionMenu(diff_frame, self.diff_var, *diffs).pack(side="left", fill="x", expand=True)

        style_frame = Frame(main_frame)
        style_frame.pack(fill="x", pady=2)
        Label(style_frame, text="Стиль оформления:", width=20, anchor="w").pack(side="left")
        self.style_var = StringVar(value="Чёрно-белый для печати")
        styles = ["Минималистичный", "Весёлый", "Учебный", "Чёрно-белый для печати"]
        OptionMenu(style_frame, self.style_var, *styles).pack(side="left", fill="x", expand=True)

        # Block 3: Additional
        self._add_section_title(main_frame, "Дополнительно")

        self.answers_var = IntVar(value=1)
        Checkbutton(main_frame, text="Добавить ответы",
                    variable=self.answers_var).pack(anchor="w", pady=2)

        self.instruction_var = IntVar(value=1)
        Checkbutton(main_frame, text="Добавить инструкцию для родителя",
                    variable=self.instruction_var).pack(anchor="w", pady=2)

        name_frame = Frame(main_frame)
        name_frame.pack(fill="x", pady=2)
        Label(name_frame, text="Имя ребёнка (необязательно):", width=25, anchor="w").pack(side="left")
        self.name_var = StringVar()
        Entry(name_frame, textvariable=self.name_var, width=25).pack(side="left")

        out_frame = Frame(main_frame)
        out_frame.pack(fill="x", pady=2)
        Label(out_frame, text="Папка сохранения:", width=25, anchor="w").pack(side="left")
        self.out_dir_var = StringVar(value=os.path.abspath("output"))
        Entry(out_frame, textvariable=self.out_dir_var, width=30).pack(side="left", padx=(0, 5))
        Button(out_frame, text="Обзор", command=self._browse_output).pack(side="left")

        # Block 4: Buttons
        self._add_section_title(main_frame, "")

        btn_frame = Frame(main_frame)
        btn_frame.pack(fill="x", pady=5)

        self.generate_btn = Button(btn_frame, text="Сгенерировать PDF",
                                   font=("Arial", 11, "bold"), bg="#4CAF50", fg="white",
                                   width=20, command=self._on_generate)
        self.generate_btn.pack(side="left", padx=3)

        Button(btn_frame, text="Открыть папку", width=14,
               command=self._open_output).pack(side="left", padx=3)
        Button(btn_frame, text="Последний PDF", width=14,
               command=self._open_last_pdf).pack(side="left", padx=3)
        Button(btn_frame, text="Настройки API", width=14,
               command=self._show_api_settings).pack(side="left", padx=3)

        self.status_var = StringVar(value="Готов к работе")
        self.status_label = Label(main_frame, textvariable=self.status_var,
                                  font=("Arial", 9), fg="gray")
        self.status_label.pack(pady=(5, 2))

        self.progress = Progressbar(main_frame, mode="indeterminate")
        self.progress.pack(fill="x", pady=2, padx=20)

    def _add_section_title(self, parent, text):
        if text:
            sep = Frame(parent, height=1, bg="#cccccc")
            sep.pack(fill="x", pady=(10, 3))
            Label(parent, text=text, font=("Arial", 10, "bold"),
                  fg="#333333").pack(anchor="w", pady=(0, 3))

    def _browse_output(self):
        path = filedialog.askdirectory(title="Выберите папку сохранения")
        if path:
            self.out_dir_var.set(path)

    def _open_output(self):
        path = self.out_dir_var.get()
        if os.path.isdir(path):
            os.startfile(path)

    def _open_last_pdf(self):
        if self.last_pdf_path and os.path.exists(self.last_pdf_path):
            os.startfile(self.last_pdf_path)
        else:
            messagebox.showinfo("StudyPack AI", "PDF ещё не создан или файл не найден.")

    def _show_api_settings(self):
        win = Toplevel(self.root)
        win.title("Настройки API")
        win.geometry("450x200")
        win.resizable(False, False)

        try:
            from dotenv import load_dotenv, set_key
            load_dotenv()
        except ImportError:
            set_key = None

        Frame(win, padx=15, pady=15).pack(fill="both", expand=True)

        Label(win, text="API ключ OpenRouter:").pack(anchor="w")
        api_var = StringVar(value=os.getenv("OPENROUTER_API_KEY", ""))
        Entry(win, textvariable=api_var, width=50, show="*").pack(fill="x", pady=5)

        Label(win, text="Модель:").pack(anchor="w")
        model_var = StringVar(value=os.getenv("OPENROUTER_MODEL", "openrouter/free"))
        Entry(win, textvariable=model_var, width=50).pack(fill="x", pady=5)

        def save():
            env_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), ".env")
            if set_key:
                set_key(env_path, "OPENROUTER_API_KEY", api_var.get())
                set_key(env_path, "OPENROUTER_MODEL", model_var.get())
            else:
                with open(env_path, "w") as f:
                    f.write(f"OPENROUTER_API_KEY={api_var.get()}\n")
                    f.write(f"OPENROUTER_MODEL={model_var.get()}\n")
            messagebox.showinfo("StudyPack AI", "Настройки сохранены.")
            win.destroy()

        Button(win, text="Сохранить", command=save).pack(pady=10)

    def _on_generate(self):
        try:
            age = int(self.age_var.get())
            if age < 4 or age > 10:
                raise ValueError
        except ValueError:
            messagebox.showerror("Ошибка", "Возраст должен быть числом от 4 до 10.")
            return

        lang_map = {
            "Русский": "ru",
            "Украинский": "uk",
            "Английский": "en",
            "Украинский + английский": "uk+en",
            "Русский + английский": "ru+en",
        }
        language = lang_map.get(self.lang_var.get(), "ru")

        pack_map = {
            "Подготовка к школе": "preschool",
            "Математика": "math",
            "Чтение": "reading",
            "Украинский язык": "ukrainian",
            "Английский": "english",
            "Логика": "logic",
            "Смешанный набор на неделю": "mixed_week",
        }
        pack_type = pack_map.get(self.pack_var.get(), "mixed_week")

        topic_map = {t["name_ru"]: t["id"] for t in self.topics["topics"]}
        topic_id = topic_map.get(self.topic_var.get(), "custom")

        if topic_id == "custom":
            topic = self.custom_topic_var.get().strip() or "general"
        else:
            topic = topic_id

        pages_count = int(self.pages_var.get())

        diff_map = {
            "Лёгкая": "easy",
            "Средняя": "medium",
            "Сложная": "hard",
            "Подобрать автоматически по возрасту": "auto",
        }
        difficulty = diff_map.get(self.diff_var.get(), "auto")

        style_map = {
            "Минималистичный": "minimal",
            "Весёлый": "fun",
            "Учебный": "academic",
            "Чёрно-белый для печати": "print_bw",
        }
        style = style_map.get(self.style_var.get(), "print_bw")

        request = PackRequest(
            age=age,
            grade=self.grade_var.get(),
            language=language,
            pack_type=pack_type,
            topic=topic,
            pages_count=pages_count,
            difficulty=difficulty,
            include_answers=bool(self.answers_var.get()),
            include_parent_instruction=bool(self.instruction_var.get()),
            style=style,
            child_name=self.name_var.get().strip(),
            output_dir=self.out_dir_var.get().strip() or "output",
        )

        self.generate_btn.config(state="disabled", text="Генерация...")
        self.progress.start()
        self.status_var.set("Генерация текста через AI...")
        self.root.update()

        thread = threading.Thread(target=self._generate_thread, args=(request,), daemon=True)
        thread.start()

    def _generate_thread(self, request):
        try:
            generator = StudyPackGenerator()
            self.root.after(0, lambda: self.status_var.set("Генерация заданий через AI..."))
            result = generator.generate(request)

            if result.success:
                self.last_pdf_path = result.pdf_path
                self.root.after(0, lambda: self.status_var.set(
                    f"Готово! PDF: {os.path.basename(result.pdf_path)}"
                ))
                self.root.after(0, lambda: messagebox.showinfo(
                    "StudyPack AI",
                    f"PDF успешно создан!\n\n{result.pdf_path}"
                ))
                if result.warnings:
                    self.root.after(0, lambda: messagebox.showwarning(
                        "Предупреждения", "\n".join(result.warnings)
                    ))
            else:
                self.root.after(0, lambda: self.status_var.set(f"Ошибка: {result.error[:60]}..."))
                self.root.after(0, lambda: messagebox.showerror("Ошибка", result.error))
        except Exception as e:
            self.root.after(0, lambda: self.status_var.set("Критическая ошибка"))
            self.root.after(0, lambda: messagebox.showerror(
                "Критическая ошибка", str(e)
            ))
        finally:
            self.root.after(0, lambda: self.generate_btn.config(
                state="normal", text="Сгенерировать PDF"
            ))
            self.root.after(0, lambda: self.progress.stop())

    def run(self):
        self.root.mainloop()
