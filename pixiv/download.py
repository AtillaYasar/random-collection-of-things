import os, time, sys, copy

try:
    import PIL
except ImportError:
    name = 'Pillow'
    print(f"Trying to Install required module: {name}\n")
    os.system(f'python -m pip install {name}')
from PIL import Image

try:
    import requests
except ImportError:
    name = 'requests'
    print(f"Trying to Install required module: {name}\n")
    os.system(f'python -m pip install {name}')
import requests

debug = False

def get_urls(url):
    ID = url.split('/')[-1]
    api_url = f'https://www.pixiv.net/ajax/illust/{ID}/pages?lang=en'
    
    urls = []
    result = requests.get(api_url, headers = {'Referer': 'http://www.pixiv.net/'})
    b = result.json()['body']
    for d in b:
        urls.append(d['urls']['original'])
    return urls

def pixiv_download(url, path):
    result = requests.get(url, headers = {'Referer': 'http://www.pixiv.net/'})

    if debug:
        print(result)
    content = result.content

    if debug:
        print(content)
    
    image = content
    with open(path, 'wb') as f:
        f.write(image)
        image = Image.open(path)
        '''if get_meta(image) == 'not a NAI image':
            print('not NAI image')
            print(url)
            exit()'''
        f.close()

class Progress_tracker:
    def __init__(self, total):
        self.total = total
        self.progress = 0
        
    def tick(self):
        self.progress += 1

    def show(self, extra=False):
        chars = len(str(self.total))
        s0 = '0'*(chars-len(str(self.progress))) + str(self.progress)
        s1 = str(self.total)
        if extra:
            return f'{s0}/{s1}{extra}'
        else:
            return f'{s0}/{s1}'

#pt = Progress_tracker(len(urls))  # simple object for printing the progress
def download(url, folder):
    if folder == '<random>':
        alphabet = 'abcdefghijklmnopqrstuvwxyz'
        files = os.listdir(os.getcwd())
        n = 1
        while True:
            for letter in alphabet:
                if letter*n not in files:
                    name = letter*n
                    break
            if name not in files:
                break
        folder = name
        dl_settings['folder'] = name
    if folder not in os.listdir(os.getcwd()):
        os.mkdir(folder)
    urls = get_urls(url)
    pt = Progress_tracker(len(urls))
    to_print = 'note: ' + pt.show('  (downloading images...)')
    change_line(dist_to_note, to_print)
    for n, url in enumerate(urls):
        timestamp = str(time.time()).replace('.', '-')
        filename = f'n={n}_{timestamp}.png'
        path = f'{folder}/{filename}'
        pixiv_download(url, path)  # uses a special header to allow downloading without login
        pt.tick()
        to_print = 'note: ' + pt.show('  (downloading images...)')
        change_line(dist_to_note, to_print)

def write(*arg):
    if len(arg) == 1:
        sys.stdout.write(arg[0])
    else:
        for a in arg:
            sys.stdout.write(a)

def code(c, s):
    u = '\u001b'
    return f'{u}{c}{s}{u}[0m'

# black-30, red-31, green-32, yellow-33, blue-34, magenta-35, cyan-36, white-37
def col(ft, s):
    u = '\u001b'
    numbers = dict([(string,30+n) for n, string in enumerate(('bl','re','gr','ye','blu','ma','cy','wh'))])
    n = numbers[ft]
    return f'{u}[{n}m{s}{u}[0m'

u = '\u001b'
fl = sys.stdout.flush
screenwidth = 100
screenheight = 25
os.system(f'mode con: cols={screenwidth} lines={screenheight}')

def get_defaults():
    dl_settings = {'folder':'<random>',
                   'url':'https://www.pixiv.net/en/artworks/101844438'}
    co_settings = {'folder':'none',
                   'maxsize':32}
    
    return {'dl':dl_settings,
            'co':co_settings}

def get_main_square():
    lines = []
    ind = ' '*2
    edge = '-'*40

    lines.append(edge)
    lines.append('')
    lines.append(f'{ind}{ind}Welcome to {col("ma","download.py")} {col("re",chr(3))}')
    lines.append('')
    lines.append(chr(25)*3 + col('cy',' how to use ') + chr(25)*3)
    lines.append(f'{ind}- set a url with ' + col('cy','url <url>') + ' for example: ' + col('cy','url https://www.pixiv.net/en/artworks/101844438'))
    lines.append(f'{ind}- ' + col('cy','download'))
    lines.append(f'{ind}- ' + 'then use ' + col('ma','collage.py') + ' to make a collage')
    lines.append('')
    
    lines.append(chr(25)*3 + col('cy',' commands ') + chr(25)*3 + f'{ind}{ind}(type it and press enter)')
    for a,b in ([(f'to change a {col("ye","setting")}', col('cy','<setting> <new_value>') + ' for example: ' + col('cy','folder images')),
                 ('to ' + col('cy','download'), col('cy','download'))]):
        if (a,b) == ('',''):
            lines.append('')
        else:
            lines.append(f'{ind}{a} -{chr(26)} {b}')


    lines.append('')
    lines.append('settings: ' + get_settings(dl_settings))
    lines.append('')
    lines.append('note: ' + check_dl(dl_settings))
    lines.append('')
    lines.append(edge)
    return '\n'.join(lines)

