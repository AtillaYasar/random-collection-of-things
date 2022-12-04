import os, math, ast, sys, time, json

import sys
sys.path.append(os.getcwd() + '/PIL')


try:
    import PIL
except ImportError:
    name = 'Pillow'
    print(f"Trying to Install required module: {name}\n")
    os.system(f'python -m pip install {name}')

from PIL import Image, ImageDraw, ImageFont

try:
    import requests
except ImportError:
    name = 'requests'
    print(f"Trying to Install required module: {name}\n")
    os.system(f'python -m pip install {name}')
import requests

# the basic idea of this command line interface is summarized by this little loop:
'''
while True:
    i = input()  <-- store user input in i.
                     and in the terminal it moves the cursor one line down and leaves their input on the screen.
    then:
        1) write ansi code for moving the cursor up 1 line
        2) write ansi code for deleting a line
        3) do stuff with i.
        
    so you get the effect of running a command when enter is pressed.
'''

# note:
#   - in the looping, the collage_settings dictionary is basically being used as a global variable. annoying but idk how to fix


debug = False
inner_offset = 20
outer_offset = 40

def make_json(dic, filename):
    with open(filename, 'w', encoding="utf-8") as f:
        json.dump(dic, f, indent=2)
        f.close()

def open_json(filename):
    with open(filename, 'r', encoding="utf-8") as f:
        contents = json.load(f)
        f.close()
    return contents

def text_append(path, appendage):
    with open(path, 'a', encoding='utf-8') as f:
        f.write(appendage)

def text_create(path, content='', overwrite=True):
    if overwrite:
        mode = 'w'
    else:
        mode = 'x'
    with open(path, mode, encoding='utf-8') as f:
        f.write(content)

def text_read(fileName):
    with open(fileName, 'r', encoding='utf-8') as f:
        contents = f.read()
    return contents

class Progress_tracker:
    def __init__(self, total):
        self.total = total
        self.progress = 0
        
    def tick(self):
        self.progress += 1

    def show(self, extra=False, goodness=0):
        chars = len(str(self.total))
        s0 = '0'*(chars-len(str(self.progress))) + str(self.progress)
        s1 = str(self.total)
        change_note(f'{s0}/{s1}' + extra, goodness)

def checker(text, font, allowed_space):
    tw, th = get_text_dimensions(text, font)
    
    if tw > allowed_space:
        return False
    else:
        return True

def fix(text, font, allowed_space):
    success = False
    
    words = text.split(' ')
    for i in reversed(range(len(words))):
        joined = ' '.join(words[:i])
        if checker(joined, font, allowed_space):
            success = True
            break
    if success:
        rest = ' '.join(words[i:])
        return joined + '\n' + rest
    else:
        exit('could not fix')

def get_meta(img, keys=['prompt']):
    
    info = img.info
        
    lines = [] # <-- this will become the returned string, after a '\n'.join
    
    if 'Software' in info:
        if info['Software'] == 'NovelAI':
            prompt = info['Description']
            
            if keys == 'all':
                lines.append(f'prompt:{prompt}') # <-- append lines
            elif 'prompt' in keys:
                lines.append(f'prompt:{prompt}') # <-- append lines
                
            settings = ast.literal_eval(info['Comment'])
                
            for k,v in settings.items():
                if keys == 'all':
                    lines.append(f'{k}: {v}') # <-- append lines
                elif k in keys:
                    lines.append(f'{k}: {v}') # <-- append lines
        else:
            lines.append("couldn't find NAI metadata") # <-- append lines
    else:
        lines.append("couldn't find NAI metadata") # <-- append lines

    return '\n'.join(lines)# <-- return lines

def gridify_sequence(list_arg, columns):
    # takes a sequence and turns it into a 2d array
    subsets = []
    rows = len(list_arg)//columns
    for r in range(rows):
        # i dont fucking know
        subsets.append([*list_arg[r*columns:r*columns+columns]])
        i = r*columns+columns
        
    if len(list_arg) != rows*columns:
        subsets.append([*list_arg[i:]])
    return subsets

