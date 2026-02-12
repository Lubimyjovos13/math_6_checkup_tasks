import sys
import random
import math
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QVBoxLayout, QHBoxLayout, QWidget,
    QPushButton, QLabel, QLineEdit, QGridLayout, QFrame, QScrollArea,
    QDialog, QFormLayout, QSlider  # Добавлены для окна настроек
)
from PyQt5.QtCore import Qt, QSettings
from PyQt5.QtGui import QFont, QPalette, QColor
from fractions import Fraction


class SettingsDialog(QDialog):
    def __init__(self, parent=None, text_scale=1.0, ui_scale=1.0):
        super().__init__(parent)
        self.setWindowTitle("Настройки")
        self.setGeometry(300, 300, 400, 200)

        layout = QFormLayout()

        self.text_scale_slider = QSlider(Qt.Horizontal)
        self.text_scale_slider.setMinimum(50)  # 0.5x
        self.text_scale_slider.setMaximum(200) # 2.0x
        self.text_scale_slider.setValue(int(text_scale * 100))
        self.text_scale_slider.valueChanged.connect(self.on_text_scale_changed)
        layout.addRow("Размер текста и задания:", self.text_scale_slider)

        self.ui_scale_slider = QSlider(Qt.Horizontal)
        self.ui_scale_slider.setMinimum(50)  # 0.5x
        self.ui_scale_slider.setMaximum(200) # 2.0x
        self.ui_scale_slider.setValue(int(ui_scale * 100))
        self.ui_scale_slider.valueChanged.connect(self.on_ui_scale_changed)
        layout.addRow("Размер клавиатуры и кнопок:", self.ui_scale_slider)

        close_button = QPushButton("Закрыть")
        close_button.clicked.connect(self.accept)
        layout.addRow(close_button)

        self.setLayout(layout)

    def on_text_scale_changed(self, value):
        scale = value / 100.0
        self.parent().apply_text_scaling(scale)

    def on_ui_scale_changed(self, value):
        scale = value / 100.0
        self.parent().apply_ui_scaling(scale)

    def get_values(self):
        return self.text_scale_slider.value() / 100.0, self.ui_scale_slider.value() / 100.0


# Абстрактный базовый класс для задания
class BaseTask(QWidget):
    def __init__(self, text_scale=1.0, ui_scale=1.0):
        super().__init__()
        self.text_scale = text_scale
        self.ui_scale = ui_scale
        self.layout = QVBoxLayout()
        self.setLayout(self.layout)

    def generate_task(self):
        raise NotImplementedError

    def check_answer(self):
        raise NotImplementedError

    def reset_task(self):
        raise NotImplementedError

    def apply_text_scaling(self, scale):
        self.text_scale = scale
        # Этот метод должен быть переопределен в каждом конкретном задании
        pass

    def apply_ui_scaling(self, scale):
        self.ui_scale = scale
        # Этот метод должен быть переопределен в каждом конкретном задании
        pass

class Task1(BaseTask):
    def __init__(self, text_scale=1.0, ui_scale=1.0):
        super().__init__(text_scale, ui_scale)

        # Создаем ScrollArea
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setStyleSheet("border: none;")
        # Виджет внутри ScrollArea
        self.scroll_content = QWidget()
        self.scroll_layout = QVBoxLayout(self.scroll_content)
        self.scroll_layout.setAlignment(Qt.AlignTop)

        self.label = QLabel("Нажмите 'Новый пример', чтобы начать.")
        self.label.setAlignment(Qt.AlignCenter)
        font = QFont()
        font.setPointSize(int(60 * self.text_scale))
        self.label.setFont(font)

        self.input_field = QLineEdit()
        self.input_field.setAlignment(Qt.AlignCenter)
        self.input_field.setStyleSheet(f"""
            QLineEdit {{
                background-color: white;
                border: 2px solid #ccc;
                border-radius: 8px;
                padding: 8px;
                font-size: {int(60 * self.text_scale)}px;
                color: black;
                width: {int(300 * self.text_scale)}px;
                height: {int(60 * self.text_scale)}px;
            }}
            QLineEdit:focus {{
                border: 2px solid #007acc;
            }}
        """)

        self.result_label = QLabel("")
        self.result_label.setAlignment(Qt.AlignCenter)
        self.result_label.setStyleSheet(f"font-size: {int(60 * self.text_scale)}px;")
        self.result_label.hide()

        self.submit_btn = QPushButton("Проверить")
        self.next_btn = QPushButton("Продолжить")
        self.next_btn.setVisible(False)

        # Стиль кнопок
        button_style = f"""
            QPushButton {{
                background-color: #f0f0f0;
                border: 1px solid #ccc;
                border-radius: 6px;
                padding: 8px 16px;
                font-size: {int(60 * self.text_scale)}px;
                color: black;
                min-width: {int(100 * self.ui_scale)}px;
                min-height: {int(50 * self.ui_scale)}px;
            }}
            QPushButton:hover {{
                background-color: #e0e0e0;
            }}
            QPushButton:pressed {{
                background-color: #d0d0d0;
            }}
            QPushButton:disabled {{
                background-color: #cccccc;
                color: #888888;
            }}
        """
        self.submit_btn.setStyleSheet(button_style)
        self.next_btn.setStyleSheet(button_style)

        self.a = 0
        self.b = 0
        self.c = 0
        self.correct_answer = 0

        self.scroll_layout.addWidget(self.label)
        self.scroll_layout.addSpacing(int(20 * self.text_scale))
        self.scroll_layout.addWidget(self.input_field)
        self.setup_virtual_keyboard(self.scroll_layout)
        self.scroll_layout.addWidget(self.submit_btn)
        self.scroll_layout.addWidget(self.result_label)
        self.scroll_layout.addWidget(self.next_btn)

        # Устанавливаем контент в scroll area
        self.scroll_area.setWidget(self.scroll_content)
        # Добавляем scroll area в основной layout (от BaseTask)
        self.layout.addWidget(self.scroll_area)

        self.submit_btn.clicked.connect(self.check_answer)
        self.next_btn.clicked.connect(self.reset_task)

    def setup_virtual_keyboard(self, parent_layout):
        self.keyboard_layout = QGridLayout() # Сделаем его атрибутом класса
        self.keyboard_buttons = [] # Список кнопок клавиатуры

        buttons = [
            ['1', '2', '3'],
            ['4', '5', '6'],
            ['7', '8', '9'],
            ['0', '-', ',']
        ]

        for i, row in enumerate(buttons):
            button_row = []
            for j, char in enumerate(row):
                btn = QPushButton(char)
                btn.clicked.connect(lambda _, s=char: self.append_to_input(s))
                btn.setStyleSheet(f"""
                    QPushButton {{
                        background-color: #ffffff;
                        border: 1px solid #ddd;
                        border-radius: 6px;
                        padding: 8px;
                        font-size: {int(60 * self.text_scale)}px;
                        color: black;
                        min-width: {int(60 * self.ui_scale)}px;
                        min-height: {int(60 * self.ui_scale)}px;
                    }}
                    QPushButton:hover {{
                        background-color: #f5f5f5;
                    }}
                """)
                self.keyboard_layout.addWidget(btn, i, j)
                button_row.append(btn)
            self.keyboard_buttons.append(button_row)

        parent_layout.addLayout(self.keyboard_layout)

    def append_to_input(self, char):
        current_text = self.input_field.text()
        self.input_field.setText(current_text + char)

    def generate_task(self):
        self.a = random.randint(2, 10)
        self.b = random.randint(20, 90)
        self.c = random.randint(self.b + 1, 99)  # Ensure B < C
        self.correct_answer = self.a * (self.b - self.c)

        task_str = f"{self.a} × ({self.b} – {self.c}) ="
        self.label.setText(task_str)
        self.input_field.clear()
        self.result_label.clear()
        self.result_label.hide()
        self.next_btn.setVisible(False)

    def check_answer(self):
        try:
            user_input = float(self.input_field.text().replace(',', '.'))
            if user_input == self.correct_answer:
                self.result_label.setText("Правильно!")
                self.result_label.setStyleSheet(f"color: green; font-size: {int(60 * self.text_scale)}px;")
            else:
                self.result_label.setText(f"Неправильно. Правильный ответ: {self.correct_answer}")
                self.result_label.setStyleSheet(f"color: red; font-size: {int(60 * self.text_scale)}px;")
        except ValueError:
            self.result_label.setText("Введите число.")
            self.result_label.setStyleSheet(f"color: orange; font-size: {int(60 * self.text_scale)}px;")

        self.result_label.show()
        self.submit_btn.setEnabled(False)
        self.next_btn.setVisible(True)

    def reset_task(self):
        self.submit_btn.setEnabled(True)
        self.next_btn.setVisible(False)
        self.result_label.clear()
        self.result_label.hide()
        self.input_field.clear()
        self.generate_task()

    def apply_text_scaling(self, scale):
        self.text_scale = scale
        font = QFont()
        font.setPointSize(int(60 * self.text_scale))
        self.label.setFont(font)
        self.input_field.setStyleSheet(f"""
            QLineEdit {{
                background-color: white;
                border: 2px solid #ccc;
                border-radius: 8px;
                padding: 8px;
                font-size: {int(60 * self.text_scale)}px;
                color: black;
                width: {int(300 * self.text_scale)}px;
                height: {int(60 * self.text_scale)}px;
            }}
            QLineEdit:focus {{
                border: 2px solid #007acc;
            }}
        """)
        for row in self.keyboard_buttons:
            for btn in row:
                btn.setStyleSheet(f"""
                    QPushButton {{
                        background-color: #ffffff;
                        border: 1px solid #ddd;
                        border-radius: 6px;
                        padding: 8px;
                        font-size: {int(60 * self.text_scale)}px;
                        color: black;
                        min-width: {int(60 * self.ui_scale)}px;
                        min-height: {int(60 * self.ui_scale)}px;
                    }}
                    QPushButton:hover {{
                        background-color: #f5f5f5;
                    }}
                """)
        self.submit_btn.setFont(QFont("Arial", int(60 * self.text_scale)))
        self.submit_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: #f0f0f0;
                border: 1px solid #ccc;
                border-radius: 6px;
                padding: 8px 16px;
                font-size: {int(60 * self.text_scale)}px;
                color: black;
                min-width: {int(100 * self.ui_scale)}px;
                min-height: {int(50 * self.ui_scale)}px;
            }}
            QPushButton:hover {{
                background-color: #e0e0e0;
            }}
            QPushButton:pressed {{
                background-color: #d0d0d0;
            }}
            QPushButton:disabled {{
                background-color: #cccccc;
                color: #888888;
            }}
        """)
        self.next_btn.setFont(QFont("Arial", int(60 * self.text_scale)))
        self.next_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: #f0f0f0;
                border: 1px solid #ccc;
                border-radius: 6px;
                padding: 8px 16px;
                font-size: {int(60 * self.text_scale)}px;
                color: black;
                min-width: {int(100 * self.ui_scale)}px;
                min-height: {int(50 * self.ui_scale)}px;
            }}
            QPushButton:hover {{
                background-color: #e0e0e0;
            }}
            QPushButton:pressed {{
                background-color: #d0d0d0;
            }}
            QPushButton:disabled {{
                background-color: #cccccc;
                color: #888888;
            }}
        """)
        self.result_label.setStyleSheet(f"font-size: {int(60 * self.text_scale)}px;")

    def apply_ui_scaling(self, scale):
        self.ui_scale = scale
        for row in self.keyboard_buttons:
            for btn in row:
                btn.setStyleSheet(f"""
                    QPushButton {{
                        background-color: #ffffff;
                        border: 1px solid #ddd;
                        border-radius: 6px;
                        padding: 8px;
                        font-size: {int(60 * self.text_scale)}px;
                        color: black;
                        min-width: {int(60 * self.ui_scale)}px;
                        min-height: {int(60 * self.ui_scale)}px;
                    }}
                    QPushButton:hover {{
                        background-color: #f5f5f5;
                    }}
                """)
        self.submit_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: #f0f0f0;
                border: 1px solid #ccc;
                border-radius: 6px;
                padding: 8px 16px;
                font-size: {int(60 * self.text_scale)}px;
                color: black;
                min-width: {int(100 * self.ui_scale)}px;
                min-height: {int(50 * self.ui_scale)}px;
            }}
            QPushButton:hover {{
                background-color: #e0e0e0;
            }}
            QPushButton:pressed {{
                background-color: #d0d0d0;
            }}
            QPushButton:disabled {{
                background-color: #cccccc;
                color: #888888;
            }}
        """)
        self.next_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: #f0f0f0;
                border: 1px solid #ccc;
                border-radius: 6px;
                padding: 8px 16px;
                font-size: {int(60 * self.text_scale)}px;
                color: black;
                min-width: {int(100 * self.ui_scale)}px;
                min-height: {int(50 * self.ui_scale)}px;
            }}
            QPushButton:hover {{
                background-color: #e0e0e0;
            }}
            QPushButton:pressed {{
                background-color: #d0d0d0;
            }}
            QPushButton:disabled {{
                background-color: #cccccc;
                color: #888888;
            }}
        """)

