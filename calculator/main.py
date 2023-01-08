import sys
from typing import Union, Optional
from operator import add, sub, mul, truediv

from PySide6.QtWidgets import QApplication, QMainWindow
from PySide6.QtGui import QFontDatabase

from design import Ui_MainWindow

operations = {
    '+': add,
    '−': sub,
    '×': mul,
    '/': truediv
}

error_zero_div = 'Division by zero' #Ошибка при делении на ноль
error_undefined = 'Result is undefined' #Результат не определён

default_font_size = 16
default_entry_font_size = 40

#Стандартный код для запуска любого Qt приложения с файлом дизайна
class Calculator(QMainWindow):
    def __init__(self):
        super(Calculator, self).__init__()
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)

        self.entry = self.ui.le_entry
        self.temp = self.ui.lbl_temp
        self.entry_max_len = self.entry.maxLength() #Переменнная максимальной длины поля ввода

        QFontDatabase.addApplicationFont("fonts/Rubik-Regular.ttf")#Добавление шрифта

        #digits (соединяем нажатие кнопок с методом добавления цифр в поле ввода)
        self.ui.btn_0.clicked.connect(self.add_digit)
        self.ui.btn_1.clicked.connect(self.add_digit)
        self.ui.btn_2.clicked.connect(self.add_digit)
        self.ui.btn_3.clicked.connect(self.add_digit)
        self.ui.btn_4.clicked.connect(self.add_digit)
        self.ui.btn_5.clicked.connect(self.add_digit)
        self.ui.btn_6.clicked.connect(self.add_digit)
        self.ui.btn_7.clicked.connect(self.add_digit)
        self.ui.btn_8.clicked.connect(self.add_digit)
        self.ui.btn_9.clicked.connect(self.add_digit)

        #actions (действия)
        self.ui.btn_clear.clicked.connect(self.clear_all)
        self.ui.btn_ce.clicked.connect(self.clear_entry)
        self.ui.btn_point.clicked.connect(self.add_point)
        self.ui.btn_neg.clicked.connect(self.negate)
        self.ui.btn_backspace.clicked.connect(self.backspace)

        #math (математические операции)
        self.ui.btn_calc.clicked.connect(self.calculate)
        self.ui.btn_plus.clicked.connect(self.math_operation)
        self.ui.btn_sub.clicked.connect(self.math_operation)
        self.ui.btn_mul.clicked.connect(self.math_operation)
        self.ui.btn_div.clicked.connect(self.math_operation)

    def add_digit(self): #Метод добавления цифр в поле ввода
        self.remove_error()
        self.clear_temp_if_equality()
        btn = self.sender()

        digit_buttons = ('btn_0', 'btn_1', 'btn_2', 'btn_3', 'btn_4',
                         'btn_5', 'btn_6', 'btn_7', 'btn_8', 'btn_9')

        if btn.objectName() in digit_buttons:
            if self.entry.text() == '0':
                self.entry.setText(btn.text())
            else:
                self.entry.setText(self.entry.text() + btn.text())

        self.adjust_entry_font_size()


    #Метод для добавления точки (точка выбрана, т.к. проще конвертировать число в вещественное)
    def add_point(self) -> None:
        self.clear_temp_if_equality()
        if '.' not in self.entry.text():
            self.entry.setText(self.entry.text() + '.')
            self.adjust_entry_font_size()

    #Добавление отрицания
    def negate(self):
        self.clear_temp_if_equality()
        entry = self.entry.text()

        if '-' not in entry:
            if entry != '0':
                entry = '-' + entry
        else:
            entry = entry[1:]

        if len(entry) == self.entry_max_len + 1 and '-' in entry:
            self.entry.setMaxLength(self.entry_max_len + 1)
        else:
            self.entry.setMaxLength(self.entry_max_len)

        self.entry.setText(entry)
        self.adjust_entry_font_size()

    #Кнопка backspace(Ну это если кто не понял)
    def backspace(self) -> None:
        self.remove_error()
        self.clear_temp_if_equality()
        entry = self.entry.text()

        if len(entry) != 1:
            if len(entry) == 2 and '-' in entry:
                self.entry.setText('0')
            else:
                self.entry.setText(entry[:-1])
        else:
            self.entry.setText('0')
        self.adjust_entry_font_size()

    #Метод для очистки всех полей
    def clear_all(self) -> None:
        self.remove_error()
        self.entry.setText('0') #Ставим 0 в поле ввода
        self.adjust_entry_font_size()
        self.ui.lbl_temp.clear() #Очистка временного выражения

    #Метод для очистки поля ввода(временное выражение не трогаем)
    def clear_entry(self) -> None:
        self.remove_error()
        self.clear_temp_if_equality()
        self.entry.setText('0')
        self.adjust_entry_font_size()

    def clear_temp_if_equality(self) -> None:
        if self.get_math_sign() == '=':
            self.ui.lbl_temp.clear()

    @staticmethod
    def remove_trailing_zeros(num: str) -> str:
        n = str(float(num)) #Приводит аргумент к типу float
        return n[:-2] if n[-2:] == '.0' else n #возвращаем срез строки без двух последних символов, если они равны .0, иначе просто n

    #Метод для добавления временного выражения
    def add_temp(self) -> None:
        btn = self.sender()
        entry = self.remove_trailing_zeros(self.entry.text())

        if not self.ui.lbl_temp.text() or self.get_math_sign() == '=':
            self.ui.lbl_temp.setText(entry + f' {btn.text()} ') #Вставляем во временное выражение число из поля ввода со знаком аргумента
            self.entry.setText('0') #Очищаем поле ввода
            self.adjust_entry_font_size()

    def get_entry_num(self) -> Union[int, float]: #метод для получения числа из поля ввода
        entry = self.entry.text().strip('.')

        return float(entry) if '.' in entry else int(entry)

    #Метод для получения числа из временного выражения
    def get_temp_num(self) -> Union[int, float, None]:
        if self.ui.lbl_temp.text():
            temp = self.ui.lbl_temp.text().strip('.').split()[0]
            return float(temp) if '.' in temp else int(temp)

    #Метод для получения знака из временного выражения
    def get_math_sign(self) -> Optional[str]:
        if self.ui.lbl_temp.text():
            return self.ui.lbl_temp.text().strip('.').split()[-1]

    def get_entry_text_width(self) -> int:
        return self.entry.fontMetrics().boundingRect(self.entry.text()).width()

    def get_temp_text_width(self) -> int:
        return self.ui.lbl_temp.fontMetrics().boundingRect(self.ui.lbl_temp.text()).width()

    #Функция вычисления(Как не удивительно)
    def calculate(self) -> Optional[str]:
        entry = self.entry.text()
        temp = self.ui.lbl_temp.text()

        try:
            if temp:
                result = self.remove_trailing_zeros(
                    str(operations[self.get_math_sign()](self.get_temp_num(), self.get_entry_num()))
                )
                self.ui.lbl_temp.setText(temp + self.remove_trailing_zeros(entry) + ' =') #Добавление в lbl числа из поля ввода и знак "="
                self.entry.setText(result) #Ставим результат в поле ввода
                self.adjust_entry_font_size()
                return result #Возврат результата
        except KeyError:
            pass

        except ZeroDivisionError:
            if self.get_temp_num() == 0:
                self.show_error(error_undefined)
            else:
                self.show_error(error_zero_div)

    #Функция математической операции (ещё удивительнее, чем функция вычисления)
    def math_operation(self) -> None:
        temp = self.ui.lbl_temp.text()
        btn = self.sender()

        try:
            if not temp: #Если нет выражения
                self.add_temp() # То добавляем:)
            else:
                if self.get_math_sign() != btn.text:
                    if self.get_math_sign() == '=':
                        self.add_temp()
                    else:
                        self.ui.lbl_temp.setText(temp[:-2] + f'{btn.text()}')
                else:
                    self.ui.lbl_temp.setText(self.calculate() + f'{btn.text}')
        except TypeError:
            pass

    #Метод для показа ошибки
    def show_error(self, text: str) -> None:
        self.entry.setMaxLength(len(text))
        self.entry.setText(text)
        self.adjust_entry_font_size()
        self.disable_buttons(True)

    def remove_error(self) -> None:
        if self.entry.text() in (error_undefined, error_zero_div):
            self.entry.setMaxLength(self.entry_max_len)
            self.entry.setText('0')
            self.adjust_entry_font_size()
            self.disable_buttons(False)

    def disable_buttons(self, disable: bool) -> None:
        self.ui.btn_calc.setDisabled(disable)
        self.ui.btn_plus.setDisabled(disable)
        self.ui.btn_sub.setDisabled(disable)
        self.ui.btn_mul.setDisabled(disable)
        self.ui.btn_div.setDisabled(disable)
        self.ui.btn_neg.setDisabled(disable)
        self.ui.btn_point.setDisabled(disable)

        color = 'color: #888;' if disable else 'color: white;'
        self.change_buttons_color(color)

    #Метод изменения цвета кнопок
    def change_buttons_color(self, css_color: str) -> None:
        self.ui.btn_calc.setStyleSheet(css_color)
        self.ui.btn_plus.setStyleSheet(css_color)
        self.ui.btn_sub.setStyleSheet(css_color)
        self.ui.btn_mul.setStyleSheet(css_color)
        self.ui.btn_div.setStyleSheet(css_color)
        self.ui.btn_neg.setStyleSheet(css_color)
        self.ui.btn_point.setStyleSheet(css_color)

    def adjust_entry_font_size(self) -> None:
        font_size = default_entry_font_size
        while self.get_entry_text_width() > self.entry.width() - 15:
            font_size -= 1
            self.entry.setStyleSheet('font-size: ' + str(font_size) + 'pt; border: none;')

        font_size = 1
        while self.get_entry_text_width() < self.entry.width() - 60:
            font_size += 1

            if font_size > 40:
                break

            self.entry.setStyleSheet('font-size: ' + str(font_size) + 'pt; border: none;')

    def resizeEvent(self, event) -> None:
        self.adjust_entry_font_size()



if __name__ == "__main__":
    app = QApplication(sys.argv)

    window = Calculator()
    window.show()

    sys.exit(app.exec())