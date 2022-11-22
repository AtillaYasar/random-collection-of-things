import os, sys, random, time, json

debug = False  # not using this yet.
error_log = ''

# what is this program?
# 1) just run it and see.
# 2) a command line interface (for playing TTRPG), for asking questions to an oracle, which randomly gives 1 of 6 answers
# 3) the three key functions are
#   - write, which calls sys.stdout.write (which writes to the terminal)
#   - input(), which gets user input
#   - change_line, which if given a distance and string:
#       --> moves the cursor up that distance, changes the line to that string, moves back down

# neat features: pretty colors, storing stuff, flashing effects

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

# write to the terminal
def write(*arg):
    if len(arg) == 1:
        sys.stdout.write(arg[0])
    else:
        for a in arg:
            sys.stdout.write(a)

# create ansi escape sequence
def code(c, s):
    u = '\u001b'
    return f'{u}{c}{s}{u}[0m'

# returns an ansi escape sequence to color a string.  (ft is "first two", s is "string")
def col(ft, s):
    # black-30, red-31, green-32, yellow-33, blue-34, magenta-35, cyan-36, white-37
    u = '\u001b'
    numbers = dict([(string,30+n) for n, string in enumerate(('bl','re','gr','ye','blu','ma','cy','wh'))])
    n = numbers[ft]
    return f'{u}[{n}m{s}{u}[0m'

def get_main_square():
    lines = []
    ind = ' '*2
    edge = '-'*40

    lines.append(edge)
    lines.append('')
    lines.append(f'{ind}{ind}Welcome to {col("ma","Oracle")} {col("re",chr(3))}')
    lines.append('')
    lines.append('')
    lines.append(f'autosave {autosave}')
    lines.append('')
    lines.append(chr(25)*3 + ' how to use ' + chr(25)*3)
    lines.append('')    
    
    for a,b in [(f'to ask a {col("cy","question")}','end with a ' + col("cy","?question mark?") + '   (it will randomly say yes/no, and/./but)'),
                (f'to add an {col("cy","interpretation")}','end with a ' + col('cy','.period.')),
                ('',''),
                (f'to toggle {col("cy","autosave")}',col('cy','"autosave on/off"')),
                (f'for {col("cy","custom tables")}',col('cy','"custom tables"') + ' and look in the folder, then ' + col('cy','"set tables"')),
                (f'to get {col("cy","previous/next")}' + ' commands',col('cy',chr(24)) + '/' + col('cy',chr(25)))]:
        if (a,b) == ('',''):
            lines.append('')
        else:
            lines.append(f'{ind}{a} -{chr(26)} {b}')
        
    #lines.append(f'{col("cy","note: ")}write something ending with {col("cy","?question mark?")} then --> then {col("cy","enter")}')
    lines.append(f'')
    for string in ['q', 'a', 'i']:
        lines.append(col("cy",string + ':'))
    lines.append(f'')
    lines.append(edge)
    
    return '\n'.join(lines)

# change a line that is {distance} lines up, into {new_line}
def change_line(distance, new_line):
    erase = f'{u}[2K' # delete line
    if distance >= 0:
        write(f'{u}[{distance}A') # move up
        write(erase)
        write('\r') # move to start of line
        write(new_line)
        write(f'{u}[{distance}B') # move back down
        write('\r') # move to start of line

# change autosave setting and make it flash in the display
def set_autosave(string):
    global autosave  # ewwwwwwwwwww it's a global variabllllllllllllllllllle
    autosave = string
    new_line = f'autosave {string}'
    change_line(autosave_dist, f'autosave {u}[7m{string}{u}[0m')
    time.sleep(0.3)
    change_line(autosave_dist, new_line)

def roll(table_title):
    t = tables[table_title]
    choice = random.choice(list(t.keys()))
    return t[choice]