def get_settings(d):
    if d == {}:
        return ''
    
    to_write = ''
    for k,v in d.items():
        to_write += col('ye',k)
        to_write += f':{v}'
        to_write += ', '
    return to_write[:-2]

def check_dl(dl_settings):
    valid = True
    random_folder = False

    messages = []
    folder = dl_settings['folder']
    url = dl_settings['url']

    if folder == '<random>':
        messages.append('a random folder will be created')
    elif folder not in os.listdir(os.getcwd()):
        messages.append(f'{folder} doesn\'t exist, it will be created')
    

    if '/artworks/' not in url:
        messages.append(col('re', '/artworks/ is not in url'))
        valid = False
    
    if valid:
        messages.append(col('gr','good to go'))
        
    return ', '.join(messages)

def update_co(k, v):
    exit('this function does not exist')    

# positive distance to move up. be careful about horizontal spacing
def change_line(distance, new_line):
    erase = f'{u}[2K' # to delete line
    if distance == 0:
        return 0
        write(erase)
        write(new_line + '\n')
    elif distance > 0:
        write(f'{u}[{distance}A')
        write(erase)
        write('\r')
        write(new_line)
        write(f'{u}[{distance}B')
        write('\r')
    else:
        return 0
        write(f'{u}[{distance}B')
        write(erase)
        write(new_line + '\n')
        write(f'{u}[{distance}A')

dist_to_note = 3
dist_to_settings = 5
def loop():
    
    global dl_settings
    defaults = get_defaults()
    
    dl_settings = defaults['dl']
    co_settings = defaults['co']
    
    write(f'{u}[0m') # reset any effects

    write(get_main_square())
    
    write('\n\n')
    write(f'{u}[1A') #1 up

    reset = False
    while True:
        i = input()
        write(f'{u}[1A') #1 up
        write(f'{u}[2K') # delete line
        if i == 'quit':
            break
        elif i == 'reset':
            reset = True
            break
        elif i == 'laser':
            laser_color = 'ma'
            change_line(dist_to_note, f'note: {col(laser_color, "shooting laser")}')
            write(f'{u}[?25l') # hide cursor
            speed = 0.05

            beam = '---'
            
            write(f'{u}[35m') # set color to magenta

            # laser enters from left, one minus at a time
            for c in beam:
                write(c)
                fl()
                time.sleep(speed)
            write(f'{u}[2K') # delete line
            write('\r')
            
            for i in range(1, 20):
                write(' '*i + beam)
                fl()
                time.sleep(speed)
                write(f'{u}[2K') # delete line
                write('\r')
            write(f'{u}[?25h') # show cursor
            write(f'{u}[0m') # reset color (and any other effects)
            change_line(dist_to_note, f'note: ' + check_dl(dl_settings))
        elif len(i.split(' ')) == 2:
            k,v = words = i.split(' ')
            if k in dl_settings:
                dl_settings[k] = v
                note = check_dl(dl_settings)
            else:
                note = col('re', f'{v} is not a setting')
            change_line(dist_to_note, 'note: ' + note)
            change_line(dist_to_settings, 'settings: ' + get_settings(dl_settings))
            
        elif i == 'download':
            note = check_dl(dl_settings)
            if f'{u}[31' not in note:
                change_line(dist_to_note, 'note: ' + col('gr', f'downloading...'))
                download(**dl_settings)
                f = dl_settings['folder']
                change_line(dist_to_note, 'note: ' + col('gr','success! ') + f'downloaded to folder: "{col("cy",f)}"')
            else:
                # make note flash (to indicate that settings aren't correct yet)
                change_line(dist_to_note, 'note: ' + note.replace(f'{u}[31m', f'{u}[7m'))
                fl()
                time.sleep(0.3)
                change_line(dist_to_note, 'note: ' + note + f'{u}[27m')
                
    if reset:
        loop()
    else:
        exit()

if __name__ == '__main__':
    loop()






