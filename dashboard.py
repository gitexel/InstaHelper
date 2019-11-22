import time

from PyQt5 import QtWidgets, uic, QtCore
from PyQt5.QtCore import QThreadPool, pyqtSignal
from PyQt5.QtGui import QCursor
from PyQt5.QtWidgets import QTableWidgetItem, QPushButton, QLabel, QTableWidget, QMainWindow, QFrame, QProgressBar, \
    QLineEdit

from insta import InstaService, UserProfile
from helpers import Worker, CheckConnectivity, validate_input
from settings import UserData


# todo wrapper to check if cookie is valid or not

class Engine(UserData, CheckConnectivity):
    pass


class DashBoardUi(QtWidgets.QMainWindow, Engine):
    def __init__(self):
        super(DashBoardUi, self).__init__()
        uic.loadUi('ui/dashboard.ui', self)
        self.show()

        self._init_ui()

        self.threadpool = QThreadPool()

        self._init_service()

    # noinspection PyTypeChecker
    def _init_ui(self):
        self.MainWindow: QMainWindow = self.findChild(QMainWindow, 'MainWindow')
        self._init_home_ui()
        self._init_subscription_ui()

    ###################################################################################
    # Start of home Tab                                                               #
    ###################################################################################

    # noinspection PyTypeChecker
    def _init_home_ui(self):
        self.profilePic: QLabel = self.findChild(QLabel, 'profilePicLabel')
        self.usernameLabel: QLabel = self.findChild(QLabel, 'usernameLabel')
        self.fullNameLabel: QLabel = self.findChild(QLabel, 'fullNameLabel')
        self.followersLabel: QLabel = self.findChild(QLabel, 'followersLabel')
        self.followingLabel: QLabel = self.findChild(QLabel, 'followingLabel')

        self.progressBar: QProgressBar = self.findChild(QProgressBar, 'progressBar')
        self.progressBar.setValue(0)
        self.suggestedTableWidget: QTableWidget = self.findChild(QTableWidget, 'suggestedTableWidget')
        self.suggestedTableWidget.setColumnWidth(0, 50)
        self.suggestedTableWidget.setColumnWidth(1, 125)
        self.suggestedTableWidget.setColumnWidth(2, 70)
        self.suggestedTableWidget.setColumnWidth(3, 70)
        self.suggestedTableWidget.setColumnHidden(4, True)

        self.showMoreButton: QPushButton = self.findChild(QPushButton, 'showMoreButton')
        self.showMoreButton.clicked.connect(self.show_more_button_click_action)

        self.button_table_inside: QPushButton
        self.img_table_inside: QLabel

    def _init_service(self):
        service_worker = Worker(self._load_service)
        service_worker.signals.finished.connect(self._load_home)
        self.threadpool.start(service_worker)

    # noinspection PyUnusedLocal
    def _load_service(self, progress_callback: pyqtSignal):
        self.service = InstaService()
        self.service.set_cookie_dict(self.cookie)
        self.service.client_login()

    def _load_home(self):

        client_profile_worker = Worker(self._load_client_profile)
        client_profile_worker.signals.result.connect(self._fill_client_profile)

        suggested_users_worker = Worker(self._load_suggessted_users)
        suggested_users_worker.signals.progress.connect(self._fill_table_row_progress)
        suggested_users_worker.signals.finished.connect(self._enable_show_more_button)

        self.threadpool.start(client_profile_worker)
        self.threadpool.start(suggested_users_worker)

        self.showMoreButton.setEnabled(False)

    # noinspection PyUnusedLocal
    def _load_client_profile(self, progress_callback: pyqtSignal) -> UserProfile:
        result = self.service.get_client_profile(self.username)
        if isinstance(result, dict):
            profile = UserProfile(result)
        else:
            profile = UserProfile({})
        return profile

        # todo error show

    def _fill_client_profile(self, profile):
        self.usernameLabel.setText(profile.username)
        self.fullNameLabel.setText(profile.full_name)
        self.followersLabel.setText(str(profile.follower_count))
        self.followingLabel.setText(str(profile.following_count))
        self.profilePic.setPixmap(profile.profile_pic)

    def _load_suggessted_users(self, progress_callback: pyqtSignal):
        sug_users: list = self.service.get_suggested_users(enable_popular=True)
        if isinstance(sug_users, list):
            i: int

            user: UserProfile
            rows_len = self.suggestedTableWidget.rowCount()

            for row_num, user in enumerate(sug_users, rows_len):
                if isinstance(user, UserProfile):
                    progress_callback.emit({'user': user, 'row_num': row_num})
        else:
            ...
            # todo error show

    def _fill_table_row_progress(self, data: dict):
        row_num = data.get('row_num')
        user = data.get('user')
        follow_button, profile_img = self._get_table_button_and_img(user=user)

        self.suggestedTableWidget.insertRow(row_num)
        self.suggestedTableWidget.setCellWidget(row_num, 0, profile_img)
        self.suggestedTableWidget.setItem(row_num, 1, QTableWidgetItem(user.full_name + '\n@' + user.username))
        self.suggestedTableWidget.setItem(row_num, 2, QTableWidgetItem(str(user.follower_count)))
        self.suggestedTableWidget.setCellWidget(row_num, 3, follow_button)
        self.suggestedTableWidget.setItem(row_num, 4, QTableWidgetItem(user.id))

    def _get_table_button_and_img(self, user: UserProfile) -> [QPushButton, QLabel]:
        follow_button = QPushButton(self.suggestedTableWidget)
        follow_button.setText('Follow')
        follow_button.setCursor(QCursor(QtCore.Qt.PointingHandCursor))

        follow_button.clicked.connect(self.follow_button_click_action)

        profile_img = QLabel(self.suggestedTableWidget)
        profile_img.setText(user.id)
        profile_img.setFrameShape(QFrame.Panel)
        profile_img.setFixedSize(50, 45)
        profile_img.setLineWidth(2)
        profile_img.setPixmap(user.profile_pic)
        profile_img.setScaledContents(True)

        return follow_button, profile_img

    def _follow_operation(self, progress_callback: pyqtSignal) -> dict:
        row: int = self.suggestedTableWidget.currentRow()
        user_id: str = self.suggestedTableWidget.item(row, 4).text()  # get user's id from hidden column
        # can't make it with self because it will override the button, so we will return it instead.
        button_table_inside: QPushButton = self.suggestedTableWidget.cellWidget(row, 3)
        progress_callback.emit(button_table_inside)  # run _update_button_followed_table_progress to disable button

        result = self.service.follow_user(user_id=int(user_id))

        if isinstance(result, bool) and result:
            return {'done': True, 'button': button_table_inside}
        # todo show error
        return {'done': False, 'button': button_table_inside}

    def _update_button_followed_table(self, result: dict):
        done = result.get('done', False)
        button_table_inside = result.get('button', QPushButton)

        if done:
            button_table_inside.setText('Following')
            self.followingLabel.setText(str(int(self.followingLabel.text()) + 1))
            self.progressBar.setValue(self.progressBar.value() + 1)
        else:
            button_table_inside.setText('Error')

    @staticmethod
    def _disable_follow_button_table_progress(button_table_inside):
        button_table_inside.setEnabled(False)

    def _enable_show_more_button(self):
        self.showMoreButton.setEnabled(True)

    def show_more_button_click_action(self):
        self._load_home()

    def follow_button_click_action(self):
        follow_operation_worker = Worker(self._follow_operation)
        follow_operation_worker.signals.result.connect(self._update_button_followed_table)
        follow_operation_worker.signals.progress.connect(self._disable_follow_button_table_progress)
        self.threadpool.start(follow_operation_worker)

    ###################################################################################
    # End of home Tab                                                                 #
    ###################################################################################

    ###################################################################################
    # Start of subscription Tab                                                       #
    ###################################################################################

    # noinspection PyTypeChecker
    def _init_subscription_ui(self):
        self.subscriptionKeyEdit: QLineEdit = self.findChild(QLineEdit, 'subscriptionKeyEdit')

        self.subscriptionActivateButton: QPushButton = self.findChild(QPushButton, 'subscriptionActivateButton')
        self.subscriptionActivateButton.clicked.connect(self.activate_subscription_click_action)

        self.subscriptionStatusLabel: QLabel = self.findChild(QLabel, 'subscriptionStatusLabel')

    def activate_subscription_click_action(self):
        activate_worker = Worker(self._activate_subscription)
        activate_worker.signals.finished.connect(self._enable_subscription_activate_button_and_edit)
        activate_worker.signals.result.connect(self._subscription_status_result)

        self.subscriptionActivateButton.setEnabled(False)
        self.subscriptionKeyEdit.setEnabled(False)

        self.threadpool.start(activate_worker)

    # noinspection PyUnusedLocal
    def _activate_subscription(self, progress_callback: pyqtSignal) -> dict:
        key = self.subscriptionKeyEdit.text()
        key = validate_input(value=key)
        time.sleep(3)
        if len(key) > 5:
            pass
        result: dict = self.service.get_subscription_status()

        if isinstance(result, dict):
            self.set_subscription_key(key=key)
            return result

        return {}

    def _enable_subscription_activate_button_and_edit(self):
        self.subscriptionActivateButton.setEnabled(True)
        self.subscriptionKeyEdit.setEnabled(True)

    def _subscription_status_result(self, result):
        if result.get('valid', False):
            self.subscriptionStatusLabel.setText('Valid until ' + result.get('end_date', ''))

###################################################################################
# End of subscription Tab                                                         #
###################################################################################