def get_text_dimensions(text_string, font):
    if text_string == '':
        return (0,0)
    
    ascent, descent = font.getmetrics()

    text_width = font.getmask(text_string).getbbox()[2]
    text_height = font.getmask(text_string).getbbox()[3] + descent

    return (text_width, text_height)

# for dealing with overlap of filenames. will perform name --> name(2), name(2) --> name(3), etc.
def adapt_filename(name):
    try:
        int(name.partition('(')[2].partition(')')[0])
    except:
        time.sleep(5)
        return name + '(2)'
    else:
        n = int(name.partition('(')[2].partition(')')[0])
        time.sleep(5)
        return name.replace(f'({n})', f'({n+1})')

# captions = {name:string, name:string, etc.}
def image_grid(img_array, name_array, collage_settings, captions):
    change_note('loading and processing images...', 0)
    input_folder = collage_settings['folder']
    # finds the width and height for a grid segment (minus offset), and how many rows and columns there should be
    widest = 0
    tallest = 0
    columns = 0
    rows = len(img_array)
    img_sizes = {}
    for i in range(len(img_array)):
        rowlength = len(img_array[i])
        if rowlength > columns:
            columns = rowlength
        for j in range(rowlength):
            w, h = img_array[i][j].size
            img_name = name_array[i][j]
            img_sizes[img_name] = (w,h)
            if w > widest:
                widest = w
            if h > tallest:
                tallest = h

    tolerance = collage_settings['factortolerance']
    resolutions = list(map(lambda t:t[0]*t[1], img_sizes.values()))
    av = sum(resolutions)/len(resolutions)
    if max(resolutions) >= av*tolerance:
        change_note(f'aborted because one image\'s resolution is too high. (average times {tolerance})', -1)
        return 0

    # make a blank black square
    grid_size = [columns*(widest+outer_offset)+outer_offset, rows*(tallest+outer_offset+outer_offset)+outer_offset+outer_offset]
    additional_height = 0

    # calculate additional height requirement from text
    # get a font
    # get a drawing context
    font = ImageFont.truetype("arial.ttf", size=collage_settings['fontsize'])
    itcounter = 0
    for name in captions.keys():
        #print(name)
        img_width = img_sizes[name][0]
        allowed_space = img_width
        if 1:
            while True:
                itcounter+=1
                fixed = True
                lines = captions[name].split('\n')
                for n, line in enumerate(lines):
                    if checker(line, font, allowed_space):
                        continue
                    else:
                        fixed = False
                        lines[n] = fix(line, font, allowed_space)
                        captions[name] = '\n'.join(lines)
                        break

                if fixed:
                    # go to the next name
                    tw, th = get_text_dimensions(captions[name], font)
                    height_addition = th*len(captions[name].split('\n'))
                    additional_height += height_addition + inner_offset
                    break
                else:
                    # keep fixing this name
                    continue
                    

    additional_height = int(round(additional_height/rows,0))
    
    grid_size[1] += additional_height
    blank = Image.new('RGB', size=grid_size)
    d = ImageDraw.Draw(blank) # "context" for doing stuff on the blank image

    pt = Progress_tracker(sum([len(row) for row in name_array]))

    # set starting location of text
    topleft = [0 + outer_offset, 0 + outer_offset]
    current_height = topleft[0]
    
    # put images in black square
    for i in range(len(img_array)):
        height_additions = []
        for j in range(len(img_array[i])):
            img = img_array[i][j]
            name = name_array[i][j]

            # draw text
            text = captions[name]
            drawloc = tuple((topleft[0],current_height))
            d.multiline_text(drawloc, text, font=font, fill=collage_settings['fontcolor'])

            # move topleft, movement is equal to text height
            tw, th = get_text_dimensions(text, font)
            text_height = th*len(text.split('\n'))
            height_additions.append(text_height)
            
            topleft[1] += height_addition + inner_offset

            # draw image and move topleft
            blank.paste(img, box=tuple((topleft[0],drawloc[1]+text_height)))
            
            topleft[0] += img.size[0] + outer_offset
            height_additions[-1] += img.size[1] + outer_offset
            
            pt.tick()
            pt.show('   (combining images...)', 0)
        
        current_height += max(height_additions)
        #break
        topleft[0] = 0 + outer_offset

    maxmb = collage_settings['maxsize']
    # log(f'\nimages combined\nnext task: save collage, try to get under {maxmb} mb')
    change_note(f'trying to get under {maxmb} mb', 0)

    # setting the name
    front = 'collage'
    tail = 'fullsize'
    name = '_'.join([front, tail])
    path = f'{input_folder}/{name}.png'
    
    '''
    # setting the name
    unavailable = os.listdir(collage_settings['folder'])
    front = 'collage'
    while True:
        tail = 'fullsize'
        name = '_'.join([front, tail])
        path = f'{input_folder}/{name}.png'
        if name+'.png' in unavailable:
            front = adapt_filename(front)
        else:
            break'''
    
    # attempting to get under the maxsize requirement
    blank.save(path, quality=95)
    mb = os.stat(f'{path}').st_size / (1024*1024)
    # portal 1 Megabyte is equal to 1048576 bytes (binary).
    
    if mb <= maxmb:
        change_note(f'succeeded at getting under {maxmb} mb', 1)
        return 1
    
    front = 'collage'
    for q in range(95, 5-1, -10):
        tail = f'compressed_quality{q}'
        name = '_'.join([front, tail])
        path = f'{input_folder}/{name}.jpg'
        '''
        # setting the name
        front = 'collage'
        while True:
            tail = f'compressed_quality{q}'
            name = '_'.join([front, tail])
            path = f'{input_folder}/{name}.png'
            if name+'.png' in unavailable:
                front = adapt_filename(front)
            else:
                break'''
        
        blank.save(path, quality=q)
        #unavailable.append(path)
        mb = os.stat(f'{path}').st_size / (1024*1024)
        
        if mb <= collage_settings['maxsize']:
            change_note(f'succeeded at getting under {maxmb} mb', 1)
            return 1

    change_note(f'failed at getting under {maxmb} mb', -1)
    return 0