# parses oracle_custom.txt to get "rolling tables". plus some checks to head off some weird situations.
def set_tables():
    global tables  # !!booooooooooo!! global variables eeeeeeeeeeewwwwwwwwwwwwwwwwwwww

    default_table = {str(n+1):string for n, string in enumerate(['No, and...','No.','No, but...','Yes, but...','Yes.','Yes, and...'])}
    
    if 'oracle_custom.txt' in os.listdir(os.getcwd()):
        sections = text_read('oracle_custom.txt').split('\n\n')
        pre_tables = {}
        for s in sections:
            lines = s.split('\n')
            if len(lines) < 2:
                continue
            title = lines[0]
            if title == 'help':
                continue
            
            pre_tables[title] = {}
            for line in lines[1:]:
                n, _, string = line.partition(' ')
                
                # storage might get weird if it's not stringable. not forcing int(n) because it might be funny to use non-integers
                try:
                    str(n)
                except:
                    continue
                else:
                    pre_tables[title][n] = string

        # cutting out weird things and getting the real tables dictionary
        tables = {}
        for title, table in pre_tables.items():
            if title == '' or table == {}:
                continue
            tables[title] = {}

            for n, string in table.items():
                if string == '':
                    continue
                tables[title][n] = string

        if 'default' not in tables:
            tables['default'] = default_table
    else:
        tables = {'default':default_table}
    if tables['default'] != default_table:
        animation_parameters['do'] = True

u = '\u001b'
fl = sys.stdout.flush
screenwidth = 100
screenheight = 25
os.system(f'mode con: cols={screenwidth} lines={screenheight}')  # this will also clear the screen
autosave = 'on'
data = {}

# variables for how far up things are relative to the cursor position.
    # because 1) to call change_line, 2) there is no automated system for keeping track of what is where
q_dist = 5
a_dist = 4
i_dist = 3
how_distance = 14
autosave_dist = 16
oracle_dist = 19
animation_parameters = {'do':False}
set_tables()