class Task2(BaseTask):
    def __init__(self, text_scale=1.0, ui_scale=1.0):
        super().__init__(text_scale, ui_scale)

        # Создаем ScrollArea
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setStyleSheet("border: none;")
        # Виджет внутри ScrollArea
        self.scroll_content = QWidget()
        self.scroll_layout = QVBoxLayout(self.scroll_content)
        self.scroll_layout.setAlignment(Qt.AlignTop)

        # Текст задания (с дробями)
        self.label = QLabel("Нажмите 'Новый пример', чтобы начать.")
        self.label.setAlignment(Qt.AlignCenter)
        font = QFont()
        font.setPointSize(int(60 * self.text_scale))
        self.label.setFont(font)

        # Поля для ответа (числитель и знаменатель)
        self.answer_num = QLineEdit()  # числитель
        self.answer_num.setPlaceholderText("Числитель")
        self.answer_num.setAlignment(Qt.AlignCenter)
        # Устанавливаем фокус в числитель при создании
        self.answer_num.setFocus()
        self.last_active_field = self.answer_num # Запоминаем, что числитель - активное поле

        self.answer_div_line = QLabel("___________")  # дробная черта
        self.answer_div_line.setAlignment(Qt.AlignCenter)

        self.answer_den = QLineEdit()  # знаменатель
        self.answer_den.setPlaceholderText("Знаменатель")
        self.answer_den.setAlignment(Qt.AlignCenter)

        # Подключаем события фокуса к полям ввода
        self.answer_num.focusInEvent = self.make_focus_in_handler(self.answer_num)
        self.answer_den.focusInEvent = self.make_focus_in_handler(self.answer_den)

        # Виртуальная клавиатура
        self.keyboard_layout = QGridLayout()
        self.keyboard_buttons = [] # Список кнопок клавиатуры
        self.setup_virtual_keyboard()

        # Кнопки
        self.submit_btn = QPushButton("Проверить")
        self.next_btn = QPushButton("Продолжить")
        self.next_btn.setVisible(False)

        # Результат
        self.result_label = QLabel("")
        self.result_label.setAlignment(Qt.AlignCenter)
        self.result_label.hide()

        # Стили
        input_style = f"""
            QLineEdit {{
                background-color: white;
                border: 2px solid #ccc;
                border-radius: 8px;
                padding: 8px;
                font-size: {int(60 * self.text_scale)}px;
                color: black;
                min-width: {int(80 * self.text_scale)}px;
                width: {int(200 * self.text_scale)}px;
                height: {int(60 * self.text_scale)}px;
            }}
        """
        self.answer_num.setStyleSheet(input_style)
        self.answer_den.setStyleSheet(input_style)

        button_style = f"""
            QPushButton {{
                background-color: #f0f0f0;
                border: 1px solid #ccc;
                border-radius: 6px;
                padding: 8px 16px;
                font-size: {int(60 * self.text_scale)}px;
                color: black;
                min-width: {int(100 * self.ui_scale)}px;
                min-height: {int(50 * self.ui_scale)}px;
            }}
            QPushButton:hover {{
                background-color: #e0e0e0;
            }}
            QPushButton:pressed {{
                background-color: #d0d0d0;
            }}
            QPushButton:disabled {{
                background-color: #cccccc;
                color: #888888;
            }}
        """
        self.submit_btn.setStyleSheet(button_style)
        self.next_btn.setStyleSheet(button_style)

        # Собираем layout
        self.scroll_layout.addWidget(self.label)
        self.scroll_layout.addSpacing(int(20 * self.text_scale))
        self.scroll_layout.addWidget(self.answer_num)
        self.scroll_layout.addWidget(self.answer_div_line)
        self.scroll_layout.addWidget(self.answer_den)
        self.scroll_layout.addLayout(self.keyboard_layout)
        self.scroll_layout.addWidget(self.submit_btn)
        self.scroll_layout.addWidget(self.result_label)
        self.scroll_layout.addWidget(self.next_btn)

        # Устанавливаем контент в scroll area
        self.scroll_area.setWidget(self.scroll_content)
        # Добавляем scroll area в основной layout (от BaseTask)
        self.layout.addWidget(self.scroll_area)

        self.submit_btn.clicked.connect(self.check_answer)
        self.next_btn.clicked.connect(self.reset_task)

    def make_focus_in_handler(self, field):
        """Возвращает функцию-обработчик для focusInEvent конкретного поля."""
        def handler(event):
            # Вызываем стандартный обработчик
            super(QLineEdit, field).focusInEvent(event)
            # Обновляем last_active_field
            self.last_active_field = field
        return handler

    def append_to_active_input(self, char):
        # Используем last_active_field для добавления символа
        if self.last_active_field:
            current_text = self.last_active_field.text()
            self.last_active_field.setText(current_text + char)

    def setup_virtual_keyboard(self):
        buttons = [
            ['1', '2', '3'],
            ['4', '5', '6'],
            ['7', '8', '9'],
            ['0', '-', ',']
        ]

        for i, row in enumerate(buttons):
            button_row = []
            for j, char in enumerate(row):
                btn = QPushButton(char)
                btn.clicked.connect(lambda _, s=char: self.append_to_active_input(s))
                btn.setStyleSheet(f"""
                    QPushButton {{
                        background-color: #ffffff;
                        border: 1px solid #ddd;
                        border-radius: 6px;
                        padding: 8px;
                        font-size: {int(60 * self.text_scale)}px;
                        color: black;
                        min-width: {int(60 * self.ui_scale)}px;
                        min-height: {int(60 * self.ui_scale)}px;
                    }}
                    QPushButton:hover {{
                        background-color: #f5f5f5;
                    }}
                """)
                self.keyboard_layout.addWidget(btn, i, j)
                button_row.append(btn)
            self.keyboard_buttons.append(button_row)

    def generate_task(self):
        # Генерация чисел
        b = random.randint(2, 8)
        a = random.randint(b + 1, 9)
        d = random.randint(2, 8)
        c = random.randint(d + 1, 9)
        e = random.randint(5, 25)
        f = random.randint(5, 9)
        while f == e:
            f = random.randint(5, 9)

        self.a, self.b, self.c, self.d, self.e, self.f = a, b, c, d, e, f

        # Формирование строки задания
        task_html = f"""
        <div style="text-align: center;">
        <span style="font-size: {int(60 * self.text_scale)}px;">
        (<sup>{a}</sup>&frasl;<sub>{b}</sub> &minus; <sup>{c}</sup>&frasl;<sub>{d}</sub>) &divide; <sup>{e}</sup>&frasl;<sub>{f}</sub>
        </span>
        </div>
        """
        # Вместо прямого setText — вызываем update_label_html
        self.update_label_html()

        # Очистка полей
        self.answer_num.clear()
        self.answer_den.clear()
        self.result_label.clear()
        self.result_label.hide()
        self.next_btn.setVisible(False)
        # Устанавливаем фокус на числитель при новом задании
        self.answer_num.setFocus()
        self.last_active_field = self.answer_num

    def update_label_html(self):
        """Пересоздаёт HTML-строку для self.label с учётом текущего text_scale."""
        if not hasattr(self, 'a'):
            # Если задача ещё не сгенерирована, ничего не делаем
            return

        # Формируем HTML с новым font-size
        task_html = f"""
        <div style="text-align: center;">
        <span style="font-size: {int(60 * self.text_scale)}px;">
        (<sup>{self.a}</sup>&frasl;<sub>{self.b}</sub> &minus; <sup>{self.c}</sup>&frasl;<sub>{self.d}</sub>) &divide; <sup>{self.e}</sup>&frasl;<sub>{self.f}</sub>
        </span>
        </div>
        """
        self.label.setText(task_html)

    def check_answer(self):
        try:
            num = int(self.answer_num.text())
            den = int(self.answer_den.text())

            # Проверка знаменателя
            if den == 0:
                self.result_label.setText("Знаменатель не может быть 0.")
                self.result_label.setStyleSheet(f"color: orange; font-size: {int(60 * self.text_scale)}px;")
                self.result_label.show()
                return

            user_fraction = Fraction(num, den)

            # Вычисляем правильный ответ
            frac1 = Fraction(self.a, self.b)
            frac2 = Fraction(self.c, self.d)
            div_frac = Fraction(self.e, self.f)

            correct_result = (frac1 - frac2) / div_frac

            if user_fraction == correct_result:
                self.result_label.setText("Правильно!")
                self.result_label.setStyleSheet(f"color: green; font-size: {int(60 * self.text_scale)}px;")
                self.submit_btn.setEnabled(False)
            else:
                self.result_label.setText(
                    f"Неправильно. Правильный ответ: {correct_result.numerator}/{correct_result.denominator}"
                )
                self.result_label.setStyleSheet(f"color: red; font-size: {int(60 * self.text_scale)}px;")
                self.submit_btn.setEnabled(False)

        except ValueError:
            self.result_label.setText("Введите числа в оба поля.")
            self.result_label.setStyleSheet(f"color: orange; font-size: {int(60 * self.text_scale)}px;")

        self.result_label.show()
        #self.submit_btn.setEnabled(False)
        self.next_btn.setVisible(True)

    def reset_task(self):
        self.submit_btn.setEnabled(True)
        self.next_btn.setVisible(False)
        self.result_label.clear()
        self.result_label.hide()
        self.answer_num.clear()
        self.answer_den.clear()
        self.generate_task()

    def apply_text_scaling(self, scale):
        self.text_scale = scale
        font = QFont()
        font.setPointSize(int(60 * self.text_scale))
        self.label.setFont(font)
        input_style = f"""
            QLineEdit {{
                background-color: white;
                border: 2px solid #ccc;
                border-radius: 8px;
                padding: 8px;
                font-size: {int(60 * self.text_scale)}px;
                color: black;
                min-width: {int(80 * self.text_scale)}px;
                width: {int(200 * self.text_scale)}px;
                height: {int(60 * self.text_scale)}px;
            }}
        """
        self.answer_num.setStyleSheet(input_style)
        self.answer_den.setStyleSheet(input_style)
        self.answer_div_line.setStyleSheet(f"font-size: {int(60 * self.text_scale)}px;")
        for row in self.keyboard_buttons:
            for btn in row:
                btn.setStyleSheet(f"""
                    QPushButton {{
                        background-color: #ffffff;
                        border: 1px solid #ddd;
                        border-radius: 6px;
                        padding: 8px;
                        font-size: {int(60 * self.text_scale)}px;
                        color: black;
                        min-width: {int(60 * self.ui_scale)}px;
                        min-height: {int(60 * self.ui_scale)}px;
                    }}
                    QPushButton:hover {{
                        background-color: #f5f5f5;
                    }}
                """)
        self.submit_btn.setFont(QFont("Arial", int(60 * self.text_scale)))
        self.submit_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: #f0f0f0;
                border: 1px solid #ccc;
                border-radius: 6px;
                padding: 8px 16px;
                font-size: {int(60 * self.text_scale)}px;
                color: black;
                min-width: {int(100 * self.ui_scale)}px;
                min-height: {int(50 * self.ui_scale)}px;
            }}
            QPushButton:hover {{
                background-color: #e0e0e0;
            }}
            QPushButton:pressed {{
                background-color: #d0d0d0;
            }}
            QPushButton:disabled {{
                background-color: #cccccc;
                color: #888888;
            }}
        """)
        self.next_btn.setFont(QFont("Arial", int(60 * self.text_scale)))
        self.next_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: #f0f0f0;
                border: 1px solid #ccc;
                border-radius: 6px;
                padding: 8px 16px;
                font-size: {int(60 * self.text_scale)}px;
                color: black;
                min-width: {int(100 * self.ui_scale)}px;
                min-height: {int(50 * self.ui_scale)}px;
            }}
            QPushButton:hover {{
                background-color: #e0e0e0;
            }}
            QPushButton:pressed {{
                background-color: #d0d0d0;
            }}
            QPushButton:disabled {{
                background-color: #cccccc;
                color: #888888;
            }}
        """)
        self.result_label.setStyleSheet(f"font-size: {int(60 * self.text_scale)}px;")
        self.update_label_html() 

    def apply_ui_scaling(self, scale):
        self.ui_scale = scale
        for row in self.keyboard_buttons:
            for btn in row:
                btn.setStyleSheet(f"""
                    QPushButton {{
                        background-color: #ffffff;
                        border: 1px solid #ddd;
                        border-radius: 6px;
                        padding: 8px;
                        font-size: {int(60 * self.text_scale)}px;
                        color: black;
                        min-width: {int(60 * self.ui_scale)}px;
                        min-height: {int(60 * self.ui_scale)}px;
                    }}
                    QPushButton:hover {{
                        background-color: #f5f5f5;
                    }}
                """)
        self.submit_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: #f0f0f0;
                border: 1px solid #ccc;
                border-radius: 6px;
                padding: 8px 16px;
                font-size: {int(60 * self.text_scale)}px;
                color: black;
                min-width: {int(100 * self.ui_scale)}px;
                min-height: {int(50 * self.ui_scale)}px;
            }}
            QPushButton:hover {{
                background-color: #e0e0e0;
            }}
            QPushButton:pressed {{
                background-color: #d0d0d0;
            }}
            QPushButton:disabled {{
                background-color: #cccccc;
                color: #888888;
            }}
        """)
        self.next_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: #f0f0f0;
                border: 1px solid #ccc;
                border-radius: 6px;
                padding: 8px 16px;
                font-size: {int(60 * self.text_scale)}px;
                color: black;
                min-width: {int(100 * self.ui_scale)}px;
                min-height: {int(50 * self.ui_scale)}px;
            }}
            QPushButton:hover {{
                background-color: #e0e0e0;
            }}
            QPushButton:pressed {{
                background-color: #d0d0d0;
            }}
            QPushButton:disabled {{
                background-color: #cccccc;
                color: #888888;
            }}
        """)

