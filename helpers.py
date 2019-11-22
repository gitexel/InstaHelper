import time
import socket
import sys
import traceback
from urllib.request import urlopen
from PyQt5.QtCore import QObject, QRunnable, pyqtSignal, pyqtSlot
from PyQt5.QtGui import QPixmap, QImage
from errors import ChallengeError
from instagram_web_api.errors import ClientError
import webbrowser

REMOTE_SERVER = "www.google.com"


def check_instagram_errors(func):
    def decorator(*args, **kwargs):
        try:
            result = func(*args, **kwargs)
        except ChallengeError as ce:
            print(ce)
            webbrowser.open(ce.msg)
            return ce
        except ClientError as ce:
            print(ce)
            return ce

        return result

    return decorator


def img_from_url(url: str) -> QPixmap:
    try:
        data = urlopen(url).read()
        image = QImage()
        image.loadFromData(data)
    except ValueError:
        return QPixmap(QImage('src/profile_picture.jpg'))
    return QPixmap(image)


def validate_input(value: str = '') -> str:
    """
    :rtype: str
    :param value: string to be validate
    :return: validated string or empty if not valid
    """
    if not isinstance(value, str):
        return ''
    value = value.strip()
    if len(value) < 5:
        return ''

    return value


def is_connected(hostname):
    try:
        # see if we can resolve the host name -- tells us if there is
        # a DNS listening
        host = socket.gethostbyname(hostname)
        # connect to the host -- tells us if the host is actually
        # reachable
        s = socket.create_connection((host, 80), 2)
        s.close()
        return 1
    except:
        pass
    return 0


def check_internet_all_time(progress_callback):
    while True:
        progress_callback.emit(is_connected(REMOTE_SERVER))
        time.sleep(2)


class CheckConnectivity:
    def __init__(self):
        self.msg = ''

        self.check_net_worker = Worker(check_internet_all_time)
        # self.check_net_worker.signals.result.connect(self.l_result)
        # self.check_net_worker.signals.finished.connect(self._finished)
        self.check_net_worker.signals.progress.connect(self.process_result)

    def process_result(self, net_status):
        if net_status:
            self.msg = "You are connected to the Internet."
        else:
            self.msg = "You are not connected to the Internet."


class WorkerSignals(QObject):
    """
    Defines the signals available from a running worker thread.

    Supported signals are:

    finished
        No data

    error
        `tuple` (exctype, value, traceback.format_exc() )

    result
        `object` data returned from processing, anything

    progress
        `int` indicating % progress

    """
    finished = pyqtSignal()
    error = pyqtSignal(tuple)
    result = pyqtSignal(object)
    progress = pyqtSignal(object)


class Worker(QRunnable):
    """
    Worker thread

    Inherits from QRunnable to handler worker thread setup, signals and wrap-up.

    :param callback: The function callback to run on this worker thread. Supplied args and
                     kwargs will be passed through to the runner.
    :type callback: function
    :param args: Arguments to pass to the callback function
    :param kwargs: Keywords to pass to the callback function

    """

    def __init__(self, fn, *args, **kwargs):
        super(Worker, self).__init__()

        # Store constructor arguments (re-used for processing)
        self.fn = fn
        self.args = args
        self.kwargs = kwargs
        self.signals = WorkerSignals()

        # Add the callback to our kwargs
        self.kwargs['progress_callback'] = self.signals.progress

    @pyqtSlot()
    def run(self):
        """
        Initialise the runner function with passed args, kwargs.
        """

        # Retrieve args/kwargs here; and fire processing using them
        try:
            result = self.fn(*self.args, **self.kwargs)
        except:
            traceback.print_exc()
            exctype, value = sys.exc_info()[:2]
            self.signals.error.emit((exctype, value, traceback.format_exc()))
        else:
            self.signals.result.emit(result)  # Return the result of the processing
        finally:
            self.signals.finished.emit()  # Done
