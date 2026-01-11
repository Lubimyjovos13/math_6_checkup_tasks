import sys
import random
import math
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QVBoxLayout, QHBoxLayout, QWidget,
    QPushButton, QLabel, QLineEdit, QGridLayout, QFrame
)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont, QPalette, QColor
from fractions import Fraction 


# Абстрактный базовый класс для задания
class BaseTask(QWidget):
    def __init__(self):
        super().__init__()
        self.layout = QVBoxLayout()
        self.setLayout(self.layout)

    def generate_task(self):
        raise NotImplementedError

    def check_answer(self):
        raise NotImplementedError

    def reset_task(self):
        raise NotImplementedError


# Задание №1: A * (B - C), где B < C => результат всегда отрицательный
class Task1(BaseTask):
    def __init__(self):
        super().__init__()

        # Центральный виджет для контента
        self.central_frame = QFrame()
        central_layout = QVBoxLayout()
        central_layout.setAlignment(Qt.AlignCenter)

        self.label = QLabel("Нажмите 'Новый пример', чтобы начать.")
        self.label.setAlignment(Qt.AlignCenter)
        font = QFont()
        font.setPointSize(16)
        self.label.setFont(font)

        self.input_field = QLineEdit()
        self.input_field.setAlignment(Qt.AlignCenter)
        self.input_field.setStyleSheet("""
            QLineEdit {
                background-color: white;
                border: 2px solid #ccc;
                border-radius: 8px;
                padding: 8px;
                font-size: 16px;
                color: black;
            }
            QLineEdit:focus {
                border: 2px solid #007acc;
            }
        """)

        self.result_label = QLabel("")
        self.result_label.setAlignment(Qt.AlignCenter)
        self.result_label.setStyleSheet("font-size: 16px;")
        self.result_label.hide()

        self.submit_btn = QPushButton("Проверить")
        self.next_btn = QPushButton("Продолжить")
        self.next_btn.setVisible(False)

        # Стиль кнопок
        button_style = """
            QPushButton {
                background-color: #f0f0f0;
                border: 1px solid #ccc;
                border-radius: 6px;
                padding: 8px 16px;
                font-size: 14px;
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
        """
        self.submit_btn.setStyleSheet(button_style)
        self.next_btn.setStyleSheet(button_style)

        self.a = 0
        self.b = 0
        self.c = 0
        self.correct_answer = 0

        central_layout.addWidget(self.label)
        central_layout.addSpacing(20) 
        central_layout.addWidget(self.input_field)
        self.setup_virtual_keyboard(central_layout)
        central_layout.addWidget(self.submit_btn)
        central_layout.addWidget(self.result_label)
        central_layout.addWidget(self.next_btn)

        self.central_frame.setLayout(central_layout)
        self.layout.addWidget(self.central_frame)

        self.submit_btn.clicked.connect(self.check_answer)
        self.next_btn.clicked.connect(self.reset_task)

    def setup_virtual_keyboard(self, parent_layout):
        keyboard_layout = QGridLayout()

        buttons = [
            ['1', '2', '3'],
            ['4', '5', '6'],
            ['7', '8', '9'],
            ['0', '-', ',']
        ]

        for i, row in enumerate(buttons):
            for j, char in enumerate(row):
                btn = QPushButton(char)
                btn.clicked.connect(lambda _, s=char: self.append_to_input(s))
                btn.setStyleSheet("""
                    QPushButton {
                        background-color: #ffffff;
                        border: 1px solid #ddd;
                        border-radius: 6px;
                        padding: 8px;
                        font-size: 16px;
                        color: black;
                    }
                    QPushButton:hover {
                        background-color: #f5f5f5;
                    }
                """)
                keyboard_layout.addWidget(btn, i, j)

        parent_layout.addLayout(keyboard_layout)

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
                self.result_label.setStyleSheet("color: green; font-size: 16px;")
            else:
                self.result_label.setText(f"Неправильно. Правильный ответ: {self.correct_answer}")
                self.result_label.setStyleSheet("color: red; font-size: 16px;")
        except ValueError:
            self.result_label.setText("Введите число.")
            self.result_label.setStyleSheet("color: orange; font-size: 16px;")

        self.result_label.show()
        self.submit_btn.setEnabled(False)
        self.next_btn.setVisible(True)

    def reset_task(self):
        self.generate_task()
        self.submit_btn.setEnabled(True)