def make_collage(collage_settings):
    columns = collage_settings['columns']
    keys = collage_settings['metadata']

    input_folder = collage_settings['folder']

    # get list of names, get list of image objects, get captions
    names = []
    imgs = []

    if 'captions.txt' not in os.listdir(input_folder):
        create_captions(input_folder)
    captions = get_captions(f'{input_folder}/captions.txt')
    
    for name in captions:
        if '.py' in name or 'collage' in name or '.txt' in name or '.json' in name:
            continue
        names.append(name)
        imgs.append(Image.open(f'{input_folder}/{name}'))
 
    # make 2d array of PIL.Image objects and names
    img_array = gridify_sequence(imgs, columns)#math.ceil(len(imgs)**0.5))
    name_array = gridify_sequence(names, columns)

    # log(f'\n{len(names)} images loaded. next task: combine images')


    
    # combine them in a grid and save the image in the same folder
    return image_grid(img_array, name_array, collage_settings, captions)

def get_captions(path):
    seperators = ('\n\n', '\n', ':')
    txt = text_read(path)

    namelist = os.listdir(collage_settings['folder'])
    
    captions = {}
    for section in txt.split(seperators[0]):
        lines = section.split(seperators[1])
        title = lines[0]
        if title not in namelist:
            continue
        if len(lines) == 1:
            captions[title] = 'no NAI metadata found'
        else:
            captions[title] = '\n'.join(lines[1:])

    return captions

