# import re


class Branch:
    def __init__(self, name):
        self.name = name
        self._leaves = []
        self._branches = []

    def add_leaf(self, key, value):
        self._leaves.append((key, value))

    def add_branch(self, branch):
        self._branches.append(branch)


def parse_line(line):
    # Clean line and don't parse comment lines or empty lines
    line = line.strip()
    if line.startswith('//') or len(line) == 0:
        return None

    if line in ('{', '}'):
        # Line is entering a branch, previous line was branch name
        return line

    if line.startswith('"'):
        # Quoted string key
        line = line[1:]
        end_quote = line.find('"')
        key = line[0:end_quote]
        line = line[end_quote + 1:]
    else:
        # Unquoted string key
        try:
            key, line = line.split(maxsplit=1)
        except ValueError:
            # Key is all there is to this line, line is branch name
            return line

    if line == '':
        # Line was quoted branch name
        return key

    if line.startswith('"'):
        # Quoted string value
        line = line[1:]
        value = line[0:line.find('"')]
    else:
        # Unquoted string value
        value = line.split(maxsplit=1)[0]

    # Anything after the value can be discarded
    return key, value


with open('gameinfo.txt', 'r') as f:
    lines = f.readlines()

parsed_lines = []
for line in lines:
    line = parse_line(line)
    if line is not None:
        parsed_lines.append(line)

with open('clean_gameinfo.txt', 'w') as f:
    f.write('\n'.join(map(str, parsed_lines)))
