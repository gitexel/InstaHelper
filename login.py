from PyQt5 import QtWidgets, uic
from PyQt5.QtCore import QThreadPool

from insta import InstaService
from helpers import validate_input, CheckConnectivity, Worker
from settings import UserData


# from dashboard import DashBoardUi


# todo detect OS and change user agent

class LoginUi(QtWidgets.QMainWindow, CheckConnectivity, UserData):
    def __init__(self):
        super(LoginUi, self).__init__()
        uic.loadUi('ui/login.ui', self)

        self.button_qt = self.findChild(QtWidgets.QPushButton, 'loginButton')
        self.button_qt.clicked.connect(self.login_action)
        self.username_qt = self.findChild(QtWidgets.QLineEdit, 'usernameEdit')
        self.password_qt = self.findChild(QtWidgets.QLineEdit, 'passwordEdit')
        self.status_qt = self.findChild(QtWidgets.QLabel, 'status')
        self.loginBox_qt = self.findChild(QtWidgets.QGroupBox, 'loginBox')
        self.rememberCheckBox_qt = self.findChild(QtWidgets.QCheckBox, 'rememberCheckBox')
        self.statusBar_qt = self.findChild(QtWidgets.QStatusBar, 'statusBar')
        self.show()

        self.threadpool = QThreadPool()
        self.password = ''
        self.service = None

        self.threadpool.start(self.check_net_worker)

    def login_gui_job(self, enable=False, msg='Loading...'):
        self.status_qt.setText(msg)
        self.loginBox_qt.setEnabled(enable)

    def login_action(self):
        self.username = validate_input(self.username_qt.text()).lower()
        self.password = validate_input(self.password_qt.text())

        if not self.username or not self.password:
            self.login_gui_job(True, 'Invalid username or password')
        else:
            worker = Worker(self.login_to_service_start)
            worker.signals.result.connect(self.login_to_service_result)
            worker.signals.finished.connect(self.login_to_service_finished)
            worker.signals.progress.connect(self.login_to_service_progress)
            self.threadpool.start(worker)

    def login_to_service_start(self, progress_callback):
        self.login_gui_job(False, 'Loading...')
        progress_callback.emit(0)  # send progress int info to progress function.
        self.service = InstaService(self.username, self.password)
        result = self.service.client_login()
        progress_callback.emit(100)  # send progress int info to progress function.
        return result

    def login_to_service_result(self, msg):
        self.statusBar_qt.showMessage(str(msg))

    def login_to_service_finished(self):

        if self.service.client.is_authenticated:

            self.login_gui_job(True, 'Success login')

            # save client cookie for later usage
            if self.rememberCheckBox_qt.isChecked():
                self.set_username(self.username)
                self.set_cookie(self.service.cookie_dict)
                self.password = ''  # remove password

            self.close()
            # todo open Dashboard window
        else:
            self.login_gui_job(True, 'Failed to login')

    def process_result(self, net_status):
        if net_status:
            self.msg = "You are connected to the Internet."
            self.statusBar_qt.showMessage(self.msg)
            self.loginBox_qt.setEnabled(True)
        else:
            self.msg = "You are not connected to the Internet."
            self.statusBar_qt.showMessage(self.msg)
            self.loginBox_qt.setEnabled(False)

    @staticmethod
    def login_to_service_progress(n):
        print("%d%% login done" % n)
