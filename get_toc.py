import os

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

ind = '  '
while True:
    # let user choose a .md file
    options = [f for f in os.listdir() if '.md' in f]
    
    for n, md in enumerate(options):
        print(col('cy',n) + f': {md}')
    i = input(f'Write a {col("cy","number")} and hit enter to get the {col("gr","table of contents")}        (wait it\'s not actually a table{col("ma","??!")})\n')
    try:
        options[int(i)]
    except:
        i = None
        print(col('re','use correct input plz'))
        continue
    else:
        choice = options[int(i)]

    print('you chose:', col('cy',choice))
    # show table of contents in .md
    print(f'\n{col("gr","table of contents")}')
    print('```')
    docstarted = False
    for line in text_read(choice).split('\n'):
        if line == '(start)':
            docstarted = True
        if not docstarted:
            continue
        
        if len(line) == 0:
            continue
        else:
            if line[0] == '#':
                print(ind*(line.count('#')-1) + line)
    if not docstarted:
        print(f'{col("re","yo:")} you need a line in your {col("cy",".md")} file that only has {col("cy","(start)")} in it')
    print('```')

    print('\n\n\n')
    just_waiting = input('hit enter to go again\n')
