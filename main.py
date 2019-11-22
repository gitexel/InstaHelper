import sys
from PyQt5 import QtWidgets

from login import LoginUi
from dashboard import DashBoardUi
from settings import UserData

user_data = UserData()

app = QtWidgets.QApplication(sys.argv)

if user_data.cookie:
    window = DashBoardUi()
else:
    window = LoginUi()

if __name__ == "__main__":
    sys.exit(app.exec_())
