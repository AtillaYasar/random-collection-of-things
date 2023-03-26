import os, sys

def text_append(path, appendage):
    with open(path, 'a', encoding='utf-8') as f:
        f.write(appendage)

def text_create(path, content=''):
    with open(path, 'w', encoding='utf-8') as f:
        f.write(content)

def text_read(fileName):
    with open(fileName, 'r', encoding='utf-8') as f:
        contents = f.read()
    return contents

# returns an ansi escape sequence to color a string.  (ft is "first two", s is "string")
def col(ft, s):
    # black-30, red-31, green-32, yellow-33, blue-34, magenta-35, cyan-36, white-37
    u = '\u001b'
    numbers = dict([(string,30+n) for n, string in enumerate(('bl','re','gr','ye','blu','ma','cy','wh'))])
    n = numbers[ft]
    return f'{u}[{n}m{s}{u}[0m'

default_py = '''
"""
import sys, json, copy, time, requests, os
import tkinter as tk

# my own modules
## make available for import
with open('module_path.txt', 'r') as f:
    module_path = f.read()  # ../code_library
sys.path.append(module_path)
## then import
from examples.draggable_circles import DraggableCircle
from general_utils.for_colors import col
from general_utils.misc import Recursion, HierarchyItem, message, is_empty
from tkinter_utils.class_extensions import MyText


def col(ft, s):
    """For printing text with colors.
    
    Uses ansi escape sequences. (ft is "first two", s is "string")"""
    # black-30, red-31, green-32, yellow-33, blue-34, magenta-35, cyan-36, white-37
    u = '\u001b'
    numbers = dict([(string,30+n) for n, string in enumerate(('bl','re','gr','ye','blu','ma','cy','wh'))])
    n = numbers[ft]
    return f'{u}[{n}m{s}{u}[0m'


"""
'''[1:-1]

default_html = '''
<html>
<body>

<script src='...js' type='module'>
</script>

</body>
</html>
'''[1:-1]

base_level = ''

default_defaults = {
    'py':default_py,
    'html':default_html,
}
custom_default_files = {
    'py':'make_something_defaultpy.txt',
}
#custom_default_files = {k:v for k,v in custom_default_files.items() if os.path.isfile(v) == True}  # validation

def get_default(ext):
    """First try custom_default, then default_default, then resort to base_level."""
    
    base_level = ''
    if ext in custom_default_files.keys():
        path = custom_default_files[ext]
        if os.path.isfile(path):
            finding = text_read(path)
        else:
            finding = None
    elif ext in default_defaults[ext]:
        finding = default_defaults[ext]
    else:
        finding = None
    
    if finding == None:
        return base_level
    else:
        return finding

while True:
    print('-')
    for line in [
        'to make custom default files, put them in these filenames:',
        '-'*10,
        '\n'.join([
            f'extension:{k}, path:{v}' for k,v in custom_default_files.items()
        ]),
        '-'*10,
        col('cy', 'write a file name'),
    ]:
        print(line)
    print()

    print()
    i = input()
    if i not in os.listdir():
        ext = i.split('.')[-1]
        content = get_default(ext)
        text_create(i, content)
        print(col('gr',f'successfully created ') + f'{i}')
    else:
        print(col('re', 'cannot overwrite'))
