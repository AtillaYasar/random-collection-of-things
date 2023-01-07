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

while True:
    print('-')
    print(col('cy', 'write a file name'))
    i = input()
    if i not in os.listdir():
        if i.partition('.')[2] == 'html':
            content = '\n'.join([
                '<html>',
                '<body>',
                '',
                '''<script src='...js' type='module'>''',
                '</script>',
                    '',
                '</body>',
                '</html>'
                ])
        else:
            content = ''
        text_create(i, content)
        print(col('gr',f'successfully created ') + f'{i}')
    else:
        print(col('re', 'cannot overwrite'))









