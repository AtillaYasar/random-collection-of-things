import tkinter as tk
import threading
import pygame
pygame.mixer.init()
# Your provided play_music function
def play_music(path, lyric_timestamp, start_from=0):
    '''Stream music_file in a blocking manner and display lyrics at the corresponding timestamps.
    
    Parameters:
    - path: str, the path to the music file.
    - lyric_timestamp: list of tuples, where each tuple contains a timestamp and a lyric line.
    - start_from: float, optional start timestamp in seconds.
    '''
    
    # Initialize pygame mixer
    
    clock = pygame.time.Clock()
    
    # Load the music
    pygame.mixer.music.load(path)
    
    # Start playing music from the specified timestamp
    pygame.mixer.music.play(start=0, fade_ms=0)
    pygame.mixer.music.set_pos(start_from)
    
    # Find the first lyric index to display based on the start_from timestamp
    current_lyric_index = next((index for index, (stamp, _) in enumerate(lyric_timestamp) if stamp >= start_from), len(lyric_timestamp))
    
    while pygame.mixer.music.get_busy():
        # Time elapsed in seconds since the start of the music plus the starting offset
        elapsed_time = pygame.mixer.music.get_pos() / 1000 + start_from
        app.label.config(text=f't: {round(elapsed_time, 1)}')
        
        # Check if the current time has reached the next lyric timestamp
        if (current_lyric_index < len(lyric_timestamp)) and (elapsed_time >= lyric_timestamp[current_lyric_index][0]):
            # Print the current line of the lyrics
            print(lyric_timestamp[current_lyric_index][1])
            app.hline(str(current_lyric_index+1))

            # Move to the next lyric index
            current_lyric_index += 1

        clock.tick(30)

# Function to handle music playing in a separate thread
def threaded_play_music(path, lyric_timestamp, start_from):
    pygame.quit()
    
    # Initialize all Pygame modules
    pygame.init()
    pygame.mixer.init()  # Explicitly initialize the mixer module just in case
    play_music(path, lyric_timestamp, start_from)

# Tkinter application setup
class MusicPlayerApp(tk.Tk):
    def __init__(self, *args, **kwargs):
        tk.Tk.__init__(self, *args, **kwargs)
        self.geometry('-0+0')
        self.text_widget = tk.Text(self)
        self.text_widget.pack()
        self.text_widget.insert('1.0', '\n'.join([i['text'] for i in transcript]))

        self.label = tk.Label(self)
        self.label.pack()

        # Event binding to handle text click
        self.text_widget.bind('<Button-1>', self.on_text_click)
        self.text_widget.bind('<Button-3>', self.on_text_rightclick)

        self.tag = 'highlight'
        self.text_widget.tag_config(self.tag, foreground='purple')

    def hline(self, idx):
        print(f'highlighting {idx}')
        self.text_widget.tag_remove(self.tag, '1.0', 'end')
        self.text_widget.tag_add(self.tag, f'{idx}.0 linestart', f'{idx}.0 lineend')

    # Event callback for text click
    def on_text_click(self, event):
        # Get the index of the current mouse click
        index = self.text_widget.index("@%d,%d" % (event.x, event.y))

        # Convert the index to a line number
        line = int(index.split(".")[0])-1
        
        # Get the corresponding timestamp for the line
        start_from = index_to_timestamp_func(line)

        # Play music from the start_from timestamp in a new thread
        threading.Thread(target=threaded_play_music, args=(path, lyric_timestamp, start_from)).start()

    def on_text_rightclick(self, event):
        pygame.mixer.music.stop()

def readfile(path):
    with open(path, 'r', encoding='utf-8') as f:
        if path.endswith('.json'):
            content = json.load(f)
        else:
            content = f.read()
    return content
from colorama import init
init()
def col(ft, s):
    """For printing text with colors.
    
    Uses ansi escape sequences. (ft is "first two", s is "string")"""
    # black-30, red-31, green-32, yellow-33, blue-34, magenta-35, cyan-36, white-37
    u = '\u001b'
    numbers = dict([(string,30+n) for n, string in enumerate(('bl','re','gr','ye','blu','ma','cy','wh'))])
    n = numbers[ft]
    return f'{u}[{n}m{s}{u}[0m'
def writefile(path, content):
    with open(path, 'w', encoding='utf-8') as f:
        if isinstance(content, (dict, list)):
            json.dump(content, f, indent=2)
        else:
            f.write(content)

def recreate():
    global transcript, lyric_timestamp
    og = [i['text'] for i in transcript]
    new = app.text_widget.get('1.0', 'end -1c').split('\n')
    if not len(og) == len(new):
        print(og)
        print(new)
        exit()
    newt = []
    for n, tup in enumerate(zip(og, new)):
        a,b = tup
        if a == b:
            print([a,b])
        else:
            print(col('gr', str([a,b])))
        newt.append({
            'text': b,
            'start': transcript[n]['start'],
            'duration': transcript[n]['duration']
        })
    
    writefile('bari_arakeel.json', newt)
    lyric_timestamp = [(i['start'], i['text']) for i in newt]
    threading.Thread(target=threaded_play_music, args=(path, lyric_timestamp, 0)).start()

import json
# Replace with your music file path and timestamps
path = 'bari_arakeel.mp3'
transcript = readfile('bari_arakeel.json')
lyric_timestamp = [(i['start'], i['text']) for i in transcript]
# Dummy function to handle index to timestamp conversion
def index_to_timestamp_func(index):
    # Replace this with your actual implementation
    return transcript[index]['start']

# Run the application
app = MusicPlayerApp()

def stop():
    pygame.mixer.music.stop()
    exit()

app.bind('<Escape>', lambda e:stop())
app.protocol("WM_DELETE_WINDOW", stop)
app.bind('<F1>', lambda e:recreate())
entry = tk.Entry(app)
entry.pack()
entry.insert(0, '0.5')
def replace(newt, play_from=0):
    global transcript, lyric_timestamp
    writefile('bari_arakeel.json', newt)
    transcript = newt
    lyric_timestamp = [(i['start'], i['text']) for i in newt]
    threading.Thread(target=threaded_play_music, args=(path, lyric_timestamp, play_from)).start()

def get_idx():
    w = app.text_widget
    idx = int(w.index('insert').split('.')[0])-1
    return idx

def increment(sec):
    cur = get_idx()
    newt = []
    for n, item in enumerate(transcript):
        if n >= cur:
            item['start'] += sec
        newt.append(item)
    replace(newt, newt[cur]['start'])

def on_pup():
    size = float(entry.get())
    increment(-size)

def on_pdown():
    size = float(entry.get())
    increment(size)

app.bind('<Next>', lambda e:on_pdown())
app.bind('<Prior>', lambda e:on_pup())

threading.Thread(target=threaded_play_music, args=(path, lyric_timestamp, 0)).start()

app.mainloop()