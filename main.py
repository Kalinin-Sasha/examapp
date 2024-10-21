"""Запуск всех компонентов приложения."""
import os
import sys
from PyQt5.QtWidgets import QApplication

from db_manager import DBManager
from gui import MyWindow, except_hook


def main():
    manager = DBManager(os.path.abspath('data_bases\\v0-0-1.db'))  # подключение к базе данных

    # запуск графического интерфейса
    app = QApplication(sys.argv)
    gui = MyWindow(manager)
    gui.show()
    sys.excepthook = except_hook
    sys.exit(app.exec())


if __name__ == '__main__':  # условие, чтобы программа выполнялась только при прямом ее запуске
    main()
