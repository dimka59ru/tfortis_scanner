## TFortis Scanner
## Программа для поиска устройств TFortis в сети

import hashlib
import logging
import queue
import socket
import time
import urllib.parse
import webbrowser
from PyQt5 import QtGui
from threading import Thread
# import ipdb
import binascii
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QIcon
from PyQt5.QtGui import QMovie
from PyQt5.QtWidgets import QAbstractItemView, QLineEdit, QDialog, QMessageBox, QHeaderView, QAction, qApp, QMenu, \
    QStyle
from PyQt5.QtWidgets import QApplication
from PyQt5.QtWidgets import QLabel
from PyQt5.QtWidgets import QTableWidgetItem
from PyQt5.QtWidgets import QWidget
from PyQt5.uic import loadUi

# logging.basicConfig(level=logging.DEBUG,
#                     format='(%(threadName)-9s) %(message)s', )

# Настройки
BUF_SIZE = 10  # Размер буфера для очереди
q = queue.Queue(BUF_SIZE)  # Очередь, в которую будем класть найденные коммутаторы
UDP_PORT = 6123  # Порт, по которому работаем
IP_SEND = "255.255.255.255"  # Адрес для широковещательного запроса
MESSAGE = b'\xE0' + b'\x00' * 443  # Сообщение для широковещательнго запроса на поиск
MESSAGE_SIZE = len(MESSAGE)

ROW_COUNT = 12  # Начальное количество строк в такблице в окне
ROW_HEIGHT = 21  # Высота строк в окне
SEARCH_TIME = 5  # 10 сек. Время посика (прослушивания сети)
# Список моделей коммутаторов
MODELS = {
    255: 'Unknown',
    1: 'PSW-2G',
    2: 'PSW-2G-UPS',
    3: 'PSW-2G+',
    4: 'PSW-1G4F',
    5: 'PSW-2G4F',
    6: 'PSW-2G6F+',
    7: 'PSW-2G8F+',
    8: 'PSW-1G4F-UPS',
    9: 'PSW-2G4F-UPS',
    10: 'PSW-2G2F+',
    11: 'PSW-2G2F+UPS',
    200: 'SWU-16',
    101: 'TELEPORT-1',
    102: 'TELEPORT-2'

}

# /Настройки


appStyle = """
 QTableView QTableCornerButton::section {
            border-top: 1px;
            border-bottom: 1px solid #CCC;
            border-right: 1px solid #CCC;
 }

QTableView QHeaderView::section{
            border-top: 1px;
            border-bottom: 1px solid #CCC;
            border-right: 1px solid #CCC;
            font: bold;
            padding:3px;            

}
"""