class Task3(BaseTask):
    def __init__(self, text_scale=1.0, ui_scale=1.0):
        super().__init__(text_scale, ui_scale)
        self.label = QLabel("Нажмите 'Новый пример', чтобы начать.")
        self.label.setAlignment(Qt.AlignCenter)
        font = QFont()
        font.setPointSize(int(60 * self.text_scale))
        self.label.setFont(font)

        self.input_field = QLineEdit()
        self.input_field.setAlignment(Qt.AlignCenter)

        # Стиль поля ввода
        self.input_field.setStyleSheet(f"""
            QLineEdit {{
                background-color: white;
                border: 2px solid #ccc;
                border-radius: 8px;
                padding: 8px;
                font-size: {int(60 * self.text_scale)}px;
                color: black;
                width: {int(300 * self.text_scale)}px;
                height: {int(60 * self.text_scale)}px;
            }}
            QLineEdit:focus {{
                border: 2px solid #007acc;
            }}
        """)

        self.result_label = QLabel("")
        self.result_label.setAlignment(Qt.AlignCenter)
        self.result_label.setStyleSheet(f"font-size: {int(60 * self.text_scale)}px;")
        self.result_label.hide()

        self.submit_btn = QPushButton("Проверить")
        self.next_btn = QPushButton("Продолжить")
        self.next_btn.setVisible(False)

        # Стиль кнопок
        button_style = f"""
            QPushButton {{
                background-color: #f0f0f0;
                border: 1px solid #ccc;
                border-radius: 6px;
                padding: 8px 16px;
                font-size: {int(60 * self.text_scale)}px;
                color: black;
                min-width: {int(100 * self.ui_scale)}px;
                min-height: {int(50 * self.ui_scale)}px;
            }}
            QPushButton:hover {{
                background-color: #e0e0e0;
            }}
            QPushButton:pressed {{
                background-color: #d0d0d0;
            }}
            QPushButton:disabled {{
                background-color: #cccccc;
                color: #888888;
            }}
        """
        self.submit_btn.setStyleSheet(button_style)
        self.next_btn.setStyleSheet(button_style)

        self.a = 0.0
        self.b = 0.0
        self.c = 0.0
        self.correct_answer = 0.0

        # Создаем ScrollArea
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setStyleSheet("border: none;")
        # Виджет внутри ScrollArea
        self.scroll_content = QWidget()
        self.scroll_layout = QVBoxLayout(self.scroll_content)
        self.scroll_layout.setAlignment(Qt.AlignTop)

        # Компоновка
        self.scroll_layout.addWidget(self.label)
        self.scroll_layout.addSpacing(int(20 * self.text_scale))
        self.scroll_layout.addWidget(self.input_field)
        self.setup_virtual_keyboard()
        self.scroll_layout.addWidget(self.submit_btn)
        self.scroll_layout.addWidget(self.result_label)
        self.scroll_layout.addWidget(self.next_btn)

        # Устанавливаем контент в scroll area
        self.scroll_area.setWidget(self.scroll_content)
        # Добавляем scroll area в основной layout (от BaseTask)
        self.layout.addWidget(self.scroll_area)

        self.submit_btn.clicked.connect(self.check_answer)
        self.next_btn.clicked.connect(self.reset_task)

    def setup_virtual_keyboard(self):
        self.keyboard_layout = QGridLayout() # Сделаем его атрибутом класса
        self.keyboard_buttons = [] # Список кнопок клавиатуры

        buttons = [
            ['1', '2', '3'],
            ['4', '5', '6'],
            ['7', '8', '9'],
            ['0', '-', ',']
        ]

        for i, row in enumerate(buttons):
            button_row = []
            for j, char in enumerate(row):
                btn = QPushButton(char)
                btn.clicked.connect(lambda _, s=char: self.append_to_input(s))
                btn.setStyleSheet(f"""
                    QPushButton {{
                        background-color: #ffffff;
                        border: 1px solid #ddd;
                        border-radius: 6px;
                        padding: 8px;
                        font-size: {int(60 * self.text_scale)}px;
                        color: black;
                        min-width: {int(60 * self.ui_scale)}px;
                        min-height: {int(60 * self.ui_scale)}px;
                    }}
                    QPushButton:hover {{
                        background-color: #f5f5f5;
                    }}
                """)
                self.keyboard_layout.addWidget(btn, i, j)
                button_row.append(btn)
            self.keyboard_buttons.append(button_row)

        self.scroll_layout.addLayout(self.keyboard_layout)

    def append_to_input(self, char):
        current_text = self.input_field.text()
        self.input_field.setText(current_text + char)

    def generate_task(self):
        # Генерация чисел
        a = round(random.uniform(1.20, 1.99), 2)
        b = round(random.uniform(0.1, 0.9), 1)
        c = round(random.uniform(-2.9, -1.2), 1)

        self.a, self.b, self.c = a, b, c
        self.correct_answer = a - b * c

        task_str = f"{a} – {b} × ({c}) ="
        self.label.setText(task_str)
        self.input_field.clear()
        self.result_label.clear()
        self.result_label.hide()
        self.next_btn.setVisible(False)

    def check_answer(self):
        try:
            user_input = float(self.input_field.text().replace(',', '.'))
            if abs(user_input - self.correct_answer) < 1e-6:  # Проверка с допуском
                self.result_label.setText("Правильно!")
                self.result_label.setStyleSheet(f"color: green; font-size: {int(60 * self.text_scale)}px;")
            else:
                self.result_label.setText(f"Неправильно. Правильный ответ: {round(self.correct_answer, 2)}")
                self.result_label.setStyleSheet(f"color: red; font-size: {int(60 * self.text_scale)}px;")
        except ValueError:
            self.result_label.setText("Введите число.")
            self.result_label.setStyleSheet(f"color: orange; font-size: {int(60 * self.text_scale)}px;")

        self.result_label.show()
        self.submit_btn.setEnabled(False)
        self.next_btn.setVisible(True)

    def reset_task(self):
        self.submit_btn.setEnabled(True)
        self.next_btn.setVisible(False)
        self.result_label.clear()
        self.result_label.hide()
        self.input_field.clear()
        self.generate_task()

    def apply_text_scaling(self, scale):
        self.text_scale = scale
        font = QFont()
        font.setPointSize(int(60 * self.text_scale))
        self.label.setFont(font)
        self.input_field.setStyleSheet(f"""
            QLineEdit {{
                background-color: white;
                border: 2px solid #ccc;
                border-radius: 8px;
                padding: 8px;
                font-size: {int(60 * self.text_scale)}px;
                color: black;
                width: {int(300 * self.text_scale)}px;
                height: {int(60 * self.text_scale)}px;
            }}
            QLineEdit:focus {{
                border: 2px solid #007acc;
            }}
        """)
        for row in self.keyboard_buttons:
            for btn in row:
                btn.setStyleSheet(f"""
                    QPushButton {{
                        background-color: #ffffff;
                        border: 1px solid #ddd;
                        border-radius: 6px;
                        padding: 8px;
                        font-size: {int(60 * self.text_scale)}px;
                        color: black;
                        min-width: {int(60 * self.ui_scale)}px;
                        min-height: {int(60 * self.ui_scale)}px;
                    }}
                    QPushButton:hover {{
                        background-color: #f5f5f5;
                    }}
                """)
        self.submit_btn.setFont(QFont("Arial", int(60 * self.text_scale)))
        self.submit_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: #f0f0f0;
                border: 1px solid #ccc;
                border-radius: 6px;
                padding: 8px 16px;
                font-size: {int(60 * self.text_scale)}px;
                color: black;
                min-width: {int(100 * self.ui_scale)}px;
                min-height: {int(50 * self.ui_scale)}px;
            }}
            QPushButton:hover {{
                background-color: #e0e0e0;
            }}
            QPushButton:pressed {{
                background-color: #d0d0d0;
            }}
            QPushButton:disabled {{
                background-color: #cccccc;
                color: #888888;
            }}
        """)
        self.next_btn.setFont(QFont("Arial", int(60 * self.text_scale)))
        self.next_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: #f0f0f0;
                border: 1px solid #ccc;
                border-radius: 6px;
                padding: 8px 16px;
                font-size: {int(60 * self.text_scale)}px;
                color: black;
                min-width: {int(100 * self.ui_scale)}px;
                min-height: {int(50 * self.ui_scale)}px;
            }}
            QPushButton:hover {{
                background-color: #e0e0e0;
            }}
            QPushButton:pressed {{
                background-color: #d0d0d0;
            }}
            QPushButton:disabled {{
                background-color: #cccccc;
                color: #888888;
            }}
        """)
        self.result_label.setStyleSheet(f"font-size: {int(60 * self.text_scale)}px;")

    def apply_ui_scaling(self, scale):
        self.ui_scale = scale
        for row in self.keyboard_buttons:
            for btn in row:
                btn.setStyleSheet(f"""
                    QPushButton {{
                        background-color: #ffffff;
                        border: 1px solid #ddd;
                        border-radius: 6px;
                        padding: 8px;
                        font-size: {int(60 * self.text_scale)}px;
                        color: black;
                        min-width: {int(60 * self.ui_scale)}px;
                        min-height: {int(60 * self.ui_scale)}px;
                    }}
                    QPushButton:hover {{
                        background-color: #f5f5f5;
                    }}
                """)
        self.submit_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: #f0f0f0;
                border: 1px solid #ccc;
                border-radius: 6px;
                padding: 8px 16px;
                font-size: {int(60 * self.text_scale)}px;
                color: black;
                min-width: {int(100 * self.ui_scale)}px;
                min-height: {int(50 * self.ui_scale)}px;
            }}
            QPushButton:hover {{
                background-color: #e0e0e0;
            }}
            QPushButton:pressed {{
                background-color: #d0d0d0;
            }}
            QPushButton:disabled {{
                background-color: #cccccc;
                color: #888888;
            }}
        """)
        self.next_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: #f0f0f0;
                border: 1px solid #ccc;
                border-radius: 6px;
                padding: 8px 16px;
                font-size: {int(60 * self.text_scale)}px;
                color: black;
                min-width: {int(100 * self.ui_scale)}px;
                min-height: {int(50 * self.ui_scale)}px;
            }}
            QPushButton:hover {{
                background-color: #e0e0e0;
            }}
            QPushButton:pressed {{
                background-color: #d0d0d0;
            }}
            QPushButton:disabled {{
                background-color: #cccccc;
                color: #888888;
            }}
        """)

class Task4(BaseTask):
    def __init__(self, text_scale=1.0, ui_scale=1.0):
        super().__init__(text_scale, ui_scale)
        # Создаем ScrollArea
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setStyleSheet("border: none;")
        # Виджет внутри ScrollArea
        self.scroll_content = QWidget()
        self.scroll_layout = QVBoxLayout(self.scroll_content)
        self.scroll_layout.setAlignment(Qt.AlignTop)

        # Метка с длинным текстом задачи
        self.label = QLabel("Нажмите 'Новый пример', чтобы начать.")
        self.label.setAlignment(Qt.AlignCenter)
        self.label.setWordWrap(True)  # Разрешить перенос строк
        font = QFont()
        font.setPointSize(int(60 * self.text_scale))
        self.label.setFont(font)

        # Добавляем метку в scroll_layout
        self.scroll_layout.addWidget(self.label)

        # Поле ввода ответа
        self.input_field = QLineEdit()
        self.input_field.setAlignment(Qt.AlignCenter)
        # Стиль поля ввода
        line_edit_style = f"""
        QLineEdit {{
            background-color: white;
            border: 2px solid #ccc;
            border-radius: 8px;
            padding: 8px;
            font-size: {int(60 * self.text_scale)}px;
            color: black;
            width: {int(300 * self.text_scale)}px;
            height: {int(60 * self.text_scale)}px;
        }}
        QLineEdit:focus {{
            border: 2px solid #007acc;
        }}
        """
        self.input_field.setStyleSheet(line_edit_style)
        self.scroll_layout.addWidget(self.input_field)

        # Виртуальная клавиатура
        self.keyboard_layout = QGridLayout() # Сделаем его атрибутом класса
        buttons = [
            ['1', '2', '3'],
            ['4', '5', '6'],
            ['7', '8', '9'],
            ['0', '-', ',']
        ]
        self.keyboard_buttons = [] # Список кнопок клавиатуры
        for i, row in enumerate(buttons):
            button_row = []
            for j, char in enumerate(row):
                btn = QPushButton(char)
                btn.clicked.connect(lambda _, s=char: self.append_to_input(s))
                btn.setStyleSheet(f"""
                QPushButton {{
                    background-color: #ffffff;
                    border: 1px solid #ddd;
                    border-radius: 6px;
                    padding: 8px;
                    font-size: {int(60 * self.text_scale)}px;
                    color: black;
                    min-width: {int(60 * self.ui_scale)}px;
                    min-height: {int(60 * self.ui_scale)}px;
                }}
                QPushButton:hover {{
                    background-color: #f5f5f5;
                }}
                """)
                self.keyboard_layout.addWidget(btn, i, j)
                button_row.append(btn)
            self.keyboard_buttons.append(button_row)
        self.scroll_layout.addLayout(self.keyboard_layout)

        # Кнопки
        self.submit_btn = QPushButton("Проверить")
        self.next_btn = QPushButton("Продолжить")
        self.next_btn.setVisible(False)
        button_style = f"""
        QPushButton {{
            background-color: #f0f0f0;
            border: 1px solid #ccc;
            border-radius: 6px;
            padding: 8px 16px;
            font-size: {int(60 * self.text_scale)}px;
            color: black;
            min-width: {int(100 * self.ui_scale)}px;
            min-height: {int(50 * self.ui_scale)}px;
        }}
        QPushButton:hover {{
            background-color: #e0e0e0;
        }}
        QPushButton:pressed {{
            background-color: #d0d0d0;
        }}
        QPushButton:disabled {{
            background-color: #cccccc;
            color: #888888;
        }}
        """
        self.submit_btn.setStyleSheet(button_style)
        self.next_btn.setStyleSheet(button_style)
        self.scroll_layout.addWidget(self.submit_btn)
        self.scroll_layout.addWidget(self.next_btn)

        # Результат
        self.result_label = QLabel("")
        self.result_label.setAlignment(Qt.AlignCenter)
        self.result_label.setStyleSheet(f"font-size: {int(60 * self.text_scale)}px;")
        self.result_label.hide()
        self.scroll_layout.addWidget(self.result_label)

        # Устанавливаем контент в scroll area
        self.scroll_area.setWidget(self.scroll_content)
        # Добавляем scroll area в основной layout (от BaseTask)
        self.layout.addWidget(self.scroll_area)

        self.a = 0
        self.b = 0
        self.c = 0
        self.correct_answer = 0

        self.submit_btn.clicked.connect(self.check_answer)
        self.next_btn.clicked.connect(self.reset_task)

    def append_to_input(self, char):
        current_text = self.input_field.text()
        self.input_field.setText(current_text + char)

    def generate_task(self):
        # Генерация чисел
        a = random.randint(-9, -2)
        b = random.randint(2, 9)
        c = random.randint(-19, -10)

        self.a, self.b, self.c = a, b, c
        # Вычисляем: a * |c + b|
        self.correct_answer = a * abs(c + b)

        task_str = f"Найдите значение выражения {a} × |y + {b}| при y = {c}"
        self.label.setText(task_str)
        self.input_field.clear()
        self.result_label.clear()
        self.result_label.hide()
        self.next_btn.setVisible(False)

    def check_answer(self):
        try:
            user_input = float(self.input_field.text().replace(',', '.'))
            if user_input == self.correct_answer:
                self.result_label.setText("Правильно!")
                self.result_label.setStyleSheet(f"color: green; font-size:{int(60 * self.text_scale)}px;")
            else:
                self.result_label.setText(f"Неправильно. Правильный ответ: {self.correct_answer}")
                self.result_label.setStyleSheet(f"color: red; font-size: {int(60 * self.text_scale)}px;")
        except ValueError:
            self.result_label.setText("Введите число.")
            self.result_label.setStyleSheet(f"color: orange; font-size: {int(60 * self.text_scale)}px;")

        self.result_label.show()
        self.submit_btn.setEnabled(False)
        self.next_btn.setVisible(True)

    def reset_task(self):
        self.submit_btn.setEnabled(True)
        self.next_btn.setVisible(False)
        self.result_label.clear()
        self.result_label.hide()
        self.input_field.clear()
        self.generate_task()

    def apply_text_scaling(self, scale):
        self.text_scale = scale
        font = QFont()
        font.setPointSize(int(60 * self.text_scale))
        self.label.setFont(font)
        line_edit_style = f"""
        QLineEdit {{
            background-color: white;
            border: 2px solid #ccc;
            border-radius: 8px;
            padding: 8px;
            font-size: {int(60 * self.text_scale)}px;
            color: black;
            width: {int(300 * self.text_scale)}px;
            height: {int(60 * self.text_scale)}px;
        }}
        QLineEdit:focus {{
            border: 2px solid #007acc;
        }}
        """
        self.input_field.setStyleSheet(line_edit_style)
        for row in self.keyboard_buttons:
            for btn in row:
                btn.setStyleSheet(f"""
                QPushButton {{
                    background-color: #ffffff;
                    border: 1px solid #ddd;
                    border-radius: 6px;
                    padding: 8px;
                    font-size: {int(60 * self.text_scale)}px;
                    color: black;
                    min-width: {int(60 * self.ui_scale)}px;
                    min-height: {int(60 * self.ui_scale)}px;
                }}
                QPushButton:hover {{
                    background-color: #f5f5f5;
                }}
                """)
        self.submit_btn.setFont(QFont("Arial", int(60 * self.text_scale)))
        self.submit_btn.setStyleSheet(f"""
        QPushButton {{
            background-color: #f0f0f0;
            border: 1px solid #ccc;
            border-radius: 6px;
            padding: 8px 16px;
            font-size: {int(60 * self.text_scale)}px;
            color: black;
            min-width: {int(100 * self.ui_scale)}px;
            min-height: {int(50 * self.ui_scale)}px;
        }}
        QPushButton:hover {{
            background-color: #e0e0e0;
        }}
        """)
        self.next_btn.setFont(QFont("Arial", int(60 * self.text_scale)))
        self.next_btn.setStyleSheet(f"""
        QPushButton {{
            background-color: #f0f0f0;
            border: 1px solid #ccc;
            border-radius: 6px;
            padding: 8px 16px;
            font-size: {int(60 * self.text_scale)}px;
            color: black;
            min-width: {int(100 * self.ui_scale)}px;
            min-height: {int(50 * self.ui_scale)}px;
        }}
        QPushButton:hover {{
            background-color: #e0e0e0;
        }}
        """)
        self.result_label.setStyleSheet(f"font-size: {int(60 * self.text_scale)}px;")

    def apply_ui_scaling(self, scale):
        self.ui_scale = scale
        for row in self.keyboard_buttons:
            for btn in row:
                btn.setStyleSheet(f"""
                QPushButton {{
                    background-color: #ffffff;
                    border: 1px solid #ddd;
                    border-radius: 6px;
                    padding: 8px;
                    font-size: {int(60 * self.text_scale)}px;
                    color: black;
                    min-width: {int(60 * self.ui_scale)}px;
                    min-height: {int(60 * self.ui_scale)}px;
                }}
                QPushButton:hover {{
                    background-color: #f5f5f5;
                }}
                """)
        self.submit_btn.setStyleSheet(f"""
        QPushButton {{
            background-color: #f0f0f0;
            border: 1px solid #ccc;
            border-radius: 6px;
            padding: 8px 16px;
            font-size: {int(60 * self.text_scale)}px;
            color: black;
            min-width: {int(100 * self.ui_scale)}px;
            min-height: {int(50 * self.ui_scale)}px;
        }}
        QPushButton:hover {{
            background-color: #e0e0e0;
        }}
        """)
        self.next_btn.setStyleSheet(f"""
        QPushButton {{
            background-color: #f0f0f0;
            border: 1px solid #ccc;
            border-radius: 6px;
            padding: 8px 16px;
            font-size: {int(60 * self.text_scale)}px;
            color: black;
            min-width: {int(100 * self.ui_scale)}px;
            min-height: {int(50 * self.ui_scale)}px;
        }}
        QPushButton:hover {{
            background-color: #e0e0e0;
        }}
        """)

