import tkinter as tk
import os, json, time
from overall_imports import make_json, open_json
from tkinter import ttk

from chatgpt_stuff import Chatbot

def text_create(path, content=''):
    with open(path, 'w', encoding='utf-8') as f:
        f.write(content)

def window_on_keypress(event):
    '''
    navigate widgets on alt+arrows
    '''
    if event.keysym == 'Left' and event.state == 393224:
        listbox.focus_set()
    elif event.keysym == 'Down' and event.state == 393224:
        entry_box.focus_set()
    elif event.keysym == 'Up' and event.state == 393224:
        text_box.focus_set()
    elif event.keysym == 'Right' and event.state == 393224:
        right_text.focus_set()

def main_on_keypress(event):
    '''
    Ctrl + S: save
    ctrl + g: use chatgpt api to generate text
    '''
    if event.keysym == 's' and event.state == 12:
        text = text_box.get("1.0", "end")[:-1]
        text_create(working_textfile, text)
        print('Saved main text')
    elif event.keysym == 'g' and event.state == 12:
        selected = get_selected(event.widget)
        if selected == None:
            pass
        else:
            bot = Chatbot(0)
            instruction = entry_box.get()
            '''
            instruction ideas:
                - zonder het neppe, "ben je op zoek naar? ... dan is ... voor jou!" meer oprecht
                - herschrijven
            '''
            script = right_text.get("1.0", "end")[:-1]
            messages = json.loads(script)

            replacements = {
                '{instruction}': instruction,
                '{selected}': selected,
                '{1}': thingy.get('1'),
                '{2}': thingy.get('2'),
                '{3}': thingy.get('3'),
            }
            for n, message in enumerate(messages):
                for k, v in replacements.items():
                    messages[n][1] = messages[n][1].replace(k, v)
            print(json.dumps(messages, indent=2))
            for message in messages:
                bot.add_message(message[0], message[1])
            resp = bot.use_api()
            print(resp)

def add_message(role):
    current_script = right_text.get("1.0", "end")[:-1]
    as_list = json.loads(current_script)
    as_list.append([role, ''])
    right_text.delete("1.0", "end")
    right_text.insert("1.0", json.dumps(as_list, indent=4))
    right_text.see("end")

backup_folder = 'backups'
if not os.path.exists(backup_folder):
    os.mkdir(backup_folder)
def rightbox_on_keypress(event):
    '''
    save on ctrl + s to script.json
    on ctrl+b create a backup
    on ctrl+1 add 'system' message
    on ctrl+2 add 'user' message
    on ctrl+3 add 'assistant' message
    on ctrl+r remove last message
    '''
    if event.keysym == 's' and event.state == 12:
        text = right_text.get("1.0", "end")[:-1]
        dic = json.loads(text)
        with open('script.json', 'w') as f:
            json.dump(dic, f, indent=4)
        print('Saved script')
    elif event.keysym == 'b' and event.state == 12:
        text = right_text.get("1.0", "end")[:-1]
        dic = json.loads(text)
        fname = time.time()
        with open(os.path.join(backup_folder, f'{fname}.json'), 'w') as f:
            json.dump(dic, f, indent=2)
        print('Saved backup script')
    elif event.keysym == '1' and event.state == 12:
        add_message('system')
    elif event.keysym == '2' and event.state == 12:
        add_message('user')
    elif event.keysym == '3' and event.state == 12:
        add_message('assistant')
    elif event.keysym == 'r' and event.state == 12:
        current_script = right_text.get("1.0", "end")[:-1]
        as_list = json.loads(current_script)
        as_list = as_list[:-1]
        right_text.delete("1.0", "end")
        right_text.insert("1.0", json.dumps(as_list, indent=4))
        right_text.see("end")


def get_selected(w):
    try:
        w.selection_get()
    except:
        return None
    else:
        return w.selection_get()

def display_selected_count():
    selected = get_selected(text_box)
    if selected != None:
        words = selected.split(' ')
        # update the label with the number of words
        word_count.config(text="Word Count: " + str(len(words)))
    else:
        pass

def on_motion(event):
    display_selected_count()

def update_listbox():
    # go through the text and find line numbers that start with a #
    # then add those headers to the listbox
    # will call on escape to test
    global global_header_info

    text = text_box.get("1.0", "end")
    lines = text.split('\n')
    global_header_info = {}
    for i, line in enumerate(lines):
        if line.startswith('#'):
            global_header_info[line] = i+1
    listbox.delete(0, 'end')
    for header in global_header_info.keys():
        listbox.insert('end', header)

def on_listbox_select(event):
    # scroll to the header and highlight it
    selected = listbox.curselection()
    if selected != ():
        index = int(selected[0])
        text = listbox.get(index)
        line = global_header_info[text]
        text_box.see(f'{line}.0')
        text_box.mark_set('insert', f'{line}.0')
        text_box.tag_remove('to_highlight', '1.0', 'end')
        text_box.tag_add('to_highlight', f'{line}.0', f'{line}.0 lineend')
        text_box.tag_config('to_highlight', foreground='yellow')

def main_on_mouse_release(event):
    # display global word count if nothing is selected
    if get_selected(text_box) == None:
        words = text_box.get("1.0", "end")[:-1].split(' ')
        word_count.config(text="Word Count: " + str(len(words)))

def listbox_on_keypress(event):
    # go to selected header on enter
    if event.keysym == 'Return':
        text_box.focus()

# create full screen window
window = tk.Tk()
window.title("Word Counter")
window.geometry("1920x1080")
window.attributes("-fullscreen", True)

