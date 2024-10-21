import sys
from styles_gui import Ui_MainWindow  # настройка внешнего вида окон
from PyQt5.QtWidgets import QMainWindow, QFileDialog, QMessageBox

from useful_stuff import save_file


class MyWindow(QMainWindow, Ui_MainWindow):
    """Основной интерфейс приложения."""
    table_types = {18, 25, 26, 27}

    def __init__(self, db_manager):
        super().__init__()
        self.manager = db_manager
        # переменные для хранения данных, используемых пользователем при работе
        self.current_task = []  # текущее задание, которое решает пользователь
        # здесь текущий вариант
        self.current_var = {'ids': [], 'text': [], 'links': [],
                            'correct_answers': [], 'user_answers': ['' for _ in range(27)]}
        self.active_task = 0  # ID текущего задания
        self.block_lonely = False  # флаг отвечает за то, решает ли пользователь вариант

        self.setupUi(self)  # настройка внешнего вида окна (унаследовано от Ui_MainWindow)

        self.loadBoxes()  # запускаем функцию, которая подгружает данные в ComboBox

        # привязываем ко всем кнопкам функции
        self.allow1.clicked.connect(self.filterByType)
        self.showTask1.clicked.connect(self.showLonelyTask)
        self.showSol1.clicked.connect(self.showLonelyTaskWithAnswer)
        self.answer1.clicked.connect(self.checkLonelyAnswer)
        self.saveFile1.clicked.connect(self.downloadFile)
        self.prev1.clicked.connect(self.showPrevLonelyTask)
        self.next1.clicked.connect(self.showNextLonelyTask)

        self.createVar.clicked.connect(self.createVariant)
        self.allow2.clicked.connect(self.showVarTask)
        self.saveFile2.clicked.connect(self.downloadFile)
        self.prev2.clicked.connect(self.showPrevVarTask)
        self.next2.clicked.connect(self.showNextVarTask)
        self.showRes.clicked.connect(self.endSolvingVar)
        self.saveAnswer.clicked.connect(self.saveVarAnswer)

    def loadBoxes(self):
        """Загружает данные из базы в ComboBox."""
        types = list(map(str, range(1, 28)))
        tasks = list(map(str, self.manager.get_tasks()))

        self.typeBox.addItems(types)
        self.taskBox.addItems(tasks)

        self.varBox.addItems(types)

    def createVariant(self):
        """Сгенерировать новый вариант из случайных заданий и отобразить его"""
        self.block_lonely = True
        for key in self.current_var:
            self.current_var[key].clear()
        self.current_var['user_answers'] = ['' for _ in range(27)]
        self.chooseLink2.clear()
        self.current_task = 0
        self.active_task = 0
        # сохраняем все задания из текущего варианта, чтобы не доставать из заново из базы потом
        for task in self.manager.generate_variant():
            self.current_var['ids'].append(task[0])
            self.current_var['text'].append(f'Тип задания: {task[1]}\n\n{task[2]}')
            self.current_var['correct_answers'].append(task[-2])
            self.current_var['links'].extend(task[-1])

        self.chooseLink2.addItems(self.current_var['links'])

    def getVarCheck(self):
        """Проверить, что можно решать вариант."""
        if self.active_task not in self.current_var['ids']:
            QMessageBox.warning(self, 'Действие невозможно',
                                'Необходимо сгенерировать вариант и выбрать номер задания')
            return False
        return True

    def showVarTask(self):
        """Показать текст задания варианта в нужном окне."""
        self.variantTask.clear()
        try:
            index = int(self.varBox.currentText()) - 1
            self.active_task = self.current_var['ids'][index]
            self.variantTask.setPlainText(self.current_var['text'][index])

            if '&' in self.current_var['correct_answers'][index]:
                self.answerAlone.setReadOnly(True)
            else:
                self.answerAlone.setReadOnly(False)
            self.answerTable2.setRowCount(len(
                self.current_var['correct_answers'][index].split('&')) // 2)
        except Exception:  # ловим исключение, если вариант не сгенерирован
            QMessageBox.warning(self, 'Действие невозможно',
                                'Необходимо сгенерировать вариант и выбрать номер задания')

    def saveVarAnswer(self):
        """Сохранить ответ на задание из варианта в self.current_var"""
        if not self.getVarCheck():
            return

        index = self.current_var['ids'].index(self.active_task)
        if '&' in self.current_var['correct_answers'][index]:
            answer = self.checkTableAnswer(lonely=False, index=index + 1)
        else:
            answer = self.answerVariant.text()
        self.current_var['user_answers'][index] = answer

    def endSolvingVar(self):
        """Конец решения варианта + вывод результата."""
        if not self.getVarCheck():
            return
        if QMessageBox.question(self, 'Завершение выполнения',
                                'Хотите завершить и узнать результат?') == QMessageBox.No:
            return
        result = 'Ваш результат:\n\n№\tВаш ответ - Правильный ответ\n'
        summ = 0
        for i, us_ans, cor_ans in zip(range(27), self.current_var['user_answers'],
                                      self.current_var['correct_answers']):
            self.manager.save_user_answer(us_ans, self.current_var['ids'][i])
            result += f'{i + 1})\t{us_ans}\t\t{cor_ans}\n'
            if us_ans == cor_ans:
                summ += 1
        result += f'Итого:\t{summ} / 27'
        QMessageBox.information(self, 'Результат', result)

        # очистка полей
        for key in self.current_var:
            self.current_var[key].clear()
        self.current_var['user_answers'] = ['' for _ in range(27)]
        self.chooseLink2.clear()
        self.active_task = 0
        self.block_lonely = False

    def showPrevVarTask(self):
        """Показать предыдущее по очереди задание из варианта."""
        if not self.getVarCheck():
            return
        index = int(self.varBox().text()) - 1
        if not index:
            return
        self.varBox.setCurrentIndex(self.varBox.currentIndex() - 1)
        self.showVarTask()

    def showNextVarTask(self):
        """Показать следующее по очереди задание варианта."""
        if not self.getVarCheck():
            return
        index = int(self.varBox().text()) - 1
        if index == 26:
            return
        self.varBox.setCurrentIndex(self.varBox.currentIndex() + 1)
        self.showVarTask()

    def showLonelyTask(self):
        """Отобразить задание (вне варианта) в соответствующем поле и подгрузить нужную инфу."""
        if self.block_lonely:
            QMessageBox.critical(self, 'Невозможно', 'Сначала завершите выполнение варианта.')
            return
        try:
            task_id = int(self.taskBox.currentText())
            self.active_task = task_id
            self.current_task = self.manager.get_task(task_id)
            self.lonelyTask.clear()
            self.lonelyTask.setPlainText(f'Тип задания: {self.current_task[0]}'
                                         f'\n\n{self.current_task[1]}')
            tp = int(self.typeBox.currentText())
            if tp in self.table_types:
                self.answerAlone.setReadOnly(True)
            else:
                self.answerAlone.setReadOnly(False)
            self.answerTable1.setRowCount(len(self.current_task[3].split('&')) // 2)

            self.showLonelyLinks()

            self.active_task = task_id

        except TypeError:
            QMessageBox.warning(self, 'Действие невозможно', 'Необходимо выбрать номер задания.')

    def showPrevLonelyTask(self):
        """Показать предыдущее задание того же типа"""
        if self.block_lonely:
            QMessageBox.critical(self, 'Невозможно', 'Сначала завершите выполнение варианта.')
            return
        if not self.active_task:
            QMessageBox.warning(self, 'Действие невозможно', 'Необходимо выбрать номер задания.')
            return
        ids = self.manager.get_tasks_by_type(int(self.typeBox.currentText()))
        if self.active_task == ids[0]:
            QMessageBox.warning(self, 'Действие невозможно',
                                'Это первое задание данного типа в базе.')
            return
        self.taskBox.setCurrentIndex(self.taskBox.currentIndex() - 1)
        self.showLonelyTask()

    def showNextLonelyTask(self):
        """Показать следующее задание того же типа."""
        if self.block_lonely:
            QMessageBox.critical(self, 'Невозможно', 'Сначала завершите выполнение варианта.')
            return
        if not self.active_task:
            QMessageBox.warning(self, 'Действие невозможно', 'Необходимо выбрать номер задания.')
            return
        ids = self.manager.get_tasks_by_type(int(self.typeBox.currentText()))
        if self.active_task == ids[-1]:
            QMessageBox.warning(self, 'Действие невозможно',
                                'Это последнее задание данного типа в базе.')
            return
        self.taskBox.setCurrentIndex(self.taskBox.currentIndex() + 1)
        self.showLonelyTask()

    def showLonelyTaskWithAnswer(self):
        """Показать задание с решением (вне варианта)"""
        if self.block_lonely:
            QMessageBox.critical(self, 'Невозможно', 'Сначала завершите выполнение варианта.')
            return
        if not self.current_task:
            self.showLonelyTask()
            if not self.current_task:
                QMessageBox.warning(self, 'Действие невозможно', 'Необходимо выбрать номер задания.')
                return
        self.lonelyTask.clear()
        answer = "\n".join(self.current_task[3].split('&'))
        self.lonelyTask.setPlainText(f'Тип задания: {self.current_task[0]}'
                                     f'\n\n{self.current_task[1]}\n\n\n{self.current_task[2]}\n'
                                     f'Ответ: {answer}')

    def showLonelyLinks(self):
        """Прикрепить ссылки к заданию."""
        self.chooseLink1.clear()
        if not self.active_task:
            self.showLonelyTask()
        if not self.current_task[-1]:
            return
        self.chooseLink1.addItems(self.current_task[-1])

    def filterByType(self):
        """Вспомогательная функция, сортирующая задания по типу."""
        if self.block_lonely:
            QMessageBox.critical(self, 'Невозможно', 'Сначала завершите выполнение варианта.')
            return
        try:
            tp = int(self.typeBox.currentText())
            tasks = list(map(str, self.manager.get_tasks_by_type(tp)))
            self.taskBox.clear()
            self.taskBox.addItems(tasks)

        except TypeError:
            QMessageBox.warning(self, 'Действие невозможно', 'Необходимо выбрать тип задания.')

    def checkTableAnswer(self, tp=0, index=-1, lonely=True):
        """Преобразовать ответ из таблицы в нужный формат - для заданий типа 25, 27 и т.п."""
        if lonely:
            table = self.answerTable1
        else:
            table = self.answerTable2

        try:
            if tp != 25 and index != 25:
                answer = f'{str(table.item(0, 0).text())}&' \
                         f'{str(table.item(0, 1).text())}'
                return answer
            answer = []
            for r in range(table.rowCount()):
                answer.append(f'{str(table.item(r, 0).text())}&'
                              f'{str(table.item(r, 1).text())}')
            return '&'.join(answer)

        except Exception:
            QMessageBox.warning(self, 'Действие невозможно', 'Необходимо ввести ответ.')

    def checkLonelyAnswer(self):
        """Проверить ответ на задание вне варианта."""
        if self.block_lonely:
            QMessageBox.critical(self, 'Невозможно', 'Сначала завершите выполнение варианта.')
            return
        if not self.current_task:
            QMessageBox.warning(self, 'Действие невозможно',
                                'Необходимо выбрать номер задания и ввести ответ.')
            return
        tp = int(self.typeBox.currentText())
        if tp in self.table_types:
            user_answer = self.checkTableAnswer(tp)
        else:
            user_answer = str(self.answerAlone.text())
        print(user_answer)
        print(self.current_task[3])
        if user_answer == self.current_task[3]:
            QMessageBox.information(self, ':)', 'Вы ответили верно!')
        else:
            QMessageBox.warning(self, ':(', 'Ответ неверен.')
        self.manager.save_user_answer(user_answer,
                                      self.manager.get_task_id_by_text(self.current_task[1]))

    def downloadFile(self):
        """Сохранить файл на диск (прикрепленный к заданию)."""
        box = self.chooseLink1 if not self.current_var['ids'] else self.chooseLink2
        if not box.currentText():
            QMessageBox.warning(self, 'Действие невозможно', 'Невозможно открыть ссылку на файл.')
        try:
            task_type = self.manager.get_type_by_task(self.active_task)
        except IndexError:
            QMessageBox.warning(self, 'Действие невозможно',
                                'Сначала выберите номер задания и посмотрите ссылку.')
            return
        url = str(box.currentText())
        if '?' in url:
            if task_type in {17, 24, 26, 27}:
                end = url.split('=')[-1] + '.txt'
            elif task_type in {3, 9, 18, 22}:
                end = url.split('=')[-1] + '.xlsx'
            elif task_type == 10:
                end = url.split('=')[-1] + '.docx'
            elif task_type == 1:
                end = url.split('=')[-1] + '.svg'
            else:
                end = url.split('=')[-1] + '.png'
        else:
            end = url.split("/")[-1]
        filename = f'{str(self.active_task)}_{end}'
        f = QFileDialog.getSaveFileName(self, 'Выберите место для сохранения файла.',
                                        '\\saves\\' + filename)[0]
        try:
            save_file(url, f)
        except Exception:
            QMessageBox.critical(self, 'Ошибка', 'Не удалось сохранить файл.')

    def closeEvent(self, a0):
        """Переопределяем завершение программы так, чтобы сессия с базой данных тоже завершалась."""
        self.manager.close_session()


def except_hook(tp, value, traceback):
    sys.excepthook(tp, value, traceback)