# Главное окно
class MainWindow(QWidget):
    def __init__(self, window_title, window_icon):
        super(MainWindow, self).__init__()
        try:
            loadUi("resource/main_window.ui", self)
            self.show()
        except FileNotFoundError:
            self.label = QLabel(
                u"""<center><h2><font color=brown>
                File form.ui not found!
                </font></h2></center>
                """
            )
            self.label.show()

        else:
            self.setStyleSheet(appStyle)
            self.setWindowTitle(window_title)
            self.setWindowIcon(QIcon(window_icon))

            self.resize(660, 360)
            # Отображаем таблицу в окне
            self.init_table(self.table, row_count=ROW_COUNT, column_count=7,
                            column_name=["Device", "IP", "Mask", "MAC", "Description", "Location", "Firmware"])

            self.table.setContextMenuPolicy(Qt.CustomContextMenu)
            self.table.customContextMenuRequested.connect(self.open_menu)

            # Связывание кнопок с функциями
            self.button_search.clicked.connect(self.clicked_search)
            # self.button_edit.clicked.connect(self.clicked_edit)

            # self.table.itemDoubleClicked.connect(self.open_in_browser)
            # self.table.itemSelectionChanged.connect(self.show_list_cam)

            # Список, в который будем класть объекты потоков
            self.list_thread = []

            # gif'ка прогресса
            self.movie = QMovie("resource/ajax-loader.gif")
            self.label_progress.setMovie(self.movie)

            # Связываем выбор адреса в окне с функцией
            self.iface_box.activated.connect(self.combo_chosen)

            # Заполняем адресами бокс выбора IP в окне
            for addr in self.get_ip_addresses():
                self.iface_box.addItem(addr)
            # IP по умолчанию, если не выбран из списка
            self.my_ip = self.iface_box.itemText(0)

            # Объект модального окна для изменения настроек коммутатора
            self.win_edit = EditWindow(parent=self)

    def open_menu(self, position):
        if self.table.selectedItems() and self.movie.state() == 0:
            menu = QMenu()
            open_in_browser_action = menu.addAction(QIcon("resource/internet-web-browser.png"),
                                                    "Открыть в браузере")
            open_in_browser_action.triggered.connect(self.open_in_browser)

            edit_device_settings_action = menu.addAction(QIcon("resource/system-settings.png"),
                                                         "Изменить настройки")
            edit_device_settings_action.triggered.connect(self.clicked_edit)

            show_list_cam_action = menu.addAction(QIcon("resource/view-media.png"),
                                                  "Посмотреть список камер")
            show_list_cam_action.triggered.connect(self.show_list_cam)

            menu.exec_(self.table.mapToGlobal(position))
            # quit_action = menu.addAction("Quit")
            # quit_action.triggered.connect(qApp.quit)
            # show_list_cam_action.triggered.connect(self.show_list_cam)
            # action = menu.exec_(self.table.mapToGlobal(position))

            # if action == show_list_cam_action:
            #     self.show_list_cam()
            # elif action == open_in_browser_action:
            #     self.open_in_browser()
            # elif action == quit_action:
            #     qApp.quit()

    def show_list_cam(self):
        if self.table.selectedItems():
            cams = list_cam[self.selected_row()]
            str = ""
            for i, cam in enumerate(cams, 1):

                if not cam[1] == "0.0.0.0":
                    str += "port #{0:2d}: {1:>14s} - {2:>18}\n".format(i, cam[1], cam[0])
            if str == "":
                self.information_message("Нет данных", "Список камер")
            else:
                self.information_message(str, "Список камер")

    # Функция для обработки нажатия кнопки "Искать"
    def clicked_search(self):
        self.table.clearContents()  # Очищаем таблицу от контента
        self.table.setRowCount(ROW_COUNT)  # Устанавливаем некоторое количество строк в таблице

        # Делаем кнопки неактивными
        self.button_search.setDisabled(True)
        # self.button_edit.setDisabled(True)

        # Отображаем gif прогресса
        self.label_progress.show()
        self.movie.start()

        # сокеты
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
        # sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        # sock.setblocking(False)  # Неблокирующий сокет
        # sock.settimeout(1)
        sock.bind((self.my_ip, UDP_PORT))  # связываем сокет
        sock.sendto(MESSAGE, (IP_SEND, UDP_PORT))
        self.create_and_start_threads(sock)  # Создаем и запускаем треды

        return

    # Функция для обработки нажатия кнопки "Изменить"
    def clicked_edit(self):

        if self.table.selectedItems():
            model = self.table.item(self.selected_row(), 0).text()
            if (model == "PSW-2G") or (model == "PSW-2G-UPS"):
                self.information_message("Коммутаторы PSW-2G и PSW-2G-UPS \n не поддерживают изменение настроек!")
            elif (model == "TELEPORT-1") or (model == "TELEPORT-2"):
                self.win_edit.set_fields()
                self.win_edit.show()
            else:
                if int(self.table.item(self.selected_row(), 6).text().replace(".", "")) >= 109:
                    self.win_edit.set_fields()
                    self.win_edit.show()
                else:
                    self.information_message("Для изменения настроек требуется прошивка версии не ниже 1.09")

    def selected_row(self):
        indexes = self.table.selectionModel().selectedRows()
        row = indexes[0].row()
        return row

    # def init_table_view_list_cam(self, row_count=16, column_count=2, column_name=None):
    #     if column_name is None:
    #         column_name = ["MAC", "IP"]
    #
    #     self.table_view_list_cam.setRowCount(row_count)  # Устанавливаем количество строк
    #     self.table.setHorizontalHeaderLabels(column_name)  # Именуем столбцы таблицы
    #     self.table.verticalHeader().setDefaultSectionSize(ROW_HEIGHT)  # Устанавливаем высоту строк

    # Функция начальной инициализации таблиц в окне
    def init_table(self, table, row_count=12, column_count=7,
                   column_name=None):

        # if column_name is None:
        #     column_name = ["Device", "IP", "Mask", "MAC", "Description", "Location", "Firmware"]

        table.horizontalHeader().setStretchLastSection(True)
        # ipdb.set_trace()  ######### Break Point ###########

        # Режим выделения.
        table.setSelectionBehavior(QAbstractItemView.SelectRows)  # Выделяем только строки.
        table.setSelectionMode(QAbstractItemView.SingleSelection)  # Выделяем только одну строку.

        table.setEditTriggers(QAbstractItemView.NoEditTriggers)  # Запрет редактирования таблицы
        table.setRowCount(row_count)  # Устанавливаем количество строк
        table.setColumnCount(column_count)  # Устанавливаем количество столбцов
        table.setHorizontalHeaderLabels(column_name)  # Именуем столбцы таблицы
        table.verticalHeader().setDefaultSectionSize(ROW_HEIGHT)  # Устанавливаем высоту строк
        # Ширина столбцов
        for i in range(0, column_count):
            table.horizontalHeader().resizeSection(i, 85)

        table.horizontalHeader().resizeSection(3, 100)
        # table.horizontalHeader().resizeSection(1, 80)
        # table.horizontalHeader().resizeSection(2, 80)
        # table.horizontalHeader().resizeSection(3, 100)
        # table.horizontalHeader().resizeSection(6, 70)
        # self.table.verticalHeader().setVisible(False)  # Выключаем отображение номеров строк

    # Функция, вызываемая при закрытии окна
    def closeEvent(self, event):
        self.hide()
        for item in self.list_thread:
            item.running = False
            item.join(2)

        event.accept()

    def create_and_start_threads(self, sock):
        end_time = time.time() + SEARCH_TIME  # Время длительности потоков

        # Создаем потоки-производители, для складывания
        # полученных данных в очередь
        p1 = ProducerThread(name='producer1', args=(end_time, sock))
        p2 = ProducerThread(name='producer2', args=(end_time, sock))

        # Создаем потоки-получатели, для чтения очереди данных
        c = ConsumerThread(name='consumer', args=(end_time, sock))

        # Стартуем потоки
        p1.start()
        p2.start()
        c.start()

        # Добавляем объекты потоков в список, чтобы в будущем,
        # пройдя по списку, завершить потоки
        self.list_thread.append(p1)
        self.list_thread.append(p2)
        self.list_thread.append(c)

    # Функция для получения IP-адресов сетевых карт
    # @staticmethod
    def get_ip_addresses(self):
        try:
            addrs = socket.gethostbyname_ex(socket.gethostname())[2]
            return addrs
        except Exception as e:
            self.information_message(e)

    def combo_chosen(self, i):
        self.my_ip = self.iface_box.itemText(i)

    def open_in_browser(self):
        url = 'http://{}'.format(self.table.item(self.selected_row(), 1).text())
        webbrowser.open_new_tab(url)

    def information_message(self, message, head_text="Message"):
        QMessageBox.information(self, head_text, message)


