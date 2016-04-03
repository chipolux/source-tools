import os
import sys

from PyQt5.QtCore import Qt, QProcess, QProcessEnvironment
from PyQt5.QtWidgets import QApplication, QWidget, QListWidgetItem

from core.ui.launcher_ui import Ui_Launcher

from core.config import CONFIG
from core.utils import show_dialog


def get_steam_apps_path():
    program_files = os.getenv('PROGRAMFILES(x86)')
    if program_files is None:
        # Running on 32 bit Windows
        program_files = os.getenv('PROGRAMFILES')
    path = os.path.join(program_files,  'Steam', 'steamapps', 'common')

    return path


def get_available_toolsets():
    available_toolsets = []

    for toolset in CONFIG['toolsets']:
        toolset = build_toolset_paths(toolset)

        if os.path.isfile(toolset['hammer_path']):
            available_toolsets.append(toolset)

    return available_toolsets


def build_toolset_paths(toolset):
    apps_path = get_steam_apps_path()

    toolset['root_path'] = os.path.join(apps_path, *toolset['root_path'])
    toolset['bin_path'] = os.path.join(toolset['root_path'], 'bin')
    toolset['gameinfo_dir'] = os.path.join(
        toolset['root_path'], toolset['gameinfo_dir']
    )
    game_arg = '-game "{}"'.format(toolset['gameinfo_dir'])

    toolset['hammer_path'] = os.path.join(toolset['bin_path'], 'hammer.exe')

    toolset['viewer_path'] = os.path.join(toolset['bin_path'], 'hlmv.exe')
    toolset.setdefault('viewer_args', [])
    toolset['viewer_args'].append(game_arg)

    toolset['poser_path'] = os.path.join(toolset['bin_path'], 'hlfaceposer.exe')
    toolset.setdefault('poser_args', [])
    toolset['poser_args'].append(game_arg)

    return toolset


class Launcher(QWidget, Ui_Launcher):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setupUi(self)

        self.toolset = None
        self.populate_toolset_list()
        self.toolset_list.itemClicked.connect(self.toolset_selected)

        self.open_hammer_button.clicked.connect(self.open_hammer)
        self.hammer_instance = QProcess(self)

        self.open_viewer_button.clicked.connect(self.open_viewer)
        self.viewer_instance = QProcess(self)

        self.open_poser_button.clicked.connect(self.open_poser)
        self.poser_instance = QProcess(self)

    def populate_toolset_list(self):
        for toolset in get_available_toolsets():
            item = QListWidgetItem(toolset['name'])
            item.setData(Qt.UserRole, toolset)
            self.toolset_list.addItem(item)

    def toolset_selected(self, item):
        self.toolset = item.data(Qt.UserRole)
        self.open_hammer_button.setDisabled(True)
        self.open_viewer_button.setDisabled(True)
        self.open_poser_button.setDisabled(True)

        if os.path.isfile(self.toolset['hammer_path']):
            self.open_hammer_button.setEnabled(True)
        if os.path.isfile(self.toolset['viewer_path']):
            self.open_viewer_button.setEnabled(True)
        if os.path.isfile(self.toolset['poser_path']):
            self.open_poser_button.setEnabled(True)

    def open_app(self, instance, path, args, vproject):
        current_state = instance.state()
        if current_state == QProcess.NotRunning:
            env = QProcessEnvironment.systemEnvironment()
            env.insert('VPROJECT', vproject)
            instance.setProcessEnvironment(env)
            instance.start('"{}"'.format(path), args)
            instance.waitForStarted()
        else:
            show_dialog(
                title='Instance Already Running',
                text='A instance of that app is already running!',
                icon='Information',
                parent=self,
            )

    def open_hammer(self):
        self.open_app(
            self.hammer_instance,
            self.toolset['hammer_path'],
            self.toolset.get('hammer_args', []),
            self.toolset['gameinfo_dir'],
        )

    def open_viewer(self):
        self.open_app(
            self.viewer_instance,
            self.toolset['viewer_path'],
            self.toolset.get('viewer_args', []),
            self.toolset['gameinfo_dir'],
        )

    def open_poser(self):
        self.open_app(
            self.poser_instance,
            self.toolset['poser_path'],
            self.toolset.get('poser_args', []),
            self.toolset['gameinfo_dir'],
        )


if __name__ == '__main__':
    app = QApplication(sys.argv)
    app.setApplicationName('Source Tools Launcher')

    launcher = Launcher()
    launcher.show()

    app.exec_()
