# random-collection-of-things
name is self-explanatory... most of my repos will probably end up here

## Ram aid + text editor with highlighting
- my favorite tool by far, i use it for almost every single task that requires thinking and/or oversight over any problem or chunk of text
- https://github.com/AtillaYasar/mental-tools/
- AI extension: https://github.com/AtillaYasar/text-editor-OpenAI (should have been a fork or module or update or something..)
- ![image](https://user-images.githubusercontent.com/112716905/213861946-c23ddd62-79f4-4aa3-a5ab-5a9bdb4edbdb.png)

## Oracle
- command line interface  
- if you ask a question, returns 1 of 6 responses  
- video showing it https://youtu.be/B7JihYaXU6s

## lets_all_stop_writing_html_and_css
- it allows you to stop_writing_html_and_css
- example input: https://pastebin.com/yjVwMe1E  
- example output html: https://pastebin.com/KjCp2aVY
- example output css: https://pastebin.com/KdBGXzq0 
- todo: a way to manage multiple pages, and have a shared css and js library. and auto-generate a full site. im working on a blog, so i am my own client here.

## pixiv
- beautiful command line interface
- download.py: download from pixiv
- collage.py: make image collages, options for custom captions, number of columns, font size and color, ability to set maximum image size
- how to use? just run (meaning, download and double click) either app. it will be self-explanatory
- note: download.py will break if pixiv patches this dumb hack that lets you download original images without a login. lol.
![image](https://user-images.githubusercontent.com/112716905/205492410-50a187f7-1e1a-4053-9770-e4bea6ab2cb3.png)

## run_something.py
- prints a list of files, lets you enter a number, runs that file
- ![image](https://user-images.githubusercontent.com/112716905/211153821-f7d6ae51-6612-4d56-b9af-2664f8ffcb89.png)


## make_something.py
- lets you write a filename, creates that file in the current directory
- if you it's a html, it will insert some things
- if the file already exists, it wont let you make it
- ![image](https://user-images.githubusercontent.com/112716905/211151843-81bf8c17-28bf-44f8-a584-8d4f853a5090.png)

## get_toc.py
- little command line interface to find and print the table of contents of a .md file in the current directory
- usage example here: https://youtu.be/OGKUPjmPEx8
- ![image](https://user-images.githubusercontent.com/112716905/213638908-7932da0f-8b10-47b6-a031-689e3db24063.png)

## prompting_tool
- only a tkinter skeleton for now. does not actually support AI completions yet.
- (inspired by sudowrite, ) should eventually let you dynamically create prompts, combining multiple text editor windows and tabs, and output AI completions to multiple windows and tabs.
- ![tool screenshot 20th jan](https://user-images.githubusercontent.com/112716905/213690569-2a6f4f8e-6f86-4fe3-a77b-5be11dda128a.png)
  + the screenshot shows what's going on... if you can decypher it.
  + a "generation request" (or AI completion) is done inside [generate] [/generate] text in the top left. and it has directions on where the prompt is, and where to send the output.
  + it selects a prompt from a text editor (selected via window/tab combo), and sends the output to another editor (selected in the same way)
  + as the last line of the top left window says, `{window name}.{tab index}` is the way an editor is selected (or located)
- the code below shows how the layout is defined.
  + it is dynamic, as the windows are generated from this matrix, and designed to eventually be configurable from within the app
```python
layout_matrix = '''
first_square second_sq
first_in_second_row bottom_right
'''[1:-1]
matrix = []
for line in layout_matrix.split('\n'):
    matrix.append(line.split(' '))
```
