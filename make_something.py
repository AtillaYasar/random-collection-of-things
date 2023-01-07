import os

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

while True:
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
        print(f'successfully created {i}')
    else:
        print('cannot overwrite')









