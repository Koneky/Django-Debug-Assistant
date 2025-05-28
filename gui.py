import json
import os
import logging
import threading
import tkinter as tk
from tkinter import scrolledtext

from theme import *
from history import History
from updater import update_errors


logging.basicConfig(
    filename='debug_assistant.log',
    level=logging.DEBUG,
    encoding='utf-8',
    format='%(asctime)s - %(levelname)s - %(message)s'
)

ERRORS_JSON = 'errors.json'


class DjangoDebugAssistant(tk.Tk):
    def __init__(self):
        try:
            super().__init__()
            self.title('Django Debug Assistant')
            self.geometry('800x600')
            self.configure(bg=DARK_BG)
            self.errors = []
            self.history = History()

            self.create_widgets()
            self.load_errors()
            self.populate_list()
        except:
            logging.exception('Ошибка при инициализации приложения')

    def create_widgets(self):
        try:
            search_frame = tk.Frame(self, bg=DARK_BG)
            search_frame.pack(fill=tk.X, padx=10, pady=5)
        except:
            logging.exception('Ошибка при создании строки поиска')

        try:
            tk.Label(search_frame, text='Поиск по ошибке:', fg=DARK_FG, bg=DARK_BG).pack(side=tk.LEFT)
            self.search_var = tk.StringVar()
            self.search_entry = tk.Entry(search_frame, textvariable=self.search_var, width=40, bg=DARK_ENTRY_BG, fg=DARK_FG, insertbackground=DARK_FG)
            self.search_entry.pack(side=tk.LEFT, padx=5)
            self.search_entry.bind("<KeyRelease>", self.on_search)
        except:
            logging.exception('Ошибка при создании Label к строке поиска')

        try:
            self.update_btn = tk.Button(search_frame, text='Обновить ошибки из Git', command=self.update_errors_from_git, bg=BUTTON_BG, fg=BUTTON_FG)
            self.update_btn.pack(side=tk.RIGHT)
        except:
            logging.exception('Ошибка при создании кнопки обновления из Git')
        
        # ------------ Список истории (слева) ------------
        try:
            history_frame = tk.Frame(self, bg=DARK_BG)
            history_frame.pack(side=tk.LEFT, fill=tk.Y, padx=10, pady=5)
        except:
            logging.exception('Ошибка создания поля списка ошибок')

        try:
            tk.Label(history_frame, text='История ошибок:', fg=DARK_FG, bg=DARK_BG).pack()
            self.history_listbox = tk.Listbox(history_frame, width=30, bg=DARK_ENTRY_BG, fg=DARK_FG, selectbackground=DARK_SELECT_BG)
            self.history_listbox.pack(expand=True, fill=tk.Y)
            self.history_listbox.bind("<<ListboxSelect>>", lambda event: self.on_error_select(event, source='history'))
        except:
            logging.exception('Ошибка при создании Label к полю для вывода истории ошибок')

        try:
            self.clear_history_btn = tk.Button(list_frame, text='Очистить историю', command=self.clear_history, bg=BUTTON_BG, fg=BUTTON_FG)
            self.clear_history_btn.pack(pady=5)
        except:
            logging.exception('Ошибка при создании кнопки с очисткой поля истории')

        # ------------ Список ошибок (справа) ------------
        try:
            list_frame = tk.Frame(self, bg=DARK_BG)
            list_frame.pack(side=tk.LEFT, fill=tk.Y, padx=10, pady=5)
        except:
            logging.exception('Ошибка при создании поля для вывода списка ошибок')

        try:
            tk.Label(list_frame, text='Результаты поиска:', fg=DARK_FG, bg=DARK_BG).pack()
            self.error_listbox = tk.Listbox(list_frame, width=40, bg=DARK_ENTRY_BG, fg=DARK_FG, selectbackground=DARK_SELECT_BG)
            self.error_listbox.pack(expand=True, fill=tk.Y)
            self.error_listbox.bind("<<ListboxSelect>>", lambda event: self.on_error_select(event, source='search'))
        except:
            logging.exception('Ошибка при создании Label для поля результатов поиска')

        try:
            detail_frame = tk.Frame(self, bg=DARK_BG)
            detail_frame.pack(side=tk.RIGHT, expand=True, fill=tk.BOTH, padx=10, pady=5)
        except:
            logging.exception('Ошибка при создании поля для вывода решения ошибок')

        try:
            tk.Label(detail_frame, text='Решение:', fg=DARK_FG, bg=DARK_BG).pack(anchor="w")
            self.solution_text = scrolledtext.ScrolledText(detail_frame, wrap=tk.WORD, bg=TEXT_BG, fg=DARK_FG, font=FONT)
            self.solution_text.pack(expand=True, fill=tk.BOTH)
        except:
            logging.exception('Ошибка при создании Label к полю для решения ошибок')

        try:
            self.log_label = tk.Label(self, text='', fg=GREEN, bg=DARK_BG)
            self.log_label.pack(pady=5)
        except:
            logging.exception('Ошибка при создании Label для логирования ошибок')
    
    def load_errors(self):
        if not os.path.exists(ERRORS_JSON):
            self.errors = []
            return
        try:
            with open(ERRORS_JSON, 'r', encoding='utf-8') as f:
                self.errors = json.load(f)
        except:
            logging.exception('Ошибка при загрузке файла с ошибками')

    
    def populate_list(self, filter_text = ''):
        self.error_listbox.delete(0, tk.END)

        filtered = [e for e in self.errors if filter_text.lower() in e['keyword'].lower()]
        
        try:
            for e in filtered:
                self.error_listbox.insert(tk.END, e['keyword'])
        except:
            logging.exception('Ошибка при построении истории запросов')

    
    def on_search(self, event = None):
        try:
            text = self.search_var.get()
            self.populate_list(text)
        except:
            logging.exception('Ошибка при посике решения ошибки')

    
    def on_error_select(self, event, source = 'search'):
        listbox = self.error_listbox if source == 'search' else self.history_listbox

        if not listbox.curselection():
            return
        
        try:
            idx = listbox.curselection()[0]
            keyword = listbox.get(idx)

            soluton = next((e['solution'] for e in self.errors if e['keyword'] == keyword), 'Решение не найдено.')

            self.solution_text.delete('1.0', tk.END)
            self.solution_text.insert(tk.END, soluton)

            if source == 'search':
                self.history.add(keyword)
                self.refresh_history()
        except:
            logging.exception('Ошибка при выборе редения на ошибку')


    def refresh_history(self):
        try:
            self.history_listbox.delete(0, tk.END)

            for k in self.history.get_all():
                self.history_listbox.insert(tk.END, k)
        except:
            logging.exception('Ошибка при обновлении истории поиска')


    def clear_history(self):
        try:
            self.history.clear()
            self.refresh_history()
            self.solution_text.delete('1.0', tk.END)
        except:
            logging.exception('Ошибка при очистке истории поиска')


    def update_errors_from_git(self):
        try:
            self.log_label.config(text='Обновление... Подождите...', fg=YELLOW)
            self.update_btn.config(state=tk.DISABLED)
            threading.Thread(target=self._git_pull_thread, daemon=True).start()
        except:
            logging.exception('Ошибка при обновлении списка ошибок из Git')


    def _git_pull_thread(self):
        try:
            data = update_errors()
            self.errors = data
            self.populate_list(self.search_var.get())
            self.log_label.config(text='Ошибки успешно обновлены из Git!!', fg=GREEN)
            logging.info('Обновление прошло успешно')
        except Exception as e:
            self.log_label.config(text=f'Ошибка обновления: {str(e)}', fg=RED)
            logging.exception(f'Ошибка пула из Git {e}')
        finally:
            self.update_btn.config(state=tk.NORMAL)


if __name__ == '__main__':
    try:
        app = DjangoDebugAssistant()
        app.mainloop()
    except Exception as e:
        logging.exception(f'Ошибка при щапуске приложения {e}')
