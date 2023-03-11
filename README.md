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

## deleted because they suck:
- lets_all_stop_writing_html_and_css
- run_something.py
- prompting_tool