# reads metadata of images in folder, writes it to captions.txt
def create_captions(folder, skip='all'):
    all_files = os.listdir(folder)
    
    # creates backup if necessary
    caption_path = folder + '/' + 'captions.txt'
    if 'captions.txt' not in all_files:
        text_create(caption_path, '')
    else:
        new_path = caption_path.replace('captions.txt','captions_backup.txt')
        if 'captions_backup.txt' in all_files:
            os.remove(new_path)
        os.rename(caption_path, new_path)
        text_create(caption_path, '')
        
    # for sorting by "number". the filename is: n=<number>_<restofname>   (because of how download.py works)
    def sorter(string):
        try:
            int(string.partition('=')[2].partition('_')[0])
        except:
            return -1
        else:
            return int(string.partition('=')[2].partition('_')[0])
        
    for n in sorted(all_files, key=sorter):
        ext = n.partition('.')[2]
        if 'collage' in n or ext in ['txt','py']:
            continue
        path = folder + '/' + n
        captions = get_meta(Image.open(path), skip)
        text_append(folder + '/' + 'captions.txt', n + '\n' + captions + '\n\n')
        
# returns an ansi escape sequence to color a string.  (ft is "first two", s is "string")
def col(ft, s):
    # black-30, red-31, green-32, yellow-33, blue-34, magenta-35, cyan-36, white-37
    u = '\u001b'
    numbers = dict([(string,30+n) for n, string in enumerate(('bl','re','gr','ye','blu','ma','cy','wh'))])
    n = numbers[ft]
    return f'{u}[{n}m{s}{u}[0m'

#make_collage(collage_settings, captions)

# write to the terminal
def write(*arg):
    if len(arg) == 1:
        sys.stdout.write(arg[0])
    else:
        for a in arg:
            sys.stdout.write(a)

# this returns a string which forms the "main square" of the command line interface.
    # it has 0) nice welcome message :D, 1) explanations, 2) current settings, 3) note/warning/progress comment
def get_main_square():
    # chr(3) is a heart
    # chr(25) is a downward arrow
    # chr(26) is a right arrow
    # col(first_2_letters_of_a_color,string) is that string in that color. i only have 8 colors though.
    lines = []
    ind = ' '*2
    edge = '-'*40

    lines.append('')
    lines.append(edge)
    lines.append('')
    lines.append(f'{ind}{ind}Welcome to {col("ma","collage.py")} {col("re",chr(3))}')
    lines.append('')

    lines.append(chr(25)*3 + col('cy',' how to use ') + chr(25)*3)
    lines.append(f'{ind}- if you don\'t have images yet, first use ' + col('ma','download.py'))
    lines.append(f'{ind}- pick a folder')
    lines.append(f'{ind}- for custom captions, create a captions file and edit it (optional)')
    lines.append(f'{ind}- create collage')
    lines.append('')

    lines.append(chr(25)*3 + col('cy',' commands ') + chr(25)*3 + f'{ind}{ind}(type it and press enter)')

    # this loop is fed: a list of tuples, each with 2 elements.
    # then it writes: {indentation}{element_1} {arrow_right} {element_2}
    for a,b in [(f'to create a {col("cy","collage")}', col('cy','create collage')),
                (f'to change {col("ye","collage settings")}', col('cy','<setting> <new_value>') + ' for example: ' + col('cy','folder images')),
                (f'for {col("cy","custom captions")}', col('cy','create captions') + f'    (redo this if you changed {col("ye","metadata")} in settings)')
                ]:
        if (a,b) == ('',''):
            lines.append('')
        else:
            lines.append(f'{ind}{a} -{chr(26)} {b}')

    # write the settings
    lines.append('')
    lines.append('collage settings:')
    for k,v in collage_settings.items():
        lines.append(f'{ind}{col("ye",k)}: {v}')
    lines.append('')

    # write the "note", which says if the settings are correct or not. then write the edge
    lines.append(validate_settings(collage_settings)[1])
    lines.append('')
    lines.append(edge)
    
    return '\n'.join(lines)

