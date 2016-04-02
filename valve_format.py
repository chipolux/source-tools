class Branch:
    def __init__(self, name, parent=None, is_file=False):
        self.name = name
        self.parent = parent
        self.is_file = is_file
        self.leaves = []
        self.branches = []

        if self.parent is not None:
            self.parent.add_branch(self)

    def add_branch(self, branch):
        if branch.parent != self:
            branch.parent = self

        if branch not in self.branches:
            self.branches.append(branch)

    def add_leaf(self, key, value):
        leaf = (key, value)
        if leaf not in self.leaves:
            self.leaves.append(leaf)

    def branches_by_name(self, name):
        return list(filter(lambda x: x.name == name, self.branches))

    def leaves_by_key(self, key):
        return list(filter(lambda x: x[0] == key, self.leaves))

    def serialize(self):
        if self.is_file:
            for leaf in self.leaves:
                yield '"{}"\t"{}"'.format(*leaf)
            for branch in self.branches:
                for line in branch.serialize():
                    yield line
        else:
            yield '"{}"\n'.format(self.name)
            yield '{\n'
            for leaf in self.leaves:
                yield '\t"{}"\t"{}"\n'.format(*leaf)
            for branch in self.branches:
                for line in branch.serialize():
                    yield '\t' + line
            yield '}\n'

    def __getattr__(self, name):
        branches = self.branches_by_name(name)
        if len(branches) > 1:
            raise AttributeError('Multiple branches named "{}"!'.format(name))
        elif len(branches) < 1:
            raise AttributeError('No branches named "{}"!'.format(name))
        else:
            return branches[0]

    def __repr__(self):
        return '<Branch(name={}, leaves={}, branches={})>'.format(
            self.name, len(self.leaves), len(self.branches)
        )


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
        # TODO: handle comment starting without a space after value
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
        # TODO: handle comment starting without a space after value
        value = line.split(maxsplit=1)[0]

    # Anything after the value can be discarded
    return key, value


with open('gameinfo.txt', 'r') as f:
    lines = f.readlines()

# Reduce file down to core data structure
parsed_lines = []
for line in lines:
    line = parse_line(line)
    if line is not None:
        parsed_lines.append(line)

# Build branches
root_branch = Branch(name='gameinfo.txt', is_file=True)
current_branch = root_branch
for line in parsed_lines:
    if isinstance(line, tuple):
        current_branch.add_leaf(*line)
    elif line == '{':
        # TODO: is stipping these opening quotes okay to do in parse_line?
        continue
    elif line == '}':
        # Closing branch, go back to parent
        current_branch = current_branch.parent
    else:
        current_branch = Branch(name=line, parent=current_branch)

with open('clean_gameinfo.txt', 'w') as f:
    f.writelines(root_branch.serialize())
