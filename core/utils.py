from PyQt5.QtWidgets import QMessageBox


def show_dialog(title, text, icon='Information', details=None, parent=None):
    dialog = QMessageBox(parent)
    dialog.setWindowTitle(title)
    dialog.setText(text)

    icons = {
        'NoIcon': QMessageBox.NoIcon,
        'Question': QMessageBox.Question,
        'Information': QMessageBox.Information,
        'Warning': QMessageBox.Warning,
        'Critical': QMessageBox.Critical,
    }
    dialog.setIcon(icons.get(icon, QMessageBox.NoIcon))

    if details is not None:
        dialog.setDetailedText(details)

    return dialog.exec_()