class EditWindow(QDialog):
    def __init__(self, parent=None):
        super(EditWindow, self).__init__(parent)
        loadUi('resource/edit_window.ui', self)
        # self.setWindowFlags(Qt.Dialog)
        self.setWindowModality(Qt.WindowModal)
        self.setWindowTitle("Edit")
        self.buttonBox.accepted.connect(self.press_ok)
        self.line_pswd.setEchoMode(QLineEdit.Password)
        self.setFixedSize(292, 182)

    def set_fields(self):
        indexes = mainWin.table.selectionModel().selectedRows()
        row = indexes[0].row()
        ip = mainWin.table.item(row, 1).text().split('.')
        mask = mainWin.table.item(row, 2).text().split('.')

        self.line_edit_ip.setText(ip[0])
        self.line_edit_ip_2.setText(ip[1])
        self.line_edit_ip_3.setText(ip[2])
        self.line_edit_ip_4.setText(ip[3])

        self.line_edit_mask.setText(mask[0])
        self.line_edit_mask_2.setText(mask[1])
        self.line_edit_mask_3.setText(mask[2])
        self.line_edit_mask_4.setText(mask[3])

        self.line_edit_description.setText(mainWin.table.item(row, 4).text())
        self.line_edit_location.setText(mainWin.table.item(row, 5).text())

    def check_fields(self):
        pass

    def press_ok(self):
        message = self.create_message()
        self.send_data(message)

    # создаем сообщение с настройками для отправки
    def create_message(self):
        message = b''
        psw_setting_request = b'\xe2'  # Код запроса на принятие настроек

        ip = (self.line_edit_ip.text() + "." + self.line_edit_ip_2.text() + "." + self.line_edit_ip_3.text() +
              "." + self.line_edit_ip_4.text())
        description = self.line_edit_description.text()
        location = self.line_edit_location.text()
        username = self.line_login.text()
        password = self.line_pswd.text()
        mask = (self.line_edit_mask.text() + "." + self.line_edit_mask_2.text() + "." + self.line_edit_mask_3.text() +
                "." + self.line_edit_mask_4.text())
        buff_str = """#IPADDRESS=[{}]#SYSTEM_LOCATION=[{}]#SYSTEM_NAME=[{}]#NETMASK=[{}]""".format(ip, location,
                                                                                                   description, mask)
        buff_byte = bytes(buff_str, 'utf-8')

        message += psw_setting_request
        message += binascii.unhexlify(self.get_mac())
        message += self.get_md5_bytes(self.get_mac(), username, password)
        message += buff_byte

        message += b'\x00' * (MESSAGE_SIZE - len(message))  # Добиваем сообщение нулями

        return message

    @staticmethod
    def get_mac():
        indexes = mainWin.table.selectionModel().selectedRows()
        row = indexes[0].row()
        mac = mainWin.table.item(row, 3).text()
        mac = mac.replace(':', '')
        return mac

    @staticmethod
    def get_md5_bytes(mac, username, password):
        string_for_md5 = mac + "+" + username + "+" + password
        string_md5 = hashlib.md5(string_for_md5.encode()).hexdigest()
        string_md5_b = bytes(string_md5, 'utf-8')
        return string_md5_b

    def send_data(self, message):
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
        # sock.setblocking(False)  # Неблокирующий сокет
        sock.settimeout(0.5)
        sock.bind((mainWin.my_ip, UDP_PORT))
        sock.sendto(message, (IP_SEND, UDP_PORT))
        end_time = time.time() + 2
        flag_answer = False
        while time.time() < end_time:
            logging.debug("send data")
            try:
                data = sock.recv(MESSAGE_SIZE)

                if hex(data[0]) == '0xe3':
                    flag_answer = True
                    code_error = '{d[7]:02X}'.format(d=data)

                    if code_error == "01":
                        mainWin.information_message("Ошибка авторизации!")
                    elif code_error == "00":
                        mainWin.information_message("Успешно!")
                    break
            except OSError as msg:
                continue
        if not flag_answer:
            mainWin.information_message("Ответ от устройства не получен. Попробуйте снова!")
        sock.close()