left_frame = tk.Frame(window)
middle_frame = tk.Frame(window)
right_frame = tk.Frame(window)

left_frame.grid(row=0, column=0, sticky='nsew')
middle_frame.grid(row=0, column=1, sticky='nsew', padx=10, pady=10)
right_frame.grid(row=0, column=2, sticky='nsew')

left_frame.config(bg='black')
middle_frame.config(bg='black')
right_frame.config(bg='black')

# create the text box
text_box = tk.Text(middle_frame, width=50, height=25, font=("comic sans", 14))
text_box.pack()
working_textfile = 'word_counter.txt'
if working_textfile not in os.listdir():
    with open(working_textfile, 'w') as f:
        f.write('')
with open(working_textfile, 'r', encoding='utf-8') as f:
    text = f.read()
text_box.insert('1.0', text)

default_script_path = 'script.json'
if default_script_path not in os.listdir():
    make_json([], default_script_path)
with open(default_script_path, 'r', encoding='utf-8') as f:
    default_script = json.load(f)
right_text = tk.Text(right_frame, width=35, height=25, font=("comic sans", 14))
right_text.pack()
right_text.insert('1.0', json.dumps(default_script, indent=4))
# fallback for script:
'''
[
    [
        "user",
        "hallo, kun je mij helpen met deze tekst?\n---\n{selected}\n---"
    ],
    [
        "assistant",
        "Ja, natuurlijk! Wat wil je ermee doen?"
    ],
    [
        "user",
        "{instruction}"
    ]
]
'''

# entry box
entry_box = tk.Entry(middle_frame, font=("comic sans", 14))
entry_box.pack()
# listbox
listbox = tk.Listbox(left_frame, font=("comic sans", 14))
listbox.pack(fill='both', expand=True)
listbox.config(bg='black', fg='white', selectbackground='white', selectforeground='black', width=25)
# wordcount label
word_count = tk.Label(middle_frame, text="Word Count: 0")
word_count.pack()

# apply nice colors
window.config(bg="#000000")
text_box.config(bg="#000000", fg="#ffffff", insertbackground="#ffffff", selectbackground="#ffffff", selectforeground="#000000")
word_count.config(bg="#000000", fg="#ffffff")
entry_box.config(bg="#000000", fg="#ffffff", insertbackground="#ffffff", selectbackground="#ffffff", selectforeground="#000000")
right_text.config(bg="#000000", fg="#ffffff", insertbackground="#ffffff", selectbackground="#ffffff", selectforeground="#000000")

window.bind('<Motion>', on_motion)
window.bind('<Escape>', lambda event: update_listbox())
listbox.bind('<<ListboxSelect>>', on_listbox_select)
window.bind('<KeyPress>', window_on_keypress)
text_box.bind('<KeyPress>', main_on_keypress)
right_text.bind('<KeyPress>', rightbox_on_keypress)
listbox.bind('<KeyPress>', listbox_on_keypress)
text_box.bind('<ButtonRelease>', main_on_mouse_release)

update_listbox()

# basically a toggleable text editor
class Thingy:
    def __init__(self, content=''):
        self.exists = False
        self.current_tab = None
        self.tab_amount = 3

        self.tab_contents = {str(n):{'widget':'', 'content':''} for n in range(1, self.tab_amount+1)}
        
        self.all_windows = [window]
        for w in self.all_windows:
            w.bind('<KeyPress>', self.on_press, add='+')

    # toggle the window
    def toggle(self, f_number):
        if self.exists: # store content, destroy widgets
            if f_number != self.current_tab:
                pass
            else:
                for n, info in self.tab_contents.items():
                    self.tab_contents[n]['content'] = info['widget'].get(1.0, 'end')[:-1]
                self.w.destroy()
                self.exists = False
                self.current_tab = None
        else: # re-create, re-insert content, re-bind on_press
            self.w = tk.Toplevel()
            self.w.config(background = 'black')

            self.nb = ttk.Notebook(self.w)

            # create tabs of text widgets
            for n, info in self.tab_contents.items():
                textSettings = {'width': 50, 'height': 25, 'font': ("comic sans", 14), 'bg': 'black', 'fg': 'white', 'insertbackground': 'white', 'selectbackground': 'white', 'selectforeground': 'black'}
                text_widget = tk.Text(self.nb, **textSettings)
                self.tab_contents[n]['widget'] = text_widget
                text_widget.insert(1.0, info['content'])
                
                self.nb.add(text_widget, text=f'- F{n} -')

            self.nb.pack()
            
            self.w.bind('<KeyPress>', self.on_press)
            self.nb.bind('<KeyPress>', self.on_press)
            self.exists = True
            self.current_tab = f_number
            
    def on_press(self, event):
        n = event.keysym.partition('F')[2]
        if n in self.tab_contents:
            self.toggle(n)

            if self.exists:
                tab_id = int(n)-1
                self.nb.select(tab_id)

                self.tab_contents[n]['widget'].focus_set()
                self.current_tab = n
        elif event.keysym == 's' and event.state == 12:
            self.save()
    
    def save(self):
        contents = list(map(lambda v:v['widget'].get(1.0, 'end')[:-1], self.tab_contents.values()))
        print(contents)
        path = 'thingy.json'
        with open(path, 'w', encoding='utf-8') as f:
            json.dump(contents, f, indent=4)
    
    def get(self, key):
        if key in self.tab_contents:
            return self.tab_contents[key]['widget'].get(1.0, 'end')[:-1]
        else:
            print(f'key {key} not found')
            return None

thingy = Thingy()





# start the program
window.mainloop()

