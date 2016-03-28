import os
import subprocess


ON_WINDOWS = os.name == 'nt'
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
APP_DIR = os.path.dirname(SCRIPT_DIR)


def find_designer_files():
    ui_files = []
    qrc_files = []

    for dirpath, dirnames, filenames in os.walk(APP_DIR):
        if SCRIPT_DIR in dirpath:
            continue

        for filename in filenames:
            if filename.endswith('.ui'):
                ui_files.append({'file': filename, 'dir': dirpath})
            elif filename.endswith('.qrc'):
                qrc_files.append({'file': filename, 'dir': dirpath})

    return ui_files, qrc_files


def compile_files():
    print('\tFinding UI and QRC files...')
    ui_files, qrc_files = find_designer_files()

    print('\tCompiling {} UI files...'.format(len(ui_files)))
    for ui_file in ui_files:
        compile_ui_file(ui_file)

    print('\tCompiling {} QRC files...'.format(len(qrc_files)))
    for qrc_file in qrc_files:
        compile_qrc_file(qrc_file)


def compile_ui_file(ui_file):
    input_file = os.path.join(ui_file['dir'], ui_file['file'])
    output_file = os.path.splitext(input_file)[0] + '_ui.py'

    command = ['pyuic5', input_file]
    output = subprocess.check_output(command, shell=ON_WINDOWS)

    output = fix_resource_imports(output)

    with open(output_file, 'wb') as f:
        f.write(output)


def fix_resource_imports(file_contents):
    linesep = os.linesep.encode('utf-8')
    lines = file_contents.split(linesep)

    for n, line in enumerate(lines):
        if line.startswith(b'import ') and line.endswith(b'_rc'):
            lines[n] = b'from . ' + line

    return linesep.join(lines)


def compile_qrc_file(qrc_file):
    input_file = os.path.join(qrc_file['dir'], qrc_file['file'])
    output_file = os.path.splitext(input_file)[0] + '_rc.py'

    command = ['pyrcc5', input_file, '-o', output_file]
    subprocess.check_call(command, shell=ON_WINDOWS)


if __name__ == '__main__':
    compile_files()
