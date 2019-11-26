from PyQt5.QtCore import QSettings, QCoreApplication

ORGANIZATION_NAME = 'InstaSchool App'
ORGANIZATION_DOMAIN = 'instaschool.xyz'
APPLICATION_NAME = 'InstaHelper'
APPLICATION_VERSION = 'v0.1@Beta'
SETTINGS_TRAY = 'settings/tray'
USER_DATA = 'user/data'
API_BACKEND = 'BACKEND/api_url'

QCoreApplication.setApplicationName(ORGANIZATION_NAME)
QCoreApplication.setOrganizationDomain(ORGANIZATION_DOMAIN)
QCoreApplication.setApplicationName(APPLICATION_NAME)
QCoreApplication.setApplicationVersion(APPLICATION_VERSION)

#
# settings = QSettings('data/store.ini',
#                      QSettings.IniFormat)
# settings.setValue(SETTINGS_TRAY, 'hellodddd')
# settings.setValue(USER_TRAY, {'username': 'instexel', 'cookie': co, 'subscription': ''})
# settings.sync()


USER_DATA_DEFAULT = {'username': '', 'cookie': None, 'subscription_key': ''}
# BACKEND_DEFAULT_API_URL = 'https://api.instaschool.xyz/v1/'
BACKEND_DEFAULT_API_URL = 'http://127.0.0.1:8000/v1/'

settings = QSettings('data/store.ini', QSettings.IniFormat)


class UserData:
    def __init__(self):
        self.settings = QSettings('data/store.ini', QSettings.IniFormat)
        self.data = self.settings.value(USER_DATA, USER_DATA_DEFAULT, dict)
        self.username = self.data.get('username', '')
        self.cookie = self.data.get('cookie', {})
        self.subscription_key = self.data.get('subscription_key', '')

    def refresh_settings(self):
        self.settings = QSettings('data/store.ini', QSettings.IniFormat)
        self.data = self.settings.value(USER_DATA, USER_DATA_DEFAULT, dict)

    def get_username(self, refresh_settings=True) -> str:
        if refresh_settings:
            self.refresh_settings()
        return self.data.get('username', '')

    def get_cookie(self, refresh_settings=True) -> dict:
        if refresh_settings:
            self.refresh_settings()

        return self.data.get('cookie', None)

    def get_subscription_key(self, refresh_settings=True) -> str:
        if refresh_settings:
            self.refresh_settings()
        return self.data.get('subscription_key', '')

    def set_username(self, username: str):
        self.username = username
        self.data['username'] = username
        self.settings.setValue(USER_DATA, self.data)
        self.settings.sync()

    def set_cookie(self, cookie: dict):
        self.cookie = cookie
        self.data['cookie'] = cookie
        self.settings.setValue(USER_DATA, self.data)
        self.settings.sync()

    def set_subscription_key(self, key):
        self.subscription_key = key
        self.data['subscription_key'] = key
        self.settings.setValue(USER_DATA, self.data)
        self.settings.sync()


class APIBackendData:
    def __init__(self):
        self.settings = QSettings('data/store.ini', QSettings.IniFormat)
        self.api_url = self.settings.value(API_BACKEND, BACKEND_DEFAULT_API_URL, str)

    def set_api_url(self, url: str):
        self.settings.setValue(API_BACKEND, url)