class Task2(BaseTask):
    def __init__(self):
        super().__init__()

        # Центральный фрейм
        self.central_frame = QFrame()
        central_layout = QVBoxLayout()
        central_layout.setAlignment(Qt.AlignCenter)

        # Текст задания (с дробями)
        self.label = QLabel("Нажмите 'Новый пример', чтобы начать.")
        self.label.setAlignment(Qt.AlignCenter)
        font = QFont()
        font.setPointSize(16)
        self.label.setFont(font)

        # Поля для ответа (числитель и знаменатель)
        self.answer_num = QLineEdit()  # числитель
        self.answer_div_line = QLabel("___________")  # дробная черта
        self.answer_div_line.setAlignment(Qt.AlignCenter)
        self.answer_den = QLineEdit()  # знаменатель
        self.answer_num.setAlignment(Qt.AlignCenter)
        self.answer_den.setAlignment(Qt.AlignCenter)
        self.answer_num.setPlaceholderText("Числитель")
        self.answer_den.setPlaceholderText("Знаменатель")

        # Виртуальная клавиатура
        self.keyboard_layout = QGridLayout()
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
        input_style = """
            QLineEdit {
                background-color: white;
                border: 2px solid #ccc;
                border-radius: 8px;
                padding: 8px;
                font-size: 16px;
                color: black;
                min-width: 80px;
            }
        """
        self.answer_num.setStyleSheet(input_style)
        self.answer_den.setStyleSheet(input_style)

        button_style = """
            QPushButton {
                background-color: #f0f0f0;
                border: 1px solid #ccc;
                border-radius: 6px;
                padding: 8px 16px;
                font-size: 14px;
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
        """
        self.submit_btn.setStyleSheet(button_style)
        self.next_btn.setStyleSheet(button_style)

        # Собираем layout
        central_layout.addWidget(self.label)
        central_layout.addSpacing(20) 
        central_layout.addWidget(self.answer_num)
        central_layout.addWidget(self.answer_div_line)
        central_layout.addWidget(self.answer_den)
        central_layout.addLayout(self.keyboard_layout)
        central_layout.addWidget(self.submit_btn)
        central_layout.addWidget(self.result_label)
        central_layout.addWidget(self.next_btn)

        self.central_frame.setLayout(central_layout)
        self.layout.addWidget(self.central_frame)

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
            for j, char in enumerate(row):
                btn = QPushButton(char)
                btn.clicked.connect(lambda _, s=char: self.append_to_active_input(s))
                btn.setStyleSheet("""
                    QPushButton {
                        background-color: #ffffff;
                        border: 1px solid #ddd;
                        border-radius: 6px;
                        padding: 8px;
                        font-size: 16px;
                        color: black;
                    }
                    QPushButton:hover {
                        background-color: #f5f5f5;
                    }
                """)
                self.keyboard_layout.addWidget(btn, i, j)

    def append_to_active_input(self, char, field):
        current_text = field.text()
        field.setText(current_text + char)

    def append_to_active_input(self, char):
        # Проверяем, какое поле активно (фокус)
        if self.answer_num.hasFocus():
            self.append_to_active_input_impl(char, self.answer_num)
        elif self.answer_den.hasFocus():
            self.append_to_active_input_impl(char, self.answer_den)

    def append_to_active_input_impl(self, char, field):
        current_text = field.text()
        field.setText(current_text + char)

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
        <span style="font-size: 18px;">
        (<sup>{a}</sup>&frasl;<sub>{b}</sub> &minus; <sup>{c}</sup>&frasl;<sub>{d}</sub>) &divide; <sup>{e}</sup>&frasl;<sub>{f}</sub>
        </span>
        </div>
        """
        self.label.setText(task_html)

        # Очистка полей
        self.answer_num.clear()
        self.answer_den.clear()
        self.result_label.clear()
        self.result_label.hide()
        self.next_btn.setVisible(False)

    def check_answer(self):
        try:
            num = int(self.answer_num.text())
            den = int(self.answer_den.text())

            # Проверка знаменателя
            if den == 0:
                self.result_label.setText("Знаменатель не может быть 0.")
                self.result_label.setStyleSheet("color: orange; font-size: 16px;")
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
                self.result_label.setStyleSheet("color: green; font-size: 16px;")
            else:
                self.result_label.setText(
                    f"Неправильно. Правильный ответ: {correct_result.numerator}/{correct_result.denominator}"
                )
                self.result_label.setStyleSheet("color: red; font-size: 16px;")

        except ValueError:
            self.result_label.setText("Введите числа в оба поля.")
            self.result_label.setStyleSheet("color: orange; font-size: 16px;")

        self.result_label.show()
        self.submit_btn.setEnabled(False)
        self.next_btn.setVisible(True)

    def reset_task(self):
        self.generate_task()
        self.submit_btn.setEnabled(True)

class Task3(BaseTask):
    def __init__(self):
        super().__init__()
        self.label = QLabel("Нажмите 'Новый пример', чтобы начать.")
        self.label.setAlignment(Qt.AlignCenter)
        font = QFont()
        font.setPointSize(16)
        self.label.setFont(font)

        self.input_field = QLineEdit()
        self.input_field.setAlignment(Qt.AlignCenter)

        # Стиль поля ввода
        self.input_field.setStyleSheet("""
            QLineEdit {
                background-color: white;
                border: 2px solid #ccc;
                border-radius: 8px;
                padding: 8px;
                font-size: 16px;
                color: black;
            }
            QLineEdit:focus {
                border: 2px solid #007acc;
            }
        """)

        self.result_label = QLabel("")
        self.result_label.setAlignment(Qt.AlignCenter)
        self.result_label.setStyleSheet("font-size: 16px;")
        self.result_label.hide()

        self.submit_btn = QPushButton("Проверить")
        self.next_btn = QPushButton("Продолжить")
        self.next_btn.setVisible(False)

        # Стиль кнопок
        button_style = """
            QPushButton {
                background-color: #f0f0f0;
                border: 1px solid #ccc;
                border-radius: 6px;
                padding: 8px 16px;
                font-size: 14px;
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
        """
        self.submit_btn.setStyleSheet(button_style)
        self.next_btn.setStyleSheet(button_style)

        self.a = 0.0
        self.b = 0.0
        self.c = 0.0
        self.correct_answer = 0.0

        # Компоновка
        layout = self.layout
        layout.addWidget(self.label)
        layout.addSpacing(20) 
        layout.addWidget(self.input_field)
        self.setup_virtual_keyboard()
        layout.addWidget(self.submit_btn)
        layout.addWidget(self.result_label)
        layout.addWidget(self.next_btn)

        self.submit_btn.clicked.connect(self.check_answer)
        self.next_btn.clicked.connect(self.reset_task)

    def setup_virtual_keyboard(self):
        keyboard_layout = QGridLayout()

        buttons = [
            ['1', '2', '3'],
            ['4', '5', '6'],
            ['7', '8', '9'],
            ['0', '-', ',']
        ]

        for i, row in enumerate(buttons):
            for j, char in enumerate(row):
                btn = QPushButton(char)
                btn.clicked.connect(lambda _, s=char: self.append_to_input(s))
                btn.setStyleSheet("""
                    QPushButton {
                        background-color: #ffffff;
                        border: 1px solid #ddd;
                        border-radius: 6px;
                        padding: 8px;
                        font-size: 16px;
                        color: black;
                    }
                    QPushButton:hover {
                        background-color: #f5f5f5;
                    }
                """)
                keyboard_layout.addWidget(btn, i, j)

        self.layout.addLayout(keyboard_layout)

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

        task_str = f"{a} – {b} * ({c}) ="
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
                self.result_label.setStyleSheet("color: green; font-size: 16px;")
            else:
                self.result_label.setText(f"Неправильно. Правильный ответ: {round(self.correct_answer, 2)}")
                self.result_label.setStyleSheet("color: red; font-size: 16px;")
        except ValueError:
            self.result_label.setText("Введите число.")
            self.result_label.setStyleSheet("color: orange; font-size: 16px;")

        self.result_label.show()
        self.submit_btn.setEnabled(False)
        self.next_btn.setVisible(True)

    def reset_task(self):
        self.generate_task()
        self.submit_btn.setEnabled(True)

class Task4(BaseTask):
    def __init__(self):
        super().__init__()
        self.label = QLabel("Нажмите 'Новый пример', чтобы начать.")
        self.label.setAlignment(Qt.AlignCenter)
        font = QFont()
        font.setPointSize(16)
        self.label.setFont(font)

        self.input_field = QLineEdit()
        self.input_field.setAlignment(Qt.AlignCenter)

        # Стиль поля ввода
        self.input_field.setStyleSheet("""
            QLineEdit {
                background-color: white;
                border: 2px solid #ccc;
                border-radius: 8px;
                padding: 8px;
                font-size: 16px;
                color: black;
            }
            QLineEdit:focus {
                border: 2px solid #007acc;
            }
        """)

        self.result_label = QLabel("")
        self.result_label.setAlignment(Qt.AlignCenter)
        self.result_label.setStyleSheet("font-size: 16px;")
        self.result_label.hide()

        self.submit_btn = QPushButton("Проверить")
        self.next_btn = QPushButton("Продолжить")
        self.next_btn.setVisible(False)

        # Стиль кнопок
        button_style = """
            QPushButton {
                background-color: #f0f0f0;
                border: 1px solid #ccc;
                border-radius: 6px;
                padding: 8px 16px;
                font-size: 14px;
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
        """
        self.submit_btn.setStyleSheet(button_style)
        self.next_btn.setStyleSheet(button_style)

        self.a = 0
        self.b = 0
        self.c = 0
        self.correct_answer = 0

        # Компоновка
        layout = self.layout
        layout.addWidget(self.label)
        layout.addSpacing(20) 
        layout.addWidget(self.input_field)
        self.setup_virtual_keyboard()
        layout.addWidget(self.submit_btn)
        layout.addWidget(self.result_label)
        layout.addWidget(self.next_btn)

        self.submit_btn.clicked.connect(self.check_answer)
        self.next_btn.clicked.connect(self.reset_task)

    def setup_virtual_keyboard(self):
        keyboard_layout = QGridLayout()

        buttons = [
            ['1', '2', '3'],
            ['4', '5', '6'],
            ['7', '8', '9'],
            ['0', '-', ',']
        ]

        for i, row in enumerate(buttons):
            for j, char in enumerate(row):
                btn = QPushButton(char)
                btn.clicked.connect(lambda _, s=char: self.append_to_input(s))
                btn.setStyleSheet("""
                    QPushButton {
                        background-color: #ffffff;
                        border: 1px solid #ddd;
                        border-radius: 6px;
                        padding: 8px;
                        font-size: 16px;
                        color: black;
                    }
                    QPushButton:hover {
                        background-color: #f5f5f5;
                    }
                """)
                keyboard_layout.addWidget(btn, i, j)

        self.layout.addLayout(keyboard_layout)

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

        task_str = f"Найдите значение выражения {a} * |y + {b}| при y = {c}"
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
                self.result_label.setStyleSheet("color: green; font-size: 16px;")
            else:
                self.result_label.setText(f"Неправильно. Правильный ответ: {self.correct_answer}")
                self.result_label.setStyleSheet("color: red; font-size: 16px;")
        except ValueError:
            self.result_label.setText("Введите число.")
            self.result_label.setStyleSheet("color: orange; font-size: 16px;")

        self.result_label.show()
        self.submit_btn.setEnabled(False)
        self.next_btn.setVisible(True)

    def reset_task(self):
        self.generate_task()
        self.submit_btn.setEnabled(True)

class Task5(BaseTask):
    def __init__(self):
        super().__init__()
        self.label = QLabel("Нажмите 'Новый пример', чтобы начать.")
        self.label.setAlignment(Qt.AlignCenter)
        font = QFont()
        font.setPointSize(16)
        self.label.setFont(font)

        self.input_field = QLineEdit()
        self.input_field.setAlignment(Qt.AlignCenter)

        # Стиль поля ввода
        self.input_field.setStyleSheet("""
            QLineEdit {
                background-color: white;
                border: 2px solid #ccc;
                border-radius: 8px;
                padding: 8px;
                font-size: 16px;
                color: black;
            }
            QLineEdit:focus {
                border: 2px solid #007acc;
            }
        """)

        self.result_label = QLabel("")
        self.result_label.setAlignment(Qt.AlignCenter)
        self.result_label.setStyleSheet("font-size: 16px;")
        self.result_label.hide()

        self.submit_btn = QPushButton("Проверить")
        self.next_btn = QPushButton("Продолжить")
        self.next_btn.setVisible(False)

        # Стиль кнопок
        button_style = """
            QPushButton {
                background-color: #f0f0f0;
                border: 1px solid #ccc;
                border-radius: 6px;
                padding: 8px 16px;
                font-size: 14px;
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
        """
        self.submit_btn.setStyleSheet(button_style)
        self.next_btn.setStyleSheet(button_style)

        self.a = 0
        self.b = 0
        self.c = 0.0
        self.d = 0.0
        self.correct_answer = 0.0

        # Компоновка
        layout = self.layout
        layout.addWidget(self.label)
        layout.addSpacing(20) 
        layout.addWidget(self.input_field)
        self.setup_virtual_keyboard()
        layout.addWidget(self.submit_btn)
        layout.addWidget(self.result_label)
        layout.addWidget(self.next_btn)

        self.submit_btn.clicked.connect(self.check_answer)
        self.next_btn.clicked.connect(self.reset_task)

    def setup_virtual_keyboard(self):
        keyboard_layout = QGridLayout()

        buttons = [
            ['1', '2', '3'],
            ['4', '5', '6'],
            ['7', '8', '9'],
            ['0', '-', ',']
        ]

        for i, row in enumerate(buttons):
            for j, char in enumerate(row):
                btn = QPushButton(char)
                btn.clicked.connect(lambda _, s=char: self.append_to_input(s))
                btn.setStyleSheet("""
                    QPushButton {
                        background-color: #ffffff;
                        border: 1px solid #ddd;
                        border-radius: 6px;
                        padding: 8px;
                        font-size: 16px;
                        color: black;
                    }
                    QPushButton:hover {
                        background-color: #f5f5f5;
                    }
                """)
                keyboard_layout.addWidget(btn, i, j)

        self.layout.addLayout(keyboard_layout)

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
                self.result_label.setStyleSheet("color: green; font-size: 16px;")
            else:
                self.result_label.setText(f"Неправильно. Правильный ответ: {self.correct_answer:.1f}")
                self.result_label.setStyleSheet("color: red; font-size: 16px;")
        except ValueError:
            self.result_label.setText("Введите число.")
            self.result_label.setStyleSheet("color: orange; font-size: 16px;")

        self.result_label.show()
        self.submit_btn.setEnabled(False)
        self.next_btn.setVisible(True)

    def reset_task(self):
        self.generate_task()
        self.submit_btn.setEnabled(True)

class MathTrainer(QMainWindow):
    def __init__(self):
        super().__init__()
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
                font-size: 16px;
            }
            QPushButton {
                background-color: #f0f0f0;
                border: 1px solid #ccc;
                border-radius: 6px;
                padding: 8px 16px;
                font-size: 14px;
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

        # Панель с кнопками заданий
        top_bar = QHBoxLayout()
        top_bar.setAlignment(Qt.AlignCenter)
        self.task_buttons = []
        for i in range(1, 11):
            btn = QPushButton(str(i))
            btn.setCheckable(True)
            btn.clicked.connect(lambda checked, n=i: self.select_task(n))
            btn.setStyleSheet("""
                QPushButton {
                    background-color: #ffffff;
                    border: 1px solid #ccc;
                    border-radius: 6px;
                    padding: 6px 12px;
                    font-size: 14px;
                    color: black;
                }
                QPushButton:checked {
                    background-color: #007acc;
                    color: white;
                    border: 1px solid #005fa3;
                }
            """)
            top_bar.addWidget(btn)
            self.task_buttons.append(btn)

        layout.addLayout(top_bar)

        # Контент для заданий
        self.content_area = QVBoxLayout()
        self.content_area.setAlignment(Qt.AlignCenter)
        layout.addLayout(self.content_area)

        main_widget.setLayout(layout)

        # Создаём экземпляры заданий
        self.tasks = [None] * 10
        self.tasks[0] = Task1()
        self.tasks[1] = Task2() 
        self.tasks[2] = Task3() 
        self.tasks[3] = Task4() 
        self.tasks[4] = Task5() 

        self.current_task_widget = None
        self.select_task(1)

    def select_task(self, index):
        # Сбросить предыдущее состояние
        if self.current_task_widget:
            self.content_area.removeWidget(self.current_task_widget)
            self.current_task_widget.setParent(None)

        # Выбрать новое задание
        task_idx = index - 1
        if 0 <= task_idx < len(self.tasks) and self.tasks[task_idx]:
            self.current_task_widget = self.tasks[task_idx]
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