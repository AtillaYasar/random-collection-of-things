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

## discord_testing
- very basic testing environment for discord.py.
- uses this to simulate typing messages in discord:
```python
while True:
  i = input
  handle_input(i)
```
```python
@command
def _example_command(inp):
    """Registers a command for sending a message.

    Analogous to:
    async def _example_command(ctx, *, inp):
        await ctx.send(f'your input was:{inp}')
    """
    print(f'your input was:{inp}')
```

## wiki_poc.py
- just something while playing around with the wikipedia and WikipediaAPI libraries.
- poc stands for "proof of concept". it's mostly to show how to use these libraries, for myself and others  :)
  + https://github.com/goldsmith/Wikipedia and https://github.com/martin-majlis/Wikipedia-API
- it has 3 commands: search, hierarchy, content, below are aesthetic terminal screenshots showing it in use :)
  + when you run it
    - ![wiki on_open](https://user-images.githubusercontent.com/112716905/224471617-0a14198a-1949-465a-bf54-3f2e4c2ef10f.png)
  + search  (to search pages)
    - ![wiki searc res](https://user-images.githubusercontent.com/112716905/224471633-70fbb8a1-d417-4e32-82dc-cb076d6908bd.png)
  + hierarchy  (to show a page's hierarchy)
    - ![wiki hierarchy res](https://user-images.githubusercontent.com/112716905/224471651-20c7b7f2-ffed-4e1e-8819-52ce540baf4c.png)
  + content  (to get content of a section or full page)
    - ![wiki content res](https://user-images.githubusercontent.com/112716905/224471665-22777f4d-18cb-4bef-94fc-6397b3067211.png)

## shoulder_gpt.py
- "gpt on your shoulder"
- i dont feel like explaining.
- just run it. itll be cool.
- ![Schermopname (7)](https://user-images.githubusercontent.com/112716905/224529114-c29420f4-28cf-49a1-b43c-f8fa3a72da19.png)
- ![Schermopname (8)](https://user-images.githubusercontent.com/112716905/224535016-9184863b-79b7-4d46-9c46-4dbacc7871bc.png)

## wiki_emb
- will let you search for and view wikipedia articles, embed paragraphs contained, and search embeddings, and maintain a database of embeddings

## pytube_wrapper.py
for now, just lets you see things about a Youtube video. oh and you can call .download() on the stream objects in PytubeWrapper.downloadables

## writing-tool-gpt
lil writing tool with these features:
- display selected word count if selected, otherwise global word count
- headers are in the listbox to the right, and you can click the to go to that text
  + press Escape to update the listbox
  + press Enter in the listbox to go to that line in the middle (main) textbox
- navigate boxes with alt + up/down/left/right
- in the rightmost you can write chatgpt context
  + press ctrl+1/2/3 to add "system"/"assistant"/"user" messages
  + press ctrl+r to remove the last message
  + press ctrl+g to call chatgpt api
  + 2 "placeholders":
    - {selected}, will put mouse-selected text in there
    - {instruction}, will put text from the entry box in there
    - example usage:
      + ![image](https://user-images.githubusercontent.com/112716905/231696973-80f95250-2a2a-449b-befc-50e895b22890.png)
      + ![image](https://user-images.githubusercontent.com/112716905/231697059-440d4b6c-dc76-49db-a704-7d696b2c7d69.png)
- if this writing tool seems shittily written and hacked together, that's because it is. copilot is an amazing tool  :)
- press ctrl+s in the "main" text to save to "word_counter.txt", and in the right box to save to "script.json", and then you can do ctrl+b in the right box to make a backup of the script. (because you might want multiple scripts)

## ytplaylist_cli.py
- lets you shuffle and pick from, a youtube playlist, then opens the video and searches for lyrics with the video title (because im personally using it for music)
- ![Screenshot_2](https://github.com/AtillaYasar/random-collection-of-things/assets/112716905/46633647-599e-4908-8a1e-2f0f4af0aa8f)
- ![Screenshot_3](https://github.com/AtillaYasar/random-collection-of-things/assets/112716905/f35bb6ca-0b92-4fd7-a05b-e40928adf03c)

## ytres.py
- offshoot of jre.py (for which i havent written anything yet, and which will become a bigger program in the future)
- do a youtube search, see results, open a video or get a summary from chatgpt
- ![Screenshot_6](https://github.com/AtillaYasar/random-collection-of-things/assets/112716905/d3d6de43-0623-498e-9905-1e441e3266ce)
- ![Screenshot_7](https://github.com/AtillaYasar/random-collection-of-things/assets/112716905/7e057609-5206-474a-b10b-5847523e4b9b)

## bari_arakeel
- folder has a tkinter app which i made for changing the timestamps of lyrics associated with a song. here's a video where i show it: https://youtu.be/oKr6OMyhcVM folder has the lyrics json, the mp3 file, and the app in `bari_arakeel.py`
- you can call it a prototype but that implies ill ever imporove it lol. it served its purpose for me xD