class Task5(BaseTask):
    def __init__(self, text_scale=1.0, ui_scale=1.0):
        super().__init__(text_scale, ui_scale)
        # Создаем ScrollArea
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setStyleSheet("border: none;")
        # Виджет внутри ScrollArea
        self.scroll_content = QWidget()
        self.scroll_layout = QVBoxLayout(self.scroll_content)
        self.scroll_layout.setAlignment(Qt.AlignTop)

        # Метка с длинным текстом задачи
        self.label = QLabel("Нажмите 'Новый пример', чтобы начать.")
        self.label.setAlignment(Qt.AlignCenter)
        self.label.setWordWrap(True)  # Разрешить перенос строк
        font = QFont()
        font.setPointSize(int(60 * self.text_scale))
        self.label.setFont(font)

        # Добавляем метку в scroll_layout
        self.scroll_layout.addWidget(self.label)

        # Поле ввода ответа
        self.input_field = QLineEdit()
        self.input_field.setAlignment(Qt.AlignCenter)
        # Стиль поля ввода
        line_edit_style = f"""
        QLineEdit {{
            background-color: white;
            border: 2px solid #ccc;
            border-radius: 8px;
            padding: 8px;
            font-size: {int(60 * self.text_scale)}px;
            color: black;
            width: {int(300 * self.text_scale)}px;
            height: {int(60 * self.text_scale)}px;
        }}
        QLineEdit:focus {{
            border: 2px solid #007acc;
        }}
        """
        self.input_field.setStyleSheet(line_edit_style)
        self.scroll_layout.addWidget(self.input_field)

        # Виртуальная клавиатура
        self.keyboard_layout = QGridLayout() # Сделаем его атрибутом класса
        buttons = [
            ['1', '2', '3'],
            ['4', '5', '6'],
            ['7', '8', '9'],
            ['0', '-', ',']
        ]
        self.keyboard_buttons = [] # Список кнопок клавиатуры
        for i, row in enumerate(buttons):
            button_row = []
            for j, char in enumerate(row):
                btn = QPushButton(char)
                btn.clicked.connect(lambda _, s=char: self.append_to_input(s))
                btn.setStyleSheet(f"""
                QPushButton {{
                    background-color: #ffffff;
                    border: 1px solid #ddd;
                    border-radius: 6px;
                    padding: 8px;
                    font-size: {int(60 * self.text_scale)}px;
                    color: black;
                    min-width: {int(60 * self.ui_scale)}px;
                    min-height: {int(60 * self.ui_scale)}px;
                }}
                QPushButton:hover {{
                    background-color: #f5f5f5;
                }}
                """)
                self.keyboard_layout.addWidget(btn, i, j)
                button_row.append(btn)
            self.keyboard_buttons.append(button_row)
        self.scroll_layout.addLayout(self.keyboard_layout)

        # Кнопки
        self.submit_btn = QPushButton("Проверить")
        self.next_btn = QPushButton("Продолжить")
        self.next_btn.setVisible(False)
        button_style = f"""
        QPushButton {{
            background-color: #f0f0f0;
            border: 1px solid #ccc;
            border-radius: 6px;
            padding: 8px 16px;
            font-size: {int(60 * self.text_scale)}px;
            color: black;
            min-width: {int(100 * self.ui_scale)}px;
            min-height: {int(50 * self.ui_scale)}px;
        }}
        QPushButton:hover {{
            background-color: #e0e0e0;
        }}
        QPushButton:pressed {{
            background-color: #d0d0d0;
        }}
        QPushButton:disabled {{
            background-color: #cccccc;
            color: #888888;
        }}
        """
        self.submit_btn.setStyleSheet(button_style)
        self.next_btn.setStyleSheet(button_style)
        self.scroll_layout.addWidget(self.submit_btn)
        self.scroll_layout.addWidget(self.next_btn)

        # Результат
        self.result_label = QLabel("")
        self.result_label.setAlignment(Qt.AlignCenter)
        self.result_label.setStyleSheet(f"font-size: {int(60 * self.text_scale)}px;")
        self.result_label.hide()
        self.scroll_layout.addWidget(self.result_label)

        # Устанавливаем контент в scroll area
        self.scroll_area.setWidget(self.scroll_content)
        # Добавляем scroll area в основной layout (от BaseTask)
        self.layout.addWidget(self.scroll_area)

        self.a = 0
        self.b = 0
        self.c = 0.0
        self.d = 0.0
        self.correct_answer = 0.0

        self.submit_btn.clicked.connect(self.check_answer)
        self.next_btn.clicked.connect(self.reset_task)

    def append_to_input(self, char):
        current_text = self.input_field.text()
        self.input_field.setText(current_text + char)

    def generate_task(self):
        # Генерация чисел
        a = random.randint(10, 25)  # Чтобы гарантировать, что B < A
        b = random.randint(8, a - 1)
        c = round(random.uniform(1.1, 9.9), 1)
        d = round(random.uniform(1.1, 9.9), 1)

        self.a, self.b, self.c, self.d = a, b, c, d

        # Решаем: (A - B)x = C + D => x = (C + D) / (A - B)
        denominator = a - b
        numerator = c + d
        x = numerator / denominator

        # Проверяем, что результат — конечная дробь с 1 знаком после запятой
        # Если нет — генерируем заново (до тех пор, пока не получим подходящий x)
        while True:
            x = numerator / denominator
            rounded_x = round(x, 1)
            if abs(x - rounded_x) < 1e-9:  # Проверяем, что x == rounded_x (т.е. не 1.234...)
                self.correct_answer = rounded_x
                break
            # Перегенерируем C и D, чтобы получить подходящий x
            c = round(random.uniform(1.1, 9.9), 1)
            d = round(random.uniform(1.1, 9.9), 1)
            numerator = c + d
            self.c, self.d = c, d

        task_str = f"Найдите неизвестное значение x из равенства: {a}x - {b}x = {c} + {d}"
        self.label.setText(task_str)
        self.input_field.clear()
        self.result_label.clear()
        self.result_label.hide()
        self.next_btn.setVisible(False)

    def check_answer(self):
        try:
            user_input = float(self.input_field.text().replace(',', '.'))
            if abs(user_input - self.correct_answer) < 1e-9:
                self.result_label.setText("Правильно!")
                self.result_label.setStyleSheet(f"color: green; font-size:{int(60 * self.text_scale)}px;")
            else:
                self.result_label.setText(f"Неправильно. Правильный ответ: {self.correct_answer:.1f}")
                self.result_label.setStyleSheet(f"color: red; font-size: {int(60 * self.text_scale)}px;")
        except ValueError:
            self.result_label.setText("Введите число.")
            self.result_label.setStyleSheet(f"color: orange; font-size: {int(60 * self.text_scale)}px;")

        self.result_label.show()
        self.submit_btn.setEnabled(False)
        self.next_btn.setVisible(True)

    def reset_task(self):
        self.submit_btn.setEnabled(True)
        self.next_btn.setVisible(False)
        self.result_label.clear()
        self.result_label.hide()
        self.input_field.clear()
        self.generate_task()

    def apply_text_scaling(self, scale):
        self.text_scale = scale
        font = QFont()
        font.setPointSize(int(60 * self.text_scale))
        self.label.setFont(font)
        line_edit_style = f"""
        QLineEdit {{
            background-color: white;
            border: 2px solid #ccc;
            border-radius: 8px;
            padding: 8px;
            font-size: {int(60 * self.text_scale)}px;
            color: black;
            width: {int(300 * self.text_scale)}px;
            height: {int(60 * self.text_scale)}px;
        }}
        QLineEdit:focus {{
            border: 2px solid #007acc;
        }}
        """
        self.input_field.setStyleSheet(line_edit_style)
        for row in self.keyboard_buttons:
            for btn in row:
                btn.setStyleSheet(f"""
                QPushButton {{
                    background-color: #ffffff;
                    border: 1px solid #ddd;
                    border-radius: 6px;
                    padding: 8px;
                    font-size: {int(60 * self.text_scale)}px;
                    color: black;
                    min-width: {int(60 * self.ui_scale)}px;
                    min-height: {int(60 * self.ui_scale)}px;
                }}
                QPushButton:hover {{
                    background-color: #f5f5f5;
                }}
                """)
        self.submit_btn.setFont(QFont("Arial", int(60 * self.text_scale)))
        self.submit_btn.setStyleSheet(f"""
        QPushButton {{
            background-color: #f0f0f0;
            border: 1px solid #ccc;
            border-radius: 6px;
            padding: 8px 16px;
            font-size: {int(60 * self.text_scale)}px;
            color: black;
            min-width: {int(100 * self.ui_scale)}px;
            min-height: {int(50 * self.ui_scale)}px;
        }}
        QPushButton:hover {{
            background-color: #e0e0e0;
        }}
        """)
        self.next_btn.setFont(QFont("Arial", int(60 * self.text_scale)))
        self.next_btn.setStyleSheet(f"""
        QPushButton {{
            background-color: #f0f0f0;
            border: 1px solid #ccc;
            border-radius: 6px;
            padding: 8px 16px;
            font-size: {int(60 * self.text_scale)}px;
            color: black;
            min-width: {int(100 * self.ui_scale)}px;
            min-height: {int(50 * self.ui_scale)}px;
        }}
        QPushButton:hover {{
            background-color: #e0e0e0;
        }}
        """)
        self.result_label.setStyleSheet(f"font-size: {int(60 * self.text_scale)}px;")

    def apply_ui_scaling(self, scale):
        self.ui_scale = scale
        for row in self.keyboard_buttons:
            for btn in row:
                btn.setStyleSheet(f"""
                QPushButton {{
                    background-color: #ffffff;
                    border: 1px solid #ddd;
                    border-radius: 6px;
                    padding: 8px;
                    font-size: {int(60 * self.text_scale)}px;
                    color: black;
                    min-width: {int(60 * self.ui_scale)}px;
                    min-height: {int(60 * self.ui_scale)}px;
                }}
                QPushButton:hover {{
                    background-color: #f5f5f5;
                }}
                """)
        self.submit_btn.setStyleSheet(f"""
        QPushButton {{
            background-color: #f0f0f0;
            border: 1px solid #ccc;
            border-radius: 6px;
            padding: 8px 16px;
            font-size: {int(60 * self.text_scale)}px;
            color: black;
            min-width: {int(100 * self.ui_scale)}px;
            min-height: {int(50 * self.ui_scale)}px;
        }}
        QPushButton:hover {{
            background-color: #e0e0e0;
        }}
        """)
        self.next_btn.setStyleSheet(f"""
        QPushButton {{
            background-color: #f0f0f0;
            border: 1px solid #ccc;
            border-radius: 6px;
            padding: 8px 16px;
            font-size: {int(60 * self.text_scale)}px;
            color: black;
            min-width: {int(100 * self.ui_scale)}px;
            min-height: {int(50 * self.ui_scale)}px;
        }}
        QPushButton:hover {{
            background-color: #e0e0e0;
        }}
        """)

