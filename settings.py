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


settings = QSettings('data/store.ini', QSettings.IniFormat)

USER_DATA_DEFAULT = {'username': '', 'cookie': None, 'subscription_key': ''}
BACKEND_DEFAULT_API_URL = 'https://api.instaschool.xyz/v1/'


class UserData:
    def __init__(self):
        self.data = settings.value(USER_DATA, USER_DATA_DEFAULT, dict)
        self.username = self.data.get('username', '')
        self.cookie = self.data.get('cookie', None)
        self.subscription_key = self.data.get('subscription_key', '')

    def set_username(self, username: str):
        self.data['username'] = username
        settings.setValue(USER_DATA, self.data)
        settings.sync()

    def set_cookie(self, cookie: dict):
        self.data['cookie'] = cookie
        settings.setValue(USER_DATA, self.data)
        settings.sync()

    def set_subscription_key(self, key):
        self.data['subscription_key'] = key
        settings.setValue(USER_DATA, self.data)
        settings.sync()


class APIBackendData:
    def __init__(self):
        self.API_URL = settings.value(API_BACKEND, BACKEND_DEFAULT_API_URL, str)

    @staticmethod
    def set_api_url(url: str):
        settings.setValue(API_BACKEND, url)
