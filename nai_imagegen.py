import requests, time, json, os, zipfile, threading
import tkinter as tk

nai_token = 'find this via dev tools'
if nai_token == 'find this via dev tools':
  print('nai token is invalid.')
  exit()

class Cache:
    def __init__(self, filename):
        self.filename = filename
        if not os.path.exists(self.filename):
            with open(self.filename, 'w') as f:
                json.dump([], f)
        self.cache = self.load_cache()
    
    def load_cache(self):
        with open(self.filename, 'r') as f:
            cache = json.load(f)
        return cache

    def save_cache(self):
        with open(self.filename, 'w') as f:
            json.dump(self.cache, f)

    def get(self, inp):
        for item in self.cache:
            if item['input'] == inp:
                return item['output']
        return None

    def add(self, inp, outp):
        self.cache.append({'input':inp, 'output':outp})
        self.save_cache()
cache = Cache('cache.json')

def suggest_tags(prompt):
    cached = cache.get(prompt)
    print(f'cached: {cached}')
    if cached is not None:
        to_return = cached
    else:
        url = "https://api.novelai.net/ai/generate-image/suggest-tags"
        params = {
            "model": "nai-diffusion",
            "prompt": prompt
        }
        headers = {
            "Authorization": f"Bearer {nai_token}",
        }
        response = requests.get(url, params=params, headers=headers)
        response.raise_for_status()
        to_return = response.json()
        cache.add(prompt, to_return)
    return to_return


def nai_image(payload):
    url = "https://api.novelai.net/ai/generate-image"
    headers = {
        "Authorization": f"Bearer {nai_token}",
        "Content-Type": "application/json",
        'Accept': 'application/json',
    }

    response = requests.post(url, json=payload, headers=headers)
    response.raise_for_status()  # Raise exception if invalid response

    t = time.time()
    t = str(t).replace('.', '_')
    folder = f'images/{t}'
    os.mkdir(folder)

    # Save the zip file
    with open(f'{folder}/zipfile.zip', "wb") as f:
        f.write(response.content)

    # Extract the image from the zip file
    with zipfile.ZipFile(f'{folder}/zipfile.zip', 'r') as zip_ref:
        zip_ref.extractall(folder)
    with open(f'{folder}/payload.json', 'w') as f:
        f.write(json.dumps(payload, indent=4))

    return folder + '/image_0.png', folder + '/image_1.png'

def get_selected(text_widget):
    # returns mouse-selected text from a tk.Text widget
    try:
        text_widget.selection_get()
    except:
        return None
    else:
        return text_widget.selection_get()

def on_release(event):
    sel = get_selected(text)
    if sel is None:
        prompt = text.get('insert wordstart', 'insert wordend')
    else:
        prompt = sel

    def to_call():
        suggestions = suggest_tags(prompt)['tags']
        textup.delete('1.0', tk.END)
        to_insert = '\n'.join([s['tag'] for s in suggestions])
        textup.insert(tk.END, to_insert)
    threading.Thread(target=to_call).start()

def on_click_textup(event):
    if event.state == 12:
        idx = textup.index(f'@{event.x},{event.y}')
        clicked_line = textup.get(idx + ' linestart', idx + ' lineend')

        sel = get_selected(text)
        if sel is not None:
            text.delete('sel.first', 'sel.last')
            text.insert(tk.INSERT, clicked_line)

            length = len(clicked_line)
            idx = text.index(f'insert -{length}c')
            text.tag_add(tk.SEL, f'{idx}', f'{idx}+{length}c')

            do_nai_image()

payload_path = 'default_payload.json'
if payload_path not in os.listdir():
    default_payload = {
        "input": "tree of life, outdoors, pigeon, bees",
        "model": "nai-diffusion",
        "action": "generate",
        "parameters": {
            "width": 512,
            "height": 768,
            "scale": 11,
            "seed": 1,
            "sampler": "k_dpmpp_2m",
            "steps": 28,
            "n_samples": 1,
            "ucPreset": 0,
            "qualityToggle": false,
            "sm": false,
            "sm_dyn": false,
            "dynamic_thresholding": false,
            "controlnet_strength": 1,
            "legacy": true,
            "add_original_image": false,
            "negative_prompt": "lowres, bad anatomy, bad hands, worst quality, low quality"
        }
    }
    with open(payload_path, 'w') as f:
        f.write(json.dumps(default_payload, indent=4))
else:
    with open(payload_path, 'r') as f:
        default_payload = json.load(f)
if 'images' not in os.listdir():
    os.mkdir('images')

def do_nai_image():
    def to_call():
        global img, img2

        payload = text.get('1.0', tk.END)[:-1]
        payload = json.loads(payload)
        paths = nai_image(payload)

        img = tk.PhotoImage(file=paths[0])
        canvas.create_image(0, 0, anchor=tk.NW, image=img)

        if payload['parameters']['n_samples'] == 2:
            img2 = tk.PhotoImage(file=paths[1])
            canvas2.create_image(0, 0, anchor=tk.NW, image=img2)
        else:
            canvas2.delete('all')

    threading.Thread(target=to_call).start()

def on_keypress(event):
    if event.keysym == 'Escape':
        do_nai_image()
    elif event.keysym == 's' and event.state == 12:
        payload = text.get('1.0', tk.END)[:-1]
        with open('default_payload.json', 'w') as f:
            f.write(payload)

root = tk.Tk()
root.geometry('+0+0')
root.configure(background='black')

left = tk.Frame(root, bg='black')
middle = tk.Frame(root, bg='black')
right = tk.Frame(root, bg='black')

left.grid(row=0, column=0)
middle.grid(row=0, column=1)
right.grid(row=0, column=2)
canvas = tk.Canvas(left, width=512, height=768, bg='black')
canvas.pack()

canvas2 = tk.Canvas(middle, width=512, height=768, bg='black')
canvas2.pack()

textup = tk.Text(right, bg='black', fg='beige', insertbackground='white', font=('Calibri', 14), selectbackground='beige', selectforeground='black', height=15)
textup.pack()
text = tk.Text(right, bg='black', fg='beige', insertbackground='white', font=('Calibri', 14), selectbackground='beige', selectforeground='black')
text.pack()
text.insert(tk.END, json.dumps(default_payload, indent=4))


root.bind('<KeyPress>', on_keypress)
text.bind('<ButtonRelease-1>', on_release)
textup.bind('<ButtonPress-1>', on_click_textup)

root.mainloop()
