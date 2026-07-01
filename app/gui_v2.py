import json
import os
import sys
import threading
import webbrowser
from tkinter import messagebox, filedialog, scrolledtext, Toplevel
import customtkinter as ctk

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

ctk.set_appearance_mode("system")
ctk.set_default_color_theme("blue")


class StudyPackGUI(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("StudyPack AI")
        self.geometry("860x960")
        self.resizable(False, False)
        self.minsize(860, 960)

        try:
            from core.paths import logo_path
            icon_path = logo_path()
            if os.path.exists(icon_path):
                self.iconbitmap(icon_path)
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
        main = ctk.CTkScrollableFrame(self, label_text="")
        main.pack(fill="both", expand=True, padx=18, pady=8)

        ctk.CTkLabel(main, text="StudyPack AI", font=("Segoe UI", 26, "bold")).pack(pady=(4, 2))
        ctk.CTkLabel(main, text="PDF-задания для детей 4-10 лет",
                      font=("Segoe UI", 11)).pack(pady=(0, 14))

        sec_child = ctk.CTkFrame(main)
        sec_child.pack(fill="x", pady=(0, 10), padx=2)
        ctk.CTkLabel(sec_child, text="    Параметры ребёнка",
                      font=("Segoe UI", 14, "bold")).pack(anchor="w", pady=(10, 6), padx=12)

        row = ctk.CTkFrame(sec_child, fg_color="transparent")
        row.pack(fill="x", padx=18, pady=3)
        ctk.CTkLabel(row, text="Возраст:", width=140, anchor="w").pack(side="left")
        self.age_var = ctk.StringVar(value="7")
        self.age_entry = ctk.CTkEntry(row, textvariable=self.age_var, width=60)
        self.age_entry.pack(side="left")

        row2 = ctk.CTkFrame(sec_child, fg_color="transparent")
        row2.pack(fill="x", padx=18, pady=3)
        ctk.CTkLabel(row2, text="Уровень:", width=140, anchor="w").pack(side="left")
        self.grade_var = ctk.StringVar(value="Дошкольник")
        grades = ["Дошкольник", "1 класс", "2 класс", "3 класс", "4 класс",
                   "Автоподбор"]
        ctk.CTkOptionMenu(row2, variable=self.grade_var, values=grades,
                           width=220).pack(side="left")

        row3 = ctk.CTkFrame(sec_child, fg_color="transparent")
        row3.pack(fill="x", padx=18, pady=3)
        ctk.CTkLabel(row3, text="Язык:", width=140, anchor="w").pack(side="left")
        self.lang_var = ctk.StringVar(value="Русский")
        langs = ["Русский", "Украинский", "Английский",
                  "Украинский + английский", "Русский + английский"]
        ctk.CTkOptionMenu(row3, variable=self.lang_var, values=langs,
                           width=220).pack(side="left")

        sec_pack = ctk.CTkFrame(main)
        sec_pack.pack(fill="x", pady=(0, 10), padx=2)
        ctk.CTkLabel(sec_pack, text="    Параметры набора",
                      font=("Segoe UI", 14, "bold")).pack(anchor="w", pady=(10, 6), padx=12)

        row4 = ctk.CTkFrame(sec_pack, fg_color="transparent")
        row4.pack(fill="x", padx=18, pady=3)
        ctk.CTkLabel(row4, text="Тип:", width=140, anchor="w").pack(side="left")
        self.pack_var = ctk.StringVar(value="Смешанный набор (неделя)")
        packs = ["Подготовка к школе", "Математика", "Чтение",
                  "Украинский язык", "Английский", "Логика",
                  "Смешанный набор (неделя)"]
        ctk.CTkOptionMenu(row4, variable=self.pack_var, values=packs, width=260).pack(side="left")

        row5 = ctk.CTkFrame(sec_pack, fg_color="transparent")
        row5.pack(fill="x", padx=18, pady=3)
        ctk.CTkLabel(row5, text="Тема:", width=140, anchor="w").pack(side="left")
        topic_names = [t["name_ru"] for t in self.topics["topics"] if t["id"] != "custom"]
        topic_names.append("Своя тема")
        self.topic_var = ctk.StringVar(value="Динозавры")
        ctk.CTkOptionMenu(row5, variable=self.topic_var, values=topic_names,
                           width=260).pack(side="left")

        row5b = ctk.CTkFrame(sec_pack, fg_color="transparent")
        row5b.pack(fill="x", padx=18, pady=3)
        ctk.CTkLabel(row5b, text="Своя тема:", width=140, anchor="w").pack(side="left")
        self.custom_topic_var = ctk.StringVar()
        ctk.CTkEntry(row5b, textvariable=self.custom_topic_var, width=260,
                      placeholder_text="например: Minecraft, футбол...").pack(side="left")

        row6 = ctk.CTkFrame(sec_pack, fg_color="transparent")
        row6.pack(fill="x", padx=18, pady=3)
        ctk.CTkLabel(row6, text="Страниц:", width=140, anchor="w").pack(side="left")
        self.pages_var = ctk.StringVar(value="12")
        ctk.CTkOptionMenu(row6, variable=self.pages_var, values=["8", "12", "20", "30", "40"],
                           width=80).pack(side="left")
        self.page_warn_label = ctk.CTkLabel(row6, text="", text_color="orange", font=("", 10))
        self.page_warn_label.pack(side="left", padx=6)
        self.pages_var.trace_add("write", self._on_pages_change)

        sec_extra = ctk.CTkFrame(main)
        sec_extra.pack(fill="x", pady=(0, 10), padx=2)
        ctk.CTkLabel(sec_extra, text="    Дополнительно",
                      font=("Segoe UI", 14, "bold")).pack(anchor="w", pady=(10, 6), padx=12)

        opt_row = ctk.CTkFrame(sec_extra, fg_color="transparent")
        opt_row.pack(fill="x", padx=18, pady=3)
        self.answers_var = ctk.BooleanVar(value=True)
        ctk.CTkSwitch(opt_row, text="Ответы", variable=self.answers_var).pack(side="left")
        self.instruction_var = ctk.BooleanVar(value=True)
        ctk.CTkSwitch(opt_row, text="Инструкция для родителя",
                       variable=self.instruction_var).pack(side="left", padx=(20, 0))

        mode_frame = ctk.CTkFrame(sec_extra, fg_color="transparent")
        mode_frame.pack(fill="x", padx=18, pady=3)
        ctk.CTkLabel(mode_frame, text="Режим:", width=140, anchor="w").pack(side="left")
        self.ai_mode_var = ctk.StringVar(value="Офлайн (шаблоны)")
        modes = ["Офлайн (шаблоны)", "DeepSeek", "Groq", "OpenRouter"]
        ctk.CTkOptionMenu(mode_frame, variable=self.ai_mode_var,
                           values=modes, width=220).pack(side="left")

        row7 = ctk.CTkFrame(sec_extra, fg_color="transparent")
        row7.pack(fill="x", padx=18, pady=3)
        ctk.CTkLabel(row7, text="Имя ребёнка:", width=140, anchor="w").pack(side="left")
        self.name_var = ctk.StringVar()
        ctk.CTkEntry(row7, textvariable=self.name_var, width=240,
                      placeholder_text="опционально").pack(side="left")

        row8 = ctk.CTkFrame(sec_extra, fg_color="transparent")
        row8.pack(fill="x", padx=18, pady=3)
        ctk.CTkLabel(row8, text="Папка:", width=140, anchor="w").pack(side="left")
        self.out_dir_var = ctk.StringVar(value=output_dir())
        ctk.CTkEntry(row8, textvariable=self.out_dir_var, width=280).pack(side="left", padx=(0, 6))
        ctk.CTkButton(row8, text="...", width=38, fg_color="#555555",
                       hover_color="#777777", command=self._browse_output).pack(side="left")

        ctk.CTkLabel(main, text="", height=4).pack()

        self.generate_btn = ctk.CTkButton(
            main, text="   Сгенерировать PDF   ",
            font=("Segoe UI", 16, "bold"),
            height=52, corner_radius=12,
            fg_color="#2E7D32", hover_color="#1B5E20",
            command=self._on_generate
        )
        self.generate_btn.pack(fill="x", padx=4, pady=(4, 0))

        self.status_var = ctk.StringVar(value="Готов к работе")
        self.status_label = ctk.CTkLabel(main, textvariable=self.status_var,
                                          font=("Segoe UI", 10), text_color="gray")
        self.status_label.pack(pady=(6, 2))

        self.progress = ctk.CTkProgressBar(main, mode="indeterminate")
        self.progress.pack(fill="x", padx=20, pady=(0, 8))

        self.progress.configure(mode="indeterminate")
        self.progress.start()
        self.progress.stop()

        btn_row = ctk.CTkFrame(main, fg_color="transparent")
        btn_row.pack(fill="x", pady=(6, 4))

        ctk.CTkButton(btn_row, text="Открыть PDF", width=160,
                       fg_color="#3b82f6", hover_color="#2563eb",
                       command=self._open_last_pdf).pack(side="left", padx=(0, 4))
        ctk.CTkButton(btn_row, text="Открыть папку", width=160,
                       fg_color="#64748b", hover_color="#475569",
                       command=self._open_output).pack(side="left", padx=4)
        ctk.CTkButton(btn_row, text="API настройки", width=160,
                       fg_color="#64748b", hover_color="#475569",
                       command=self._show_api_settings).pack(side="left", padx=4)

    def _on_pages_change(self, *args):
        try:
            p = int(self.pages_var.get())
            if p > 20:
                self.page_warn_label.configure(text="Рекомендуется 8-20 стр.")
            else:
                self.page_warn_label.configure(text="")
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
        win = ctk.CTkToplevel(self)
        win.title("Настройки API")
        win.geometry("520x380")
        win.resizable(False, False)

        try:
            from core.paths import env_file_path
            from dotenv import load_dotenv, set_key
            load_dotenv(env_file_path())
        except ImportError:
            set_key = None

        inner = ctk.CTkFrame(win)
        inner.pack(fill="both", expand=True, padx=20, pady=20)

        ctk.CTkLabel(inner, text="API ключи", font=("Segoe UI", 16, "bold")).pack(anchor="w", pady=(0, 10))

        ctk.CTkLabel(inner, text="Groq (основной):").pack(anchor="w")
        groq_api_var = ctk.StringVar(value=os.getenv("GROQ_API_KEY", ""))
        ctk.CTkEntry(inner, textvariable=groq_api_var, show="*", width=440).pack(fill="x", pady=2)

        ctk.CTkLabel(inner, text="DeepSeek (fallback):").pack(anchor="w", pady=(10, 0))
        ds_api_var = ctk.StringVar(value=os.getenv("DEEPSEEK_API_KEY", ""))
        ctk.CTkEntry(inner, textvariable=ds_api_var, show="*", width=440).pack(fill="x", pady=2)

        ctk.CTkLabel(inner, text="OpenRouter (опционально):").pack(anchor="w", pady=(10, 0))
        or_api_var = ctk.StringVar(value=os.getenv("OPENROUTER_API_KEY", ""))
        ctk.CTkEntry(inner, textvariable=or_api_var, show="*", width=440).pack(fill="x", pady=2)

        ctk.CTkLabel(inner, text="Gemini (опционально):").pack(anchor="w", pady=(10, 0))
        gm_api_var = ctk.StringVar(value=os.getenv("GEMINI_API_KEY", ""))
        ctk.CTkEntry(inner, textvariable=gm_api_var, show="*", width=440).pack(fill="x", pady=2)

        def save():
            from core.paths import env_file_path
            env_path = env_file_path()

            keys = {
                "GROQ_API_KEY": groq_api_var.get(),
                "DEEPSEEK_API_KEY": ds_api_var.get(),
                "OPENROUTER_API_KEY": or_api_var.get(),
                "GEMINI_API_KEY": gm_api_var.get(),
            }

            if set_key:
                for k, v in keys.items():
                    set_key(env_path, k, v)
            else:
                lines = []
                if os.path.exists(env_path):
                    with open(env_path, "r") as f:
                        lines = f.readlines()
                with open(env_path, "w") as f:
                    for line in lines:
                        if not any(line.startswith(k) for k in keys.keys()):
                            f.write(line)
                    for k, v in keys.items():
                        f.write(f"{k}={v}\n")

            for k, v in keys.items():
                os.environ[k] = v

            messagebox.showinfo("StudyPack AI", "Настройки сохранены.")
            win.destroy()

        ctk.CTkButton(inner, text="Сохранить", height=42, corner_radius=8,
                       fg_color="#2E7D32", hover_color="#1B5E20",
                       command=save).pack(pady=(18, 0))

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

        win = ctk.CTkToplevel(self)
        win.title("Редактор JSON")
        win.geometry("700x500")

        text_area = scrolledtext.ScrolledText(win, wrap="word", font=("Consolas", 10),
                                                bg="#1e1e1e", fg="#d4d4d4")
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

        ctk.CTkButton(win, text="Сохранить и собрать PDF", command=save_and_rebuild).pack(pady=5)

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
            "Смешанный набор (неделя)": "mixed_week",
        }
        pack_type = pack_map.get(self.pack_var.get(), "mixed_week")

        topic_map = {t["name_ru"]: t["id"] for t in self.topics["topics"]}
        topic_id = topic_map.get(self.topic_var.get(), "custom")
        topic = self.custom_topic_var.get().strip() or topic_id if topic_id == "custom" else topic_id

        pages_count = int(self.pages_var.get())

        difficulty = "auto"
        style = "print_bw"

        if pages_count > 20:
            if not messagebox.askyesno("Предупреждение",
                    "Большой набор (>20 страниц) может быть нестабильным.\n\n"
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

        self.generate_btn.configure(state="disabled", text="Генерация...")
        self.progress.start()
        self.update()

        thread = threading.Thread(
            target=self._generate_thread, args=(request,), daemon=True
        )
        thread.start()

    def _generate_thread(self, request):
        try:
            mode_val = self.ai_mode_var.get()
            offline = mode_val.startswith("Офлайн")

            if offline:
                self.after(0, lambda: self.status_var.set("Создание по шаблону (офлайн)..."))
                data = generate_offline(request)
                if data is None:
                    self.after(0, lambda: messagebox.showerror(
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
                self.after(0, lambda: self.status_var.set("Готово! Офлайн-режим."))
                return

            provider_name = mode_val
            generator = StudyPackGenerator(provider=provider_name)
            self.after(0, lambda: self.status_var.set(f"Генерация через {provider_name}..."))
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
                checklist.append(f"[OK] PDF: {os.path.basename(result.pdf_path)}")
                checklist.append(f"[OK] JSON: {os.path.basename(result.json_path)}")
                checklist.append(f"[OK] Путь: {result.pdf_path}")

                if math_issues:
                    checklist.append(f"[!] Мат: {len(math_issues)} ошибок")
                    for iss in math_issues[:5]:
                        checklist.append(f"    Стр.{iss['page']}: {iss['question']} -> '{iss['given_answer']}'")
                else:
                    checklist.append("[OK] Мат проверена")

                if result.warnings:
                    checklist.append(f"[!] Предупреждения:")
                    for w in result.warnings[:5]:
                        checklist.append(f"    {w}")

                msg = "\n".join(checklist)

                self.after(0, lambda: self.status_var.set(f"Готово! {os.path.basename(result.pdf_path)}"))
                self.after(0, lambda m=msg: messagebox.showinfo("StudyPack AI", m))
            else:
                self.after(0, lambda: self.status_var.set(f"Ошибка: {result.error[:60]}..."))
                self.after(0, lambda e=result.error: messagebox.showerror("Ошибка", e))
        except Exception as e:
            self.after(0, lambda: self.status_var.set("Критическая ошибка"))
            self.after(0, lambda ex=e: messagebox.showerror("Критическая ошибка", str(ex)))
        finally:
            self.after(0, lambda: self.generate_btn.configure(state="normal", text="   Сгенерировать PDF   "))
            self.after(0, lambda: self.progress.stop())

    def _check_for_updates_silently(self):
        def worker():
            from core.updater import check_for_update
            update_info = check_for_update(VERSION)
            if update_info:
                self.after(0, lambda: self._prompt_update(update_info))
        threading.Thread(target=worker, daemon=True).start()

    def _prompt_update(self, update_info):
        changelog = update_info.get("changelog", "Нет описания изменений.")
        msg = f"Доступна новая версия v{update_info['version']}!\n\nЧто нового:\n{changelog}\n\nОбновить?"
        if messagebox.askyesno("Доступно обновление", msg):
            self._start_update_process(update_info)

    def _start_update_process(self, update_info):
        from core.updater import download_update, verify_sha256, apply_update, get_current_exe_path

        win = ctk.CTkToplevel(self)
        win.title("Обновление StudyPack AI")
        win.geometry("440x180")
        win.resizable(False, False)
        win.transient(self)
        win.grab_set()

        ctk.CTkLabel(win, text=f"Загрузка обновления v{update_info['version']}...",
                      font=("Segoe UI", 12, "bold")).pack(pady=(24, 12))

        progress = ctk.CTkProgressBar(win, width=340)
        progress.pack(pady=10)
        progress.set(0)

        status_lbl = ctk.CTkLabel(win, text="0%", font=("Segoe UI", 10))
        status_lbl.pack()

        def progress_callback(fraction):
            self.after(0, lambda: progress.set(fraction))
            self.after(0, lambda: status_lbl.configure(text=f"{int(fraction * 100)}%"))

        def download_worker():
            import tempfile
            temp_dir = os.path.join(tempfile.gettempdir(), "StudyPackAIUpdate")
            new_exe_name = "StudyPack_AI_new.exe"
            new_exe_path = os.path.join(temp_dir, new_exe_name)

            success = download_update(update_info["download_url"], new_exe_path, progress_callback)
            if not success:
                self.after(0, lambda: messagebox.showerror("Ошибка", "Не удалось скачать обновление."))
                self.after(0, win.destroy)
                return

            self.after(0, lambda: ctk.CTkLabel(win, text="Проверка целостности...").pack())
            if not verify_sha256(new_exe_path, update_info["sha256"]):
                self.after(0, lambda: messagebox.showerror("Ошибка", "Хэш SHA-256 не совпал."))
                self.after(0, win.destroy)
                return

            self.after(0, lambda: ctk.CTkLabel(win, text="Применение, перезапуск...").pack())
            self.after(1000, lambda: apply_update(new_exe_path, get_current_exe_path()))

        threading.Thread(target=download_worker, daemon=True).start()

    def run(self):
        self.mainloop()