def loop():
    '''
the basic logic:

- use i = input() to ask for input and store it in i, then move the cursor up and delete the line (with ANSI stuff)

if i ends with a question mark:
    --> - call change_q, which will create a new entry in the data dictionary and (use cursor ANSI stuff to) change the display
        - write to oracle.txt if autosave == 'on'
if i ends with a dot:
    --> - call change_i, which update data[q]['i'] and (use cursor control ANSI stuff to) change the display
        - write to oracle.txt if autosave == 'on'
if i is "autosave on" or "autosave off":
    --> - set the autosave string to on or off  (which decides whether the program writes to oracle.txt)
        - change "autosave on/off" in the display

'''

    def change_q(q):
        data[q] = {'a':'', 'i':''}
        interp = data[q]['i']
        change_line(q_dist, f'{col("cy","q:")} {q}')
        change_line(i_dist, f'{col("cy","i:")} {interp}')

    def change_a(q, a):
        data[q]['a'] = a
        change_line(a_dist, f'{col("cy","a:")} {a}')

    def change_i(q, interp):
        data[q]['i'] = interp
        change_line(i_dist, f'{col("cy","i:")} {interp}')
    
    #write(f'{u}[0m') # reset any effects that may be present

    # write the main square, which puts the cursor at the end of dashes, then 2 newliens and 1 up, to keep vertical spacing consistent
    write(get_main_square())
    write('\n\n')
    write(f'{u}[1A')

    reset = False
    while True:
        # make_json(data, 'data.json')  <-- for febugging/future features

        # store input, remove input and put cursor back where it was
        i = input()
        write(f'{u}[1A') # up
        write(f'{u}[2K') # delete

        if len(i) < 2:
            continue

        if i.split(' ')[0] == 'autosave':
            if i == 'autosave on' or i == 'autosave off':
                set_autosave(i.split(' ')[1])
        elif '?' in i:
            # make new data entry, and answer the question
            
            if i[-1] == '?':
                table_title = 'default'
                q = i
            else:
                # to deal with a question mark being inside of the question
                table_title = i.split('?')[-1]
                if table_title not in tables:
                    table_title = 'default'
                q = '?'.join(i.split('?')[:-1]) + '?'
                    
            a = roll(table_title)
            
            change_q(q)
            change_a(q, a)
            interp = data[q]['i']

            addition = '\n\n' + '\n'.join(['q: '+q, 'a: '+a, 'i: '+interp])
            if autosave == 'on':
                if 'oracle.txt' not in os.listdir(os.getcwd()):
                    text_create('oracle.txt', f'Oracle answers{addition}')
                else:
                    text_append('oracle.txt', addition)
        elif i[-1] == '.':
            try:
                data[q]
            except:
                pass
            else:
                interp = i
                a = data[q]['a']
                
                change_i(q, interp)

                addition = '\n\n' + '\n'.join(['q: '+q, 'a: '+a, 'i: '+interp])
                if autosave == 'on':
                    if 'oracle.txt' not in os.listdir(os.getcwd()):
                        text_create('oracle.txt', f'Oracle answers{addition}')
                    else:
                        text_append('oracle.txt', addition)
        elif i == 'custom tables':
            if 'oracle_custom.txt' not in os.listdir(os.getcwd()):
                lines = []
                lines.append('help')
                lines.append('  - to create a custom table')
                lines.append('    --> write its name, then "<something> <response>" on new lines (see default)')
                lines.append('    --> seperate tables with a double newline (like between help and default)')
                lines.append('    --> to register a change to the txt, restart the app')
                lines.append('  - to use a custom table in the app')
                lines.append('    --> write its name in the command after the question mark')
                lines.append('    --> for example: "did the creator of this app overexplain everything?snarky"')
                lines.append('  - you can change the default')
                lines.append('  - https://homebrewery.naturalcrit.com/share/rkmo0t9k4Q shows how to play a solo game with an oracle and other cool stuff (no paywall, also not mine)')
                lines.append('')
                lines.append('default')
                for k,v in tables['default'].items():
                    lines.append(f'{k} {v}')

                content = '\n'.join(lines)
                text_create('oracle_custom.txt', content)
        elif i == 'set tables':
            # changes the "tables" dictionary, and changes "Oracle <3" with special CGI cinematic effects . (see the "else" branch below for more on that)
            
            set_tables()

            if animation_parameters['do']:
                ind = ' '*2
                original = f'{ind}{ind}Welcome to {col("ma","Oracle")} {col("re",chr(3))}'
                
                flashing = original.replace(f'{col("ma","Oracle")} {col("re",chr(3))}', f'{u}[7m{col("ma","Oracle")} {col("wh",chr(3))}{u}[27m')
                flash_speed = 0.2
                for i in range(3):
                    change_line(oracle_dist, flashing)
                    time.sleep(flash_speed)
                    fl() # its good to flush sometimes
                    change_line(oracle_dist, original)
                    time.sleep(flash_speed)

                new = f'{ind}{ind}Welcome to {col("ye","Your Personal Servant")} {col("gr",chr(2))}'
                change_line(oracle_dist, new)
                
                animation_parameters['do'] = False
            
        else:
            # flash the downward arrows in the "how to use" line, by:
                # - calling change_line
                # - [7m escape code to do "inverse mode"
                # - wait
                # - put mode back with [27m escape code
            #note_line = f'{col("cy","note: ")}write something ending with {col("cy","?question mark?")} then --> then {col("cy","enter")}'

            original = chr(25)*3 + ' how to use ' + chr(25)*3
            new = original.replace(chr(25)*3, f'{u}[7m' + chr(25)*3 + f'{u}[27m')
            change_line(how_distance, new)
            time.sleep(0.3)
            fl() # its good to flush sometimes
            change_line(how_distance, original)


def make_json(dic, filename):
    with open(filename, 'w', encoding="utf-8") as f:
        json.dump(dic, f, indent=2)
        f.close()

if __name__ == '__main__':
    loop()



