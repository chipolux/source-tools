import os
import platform
import sys

from PyQt5.QtCore import Qt, QProcess, QProcessEnvironment
from PyQt5.QtWidgets import QApplication, QWidget, QListWidgetItem

from core.ui.launcher_ui import Ui_Launcher

from core.config import CONFIG
from core.utils import show_dialog

PLATFORM = platform.system()


def get_steam_apps_path():
    if PLATFORM == 'Windows':
        program_files = os.getenv('PROGRAMFILES(x86)')
        if program_files is None:
            # Running on 32 bit Windows
            program_files = os.getenv('PROGRAMFILES')
        path = os.path.join(program_files,  'Steam', 'steamapps', 'common')
    else:
        path = None

    return path


def find_hammer_instances():
    found_versions = []
    versions = filter(
        lambda x: x['platform'] == PLATFORM, CONFIG['hammer_versions']
    )

    steam_apps_path = get_steam_apps_path()

    for version in versions:
        version['path'] = os.path.join(steam_apps_path, *version['path'])

        if 'vproject' in version:
            version['vproject'] = os.path.join(
                steam_apps_path, *version['vproject']
            )

        if os.path.isfile(version['path']):
            found_versions.append(version)

    return found_versions


class Launcher(QWidget, Ui_Launcher):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setupUi(self)

        self.hammer_versions.itemClicked.connect(
            self.hammer_version_selected
        )
        self.hammer_versions.itemDoubleClicked.connect(self.open_hammer)
        self.open_hammer_button.clicked.connect(self.open_hammer)

        self.hammer_instance = QProcess(self)
        self.populate_hammer_list()

    def populate_hammer_list(self):
        for version in find_hammer_instances():
            item = QListWidgetItem(version['name'])
            item.setData(Qt.UserRole, version)
            self.hammer_versions.addItem(item)

    def hammer_version_selected(self, item):
        self.open_hammer_button.setEnabled(True)

    def get_selected_hammer_version(self):
        item = self.hammer_versions.currentItem()
        return item.data(Qt.UserRole)

    def open_hammer(self, *args):
        current_state = self.hammer_instance.state()
        if current_state == QProcess.NotRunning:
            version = self.get_selected_hammer_version()

            if 'vproject' in version:
                env = QProcessEnvironment.systemEnvironment()
                env.insert('VPROJECT', version['vproject'])
                self.hammer_instance.setProcessEnvironment(env)

            app_path = '"{}"'.format(version['path'])
            args = version.get('args', [])

            self.hammer_instance.start(app_path, args)
            self.hammer_instance.waitForStarted()
        else:
            show_dialog(
                title='Hammer Already Running',
                text='A Hammer instance is already running!',
                icon='Information',
                parent=self,
            )


if __name__ == '__main__':
    app = QApplication(sys.argv)
    app.setApplicationName('Source Tools Launcher')

    launcher = Launcher()
    launcher.show()

    app.exec_()
