import json, os, time, requests, webbrowser

import tkinter as tk
from PIL import Image, ImageTk


# superclass for ImgContainer and TextContainer
class _Container(tk.Frame):
    def __init__(self, master, topleft, bottomright):
        self.master = master
        self.topleft = topleft
        self.bottomright = bottomright

        # calculate
        x1, y1 = topleft
        x2, y2 = bottomright
        width = x2 - x1
        height = y2 - y1
        self.width = width
        self.height = height

        # init
        super().__init__(
            master,
            width=width,
            height=height,
            bg='black',
        )
        self.pack_propagate(0)
        self.place(x=x1, y=y1)

class ImgContainer(_Container):
    def __init__(self, master, img_path, topleft, bottomright):
        # init
        super().__init__(master, topleft, bottomright)

        self.img_path = img_path
        self.label = tk.Label(self)
        self.label.pack()
        self.show_image(img_path)
        self.label.bind('<Button-1>', self.on_click)

        self.click_callback = None

    # resize to fit, then show
    def show_image(self, img_path):
        width = self.bottomright[0] - self.topleft[0]
        height = self.bottomright[1] - self.topleft[1]

        self.image = Image.open(img_path)
        self.image = self.image.resize((width, height), Image.LANCZOS)
        self.image = ImageTk.PhotoImage(self.image)
        self.label.config(image=self.image)

    def on_click(self, event):
        if callable(self.click_callback):
            self.click_callback(self, event)

    # to on_click code externally
    def add_click_callback(self, callback):
        self.click_callback = callback

class TextContainer(_Container):
    def __init__(self, master, topleft, bottomright):
        # init
        super().__init__(master, topleft, bottomright)

        # just some style options that i like
        self.text = tk.Text(
            master,
            bg='black',
            fg='white',
            insertbackground='white',
            selectbackground='white',
            selectforeground='black',
            font=('Calibri', 13),
            wrap=tk.WORD,
            width=50,
        )
        self.text.pack()

        self.text.bind('<Button-1>', self.on_click)

    def add_text(self, text):
        self.text.insert(tk.END, text)

    def clear_text(self):
        self.text.delete('1.0', tk.END)

    # just here for convenience
    def on_click(self, event):
        def get_line():
            w = event.widget
            idx = w.index('insert')
            return w.get(f'{idx} linestart', f'{idx} lineend')