def get_settings_string():
    lines = []
    ind = ' '*2
    erase = f'{u}[2K'
    
    lines.append('collage settings:')
    for k,v in collage_settings.items():
        lines.append(erase + '\r' + f'{ind}{col("ye",k)}: {v}')
    return '\n'.join(lines)

# change a line that is {distance} lines up relative to cursor position, into {new_line}.
# how? by using ANSI codes for: move up, move down, delete line, move to start of line
# works because:
#   1) cursor position where user enters commands is constant
#   2) i hardcoded the (vertical) distance between that cursor position and specific lines in the "main square".
#   2.5) see dist_note and dist_settings below.
def change_line(distance, new_line):
    line_count = len(new_line.split('\n')) # to deal with multi-line line changes messing up the "move back down" part
    erase = f'{u}[2K' # writing this deletes a line
    if distance > 0:
        write(f'{u}[{distance}A') # move up
        write(erase)
        fl()
        write('\r') # move to start of line
        write(new_line)
        write(f'{u}[{distance-(line_count-1)}B') # move back down
        write('\r') # move to start of line

def change_note(new_note, goodness):
    if goodness == 0:
        new_line = 'note: ' + new_note
    elif goodness > 0:
        new_line = 'note: ' + col('gr',new_note)
    elif goodness < 0:
        new_line = 'note: ' + col('re',new_note)
    change_line(dist_note, new_line)
    fl()

def validate_settings(settings):
    # checks if settings are correct, then returns a note
    f = settings['folder']
    if f not in os.listdir(os.getcwd()):
        new_note = col('re',f'folder "{f}" is not in this directory')
        return (False, 'note: ' + new_note)
    return (True, 'note: ' + col('gr','settings are good'))

collage_settings = {'folder':'bugged',
                    'metadata':'prompt,steps,sampler,seed,strength,noise,scale,uc',
                    'columns':3,
                    'maxsize':32.0,
                    'fontsize':25,
                    'fontcolor':'white',
                    'factortolerance':2.0}
u = '\u001b'
fl = sys.stdout.flush
screenwidth = 100
screenheight = 32
os.system(f'mode con: cols={screenwidth} lines={screenheight}')  # sets terminal size and clears screen

write(get_main_square())
write('\n')

dist_note = 3
dist_settings = dist_note + 2 + len(collage_settings)

while True:
    i = input()
    write(f'{u}[1A') # up
    write(f'{u}[2K') # delete line

    words = i.split(' ')
    
    if len(words) == 2:
        if words[0] in collage_settings:
            collage_settings[words[0]] = words[1]

            # rewrite all of settings and note
            change_line(dist_settings, get_settings_string())
            change_line(dist_note, validate_settings(collage_settings)[1])
            #change_line(dist_settings-1, '  ' + col('ye',words[0]) + ': ' + words[1])

        elif i == 'create collage':
            # if settings are right:make collage, if not:create warning
            validation = validate_settings(collage_settings)
            if validation[0]:
                collage_settings['columns'] = int(collage_settings['columns'])
                collage_settings['fontsize'] = int(collage_settings['fontsize'])
                collage_settings['maxsize'] = float(collage_settings['maxsize'])
                collage_settings['factortolerance'] = float(collage_settings['factortolerance'])
                
                change_line(dist_note, 'note: ' + col('gr', 'started...'))
                make_collage(collage_settings)
            else:
                og = 'collage settings:'
                flashing = f'{u}[7m' + og + f'{u}[27m'
                
                change_line(dist_settings, flashing)
                time.sleep(0.3)
                change_line(dist_settings, og)
        elif i == 'create captions':
            validation = validate_settings(collage_settings)
            if validation[0]:
                create_captions(collage_settings['folder'], collage_settings['metadata'].split(','))
                change_line(dist_note, 'note: ' + col('gr','captions created'))
            else:
                change_line(dist_note, validation[1])