class Task6(BaseTask):
    def __init__(self, text_scale=1.0, ui_scale=1.0):
        super().__init__(text_scale, ui_scale)

        # Создаем ScrollArea
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setStyleSheet("border: none;")
        # Виджет внутри ScrollArea
        self.scroll_content = QWidget()
        self.scroll_layout = QVBoxLayout(self.scroll_content)
        self.scroll_layout.setAlignment(Qt.AlignTop)

        # Метка с длинным текстом задачи
        self.label = QLabel("Нажмите 'Новый пример', чтобы начать.")
        self.label.setAlignment(Qt.AlignCenter)
        self.label.setWordWrap(True)  # Разрешить перенос строк
        font = QFont()
        font.setPointSize(int(60 * self.text_scale))
        self.label.setFont(font)

        # Добавляем метку в scroll_layout
        self.scroll_layout.addWidget(self.label)

        # Поле ввода ответа
        self.input_field = QLineEdit()
        self.input_field.setAlignment(Qt.AlignCenter)

        # Стиль поля ввода
        line_edit_style = f"""
            QLineEdit {{
                background-color: white;
                border: 2px solid #ccc;
                border-radius: 8px;
                padding: 8px;
                font-size: {int(60 * self.text_scale)}px;
                color: black;
            }}
            QLineEdit:focus {{
                border: 2px solid #007acc;
            }}
        """
        self.input_field.setStyleSheet(line_edit_style)
        self.scroll_layout.addWidget(self.input_field)

        # Виртуальная клавиатура
        self.keyboard_layout = QGridLayout() # Сделаем его атрибутом класса
        self.keyboard_buttons = [] # Список кнопок клавиатуры
        self.setup_virtual_keyboard()

        # Результат
        self.result_label = QLabel("")
        self.result_label.setAlignment(Qt.AlignCenter)
        self.result_label.setStyleSheet(f"font-size: {int(60 * self.text_scale)}px;")
        self.result_label.hide()
        self.scroll_layout.addWidget(self.result_label)

        # Кнопки
        self.submit_btn = QPushButton("Проверить")
        self.next_btn = QPushButton("Продолжить")
        self.next_btn.setVisible(False)

        button_style = f"""
            QPushButton {{
                background-color: #f0f0f0;
                border: 1px solid #ccc;
                border-radius: 6px;
                padding: 8px 16px;
                font-size: {int(60 * self.text_scale)}px;
                color: black;
                min-width: {int(100 * self.ui_scale)}px;
                min-height: {int(50 * self.ui_scale)}px;
            }}
            QPushButton:hover {{
                background-color: #e0e0e0;
            }}
            QPushButton:pressed {{
                background-color: #d0d0d0;
            }}
            QPushButton:disabled {{
                background-color: #cccccc;
                color: #888888;
            }}
        """
        self.submit_btn.setStyleSheet(button_style)
        self.next_btn.setStyleSheet(button_style)
        self.scroll_layout.addWidget(self.submit_btn)
        self.scroll_layout.addWidget(self.next_btn)

        # Устанавливаем контент в scroll area
        self.scroll_area.setWidget(self.scroll_content)
        # Добавляем scroll area в основной layout (от BaseTask)
        self.layout.addWidget(self.scroll_area)

        self.submit_btn.clicked.connect(self.check_answer)
        self.next_btn.clicked.connect(self.reset_task)

    def setup_virtual_keyboard(self):
        buttons = [
            ['1', '2', '3'],
            ['4', '5', '6'],
            ['7', '8', '9'],
            ['0', '-', ',']
        ]
        for i, row in enumerate(buttons):
            button_row = []
            for j, char in enumerate(row):
                btn = QPushButton(char)
                btn.clicked.connect(lambda _, s=char: self.append_to_input(s))
                btn.setStyleSheet(f"""
                    QPushButton {{
                        background-color: #ffffff;
                        border: 1px solid #ddd;
                        border-radius: 6px;
                        padding: 8px;
                        font-size: {int(60 * self.text_scale)}px;
                        color: black;
                        min-width: {int(60 * self.ui_scale)}px;
                        min-height: {int(60 * self.ui_scale)}px;
                    }}
                    QPushButton:hover {{
                        background-color: #f5f5f5;
                    }}
                """)
                self.keyboard_layout.addWidget(btn, i, j)
                button_row.append(btn)
            self.keyboard_buttons.append(button_row)
        self.scroll_layout.addLayout(self.keyboard_layout) # Добавляем лэйаут клавиатуры в scroll_layout

    def append_to_input(self, char):
        current_text = self.input_field.text()
        self.input_field.setText(current_text + char)

    def generate_task(self):
        # Генерация чисел
        a = random.randint(10, 99) * 10  # Трёхзначное, кратное 10
        b = random.randint(2, 8)         # Время в первый день
        c = random.choice([5, 10, 15, 20, 25])  # Кратное 5

        self.a, self.b, self.c = a, b, c

        # Скорость в первый день
        speed1 = a / b

        # Скорость на обратном пути
        speed2 = speed1 - c

        # Проверяем, что t2 < 10, t2 != 0, и имеет формат X.5 (одна цифра после запятой, Y = 5)
        while True:
            if speed2 == 0:
                # Перегенерация, чтобы избежать деления на 0
                a = random.randint(10, 99) * 10
                b = random.randint(2, 8)
                c = random.choice([5, 10, 15, 20, 25])
                self.a, self.b, self.c = a, b, c
                speed1 = a / b
                speed2 = speed1 - c
                continue

            t2 = a / speed2
            if t2 >= 10:
                # Перегенерация
                a = random.randint(10, 99) * 10
                b = random.randint(2, 8)
                speed1 = a / b
                speed2 = speed1 - c
                continue

            rounded_t2 = round(t2, 1)
            if abs(t2 - rounded_t2) < 1e-9:
                decimal_part = (rounded_t2 * 10) % 10
                if decimal_part == 5:
                    self.correct_answer = rounded_t2
                    break

            # Иначе снова генерируем
            a = random.randint(10, 99) * 10
            b = random.randint(2, 8)
            c = random.choice([5, 10, 15, 20, 25])
            self.a, self.b, self.c = a, b, c
            speed1 = a / b
            speed2 = speed1 - c

        # Формируем текст задачи
        task_text = (
            f"Автомобиль проехал с постоянной скоростью {a} км "
            f"от города А до города Б за {b} ч. На следующий день "
            f"автомобиль проехал тот же путь обратно со скоростью "
            f"на {c} км/ч меньше, чем в первый день. "
            f"Сколько часов потребовалось автомобилю на обратный путь?"
        )

        self.label.setText(task_text)
        self.input_field.clear()
        self.result_label.clear()
        self.result_label.hide()
        self.next_btn.setVisible(False)

    def check_answer(self):
        try:
            user_input = float(self.input_field.text().replace(',', '.'))
            if abs(user_input - self.correct_answer) < 1e-9:
                self.result_label.setText("Правильно!")
                self.result_label.setStyleSheet(f"color: green; font-size:{int(60 * self.text_scale)}px;")
            else:
                self.result_label.setText(f"Неправильно. Правильный ответ: {self.correct_answer:.1f}")
                self.result_label.setStyleSheet(f"color: red; font-size: {int(60 * self.text_scale)}px;")
        except ValueError:
            self.result_label.setText("Введите число.")
            self.result_label.setStyleSheet(f"color: orange; font-size: {int(60 * self.text_scale)}px;")

        self.result_label.show()
        self.submit_btn.setEnabled(False)
        self.next_btn.setVisible(True)

    def reset_task(self):
        self.submit_btn.setEnabled(True)
        self.next_btn.setVisible(False)
        self.result_label.clear()
        self.result_label.hide()
        self.input_field.clear()
        self.generate_task()

    def apply_text_scaling(self, scale):
        self.text_scale = scale
        font = QFont()
        font.setPointSize(int(60 * self.text_scale))
        self.label.setFont(font)
        line_edit_style = f"""
            QLineEdit {{
                background-color: white;
                border: 2px solid #ccc;
                border-radius: 8px;
                padding: 8px;
                font-size: {int(60 * self.text_scale)}px;
                color: black;
            }}
            QLineEdit:focus {{
                border: 2px solid #007acc;
            }}
        """
        self.input_field.setStyleSheet(line_edit_style)
        for row in self.keyboard_buttons:
            for btn in row:
                btn.setStyleSheet(f"""
                    QPushButton {{
                        background-color: #ffffff;
                        border: 1px solid #ddd;
                        border-radius: 6px;
                        padding: 8px;
                        font-size: {int(60 * self.text_scale)}px;
                        color: black;
                        min-width: {int(60 * self.ui_scale)}px;
                        min-height: {int(60 * self.ui_scale)}px;
                    }}
                    QPushButton:hover {{
                        background-color: #f5f5f5;
                    }}
                """)
        self.submit_btn.setFont(QFont("Arial", int(60 * self.text_scale)))
        self.submit_btn.setStyleSheet(f"""
        QPushButton {{
            background-color: #f0f0f0;
            border: 1px solid #ccc;
            border-radius: 6px;
            padding: 8px 16px;
            font-size: {int(60 * self.text_scale)}px;
            color: black;
            min-width: {int(100 * self.ui_scale)}px;
            min-height: {int(50 * self.ui_scale)}px;
        }}
        QPushButton:hover {{
            background-color: #e0e0e0;
        }}
        """)
        self.next_btn.setFont(QFont("Arial", int(60 * self.text_scale)))
        self.next_btn.setStyleSheet(f"""
        QPushButton {{
            background-color: #f0f0f0;
            border: 1px solid #ccc;
            border-radius: 6px;
            padding: 8px 16px;
            font-size: {int(60 * self.text_scale)}px;
            color: black;
            min-width: {int(100 * self.ui_scale)}px;
            min-height: {int(50 * self.ui_scale)}px;
        }}
        QPushButton:hover {{
            background-color: #e0e0e0;
        }}
        """)
        self.result_label.setStyleSheet(f"font-size: {int(60 * self.text_scale)}px;")

    def apply_ui_scaling(self, scale):
        self.ui_scale = scale
        for row in self.keyboard_buttons:
            for btn in row:
                btn.setStyleSheet(f"""
                    QPushButton {{
                        background-color: #ffffff;
                        border: 1px solid #ddd;
                        border-radius: 6px;
                        padding: 8px;
                        font-size: {int(60 * self.text_scale)}px;
                        color: black;
                        min-width: {int(60 * self.ui_scale)}px;
                        min-height: {int(60 * self.ui_scale)}px;
                    }}
                    QPushButton:hover {{
                        background-color: #f5f5f5;
                    }}
                """)
        self.submit_btn.setStyleSheet(f"""
        QPushButton {{
            background-color: #f0f0f0;
            border: 1px solid #ccc;
            border-radius: 6px;
            padding: 8px 16px;
            font-size: {int(60 * self.text_scale)}px;
            color: black;
            min-width: {int(100 * self.ui_scale)}px;
            min-height: {int(50 * self.ui_scale)}px;
        }}
        QPushButton:hover {{
            background-color: #e0e0e0;
        }}
        """)
        self.next_btn.setStyleSheet(f"""
        QPushButton {{
            background-color: #f0f0f0;
            border: 1px solid #ccc;
            border-radius: 6px;
            padding: 8px 16px;
            font-size: {int(60 * self.text_scale)}px;
            color: black;
            min-width: {int(100 * self.ui_scale)}px;
            min-height: {int(50 * self.ui_scale)}px;
        }}
        QPushButton:hover {{
            background-color: #e0e0e0;
        }}
        """)

class Task7(BaseTask):
    def __init__(self, text_scale=1.0, ui_scale=1.0):
        super().__init__(text_scale, ui_scale)

        # Создаем ScrollArea
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setStyleSheet("border: none;")
        # Виджет внутри ScrollArea
        self.scroll_content = QWidget()
        self.scroll_layout = QVBoxLayout(self.scroll_content)
        self.scroll_layout.setAlignment(Qt.AlignTop)

        # Заголовок
        self.label = QLabel("")
        self.label.setAlignment(Qt.AlignCenter)
        font = QFont()
        font.setPointSize(int(60 * self.text_scale))
        self.label.setFont(font)

        # Отображение примера в виде дробей
        self.task_display = QLabel("")
        self.task_display.setAlignment(Qt.AlignCenter)
        self.task_display.setStyleSheet(f"font-size: {int(60 * self.text_scale)}px;")

        # Поле ввода ответа в формате -1/N
        self.input_field = QLineEdit()
        self.input_field.setAlignment(Qt.AlignCenter)
        self.input_field.setPlaceholderText("Несократимая обыкновенная дробь")

        # Стиль поля ввода
        line_edit_style = f"""
            QLineEdit {{
                background-color: white;
                border: 2px solid #ccc;
                border-radius: 8px;
                padding: 8px;
                font-size: {int(40 * self.text_scale)}px;
                color: black;
                width: {int(200 * self.text_scale)}px;
                height: {int(60 * self.text_scale)}px;
            }}
            QLineEdit:focus {{
                border: 2px solid #007acc;
            }}
        """
        self.input_field.setStyleSheet(line_edit_style)

        # Виртуальная клавиатура (заменяем "," на "/")
        self.keyboard_layout = QGridLayout() # Сделаем его атрибутом класса
        self.keyboard_buttons = [] # Список кнопок клавиатуры
        buttons = [
            ['1', '2', '3'],
            ['4', '5', '6'],
            ['7', '8', '9'],
            ['0', '-', '/']  # Заменяем запятую на "/"
        ]
        for i, row in enumerate(buttons):
            button_row = []
            for j, char in enumerate(row):
                btn = QPushButton(char)
                btn.clicked.connect(lambda _, s=char: self.append_to_input(s))
                btn.setStyleSheet(f"""
                    QPushButton {{
                        background-color: #ffffff;
                        border: 1px solid #ddd;
                        border-radius: 6px;
                        padding: 8px;
                        font-size: {int(60 * self.text_scale)}px;
                        color: black;
                        min-width: {int(60 * self.ui_scale)}px;
                        min-height: {int(60 * self.ui_scale)}px;
                    }}
                    QPushButton:hover {{
                        background-color: #f5f5f5;
                    }}
                """)
                self.keyboard_layout.addWidget(btn, i, j)
                button_row.append(btn)
            self.keyboard_buttons.append(button_row)

        # Кнопки
        self.submit_btn = QPushButton("Проверить")
        self.next_btn = QPushButton("Продолжить")
        self.next_btn.setVisible(False)

        button_style = f"""
            QPushButton {{
                background-color: #f0f0f0;
                border: 1px solid #ccc;
                border-radius: 6px;
                padding: 8px 16px;
                font-size: {int(60 * self.text_scale)}px;
                color: black;
                min-width: {int(100 * self.ui_scale)}px;
                min-height: {int(50 * self.ui_scale)}px;
            }}
            QPushButton:hover {{
                background-color: #e0e0e0;
            }}
            QPushButton:pressed {{
                background-color: #d0d0d0;
            }}
            QPushButton:disabled {{
                background-color: #cccccc;
                color: #888888;
            }}
        """
        self.submit_btn.setStyleSheet(button_style)
        self.next_btn.setStyleSheet(button_style)

        # Результат
        self.result_label = QLabel("")
        self.result_label.setAlignment(Qt.AlignCenter)
        self.result_label.setStyleSheet(f"font-size: {int(60 * self.text_scale)}px;")
        self.result_label.hide()

        # Компоновка в scroll_layout
        self.scroll_layout.addWidget(self.label)
        self.scroll_layout.addWidget(self.task_display)
        self.scroll_layout.addSpacing(int(20 * self.text_scale))
        self.scroll_layout.addWidget(self.input_field)
        self.scroll_layout.addLayout(self.keyboard_layout)
        self.scroll_layout.addWidget(self.submit_btn)
        self.scroll_layout.addWidget(self.result_label)
        self.scroll_layout.addWidget(self.next_btn)

        # Устанавливаем контент в scroll area
        self.scroll_area.setWidget(self.scroll_content)
        # Добавляем scroll area в основной layout (от BaseTask)
        self.layout.addWidget(self.scroll_area)

        self.submit_btn.clicked.connect(self.check_answer)
        self.next_btn.clicked.connect(self.reset_task)

    def append_to_input(self, char):
        current_text = self.input_field.text()
        self.input_field.setText(current_text + char)

    def generate_task(self):
        # Генерация чисел
        # б: дробь, числитель < знаменателя, знаменатель от 3 до 8
        den_b = random.randint(3, 8)
        num_b = random.randint(1, den_b - 1)
        frac_b = Fraction(num_b, den_b)

        # в: дробь, числитель может быть >= знаменателя, но не кратен ему
        den_v = random.randint(4, 12)
        num_v = random.randint(1, den_v + 2)
        while num_v % den_v == 0:
            num_v = random.randint(1, den_v + 2)
        frac_v = Fraction(num_v, den_v)

        # г: аналогично в, но НЕ совпадает с в
        while True:
            den_g = random.randint(4, 12)
            num_g = random.randint(1, den_g + 2)
            while num_g % den_g == 0:
                num_g = random.randint(1, den_g + 2)
            frac_g = Fraction(num_g, den_g)
            if frac_g != frac_v:
                break  # Успешно сгенерирована дробь, отличающаяся от frac_v

        # д: числитель от 3*den до 13*den, знаменатель от 3 до 7
        den_d = random.randint(3, 7)
        num_d = random.randint(3 * den_d, 13 * den_d)
        while num_d % den_d == 0:
            num_d = random.randint(3 * den_d, 13 * den_d)
        frac_d = Fraction(num_d, den_d)

        # е: целое число от 2 до 9
        e = random.randint(2, 9)

        # Вычисляем: (1 + frac_b) * (frac_v + frac_g) - frac_d / e
        mixed_num = 1 + frac_b
        sum_fractions = frac_v + frac_g
        div_frac = frac_d / e

        result = mixed_num * sum_fractions - div_frac

        # Проверяем, что результат — отрицательная дробь вида -1/N
        while not (result < 0 and result.numerator == -1 and 2 <= result.denominator <= 9):
            # Перегенерация
            den_b = random.randint(3, 8)
            num_b = random.randint(1, den_b - 1)
            frac_b = Fraction(num_b, den_b)

            den_v = random.randint(4, 12)
            num_v = random.randint(1, den_v + 2)
            while num_v % den_v == 0:
                num_v = random.randint(1, den_v + 2)
            frac_v = Fraction(num_v, den_v)

            # г: аналогично в, но НЕ совпадает с в
            while True:
                den_g = random.randint(4, 12)
                num_g = random.randint(1, den_g + 2)
                while num_g % den_g == 0:
                    num_g = random.randint(1, den_g + 2)
                frac_g = Fraction(num_g, den_g)
                if frac_g != frac_v:
                    break

            den_d = random.randint(3, 7)
            num_d = random.randint(3 * den_d, 13 * den_d)
            while num_d % den_d == 0:
                num_d = random.randint(3 * den_d, 13 * den_d)
            frac_d = Fraction(num_d, den_d)

            e = random.randint(2, 9)

            mixed_num = 1 + frac_b
            sum_fractions = frac_v + frac_g
            div_frac = frac_d / e
            result = mixed_num * sum_fractions - div_frac

        self.frac_b = frac_b
        self.frac_v = frac_v
        self.frac_g = frac_g
        self.frac_d = frac_d
        self.e = e
        self.correct_answer = result

        # Формируем HTML-строку для отображения
        task_html = f"""
        <div style="text-align: center;">
        <span style="font-size: {int(60 * self.text_scale)}px;">
        1<sup>{frac_b.numerator}</sup>&frasl;<sub>{frac_b.denominator}</sub> &times; (<sup>{frac_v.numerator}</sup>&frasl;<sub>{frac_v.denominator}</sub> + <sup>{frac_g.numerator}</sup>&frasl;<sub>{frac_g.denominator}</sub>) &minus; <sup>{frac_d.numerator}</sup>&frasl;<sub>{frac_d.denominator}</sub> &divide; {e}
        </span>
        </div>
        """
        self.label.setText(task_html)

        self.update_label_html()  # ← Используем новый метод


        # Очистка
        self.input_field.clear()
        self.result_label.clear()
        self.result_label.hide()
        self.next_btn.setVisible(False)


    def check_answer(self):
        try:
            user_input_str = self.input_field.text().strip()
            if '/' not in user_input_str:
                raise ValueError("Введите дробь в формате -1/N")
            parts = user_input_str.split('/')
            if len(parts) != 2:
                raise ValueError("Введите дробь в формате -1/N")
            num = int(parts[0])
            den = int(parts[1])
            user_frac = Fraction(num, den)
        except ValueError:
            self.result_label.setText("Введите дробь в формате -1/N")
            self.result_label.setStyleSheet(f"color: orange; font-size: {int(60 * self.text_scale)}px;")
            self.result_label.show()
            return

        if user_frac == self.correct_answer:
            self.result_label.setText("Правильно!")
            self.result_label.setStyleSheet(f"color: green; font-size: {int(60 * self.text_scale)}px;")
        else:
            self.result_label.setText(f"Неправильно. Правильный ответ: {self.correct_answer}")
            self.result_label.setStyleSheet(f"color: red; font-size: {int(60 * self.text_scale)}px;")

        self.result_label.show()
        self.submit_btn.setEnabled(False)
        self.next_btn.setVisible(True)

    def reset_task(self):
        self.submit_btn.setEnabled(True)
        self.next_btn.setVisible(False)
        self.result_label.clear()
        self.result_label.hide()
        self.input_field.clear()
        self.generate_task()
    
    def update_label_html(self):
        """Пересоздаёт HTML-строку для self.label с учётом текущего text_scale."""
        if not hasattr(self, 'frac_b'):
            # Если задача ещё не сгенерирована, ничего не делаем
            return

        task_html = f"""
        <div style="text-align: center;">
        <span style="font-size: {int(60 * self.text_scale)}px;">
        1<sup>{self.frac_b.numerator}</sup>&frasl;<sub>{self.frac_b.denominator}</sub> &times; (<sup>{self.frac_v.numerator}</sup>&frasl;<sub>{self.frac_v.denominator}</sub> + <sup>{self.frac_g.numerator}</sup>&frasl;<sub>{self.frac_g.denominator}</sub>) &minus; <sup>{self.frac_d.numerator}</sup>&frasl;<sub>{self.frac_d.denominator}</sub> &divide; {self.e}
        </span>
        </div>
        """
        self.label.setText(task_html)

    def apply_text_scaling(self, scale):
        self.text_scale = scale
        font = QFont()
        font.setPointSize(int(60 * self.text_scale))
        self.label.setFont(font)
        self.task_display.setStyleSheet(f"font-size: {int(60 * self.text_scale)}px;")
        line_edit_style = f"""
            QLineEdit {{
                background-color: white;
                border: 2px solid #ccc;
                border-radius: 8px;
                padding: 8px;
                font-size: {int(40 * self.text_scale)}px;
                color: black;
                width: {int(200 * self.text_scale)}px;
                height: {int(60 * self.text_scale)}px;
            }}
            QLineEdit:focus {{
                border: 2px solid #007acc;
            }}
        """
        self.input_field.setStyleSheet(line_edit_style)
        for row in self.keyboard_buttons:
            for btn in row:
                btn.setStyleSheet(f"""
                    QPushButton {{
                        background-color: #ffffff;
                        border: 1px solid #ddd;
                        border-radius: 6px;
                        padding: 8px;
                        font-size: {int(60 * self.text_scale)}px;
                        color: black;
                        min-width: {int(60 * self.ui_scale)}px;
                        min-height: {int(60 * self.ui_scale)}px;
                    }}
                    QPushButton:hover {{
                        background-color: #f5f5f5;
                    }}
                """)
        self.submit_btn.setFont(QFont("Arial", int(60 * self.text_scale)))
        self.submit_btn.setStyleSheet(f"""
        QPushButton {{
            background-color: #f0f0f0;
            border: 1px solid #ccc;
            border-radius: 6px;
            padding: 8px 16px;
            font-size: {int(60 * self.text_scale)}px;
            color: black;
            min-width: {int(100 * self.ui_scale)}px;
            min-height: {int(50 * self.ui_scale)}px;
        }}
        QPushButton:hover {{
            background-color: #e0e0e0;
        }}
        """)
        self.next_btn.setFont(QFont("Arial", int(60 * self.text_scale)))
        self.next_btn.setStyleSheet(f"""
        QPushButton {{
            background-color: #f0f0f0;
            border: 1px solid #ccc;
            border-radius: 6px;
            padding: 8px 16px;
            font-size: {int(60 * self.text_scale)}px;
            color: black;
            min-width: {int(100 * self.ui_scale)}px;
            min-height: {int(50 * self.ui_scale)}px;
        }}
        QPushButton:hover {{
            background-color: #e0e0e0;
        }}
        """)
        self.result_label.setStyleSheet(f"font-size: {int(60 * self.text_scale)}px;")
        self.update_label_html()

    def apply_ui_scaling(self, scale):
        self.ui_scale = scale
        for row in self.keyboard_buttons:
            for btn in row:
                btn.setStyleSheet(f"""
                    QPushButton {{
                        background-color: #ffffff;
                        border: 1px solid #ddd;
                        border-radius: 6px;
                        padding: 8px;
                        font-size: {int(60 * self.text_scale)}px;
                        color: black;
                        min-width: {int(60 * self.ui_scale)}px;
                        min-height: {int(60 * self.ui_scale)}px;
                    }}
                    QPushButton:hover {{
                        background-color: #f5f5f5;
                    }}
                """)
        self.submit_btn.setStyleSheet(f"""
        QPushButton {{
            background-color: #f0f0f0;
            border: 1px solid #ccc;
            border-radius: 6px;
            padding: 8px 16px;
            font-size: {int(60 * self.text_scale)}px;
            color: black;
            min-width: {int(100 * self.ui_scale)}px;
            min-height: {int(50 * self.ui_scale)}px;
        }}
        QPushButton:hover {{
            background-color: #e0e0e0;
        }}
        """)
        self.next_btn.setStyleSheet(f"""
        QPushButton {{
            background-color: #f0f0f0;
            border: 1px solid #ccc;
            border-radius: 6px;
            padding: 8px 16px;
            font-size: {int(60 * self.text_scale)}px;
            color: black;
            min-width: {int(100 * self.ui_scale)}px;
            min-height: {int(50 * self.ui_scale)}px;
        }}
        QPushButton:hover {{
            background-color: #e0e0e0;
        }}
        """)

