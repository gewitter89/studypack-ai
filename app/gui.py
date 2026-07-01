import json
import os
import sys
import threading
import webbrowser
from tkinter import (
    Tk, Frame, Label, Button, Entry, OptionMenu, StringVar,
    IntVar, BooleanVar, Checkbutton, messagebox, filedialog, scrolledtext,
    Toplevel
)
from tkinter.ttk import Progressbar

from core.models import PackRequest
from core.generator import StudyPackGenerator
from core.math_checker import verify_math_in_pack
from core.templates import generate_offline
from core.paths import output_dir, ensure_dirs
from pdf.renderer import render_pdf
from pdf.preview import render_html_preview
from config.settings_loader import load_settings
from config.topics_loader import load_topics
from core.updater import VERSION


class StudyPackGUI:
    def __init__(self):
        self.root = Tk()
        self.root.title("StudyPack AI")
        self.root.geometry("720x820")
        self.root.resizable(False, False)

        try:
            from PIL import Image, ImageTk
            from core.paths import logo_path
            icon_path = logo_path()
            if os.path.exists(icon_path):
                img = Image.open(icon_path)
                photo = ImageTk.PhotoImage(img)
                self.root.wm_iconphoto(True, photo)
        except Exception:
            pass

        self.settings = load_settings()
        self.topics = load_topics()

        self.last_pdf_path = None
        self.last_json_path = None
        self.last_pack_data = None
        self._build_ui()
        
        self._check_for_updates_silently()

    def _build_ui(self):
        main_frame = Frame(self.root, padx=15, pady=8)
        main_frame.pack(fill="both", expand=True)

        Label(main_frame, text="StudyPack AI", font=("Arial", 18, "bold")).pack(pady=(0, 2))
        Label(main_frame, text="Генератор PDF-наборов заданий для детей",
              font=("Arial", 9)).pack(pady=(0, 8))

        self._add_section_title(main_frame, "Параметры ребёнка")

        age_frame = Frame(main_frame)
        age_frame.pack(fill="x", pady=1)
        Label(age_frame, text="Возраст (4-10):", width=20, anchor="w").pack(side="left")
        self.age_var = StringVar(value="7")
        Entry(age_frame, textvariable=self.age_var, width=6).pack(side="left")

        grade_frame = Frame(main_frame)
        grade_frame.pack(fill="x", pady=1)
        Label(grade_frame, text="Класс/уровень:", width=20, anchor="w").pack(side="left")
        self.grade_var = StringVar(value="Дошкольник")
        grades = ["Дошкольник", "1 класс", "2 класс", "3 класс", "4 класс",
                   "Не знаю, подобрать автоматически"]
        OptionMenu(grade_frame, self.grade_var, *grades).pack(side="left", fill="x", expand=True)

        lang_frame = Frame(main_frame)
        lang_frame.pack(fill="x", pady=1)
        Label(lang_frame, text="Язык набора:", width=20, anchor="w").pack(side="left")
        self.lang_var = StringVar(value="Русский")
        langs = ["Русский", "Украинский", "Английский",
                  "Украинский + английский", "Русский + английский"]
        OptionMenu(lang_frame, self.lang_var, *langs).pack(side="left", fill="x", expand=True)

        self._add_section_title(main_frame, "Параметры набора")

        pack_frame = Frame(main_frame)
        pack_frame.pack(fill="x", pady=1)
        Label(pack_frame, text="Тип набора:", width=20, anchor="w").pack(side="left")
        self.pack_var = StringVar(value="Смешанный набор на неделю")
        packs = ["Подготовка к школе", "Математика", "Чтение",
                  "Украинский язык", "Английский", "Логика",
                  "Смешанный набор на неделю"]
        OptionMenu(pack_frame, self.pack_var, *packs).pack(side="left", fill="x", expand=True)

        topic_frame = Frame(main_frame)
        topic_frame.pack(fill="x", pady=1)
        Label(topic_frame, text="Тема/интерес:", width=20, anchor="w").pack(side="left")
        topic_names = [t["name_ru"] for t in self.topics["topics"] if t["id"] != "custom"]
        topic_names.append("Своя тема")
        self.topic_var = StringVar(value="Динозавры")
        OptionMenu(topic_frame, self.topic_var, *topic_names).pack(side="left", fill="x", expand=True)

        custom_frame = Frame(main_frame)
        custom_frame.pack(fill="x", pady=1)
        Label(custom_frame, text="Своя тема:", width=20, anchor="w").pack(side="left")
        self.custom_topic_var = StringVar()
        Entry(custom_frame, textvariable=self.custom_topic_var, width=28).pack(side="left")

        pages_frame = Frame(main_frame)
        pages_frame.pack(fill="x", pady=1)
        Label(pages_frame, text="Количество страниц:", width=20, anchor="w").pack(side="left")
        self.pages_var = StringVar(value="12")
        OptionMenu(pages_frame, self.pages_var, "8", "12", "20", "30", "40").pack(side="left")

        self.page_warn_label = Label(pages_frame, text="", fg="red", font=("Arial", 8))
        self.page_warn_label.pack(side="left", padx=5)
        self.pages_var.trace_add("write", self._on_pages_change)

        # Removed difficulty and style to simplify UI. We will use defaults.

        self._add_section_title(main_frame, "Дополнительно")

        self.answers_var = IntVar(value=1)
        Checkbutton(main_frame, text="Добавить ответы",
                    variable=self.answers_var).pack(anchor="w", pady=1)
        self.instruction_var = IntVar(value=1)
        Checkbutton(main_frame, text="Добавить инструкцию для родителя",
                    variable=self.instruction_var).pack(anchor="w", pady=1)

        mode_frame = Frame(main_frame)
        mode_frame.pack(fill="x", pady=1)
        Label(mode_frame, text="Режим работы:", width=25, anchor="w").pack(side="left")
        self.ai_mode_var = StringVar(value="Офлайн (Быстро, шаблоны)")
        modes = ["Офлайн (Быстро, шаблоны)", "DeepSeek", "Groq", "OpenRouter"]
        OptionMenu(mode_frame, self.ai_mode_var, *modes).pack(side="left", fill="x", expand=True)

        name_frame = Frame(main_frame)
        name_frame.pack(fill="x", pady=1)
        Label(name_frame, text="Имя ребёнка (необязательно):", width=25, anchor="w").pack(side="left")
        self.name_var = StringVar()
        Entry(name_frame, textvariable=self.name_var, width=25).pack(side="left")

        out_frame = Frame(main_frame)
        out_frame.pack(fill="x", pady=1)
        Label(out_frame, text="Папка сохранения:", width=25, anchor="w").pack(side="left")
        self.out_dir_var = StringVar(value=output_dir())
        Entry(out_frame, textvariable=self.out_dir_var, width=28).pack(side="left", padx=(0, 3))
        Button(out_frame, text="Обзор", command=self._browse_output).pack(side="left")

        self._add_section_title(main_frame, "")

        btn_frame = Frame(main_frame)
        btn_frame.pack(fill="x", pady=3)

        self.generate_btn = Button(btn_frame, text="Сгенерировать PDF",
                                   font=("Arial", 11, "bold"), bg="#4CAF50", fg="white",
                                   width=18, command=self._on_generate)
        self.generate_btn.pack(side="left", padx=2)

        Button(btn_frame, text="Открыть последний PDF", width=22,
               command=self._open_last_pdf).pack(side="left", padx=2)
        Button(btn_frame, text="Настройки API", width=15,
               command=self._show_api_settings).pack(side="left", padx=2)

        self.status_var = StringVar(value="Готов к работе")
        self.status_label = Label(main_frame, textvariable=self.status_var,
                                  font=("Arial", 9), fg="gray")
        self.status_label.pack(pady=(3, 1))

        self.progress = Progressbar(main_frame, mode="indeterminate")
        self.progress.pack(fill="x", pady=1, padx=20)

    def _add_section_title(self, parent, text):
        if text:
            sep = Frame(parent, height=1, bg="#cccccc")
            sep.pack(fill="x", pady=(6, 2))
            Label(parent, text=text, font=("Arial", 10, "bold"),
                  fg="#333333").pack(anchor="w", pady=(0, 2))

    def _on_pages_change(self, *args):
        try:
            p = int(self.pages_var.get())
            if p > 20:
                self.page_warn_label.config(
                    text="Большой набор (>20 стр) может быть нестабильным. Рекомендуется 8-20."
                )
            else:
                self.page_warn_label.config(text="")
        except ValueError:
            pass

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

    def _open_examples(self):
        examples_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "examples")
        if os.path.isdir(examples_path):
            os.startfile(examples_path)
        else:
            messagebox.showinfo("StudyPack AI", "Папка examples не найдена.")

    def _show_api_settings(self):
        win = Toplevel(self.root)
        win.title("Настройки API")
        win.geometry("450x200")
        win.resizable(False, False)

        try:
            from core.paths import env_file_path
            from dotenv import load_dotenv, set_key
            load_dotenv(env_file_path())
        except ImportError:
            set_key = None

        Frame(win, padx=15, pady=15).pack(fill="both", expand=True)

        Label(win, text="API ключ DeepSeek:").pack(anchor="w")
        ds_api_var = StringVar(value=os.getenv("DEEPSEEK_API_KEY", ""))
        Entry(win, textvariable=ds_api_var, width=50, show="*").pack(fill="x", pady=2)

        Label(win, text="API ключ Groq:").pack(anchor="w")
        groq_api_var = StringVar(value=os.getenv("GROQ_API_KEY", ""))
        Entry(win, textvariable=groq_api_var, width=50, show="*").pack(fill="x", pady=2)

        Label(win, text="API ключ OpenRouter (опционально):").pack(anchor="w", pady=(5, 0))
        or_api_var = StringVar(value=os.getenv("OPENROUTER_API_KEY", ""))
        Entry(win, textvariable=or_api_var, width=50, show="*").pack(fill="x", pady=2)

        def save():
            from core.paths import env_file_path
            env_path = env_file_path()
            
            ds_val = ds_api_var.get()
            groq_val = groq_api_var.get()
            or_val = or_api_var.get()
            
            if set_key:
                set_key(env_path, "DEEPSEEK_API_KEY", ds_val)
                set_key(env_path, "GROQ_API_KEY", groq_val)
                set_key(env_path, "OPENROUTER_API_KEY", or_val)
            else:
                lines = []
                if os.path.exists(env_path):
                    with open(env_path, "r") as f:
                        lines = f.readlines()
                # Basic rewrite for fallback
                with open(env_path, "w") as f:
                    for line in lines:
                        if not any(line.startswith(k) for k in ["DEEPSEEK_API_KEY", "GROQ_API_KEY", "OPENROUTER_API_KEY"]):
                            f.write(line)
                    f.write(f"DEEPSEEK_API_KEY={ds_val}\n")
                    f.write(f"GROQ_API_KEY={groq_val}\n")
                    f.write(f"OPENROUTER_API_KEY={or_val}\n")
                    
            os.environ["DEEPSEEK_API_KEY"] = ds_val
            os.environ["GROQ_API_KEY"] = groq_val
            os.environ["OPENROUTER_API_KEY"] = or_val
            
            messagebox.showinfo("StudyPack AI", "Настройки сохранены.")
            win.destroy()

        Button(win, text="Сохранить", command=save).pack(pady=10)

    def _on_html_preview(self):
        if not self.last_pack_data:
            messagebox.showwarning("StudyPack AI", "Сначала сгенерируйте набор.")
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
                messagebox.showwarning("StudyPack AI", "Сначала сгенерируйте набор.")
                return

        win = Toplevel(self.root)
        win.title("Редактор JSON")
        win.geometry("700x500")

        text_area = scrolledtext.ScrolledText(win, wrap="word", font=("Consolas", 10))
        text_area.pack(fill="both", expand=True, padx=5, pady=5)

        with open(self.last_json_path, "r", encoding="utf-8") as f:
            text_area.insert("1.0", f.read())

        def save_and_rebuild():
            content = text_area.get("1.0", "end-1c")
            try:
                data = json.loads(content)
            except json.JSONDecodeError as e:
                messagebox.showerror("Ошибка", f"Невалидный JSON: {e}")
                return
            with open(self.last_json_path, "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            self.last_pack_data = data
            math_issues = verify_math_in_pack(data)
            msg = "JSON сохранён."
            if math_issues:
                msg += f"\n\nНайдено {len(math_issues)} проблем в математике:"
                for iss in math_issues[:5]:
                    msg += f"\n  Стр.{iss['page']}: {iss['question']} -> ответ '{iss['given_answer']}'"
            messagebox.showinfo("StudyPack AI", msg)
            win.destroy()

        Button(win, text="Сохранить и собрать PDF", command=save_and_rebuild).pack(pady=5)

    def _on_build_from_json(self):
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
            messagebox.showerror("Ошибка", f"Не удалось прочитать JSON: {e}")
            return

        self.last_pack_data = data
        self._build_pdf_from_data(data)

    def _build_pdf_from_data(self, data):
        out_dir = self.out_dir_var.get().strip() or output_dir()
        os.makedirs(out_dir, exist_ok=True)

        age = data.get("age", 7)
        topic = data.get("topic", "custom")
        from datetime import datetime
        date_str = datetime.now().strftime("%Y-%m-%d")
        base_name = f"StudyPack_{age}_{topic}_{date_str}"
        base_name = "".join(c if c.isalnum() or c in "-_" else "_" for c in base_name)

        pdf_path = os.path.join(out_dir, f"{base_name}.pdf")
        try:
            render_pdf(data, pdf_path)
            self.last_pdf_path = pdf_path
            self.last_pack_data = data
            math_issues = verify_math_in_pack(data)
            msg = f"PDF создан:\n{pdf_path}"
            if math_issues:
                msg += f"\n\n⚠ Найдено {len(math_issues)} ошибок в математике."
            messagebox.showinfo("StudyPack AI", msg)
            self.status_var.set(f"PDF создан: {base_name}.pdf")
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось создать PDF: {e}")

    def _on_generate(self):
        try:
            age = int(self.age_var.get())
            if age < 4 or age > 10:
                raise ValueError
        except ValueError:
            messagebox.showerror("Ошибка", "Возраст должен быть числом от 4 до 10.")
            return

        lang_map = {
            "Русский": "ru", "Украинский": "uk", "Английский": "en",
            "Украинский + английский": "uk+en", "Русский + английский": "ru+en",
        }
        language = lang_map.get(self.lang_var.get(), "ru")

        pack_map = {
            "Подготовка к школе": "preschool", "Математика": "math",
            "Чтение": "reading", "Украинский язык": "ukrainian",
            "Английский": "english", "Логика": "logic",
            "Смешанный набор на неделю": "mixed_week",
        }
        pack_type = pack_map.get(self.pack_var.get(), "mixed_week")

        topic_map = {t["name_ru"]: t["id"] for t in self.topics["topics"]}
        topic_id = topic_map.get(self.topic_var.get(), "custom")
        topic = self.custom_topic_var.get().strip() or topic_id if topic_id == "custom" else topic_id

        pages_count = int(self.pages_var.get())

        # Hardcoded defaults for removed UI options
        difficulty = "auto"
        style = "print_bw"

        if pages_count > 20:
            if not messagebox.askyesno("Предупреждение",
                    "Большой набор (>20 страниц) может быть нестабильным при генерации через AI.\n\n"
                    "Рекомендуется 8-20 страниц. Продолжить?"):
                return

        request = PackRequest(
            age=age, grade=self.grade_var.get(), language=language,
            pack_type=pack_type, topic=topic, pages_count=pages_count,
            difficulty=difficulty,
            include_answers=bool(self.answers_var.get()),
            include_parent_instruction=bool(self.instruction_var.get()),
            style=style, child_name=self.name_var.get().strip(),
            output_dir=self.out_dir_var.get().strip() or output_dir(),
        )

        self.generate_btn.config(state="disabled", text="Генерация...")
        self.progress.start()
        self.root.update()

        thread = threading.Thread(
            target=self._generate_thread, args=(request,), daemon=True
        )
        thread.start()

    def _generate_thread(self, request):
        try:
            ai_mode = getattr(self, 'ai_mode_var', None)
            mode_val = ai_mode.get() if ai_mode else "Офлайн (Быстро, шаблоны)"
            offline = mode_val.startswith("Офлайн")

            if offline:
                self.root.after(0, lambda: self.status_var.set("Создание по шаблону (офлайн)..."))
                data = generate_offline(request)
                if data is None:
                    self.root.after(0, lambda: messagebox.showerror(
                        "Ошибка", "Нет шаблона для выбранного типа набора."
                    ))
                    return
                self.last_pack_data = data
                import json as j
                ensure_dirs()
                from datetime import datetime
                date_str = datetime.now().strftime("%Y-%m-%d")
                base = f"StudyPack_{request.age}_{request.topic}_{date_str}"
                base = "".join(c if c.isalnum() or c in "-_" else "_" for c in base)
                json_path = os.path.join(output_dir(), f"{base}.json")
                with open(json_path, "w", encoding="utf-8") as f:
                    j.dump(data, f, ensure_ascii=False, indent=2)
                self.last_json_path = json_path
                self._build_pdf_from_data(data)
                self.root.after(0, lambda: self.status_var.set("Готово! Офлайн-режим."))
                return

            provider_name = mode_val
            generator = StudyPackGenerator(provider=provider_name)
            self.root.after(0, lambda: self.status_var.set(f"Генерация заданий через {provider_name}..."))
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

                checklist = []
                checklist.append(f"[✓] PDF создан: {os.path.basename(result.pdf_path)}")
                checklist.append(f"[✓] JSON сохранён: {os.path.basename(result.json_path)}")
                checklist.append(f"[✓] Путь: {result.pdf_path}")

                brand_check = "пройдена" if not result.warnings else "есть предупреждения"
                checklist.append(f"[{ '✓' if not result.warnings else '!' }] Проверка брендов: {brand_check}")

                if math_issues:
                    checklist.append(f"[!] Математика: {len(math_issues)} ошибок")
                    for iss in math_issues[:5]:
                        checklist.append(f"     Стр.{iss['page']}: {iss['question']} -> '{iss['given_answer']}'")
                else:
                    checklist.append("[✓] Математика: проверена, ошибок нет")

                if result.warnings:
                    checklist.append(f"[!] Предупреждения:")
                    for w in result.warnings[:5]:
                        checklist.append(f"     {w}")

                msg = "\n".join(checklist)

                self.root.after(0, lambda: self.status_var.set(
                    f"Готово! PDF: {os.path.basename(result.pdf_path)}"
                ))
                self.root.after(0, lambda: messagebox.showinfo("StudyPack AI — результат", msg))
            else:
                self.root.after(0, lambda: self.status_var.set(
                    f"Ошибка: {result.error[:60]}..."
                ))
                self.root.after(0, lambda: messagebox.showerror("Ошибка", result.error))
        except Exception as e:
            self.root.after(0, lambda: self.status_var.set("Критическая ошибка"))
            self.root.after(0, lambda: messagebox.showerror("Критическая ошибка", str(e)))
        finally:
            self.root.after(0, lambda: self.generate_btn.config(state="normal", text="Сгенерировать PDF"))
            self.root.after(0, lambda: self.progress.stop())

    def _check_for_updates_silently(self):
        def worker():
            from core.updater import check_for_update
            update_info = check_for_update(VERSION)
            if update_info:
                self.root.after(0, lambda: self._prompt_update(update_info))
        threading.Thread(target=worker, daemon=True).start()

    def _prompt_update(self, update_info):
        changelog = update_info.get("changelog", "Нет описания изменений.")
        msg = f"Доступна новая версия v{update_info['version']}!\n\nЧто нового:\n{changelog}\n\nХотите обновить программу сейчас?"
        if messagebox.askyesno("Доступно обновление", msg):
            self._start_update_process(update_info)

    def _start_update_process(self, update_info):
        from core.updater import download_update, verify_sha256, apply_update, get_current_exe_path
        from tkinter.ttk import Progressbar
        
        win = Toplevel(self.root)
        win.title("Обновление StudyPack AI")
        win.geometry("400x160")
        win.resizable(False, False)
        win.transient(self.root)
        win.grab_set()
        
        lbl = Label(win, text=f"Загрузка обновления v{update_info['version']}...", font=("Arial", 10, "bold"))
        lbl.pack(pady=(20, 10))
        
        progress = Progressbar(win, length=320, mode='determinate')
        progress.pack(pady=10)
        
        status_lbl = Label(win, text="0%", font=("Arial", 9))
        status_lbl.pack()
        
        def progress_callback(fraction):
            self.root.after(0, lambda: progress.config(value=fraction * 100))
            self.root.after(0, lambda: status_lbl.config(text=f"{int(fraction * 100)}%"))
            
        def download_worker():
            import tempfile
            temp_dir = os.path.join(tempfile.gettempdir(), "StudyPackAIUpdate")
            new_exe_name = "StudyPack_AI_new.exe"
            new_exe_path = os.path.join(temp_dir, new_exe_name)
            
            # Download file
            success = download_update(update_info["download_url"], new_exe_path, progress_callback)
            if not success:
                self.root.after(0, lambda: messagebox.showerror("Ошибка", "Не удалось скачать обновление. Проверьте интернет."))
                self.root.after(0, win.destroy)
                return
                
            # Verify SHA-256
            self.root.after(0, lambda: lbl.config(text="Проверка целостности файла..."))
            if not verify_sha256(new_exe_path, update_info["sha256"]):
                self.root.after(0, lambda: messagebox.showerror("Ошибка", "Проверка хэша SHA-256 не удалась. Файл повреждён."))
                self.root.after(0, win.destroy)
                return
                
            # Apply update
            self.root.after(0, lambda: lbl.config(text="Применение обновления, перезапуск..."))
            self.root.after(800, lambda: apply_update(new_exe_path, get_current_exe_path()))
            
        threading.Thread(target=download_worker, daemon=True).start()

    def run(self):
        self.root.mainloop()