class ProducerThread(Thread):
    """ Класс потока-производителя"""

    def __init__(self, group=None, target=None, name=None,
                 args=(), kwargs=None, verbose=None, ):
        super(ProducerThread, self).__init__()
        self.target = target
        self.name = name
        self.end_time = args[0]
        self.running = False
        self.sock = args[1]

    def run(self):
        logging.debug("Producer thread run")
        self.running = True
        while (time.time() < self.end_time) and self.running:
            if not q.full():
                try:
                    item = self.sock.recv(MESSAGE_SIZE)
                    # print(item)
                    q.put(item)
                    logging.debug('Putting ' + str(item)
                                  + ' : ' + str(q.qsize()) + ' items in queue')
                except OSError as msg:
                    # logging.debug(msg)
                    continue
                    # time.sleep(1.01)
        return


list_cam = {}


class ConsumerThread(Thread):
    """ Класс потока потребителя """

    def __init__(self, group=None, target=None, name=None,
                 args=(), kwargs=None, verbose=None):
        super(ConsumerThread, self).__init__()
        self.target = target
        self.name = name
        self.end_time = args[0]
        self.sock = args[1]
        self.running = False
        return

    def run(self):
        self.running = True

        i = 0
        while True:
            if not q.empty():
                item = q.get()
                logging.debug(str(q.qsize()) + ' items in queue. ''Getting ' + str(item)
                              )
                try:
                    if hex(item[0]) == '0xe1':
                        self.add_in_table(item, i)
                        i += 1

                except IndexError:
                    pass
            else:
                if (time.time() > self.end_time) or (not self.running):
                    break
            time.sleep(0.01)

        logging.debug("Consumer END")
        logging.debug("Socket close")
        self.sock.close()
        # Делаем кнопки активными
        mainWin.button_search.setDisabled(False)
        # mainWin.button_edit.setDisabled(False)
        mainWin.movie.stop()
        mainWin.label_progress.hide()

        return

    # преобразовываем полученные данные в строки и складываем в список
    def convert_data(self, data):

        try:
            if MODELS.get(data[1]):
                model = QTableWidgetItem(MODELS.get(data[1]))
            else:
                model = QTableWidgetItem("Unknown")
        except IndexError:
            model = QTableWidgetItem("Unknown")

        try:
            ip = QTableWidgetItem("{d[2]}.{d[3]}.{d[4]}.{d[5]}".format(d=data))
        except IndexError:
            ip = QTableWidgetItem("0.0.0.0")

        try:
            mac = QTableWidgetItem("{d[6]:02X}:{d[7]:02X}:{d[8]:02X}:{d[9]:02X}:{d[10]:02X}:{d[11]:02X}".format(d=data))
        except IndexError:
            mac = QTableWidgetItem("0:0:0:0")

        try:
            mask = QTableWidgetItem("{d[276]}.{d[277]}.{d[278]}.{d[279]}".format(d=data))
        except IndexError:
            mask = QTableWidgetItem("0.0.0.0")

        try:
            description = QTableWidgetItem(self.decoding_fields(data[12:140]))
        except IndexError:
            description = QTableWidgetItem("")

        try:
            location = QTableWidgetItem(self.decoding_fields(data[140:268]))
        except IndexError:
            location = QTableWidgetItem("")

        try:
            firmware = QTableWidgetItem("{d[274]:02X}.{d[273]:02X}.{d[272]:02X}".format(d=data))
        except IndexError:
            firmware = QTableWidgetItem("00.00.00")

        search_mac_entry = []
        for j in range(0, 16):
            temp_mac = ""
            temp_ip = ""
            for i in range(0, 6):
                temp_mac += "{0:02X}:".format(data[(284 + 10 * j) + i])
            for i in range(0, 4):
                temp_ip += "{0}.".format(data[(290 + 10 * j) + i])

            search_mac_entry.append((temp_mac[0: -1], temp_ip[0: -1]))

        return dict(model=model, ip=ip, mask=mask, mac=mac, description=description,
                    location=location, firmware=firmware, search_mac_entry=search_mac_entry)

    def add_in_table(self, data, i):
        if i >= mainWin.table.rowCount():
            mainWin.table.setRowCount(mainWin.table.rowCount() + 1)

        device = self.convert_data(data)

        list_cam[i] = device["search_mac_entry"]

        mainWin.table.setItem(i, 0, device["model"])
        mainWin.table.setItem(i, 1, device["ip"])
        mainWin.table.setItem(i, 2, device["mask"])
        mainWin.table.setItem(i, 3, device["mac"])
        mainWin.table.setItem(i, 4, device["description"])
        mainWin.table.setItem(i, 5, device["location"])
        mainWin.table.setItem(i, 6, device["firmware"])

        # self.row_counter += 1
        mainWin.table.reset()

    @staticmethod
    def decoding_fields(data):
        result = data.replace(b'\x00', b'')
        try:
            result = urllib.parse.unquote_to_bytes(result).decode('utf-8')
        except UnicodeDecodeError:
            result = urllib.parse.unquote_to_bytes(result).decode('cp1251')
        except:
            result = ''
        result = result.translate(result.maketrans('+', ' ')).strip()

        return result


if __name__ == '__main__':
    import sys

    WINDOW_TITLE = "TFortis Scanner v2.1.0"
    WINDOW_ICON = "resource/tfortis_ico.ico"

    app = QApplication(sys.argv)
    # app.setStyle("fusion")
    # p = QPalette
    # p = qApp.palette()
    # p.setColor(QPalette.Highlight, QColor(77, 98, 120))
    # qApp.setPalette(p)
    mainWin = MainWindow(WINDOW_TITLE, WINDOW_ICON)

    # mainWin.show()
    sys.exit(app.exec_())
