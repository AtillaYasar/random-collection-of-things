import tkinter as tk
from tkinter import ttk
import json, copy

# this is the thinking that spawned or preceded this app.
# (inspired by sudowrite btw. as in, im attempting to shamelessly copy some of its features  :p )
'''
layout
    ok what am i doing?
    aigh whatever. just something to describe the layout. then what?
    1 1 2
    1 1 3 --> a big window on the left (taking up 2/3 of the screen), (called 1), 3 small windows on the right, (called 2,3,4)
    1 1 4


event loop
    and some "event loop"?
    some reference to events. events being keystrokes/hotkeys, timed events.. okay.
then?

actions in response to events.
reference to each editor window.

example
    on ctrl+g:
        - triggers the "generate" event, which is defined inside [generate]-script.
        - takes window 1's text as the prompt, writes the output to window 5
        - then takes window 1's + window 2's text, writes the output to window 3.

    lets say
    1 1 2
    1 1 3
    5 5 4

    on ctrl+g, take 1 as a prompt, show response in 5.

    [set hotkeys]
    generate = ctrl+g
    [/set hotkeys]

    [generate]
    prompt = 1
    output = 5
    [/generate]

    [generate]
    prompt = 1+2
    output = 3
    [/generate]
'''

#basically for getting all the text between 2 given strings, in a big mess of a string, and putting them in a list
#plus an option to only get items with the strings in strings_list in it
def between2(mess,start,end,strings_list=None):
    mess = mess.split(start)
    for i in range(len(mess)):
        mess[i] = mess[i].partition(end)[0]
    if strings_list == None:
        return mess[1:]
    else:
        filtered_mess = []
        for i in mess[1:]:
            for string in strings_list:
                if string in i:
                    filtered_mess.append(i)
        return filtered_mess
    mess = mess.split(start)
    for i in range(len(mess)):
        mess[i] = mess[i].partition(end)[0]
    return mess[1:]

def get_scripts(source, languages):
    return {lang:[string[1:-1] for string in between2(source, start=f'[{lang}]', end=f'[/{lang}]')] for lang in languages}

def apply_layout(layout):
    for i in range(len(layout)):
        for j in range(len(layout[i])): 
            if layout[i][j] == None:
                continue
            layout[i][j].grid(row=i,column=j)

def generate(prompt):
    return f'your prompt was --> {prompt}\nand the output is: <some really cool things>'

def parse_script(lang, code):
    print(f'code:{code}')
    if lang != 'generate':
        print('can only parse generate')
        return 0
    for string in ('prompt = ', 'output_loc = '):
        if string not in code:
            print('need prompt and output_loc')
            return 0
    if len(code.split('\n')) != 2:
        print('lines must be 2')
        return 0

    instructions = {}
    for line in code.split('\n'):
        left, right = line.split(' = ')
        instructions[left] = right
    
    # get prompt and AI completion
    inp_frame_name, inp_tab_index = instructions['prompt'].split('.')
    prompt = wm.get_text(inp_frame_name, inp_tab_index)
    completion = generate(prompt)

    # put completion in output_loc
    outp_frame_name, outp_tab_index = instructions['output_loc'].split('.')
    wm.append_text(outp_frame_name, outp_tab_index, completion)


class WindowsManager:
    def __init__(self, parent, matrix):
        self.parent = parent
        self.frames = []
        self.loc_to_name = {}
        self.name_to_loc = {}

        self.available_languages = ['generate']
        # create frames and store info about their locations and names
        for row_n, row in enumerate(matrix):
            this_row = []
            self.loc_to_name[row_n] = {}
            for column_n, name in enumerate(row):
                this_row.append(tk.LabelFrame(self.parent, text=f' = {name} = ', **frame_settings))  # <-- this is the key line
                self.loc_to_name[row_n][column_n] = name
                self.name_to_loc[name] = (row_n, column_n)
            self.frames.append(this_row)
        # put stuff inside the frames
        for name in self.name_to_loc.keys():
            self.fill_frame(name)

        # places frames, by calling widget.grid
        # using row and column indices from self.frames, as the row and column options in widget.grid
        apply_layout(self.frames)

        self.append_text(matrix[0][0],0, '''\n\n[generate]
prompt = first_square.1
output_loc = bottom_right.0
[/generate]''')

        self.parent.bind('<Escape>', self.test_function)
    
    # for.. ya know. finding a frame.
    def find_frame(self, name):
        loc = self.name_to_loc[name]
        frame = self.frames[loc[0]][loc[1]]
        return frame

    # putting a notebook inside the frame, with some stuff in tabs
    def fill_frame(self, name):
        frame = self.find_frame(name)

        # add notebook to frame
        nb = ttk.Notebook(frame)
        nb.pack()

        # add text widget to notebook
        first_text_widget = tk.Text(frame, **text_settings)
        second_text_widget = tk.Text(frame, **text_settings)
        nb.add(first_text_widget, text='first tab')
        nb.add(second_text_widget, text='second tab')

        # add some default values for testing
        for n, w in enumerate((first_text_widget, second_text_widget)):
            w.insert('end', f'frame name: {name}\ntab index: {n}')

    # locates a text widget and returns its contents
    def get_text(self, frame_name, tab_index):
        frame = self.find_frame(frame_name)
        tab_index = int(tab_index)

        # find notebook
        children = frame.winfo_children()
        nb = children[0]

        # find text widget
        text_name = nb.tabs()[tab_index]
        widget = nb.nametowidget(text_name)
        
        contents = widget.get('1.0', 'end')[:-1]
        return contents
    
    # locates a text widget and inserts text at the end
    def append_text(self, frame_name, tab_index, appendage):
        frame = self.find_frame(frame_name)
        tab_index = int(tab_index)

        # find notebook
        children = frame.winfo_children()
        nb = children[0]

        # find text widget
        text_name = nb.tabs()[tab_index]
        widget = nb.nametowidget(text_name)
        
        widget.insert('end', appendage)

    def test_function(self, event):
        edge = '------'
        print(edge)
        print(event)
        # iterate over all the tabs, and get their contents
        everything = []
        for name in self.name_to_loc.keys():
            for tab_index in (0,1):
                contents = self.get_text(name, tab_index)
                extraction = {
                    'frame name':name,
                    'tab index':tab_index,
                    'contents':contents,
                    'scripts':get_scripts(source=contents, languages=self.available_languages)
                    }
                print(json.dumps(extraction, indent=2))
                print()
                everything.append(copy.deepcopy(extraction))
        print(edge)

        print(json.dumps(everything, indent=2))
        # iterate over <everything> and .. do stuff.
        for d in everything:
            print(d['frame name'], f"d['scripts']['generate']: {d['scripts']['generate']}")
            if d['scripts']['generate'] != []:
                for generation_code in d['scripts']['generate']:
                    parse_script('generate', generation_code)

root = tk.Tk()

# lets actually start simple, and not deal with 1 1 turning into [big 1], lol. that is complicated.
layout_matrix = '''
first_square second_sq
first_in_second_row bottom_right
'''[1:-1]
matrix = []
for line in layout_matrix.split('\n'):
    matrix.append(line.split(' '))

dims = (200,200)
frame_settings = {'bg':'black', 'fg':'white', 'width':dims[0], 'height':dims[1], 'borderwidth':10}
text_settings = {'bg':'black', 'fg':'grey', 'insertbackground':'white', 'width':40, 'height':10, 'font':('comic sans',14)}

wm = WindowsManager(root, matrix)


root.mainloop()



















