import os, sys, json

# returns an ansi escape sequence to color a string.  (ft is "first two", s is "string")
def col(ft, s):
    # black-30, red-31, green-32, yellow-33, blue-34, magenta-35, cyan-36, white-37
    u = '\u001b'
    numbers = dict([(string,30+n) for n, string in enumerate(('bl','re','gr','ye','blu','ma','cy','wh'))])
    n = numbers[ft]
    return f'{u}[{n}m{s}{u}[0m'

def make_json(dic, filename):
    with open(filename, 'w', encoding="utf-8") as f:
        json.dump(dic, f, indent=2)
        f.close()

def open_json(filename):
    with open(filename, 'r', encoding="utf-8") as f:
        contents = json.load(f)
        f.close()
    return contents

'''
the code block below does:
- makes the colors dictionary, which defines the color that files of the given type are shown as
- check stuff with asserts

you can create custom color mappings:
- make a json file named run_something.json
- choose one of colors as shown in the col function's commentary
- write the first 2 letters of a color as the value corresponding to an extension (except for blu and bl, they are blue and black, lol)
'''
colors_filename = 'run_something.json'
if colors_filename in os.listdir():
    colors = open_json(colors_filename)
else:
    colors = {
        'html':'re',
        'css':'re',
        'js':'ye',
        'py':'blu',
        'json':'cy',
        'png':'ma',
        'jpeg':'ma',
        'jpg':'ma',
        'txt':'gr',
        'unspecified':'wh'
        }
assert type(colors) == dict
assert 'unspecified' in colors
for k,v in colors.items():
    assert type(v) == str
    assert v in ('bl','re','gr','ye','blu','ma','cy','wh')

while True:
    files = os.listdir()
    for i,f in enumerate(files):
        ext = f.partition('.')[2]
        if ext in colors:
            first_two = colors[ext]
        else:
            first_two = colors['unspecified']
        colored_f = col(first_two, f)
        print(f'{i} {colored_f}')
    print('type a number to run that file')
    i = input()
    try:
        files[int(i)]
    except:
        print('invalid input')
        input()
    else:
        f = files[int(i)]
        ext = f.partition('.')[2]
        if ext in colors:
            first_two = colors[ext]
        else:
            first_two = colors['unspecified']
        colored_f = col(first_two, f)
        
        print('[output from ' + colored_f + ']')
        os.system(f'python {f}')
        print('[/output]')
    print()
    print('hit enter to go again')
    input()
        