class Task8(BaseTask):
    def __init__(self, text_scale=1.0, ui_scale=1.0):
        super().__init__(text_scale, ui_scale)

        # Создаем ScrollArea
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setStyleSheet("border: none;")
        # Виджет внутри ScrollArea
        self.scroll_content = QWidget()
        self.scroll_layout = QVBoxLayout(self.scroll_content)
        self.scroll_layout.setAlignment(Qt.AlignTop)

        # Метка с длинным текстом задачи
        self.label = QLabel("Нажмите 'Новый пример', чтобы начать.")
        self.label.setAlignment(Qt.AlignCenter)
        self.label.setWordWrap(True)  # Разрешить перенос строк
        font = QFont()
        font.setPointSize(int(60 * self.text_scale))
        self.label.setFont(font)

        # Добавляем метку в scroll_layout
        self.scroll_layout.addWidget(self.label)

        # Поле ввода ответа
        self.input_field = QLineEdit()
        self.input_field.setAlignment(Qt.AlignCenter)

        # Стиль поля ввода
        line_edit_style = f"""
            QLineEdit {{
                background-color: white;
                border: 2px solid #ccc;
                border-radius: 8px;
                padding: 8px;
                font-size: {int(60 * self.text_scale)}px;
                color: black;
            }}
            QLineEdit:focus {{
                border: 2px solid #007acc;
            }}
        """
        self.input_field.setStyleSheet(line_edit_style)
        self.scroll_layout.addWidget(self.input_field)

        # Виртуальная клавиатура
        self.keyboard_layout = QGridLayout() # Сделаем его атрибутом класса
        self.keyboard_buttons = [] # Список кнопок клавиатуры
        self.setup_virtual_keyboard()

        # Результат
        self.result_label = QLabel("")
        self.result_label.setAlignment(Qt.AlignCenter)
        self.result_label.setStyleSheet(f"font-size: {int(60 * self.text_scale)}px;")
        self.result_label.hide()
        self.scroll_layout.addWidget(self.result_label)

        # Кнопки
        self.submit_btn = QPushButton("Проверить")
        self.next_btn = QPushButton("Продолжить")
        self.next_btn.setVisible(False)

        button_style = f"""
            QPushButton {{
                background-color: #f0f0f0;
                border: 1px solid #ccc;
                border-radius: 6px;
                padding: 8px 16px;
                font-size: {int(60 * self.text_scale)}px;
                color: black;
                min-width: {int(100 * self.ui_scale)}px;
                min-height: {int(50 * self.ui_scale)}px;
            }}
            QPushButton:hover {{
                background-color: #e0e0e0;
            }}
            QPushButton:pressed {{
                background-color: #d0d0d0;
            }}
            QPushButton:disabled {{
                background-color: #cccccc;
                color: #888888;
            }}
        """
        self.submit_btn.setStyleSheet(button_style)
        self.next_btn.setStyleSheet(button_style)
        self.scroll_layout.addWidget(self.submit_btn)
        self.scroll_layout.addWidget(self.next_btn)

        # Устанавливаем контент в scroll area
        self.scroll_area.setWidget(self.scroll_content)
        # Добавляем scroll area в основной layout (от BaseTask)
        self.layout.addWidget(self.scroll_area)

        self.submit_btn.clicked.connect(self.check_answer)
        self.next_btn.clicked.connect(self.reset_task)

    def setup_virtual_keyboard(self):
        buttons = [
            ['1', '2', '3'],
            ['4', '5', '6'],
            ['7', '8', '9'],
            ['0', '-', ',']
        ]
        for i, row in enumerate(buttons):
            button_row = []
            for j, char in enumerate(row):
                btn = QPushButton(char)
                btn.clicked.connect(lambda _, s=char: self.append_to_input(s))
                btn.setStyleSheet(f"""
                    QPushButton {{
                        background-color: #ffffff;
                        border: 1px solid #ddd;
                        border-radius: 6px;
                        padding: 8px;
                        font-size: {int(60 * self.text_scale)}px;
                        color: black;
                        min-width: {int(60 * self.ui_scale)}px;
                        min-height: {int(60 * self.ui_scale)}px;
                    }}
                    QPushButton:hover {{
                        background-color: #f5f5f5;
                    }}
                """)
                self.keyboard_layout.addWidget(btn, i, j)
                button_row.append(btn)
            self.keyboard_buttons.append(button_row)
        self.scroll_layout.addLayout(self.keyboard_layout) # Добавляем лэйаут клавиатуры в scroll_layout

    def append_to_input(self, char):
        current_text = self.input_field.text()
        self.input_field.setText(current_text + char)

    def generate_task(self):
        # Генерация чисел
        b = random.randint(2, 6)  # Отношение этажей к квартирам на этаже
        y = random.randint(6, 25)  # Число этажей

        # Квартир на этаже = y / b
        if y % b != 0:
            # Перегенерировать y, пока оно не будет кратно b
            while y % b != 0:
                y = random.randint(6, 25)

        x = y // b  # Квартир на этаже
        a = random.randint(100, 999)  # Общее число квартир

        # Проверяем, что a делится на x
        while a % x != 0:
            a = random.randint(100, 999)

        self.a, self.b, self.y = a, b, y

        # Формируем текст задачи
        task_text = (
            f"В многоквартирном доме {a} квартир. Известно, что во всех подъездах дома "
            f"одинаковое число этажей и на любом этаже каждого подъезда одинаковое число "
            f"квартир (больше одной). Сколько этажей в этом доме, если число квартир "
            f"на каждом этаже в подъезде в {b} раза меньше числа этажей в доме?"
        )

        self.label.setText(task_text)
        self.input_field.clear()
        self.result_label.clear()
        self.result_label.hide()
        self.next_btn.setVisible(False)

    def check_answer(self):
        try:
            user_input = int(self.input_field.text().strip())
            if user_input == self.y:
                self.result_label.setText("Правильно!")
                self.result_label.setStyleSheet(f"color: green; font-size:{int(60 * self.text_scale)}px;")
            else:
                self.result_label.setText(f"Неправильно. Правильный ответ: {self.y}")
                self.result_label.setStyleSheet(f"color: red; font-size: {int(60 * self.text_scale)}px;")
        except ValueError:
            self.result_label.setText("Введите целое число.")
            self.result_label.setStyleSheet(f"color: orange; font-size: {int(60 * self.text_scale)}px;")

        self.result_label.show()
        self.submit_btn.setEnabled(False)
        self.next_btn.setVisible(True)

    def reset_task(self):
        self.submit_btn.setEnabled(True)
        self.next_btn.setVisible(False)
        self.result_label.clear()
        self.result_label.hide()
        self.input_field.clear()
        self.generate_task()

    def apply_text_scaling(self, scale):
        self.text_scale = scale
        font = QFont()
        font.setPointSize(int(60 * self.text_scale))
        self.label.setFont(font)
        line_edit_style = f"""
            QLineEdit {{
                background-color: white;
                border: 2px solid #ccc;
                border-radius: 8px;
                padding: 8px;
                font-size: {int(60 * self.text_scale)}px;
                color: black;
            }}
            QLineEdit:focus {{
                border: 2px solid #007acc;
            }}
        """
        self.input_field.setStyleSheet(line_edit_style)
        for row in self.keyboard_buttons:
            for btn in row:
                btn.setStyleSheet(f"""
                    QPushButton {{
                        background-color: #ffffff;
                        border: 1px solid #ddd;
                        border-radius: 6px;
                        padding: 8px;
                        font-size: {int(60 * self.text_scale)}px;
                        color: black;
                        min-width: {int(60 * self.ui_scale)}px;
                        min-height: {int(60 * self.ui_scale)}px;
                    }}
                    QPushButton:hover {{
                        background-color: #f5f5f5;
                    }}
                """)
        self.submit_btn.setFont(QFont("Arial", int(60 * self.text_scale)))
        self.submit_btn.setStyleSheet(f"""
        QPushButton {{
            background-color: #f0f0f0;
            border: 1px solid #ccc;
            border-radius: 6px;
            padding: 8px 16px;
            font-size: {int(60 * self.text_scale)}px;
            color: black;
            min-width: {int(100 * self.ui_scale)}px;
            min-height: {int(50 * self.ui_scale)}px;
        }}
        QPushButton:hover {{
            background-color: #e0e0e0;
        }}
        """)
        self.next_btn.setFont(QFont("Arial", int(60 * self.text_scale)))
        self.next_btn.setStyleSheet(f"""
        QPushButton {{
            background-color: #f0f0f0;
            border: 1px solid #ccc;
            border-radius: 6px;
            padding: 8px 16px;
            font-size: {int(60 * self.text_scale)}px;
            color: black;
            min-width: {int(100 * self.ui_scale)}px;
            min-height: {int(50 * self.ui_scale)}px;
        }}
        QPushButton:hover {{
            background-color: #e0e0e0;
        }}
        """)
        self.result_label.setStyleSheet(f"font-size: {int(60 * self.text_scale)}px;")

    def apply_ui_scaling(self, scale):
        self.ui_scale = scale
        for row in self.keyboard_buttons:
            for btn in row:
                btn.setStyleSheet(f"""
                    QPushButton {{
                        background-color: #ffffff;
                        border: 1px solid #ddd;
                        border-radius: 6px;
                        padding: 8px;
                        font-size: {int(60 * self.text_scale)}px;
                        color: black;
                        min-width: {int(60 * self.ui_scale)}px;
                        min-height: {int(60 * self.ui_scale)}px;
                    }}
                    QPushButton:hover {{
                        background-color: #f5f5f5;
                    }}
                """)
        self.submit_btn.setStyleSheet(f"""
        QPushButton {{
            background-color: #f0f0f0;
            border: 1px solid #ccc;
            border-radius: 6px;
            padding: 8px 16px;
            font-size: {int(60 * self.text_scale)}px;
            color: black;
            min-width: {int(100 * self.ui_scale)}px;
            min-height: {int(50 * self.ui_scale)}px;
        }}
        QPushButton:hover {{
            background-color: #e0e0e0;
        }}
        """)
        self.next_btn.setStyleSheet(f"""
        QPushButton {{
            background-color: #f0f0f0;
            border: 1px solid #ccc;
            border-radius: 6px;
            padding: 8px 16px;
            font-size: {int(60 * self.text_scale)}px;
            color: black;
            min-width: {int(100 * self.ui_scale)}px;
            min-height: {int(50 * self.ui_scale)}px;
        }}
        QPushButton:hover {{
            background-color: #e0e0e0;
        }}
        """)

class Task9(BaseTask):
    def __init__(self, text_scale=1.0, ui_scale=1.0):
        super().__init__(text_scale, ui_scale)

        # Создаем ScrollArea
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setStyleSheet("border: none;")
        # Виджет внутри ScrollArea
        self.scroll_content = QWidget()
        self.scroll_layout = QVBoxLayout(self.scroll_content)
        self.scroll_layout.setAlignment(Qt.AlignTop)

        # Метка с длинным текстом задачи
        self.label = QLabel("Нажмите 'Новый пример', чтобы начать.")
        self.label.setAlignment(Qt.AlignCenter)
        self.label.setWordWrap(True)  # Разрешить перенос строк
        font = QFont()
        font.setPointSize(int(60 * self.text_scale))
        self.label.setFont(font)

        # Добавляем метку в scroll_layout
        self.scroll_layout.addWidget(self.label)

        # Поле ввода ответа
        self.input_field = QLineEdit()
        self.input_field.setAlignment(Qt.AlignCenter)

        # Стиль поля ввода
        line_edit_style = f"""
            QLineEdit {{
                background-color: white;
                border: 2px solid #ccc;
                border-radius: 8px;
                padding: 8px;
                font-size: {int(60 * self.text_scale)}px;
                color: black;
            }}
            QLineEdit:focus {{
                border: 2px solid #007acc;
            }}
        """
        self.input_field.setStyleSheet(line_edit_style)
        self.scroll_layout.addWidget(self.input_field)

        # Виртуальная клавиатура
        self.keyboard_layout = QGridLayout() # Сделаем его атрибутом класса
        self.keyboard_buttons = [] # Список кнопок клавиатуры
        self.setup_virtual_keyboard()

        # Результат
        self.result_label = QLabel("")
        self.result_label.setAlignment(Qt.AlignCenter)
        self.result_label.setStyleSheet(f"font-size: {int(60 * self.text_scale)}px;")
        self.result_label.hide()
        self.scroll_layout.addWidget(self.result_label)

        # Кнопки
        self.submit_btn = QPushButton("Проверить")
        self.next_btn = QPushButton("Продолжить")
        self.next_btn.setVisible(False)

        button_style = f"""
            QPushButton {{
                background-color: #f0f0f0;
                border: 1px solid #ccc;
                border-radius: 6px;
                padding: 8px 16px;
                font-size: {int(60 * self.text_scale)}px;
                color: black;
                min-width: {int(100 * self.ui_scale)}px;
                min-height: {int(50 * self.ui_scale)}px;
            }}
            QPushButton:hover {{
                background-color: #e0e0e0;
            }}
            QPushButton:pressed {{
                background-color: #d0d0d0;
            }}
            QPushButton:disabled {{
                background-color: #cccccc;
                color: #888888;
            }}
        """
        self.submit_btn.setStyleSheet(button_style)
        self.next_btn.setStyleSheet(button_style)
        self.scroll_layout.addWidget(self.submit_btn)
        self.scroll_layout.addWidget(self.next_btn)

        # Устанавливаем контент в scroll area
        self.scroll_area.setWidget(self.scroll_content)
        # Добавляем scroll area в основной layout (от BaseTask)
        self.layout.addWidget(self.scroll_area)

        self.submit_btn.clicked.connect(self.check_answer)
        self.next_btn.clicked.connect(self.reset_task)

    def setup_virtual_keyboard(self):
        buttons = [
            ['1', '2', '3'],
            ['4', '5', '6'],
            ['7', '8', '9'],
            ['0', '-', ',']
        ]
        for i, row in enumerate(buttons):
            button_row = []
            for j, char in enumerate(row):
                btn = QPushButton(char)
                btn.clicked.connect(lambda _, s=char: self.append_to_input(s))
                btn.setStyleSheet(f"""
                    QPushButton {{
                        background-color: #ffffff;
                        border: 1px solid #ddd;
                        border-radius: 6px;
                        padding: 8px;
                        font-size: {int(60 * self.text_scale)}px;
                        color: black;
                        min-width: {int(60 * self.ui_scale)}px;
                        min-height: {int(60 * self.ui_scale)}px;
                    }}
                    QPushButton:hover {{
                        background-color: #f5f5f5;
                    }}
                """)
                self.keyboard_layout.addWidget(btn, i, j)
                button_row.append(btn)
            self.keyboard_buttons.append(button_row)
        self.scroll_layout.addLayout(self.keyboard_layout) # Добавляем лэйаут клавиатуры в scroll_layout

    def append_to_input(self, char):
        current_text = self.input_field.text()
        self.input_field.setText(current_text + char)

    def generate_task(self):
        # Предварительно сгенерировать все валидные комбинации
        valid_combinations = []

        for a in range(20, 31):
            for b in range(2, 10):
                for v in range(20, 31):
                    if (a * v) % 100 != 0:
                        continue
                    class_a = a
                    class_b = a - b
                    class_c = a - (a * v // 100)
                    total = class_a + class_b + class_c

                    if 50 <= total <= 90:
                        valid_combinations.append((a, b, v, total))

        if not valid_combinations:
            # Если нет валидных комбинаций, бросить исключение
            raise RuntimeError("No valid combinations found for Task9 parameters.")

        # Выбираем случайную комбинацию
        a, b, v, total = random.choice(valid_combinations)

        self.a, self.b, self.v, self.total = a, b, v, total

        # Формируем текст задачи
        task_text = (
            f"В 6 \"А\" классе учится {a} человек, что на {b} человека больше, "
            f"чем в 6 \"В\" классе. А в 6 \"Б\" классе учеников на {v}% меньше, "
            f"чем в 6 \"А\". Сколько всего учеников в этих трёх классах?"
        )

        self.label.setText(task_text)
        self.input_field.clear()
        self.result_label.clear()
        self.result_label.hide()
        self.next_btn.setVisible(False)

    def check_answer(self):
        try:
            user_input = int(self.input_field.text().strip())
            if user_input == self.total:
                self.result_label.setText("Правильно!")
                self.result_label.setStyleSheet(f"color: green; font-size:{int(60 * self.text_scale)}px;")
            else:
                self.result_label.setText(f"Неправильно. Правильный ответ: {self.total}")
                self.result_label.setStyleSheet(f"color: red; font-size: {int(60 * self.text_scale)}px;")
        except ValueError:
            self.result_label.setText("Введите целое число.")
            self.result_label.setStyleSheet(f"color: orange; font-size: {int(60 * self.text_scale)}px;")

        self.result_label.show()
        self.submit_btn.setEnabled(False)
        self.next_btn.setVisible(True)

    def reset_task(self):
        self.submit_btn.setEnabled(True)
        self.next_btn.setVisible(False)
        self.result_label.clear()
        self.result_label.hide()
        self.input_field.clear()
        self.generate_task()

    def apply_text_scaling(self, scale):
        self.text_scale = scale
        font = QFont()
        font.setPointSize(int(60 * self.text_scale))
        self.label.setFont(font)
        line_edit_style = f"""
            QLineEdit {{
                background-color: white;
                border: 2px solid #ccc;
                border-radius: 8px;
                padding: 8px;
                font-size: {int(60 * self.text_scale)}px;
                color: black;
            }}
            QLineEdit:focus {{
                border: 2px solid #007acc;
            }}
        """
        self.input_field.setStyleSheet(line_edit_style)
        for row in self.keyboard_buttons:
            for btn in row:
                btn.setStyleSheet(f"""
                    QPushButton {{
                        background-color: #ffffff;
                        border: 1px solid #ddd;
                        border-radius: 6px;
                        padding: 8px;
                        font-size: {int(60 * self.text_scale)}px;
                        color: black;
                        min-width: {int(60 * self.ui_scale)}px;
                        min-height: {int(60 * self.ui_scale)}px;
                    }}
                    QPushButton:hover {{
                        background-color: #f5f5f5;
                    }}
                """)
        self.submit_btn.setFont(QFont("Arial", int(60 * self.text_scale)))
        self.submit_btn.setStyleSheet(f"""
        QPushButton {{
            background-color: #f0f0f0;
            border: 1px solid #ccc;
            border-radius: 6px;
            padding: 8px 16px;
            font-size: {int(60 * self.text_scale)}px;
            color: black;
            min-width: {int(100 * self.ui_scale)}px;
            min-height: {int(50 * self.ui_scale)}px;
        }}
        QPushButton:hover {{
            background-color: #e0e0e0;
        }}
        """)
        self.next_btn.setFont(QFont("Arial", int(60 * self.text_scale)))
        self.next_btn.setStyleSheet(f"""
        QPushButton {{
            background-color: #f0f0f0;
            border: 1px solid #ccc;
            border-radius: 6px;
            padding: 8px 16px;
            font-size: {int(60 * self.text_scale)}px;
            color: black;
            min-width: {int(100 * self.ui_scale)}px;
            min-height: {int(50 * self.ui_scale)}px;
        }}
        QPushButton:hover {{
            background-color: #e0e0e0;
        }}
        """)
        self.result_label.setStyleSheet(f"font-size: {int(60 * self.text_scale)}px;")

    def apply_ui_scaling(self, scale):
        self.ui_scale = scale
        for row in self.keyboard_buttons:
            for btn in row:
                btn.setStyleSheet(f"""
                    QPushButton {{
                        background-color: #ffffff;
                        border: 1px solid #ddd;
                        border-radius: 6px;
                        padding: 8px;
                        font-size: {int(60 * self.text_scale)}px;
                        color: black;
                        min-width: {int(60 * self.ui_scale)}px;
                        min-height: {int(60 * self.ui_scale)}px;
                    }}
                    QPushButton:hover {{
                        background-color: #f5f5f5;
                    }}
                """)
        self.submit_btn.setStyleSheet(f"""
        QPushButton {{
            background-color: #f0f0f0;
            border: 1px solid #ccc;
            border-radius: 6px;
            padding: 8px 16px;
            font-size: {int(60 * self.text_scale)}px;
            color: black;
            min-width: {int(100 * self.ui_scale)}px;
            min-height: {int(50 * self.ui_scale)}px;
        }}
        QPushButton:hover {{
            background-color: #e0e0e0;
        }}
        """)
        self.next_btn.setStyleSheet(f"""
        QPushButton {{
            background-color: #f0f0f0;
            border: 1px solid #ccc;
            border-radius: 6px;
            padding: 8px 16px;
            font-size: {int(60 * self.text_scale)}px;
            color: black;
            min-width: {int(100 * self.ui_scale)}px;
            min-height: {int(50 * self.ui_scale)}px;
        }}
        QPushButton:hover {{
            background-color: #e0e0e0;
        }}
        """)

class Task10(BaseTask):
    def __init__(self, text_scale=1.0, ui_scale=1.0):
        super().__init__(text_scale, ui_scale)

        # Создаем ScrollArea
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setStyleSheet("border: none;")
        # Виджет внутри ScrollArea
        self.scroll_content = QWidget()
        self.scroll_layout = QVBoxLayout(self.scroll_content)
        self.scroll_layout.setAlignment(Qt.AlignTop)

        # Метка с длинным текстом задачи
        self.label = QLabel("Нажмите 'Новый пример', чтобы начать.")
        self.label.setAlignment(Qt.AlignCenter)
        self.label.setWordWrap(True)  # Разрешить перенос строк
        font = QFont()
        font.setPointSize(int(60 * self.text_scale))
        self.label.setFont(font)

        # Добавляем метку в scroll_layout
        self.scroll_layout.addWidget(self.label)

        # Поле ввода ответа
        self.input_field = QLineEdit()
        self.input_field.setAlignment(Qt.AlignCenter)

        # Стиль поля ввода
        line_edit_style = f"""
            QLineEdit {{
                background-color: white;
                border: 2px solid #ccc;
                border-radius: 8px;
                padding: 8px;
                font-size: {int(60 * self.text_scale)}px;
                color: black;
            }}
            QLineEdit:focus {{
                border: 2px solid #007acc;
            }}
        """
        self.input_field.setStyleSheet(line_edit_style)
        self.scroll_layout.addWidget(self.input_field)

        # Виртуальная клавиатура
        self.keyboard_layout = QGridLayout() # Сделаем его атрибутом класса
        self.keyboard_buttons = [] # Список кнопок клавиатуры
        self.setup_virtual_keyboard()

        # Результат
        self.result_label = QLabel("")
        self.result_label.setAlignment(Qt.AlignCenter)
        self.result_label.setStyleSheet(f"font-size: {int(60 * self.text_scale)}px;")
        self.result_label.hide()
        self.scroll_layout.addWidget(self.result_label)

        # Кнопки
        self.submit_btn = QPushButton("Проверить")
        self.next_btn = QPushButton("Продолжить")
        self.next_btn.setVisible(False)

        button_style = f"""
            QPushButton {{
                background-color: #f0f0f0;
                border: 1px solid #ccc;
                border-radius: 6px;
                padding: 8px 16px;
                font-size: {int(60 * self.text_scale)}px;
                color: black;
                min-width: {int(100 * self.ui_scale)}px;
                min-height: {int(50 * self.ui_scale)}px;
            }}
            QPushButton:hover {{
                background-color: #e0e0e0;
            }}
            QPushButton:pressed {{
                background-color: #d0d0d0;
            }}
            QPushButton:disabled {{
                background-color: #cccccc;
                color: #888888;
            }}
        """
        self.submit_btn.setStyleSheet(button_style)
        self.next_btn.setStyleSheet(button_style)
        self.scroll_layout.addWidget(self.submit_btn)
        self.scroll_layout.addWidget(self.next_btn)

        # Устанавливаем контент в scroll area
        self.scroll_area.setWidget(self.scroll_content)
        # Добавляем scroll area в основной layout (от BaseTask)
        self.layout.addWidget(self.scroll_area)

        self.submit_btn.clicked.connect(self.check_answer)
        self.next_btn.clicked.connect(self.reset_task)

    def setup_virtual_keyboard(self):
        buttons = [
            ['1', '2', '3'],
            ['4', '5', '6'],
            ['7', '8', '9'],
            ['0', '-', ',']
        ]
        for i, row in enumerate(buttons):
            button_row = []
            for j, char in enumerate(row):
                btn = QPushButton(char)
                btn.clicked.connect(lambda _, s=char: self.append_to_input(s))
                btn.setStyleSheet(f"""
                    QPushButton {{
                        background-color: #ffffff;
                        border: 1px solid #ddd;
                        border-radius: 6px;
                        padding: 8px;
                        font-size: {int(60 * self.text_scale)}px;
                        color: black;
                        min-width: {int(60 * self.ui_scale)}px;
                        min-height: {int(60 * self.ui_scale)}px;
                    }}
                    QPushButton:hover {{
                        background-color: #f5f5f5;
                    }}
                """)
                self.keyboard_layout.addWidget(btn, i, j)
                button_row.append(btn)
            self.keyboard_buttons.append(button_row)
        self.scroll_layout.addLayout(self.keyboard_layout) # Добавляем лэйаут клавиатуры в scroll_layout

    def append_to_input(self, char):
        current_text = self.input_field.text()
        self.input_field.setText(current_text + char)

    def generate_task(self):
        # Генерируем A и B
        a = random.randint(2, 6)
        b = random.randint(1, 9) * 10  # Кратное 10: 10, 20, ..., 90

        # Уравнение: (A * d) * 10 - d * 10 = B
        # => (A - 1) * d * 10 = B
        # => d = B / ((A - 1) * 10)

        denominator = (a - 1) * 10
        if b % denominator != 0:
            # Перегенерируем B, пока не найдём подходящее
            while b % denominator != 0:
                b = random.randint(1, 9) * 10

        d = b // denominator
        x = d * 10

        # Проверим, что x — двузначное и оканчивается на 0
        assert 10 <= x <= 90 and x % 10 == 0

        self.a, self.b, self.x = a, b, x

        # Формируем текст задачи
        task_text = (
            f"Задумали двузначное число, которое кратно 10. "
            f"Если цифру десятков увеличить в {a} раза, "
            f"то число увеличится на {b}. Какое число было задумано?"
        )

        self.label.setText(task_text)
        self.input_field.clear()
        self.result_label.clear()
        self.result_label.hide()
        self.next_btn.setVisible(False)

    def check_answer(self):
        try:
            user_input = int(self.input_field.text().strip())
            if user_input == self.x:
                self.result_label.setText("Правильно!")
                self.result_label.setStyleSheet(f"color: green; font-size:{int(60 * self.text_scale)}px;")
            else:
                self.result_label.setText(f"Неправильно. Правильный ответ: {self.x}")
                self.result_label.setStyleSheet(f"color: red; font-size: {int(60 * self.text_scale)}px;")
        except ValueError:
            self.result_label.setText("Введите целое число.")
            self.result_label.setStyleSheet(f"color: orange; font-size: {int(60 * self.text_scale)}px;")

        self.result_label.show()
        self.submit_btn.setEnabled(False)
        self.next_btn.setVisible(True)

    def reset_task(self):
        self.submit_btn.setEnabled(True)
        self.next_btn.setVisible(False)
        self.result_label.clear()
        self.result_label.hide()
        self.input_field.clear()
        self.generate_task()

    def apply_text_scaling(self, scale):
        self.text_scale = scale
        font = QFont()
        font.setPointSize(int(60 * self.text_scale))
        self.label.setFont(font)
        line_edit_style = f"""
            QLineEdit {{
                background-color: white;
                border: 2px solid #ccc;
                border-radius: 8px;
                padding: 8px;
                font-size: {int(60 * self.text_scale)}px;
                color: black;
            }}
            QLineEdit:focus {{
                border: 2px solid #007acc;
            }}
        """
        self.input_field.setStyleSheet(line_edit_style)
        for row in self.keyboard_buttons:
            for btn in row:
                btn.setStyleSheet(f"""
                    QPushButton {{
                        background-color: #ffffff;
                        border: 1px solid #ddd;
                        border-radius: 6px;
                        padding: 8px;
                        font-size: {int(60 * self.text_scale)}px;
                        color: black;
                        min-width: {int(60 * self.ui_scale)}px;
                        min-height: {int(60 * self.ui_scale)}px;
                    }}
                    QPushButton:hover {{
                        background-color: #f5f5f5;
                    }}
                """)
        self.submit_btn.setFont(QFont("Arial", int(60 * self.text_scale)))
        self.submit_btn.setStyleSheet(f"""
        QPushButton {{
            background-color: #f0f0f0;
            border: 1px solid #ccc;
            border-radius: 6px;
            padding: 8px 16px;
            font-size: {int(60 * self.text_scale)}px;
            color: black;
            min-width: {int(100 * self.ui_scale)}px;
            min-height: {int(50 * self.ui_scale)}px;
        }}
        QPushButton:hover {{
            background-color: #e0e0e0;
        }}
        """)
        self.next_btn.setFont(QFont("Arial", int(60 * self.text_scale)))
        self.next_btn.setStyleSheet(f"""
        QPushButton {{
            background-color: #f0f0f0;
            border: 1px solid #ccc;
            border-radius: 6px;
            padding: 8px 16px;
            font-size: {int(60 * self.text_scale)}px;
            color: black;
            min-width: {int(100 * self.ui_scale)}px;
            min-height: {int(50 * self.ui_scale)}px;
        }}
        QPushButton:hover {{
            background-color: #e0e0e0;
        }}
        """)
        self.result_label.setStyleSheet(f"font-size: {int(60 * self.text_scale)}px;")

    def apply_ui_scaling(self, scale):
        self.ui_scale = scale
        for row in self.keyboard_buttons:
            for btn in row:
                btn.setStyleSheet(f"""
                    QPushButton {{
                        background-color: #ffffff;
                        border: 1px solid #ddd;
                        border-radius: 6px;
                        padding: 8px;
                        font-size: {int(60 * self.text_scale)}px;
                        color: black;
                        min-width: {int(60 * self.ui_scale)}px;
                        min-height: {int(60 * self.ui_scale)}px;
                    }}
                    QPushButton:hover {{
                        background-color: #f5f5f5;
                    }}
                """)
        self.submit_btn.setStyleSheet(f"""
        QPushButton {{
            background-color: #f0f0f0;
            border: 1px solid #ccc;
            border-radius: 6px;
            padding: 8px 16px;
            font-size: {int(60 * self.text_scale)}px;
            color: black;
            min-width: {int(100 * self.ui_scale)}px;
            min-height: {int(50 * self.ui_scale)}px;
        }}
        QPushButton:hover {{
            background-color: #e0e0e0;
        }}
        """)
        self.next_btn.setStyleSheet(f"""
        QPushButton {{
            background-color: #f0f0f0;
            border: 1px solid #ccc;
            border-radius: 6px;
            padding: 8px 16px;
            font-size: {int(60 * self.text_scale)}px;
            color: black;
            min-width: {int(100 * self.ui_scale)}px;
            min-height: {int(50 * self.ui_scale)}px;
        }}
        QPushButton:hover {{
            background-color: #e0e0e0;
        }}
        """)


class MathTrainer(QMainWindow):
    def __init__(self):
        super().__init__()
        self.settings = QSettings("MathTrainer", "Settings")
        # Загружаем сохраненные значения или используем по умолчанию
        self.text_scale = self.settings.value("text_scale", 1.0, type=float)
        self.ui_scale = self.settings.value("ui_scale", 1.0, type=float)

        self.setWindowTitle("Математический тренажёр 6 класс")
        self.setGeometry(200, 200, 600, 500)

        # Установка светлой темы для всего приложения
        self.setStyleSheet("""
        QMainWindow {
            background-color: #ffffff;
        }
        QWidget {
            background-color: #ffffff;
            color: black;
            font-family: Arial, sans-serif;
        }
        QLabel {
            color: black;
        }
        QPushButton {
            background-color: #f0f0f0;
            border: 1px solid #ccc;
            border-radius: 6px;
            padding: 8px 16px;
            color: black;
        }
        QPushButton:hover {
            background-color: #e0e0e0;
        }
        QPushButton:pressed {
            background-color: #d0d0d0;
        }
        QPushButton:disabled {
            background-color: #cccccc;
            color: #888888;
        }
        """)

        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        layout = QVBoxLayout()

        # Панель с кнопками заданий и кнопкой настроек
        top_bar = QHBoxLayout()
        top_bar.setAlignment(Qt.AlignCenter)

        # Кнопка настроек
        self.settings_btn = QPushButton("Настройки")
        self.settings_btn.clicked.connect(self.open_settings)
        # Применяем масштабирование к кнопке настроек
        settings_btn_style = f"""
        QPushButton {{
            background-color: #f0f0f0;
            border: 1px solid #ccc;
            border-radius: 6px;
            padding: 8px 16px;
            font-size: {int(60 * self.text_scale)}px; /* Шрифт */
            color: black;
            min-width: {int(100 * self.ui_scale)}px; /* Размер */
            min-height: {int(50 * self.ui_scale)}px; /* Размер */
        }}
        QPushButton:hover {{
            background-color: #e0e0e0;
        }}
        """
        self.settings_btn.setStyleSheet(settings_btn_style)
        top_bar.addWidget(self.settings_btn)

        # Кнопки выбора задания
        self.task_buttons = []
        for i in range(1, 11):
            btn = QPushButton(str(i))
            btn.setCheckable(True)
            btn.clicked.connect(lambda checked, n=i: self.select_task(n))
            # Применяем масштабирование к кнопке задания
            task_btn_style = f"""
            QPushButton {{
                background-color: #ffffff;
                border: 1px solid #ccc;
                border-radius: 6px;
                padding: 6px 22px;
                font-size: {int(60 * self.text_scale)}px; /* Шрифт */
                color: black;
                min-width: {int(50 * self.ui_scale)}px; /* Размер */
                min-height: {int(40 * self.ui_scale)}px; /* Размер */
            }}
            QPushButton:checked {{
                background-color: #007acc;
                color: white;
                border: 1px solid #005fa3;
            }}
            """
            btn.setStyleSheet(task_btn_style)
            top_bar.addWidget(btn)
            self.task_buttons.append(btn)

        layout.addLayout(top_bar)

        # Контент для заданий
        self.content_area = QVBoxLayout()
        self.content_area.setAlignment(Qt.AlignCenter)
        layout.addLayout(self.content_area)

        main_widget.setLayout(layout)

        # Создаём экземпляры заданий с начальным масштабом
        self.tasks = [None] * 10
        self.tasks[0] = Task1(text_scale=self.text_scale, ui_scale=self.ui_scale)
        self.tasks[1] = Task2(text_scale=self.text_scale, ui_scale=self.ui_scale)
        self.tasks[2] = Task3(text_scale=self.text_scale, ui_scale=self.ui_scale)
        self.tasks[3] = Task4(text_scale=self.text_scale, ui_scale=self.ui_scale)
        self.tasks[4] = Task5(text_scale=self.text_scale, ui_scale=self.ui_scale)
        self.tasks[5] = Task6(text_scale=self.text_scale, ui_scale=self.ui_scale)
        self.tasks[6] = Task7(text_scale=self.text_scale, ui_scale=self.ui_scale)
        self.tasks[7] = Task8(text_scale=self.text_scale, ui_scale=self.ui_scale)
        self.tasks[8] = Task9(text_scale=self.text_scale, ui_scale=self.ui_scale)
        self.tasks[9] = Task10(text_scale=self.text_scale, ui_scale=self.ui_scale)

        self.current_task_widget = None
        self.select_task(1)

    def open_settings(self):
        dialog = SettingsDialog(self, self.text_scale, self.ui_scale)
        if dialog.exec_() == QDialog.Accepted:
            # Значения уже применены через сигналы при изменении ползунков
            # Но мы можем получить их снова для сохранения
            new_text_scale, new_ui_scale = dialog.get_values()
            self.text_scale = new_text_scale
            self.ui_scale = new_ui_scale
            # Сохраняем в настройки
            self.settings.setValue("text_scale", self.text_scale)
            self.settings.setValue("ui_scale", self.ui_scale)
            # Обновляем кнопки на панели
            self.apply_text_scaling(self.text_scale)
            self.apply_ui_scaling(self.ui_scale)


    def apply_text_scaling(self, scale):
        self.text_scale = scale
        # Обновить стиль кнопки настроек
        settings_btn_style = f"""
        QPushButton {{
            background-color: #f0f0f0;
            border: 1px solid #ccc;
            border-radius: 6px;
            padding: 8px 16px;
            font-size: {int(60 * self.text_scale)}px;
            color: black;
            min-width: {int(100 * self.ui_scale)}px;
            min-height: {int(50 * self.ui_scale)}px;
        }}
        QPushButton:hover {{
            background-color: #e0e0e0;
        }}
        """
        self.settings_btn.setStyleSheet(settings_btn_style)

        # Обновить стиль кнопок заданий
        for btn in self.task_buttons:
            task_btn_style = f"""
            QPushButton {{
                background-color: #ffffff;
                border: 1px solid #ccc;
                border-radius: 6px;
                padding: 6px 22px;
                font-size: {int(60 * self.text_scale)}px;
                color: black;
                min-width: {int(50 * self.ui_scale)}px;
                min-height: {int(40 * self.ui_scale)}px;
            }}
            QPushButton:checked {{
                background-color: #007acc;
                color: white;
                border: 1px solid #005fa3;
            }}
            """
            btn.setStyleSheet(task_btn_style)

        # Обновить текущее задание
        if self.current_task_widget:
            self.current_task_widget.apply_text_scaling(scale)

    def apply_ui_scaling(self, scale):
        self.ui_scale = scale
        # Обновить стиль кнопки настроек
        settings_btn_style = f"""
        QPushButton {{
            background-color: #f0f0f0;
            border: 1px solid #ccc;
            border-radius: 6px;
            padding: 8px 16px;
            font-size: {int(60 * self.text_scale)}px;
            color: black;
            min-width: {int(100 * self.ui_scale)}px;
            min-height: {int(50 * self.ui_scale)}px;
        }}
        QPushButton:hover {{
            background-color: #e0e0e0;
        }}
        """
        self.settings_btn.setStyleSheet(settings_btn_style)

        # Обновить стиль кнопок заданий
        for btn in self.task_buttons:
            task_btn_style = f"""
            QPushButton {{
                background-color: #ffffff;
                border: 1px solid #ccc;
                border-radius: 6px;
                padding: 6px 22px;
                font-size: {int(60 * self.text_scale)}px;
                color: black;
                min-width: {int(50 * self.ui_scale)}px;
                min-height: {int(40 * self.ui_scale)}px;
            }}
            QPushButton:checked {{
                background-color: #007acc;
                color: white;
                border: 1px solid #005fa3;
            }}
            """
            btn.setStyleSheet(task_btn_style)

        # Обновить текущее задание
        if self.current_task_widget:
            self.current_task_widget.apply_ui_scaling(scale)

    def select_task(self, index):
        # Сбросить предыдущее состояние
        if self.current_task_widget:
            # Сбросить состояние текущего задания перед удалением
            self.current_task_widget.reset_task()
            self.content_area.removeWidget(self.current_task_widget)
            self.current_task_widget.setParent(None)

        # Выбрать новое задание
        task_idx = index - 1
        if 0 <= task_idx < len(self.tasks) and self.tasks[task_idx]:
            self.current_task_widget = self.tasks[task_idx]
            # Применить масштабирование при переключении
            self.current_task_widget.apply_text_scaling(self.text_scale)
            self.current_task_widget.apply_ui_scaling(self.ui_scale)
            self.current_task_widget.generate_task()  # Новый пример при выборке
            self.content_area.addWidget(self.current_task_widget)

            # Обновить активную кнопку
            for btn in self.task_buttons:
                btn.setChecked(False)
            self.task_buttons[index - 1].setChecked(True)


def main():
    app = QApplication(sys.argv)
    # Дополнительно: принудительно установить светлую палитру
    palette = QPalette()
    palette.setColor(QPalette.Window, QColor(255, 255, 255))
    palette.setColor(QPalette.WindowText, QColor(0, 0, 0))
    palette.setColor(QPalette.Base, QColor(255, 255, 255))
    palette.setColor(QPalette.AlternateBase, QColor(240, 240, 240))
    palette.setColor(QPalette.Text, QColor(0, 0, 0))
    palette.setColor(QPalette.Button, QColor(240, 240, 240))
    palette.setColor(QPalette.ButtonText, QColor(0, 0, 0))
    palette.setColor(QPalette.Highlight, QColor(0, 120, 215))
    palette.setColor(QPalette.HighlightedText, QColor(255, 255, 255))
    app.setPalette(palette)

    window = MathTrainer()
    window.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
