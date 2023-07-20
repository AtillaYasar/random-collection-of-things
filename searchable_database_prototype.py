# assumes you have a text file called paulgraham.txt, i copypasted http://paulgraham.com/greatwork.html into it for this prototype

from abc import ABC, abstractmethod
import json, os

class SearchableDatabaseABC(ABC):
    @abstractmethod
    def search(self, query):
        # returns a list of (string, metadata) pairs
        pass

    @abstractmethod
    def get_context(self, location):
        # returns a string
        pass

class TestDatabase(SearchableDatabaseABC):
    def __init__(self, data):
        self.data = data
        
        Overall_Condition = lambda data: type(data) == list
        Item_Condition = lambda item: len(item) == 2 and type(item[0]) == str and type(item[1]) == dict

        if not Overall_Condition(self.data):
            raise Exception
        for item in self.data:
            if not Item_Condition(item):
                raise Exception

    def search(self, substring):
        return [(string, metadata) for string, metadata in self.data if substring in string]
    
    def get_context(self, location):
        radius = 2
        items = []
        for i in range(max(0, location-radius), min(location+radius+1, len(self.data))):
            items.append(self.data[i][0])
        return '\n\n'.join(items)  # fragile, because `\n\n`.join may not be correct

def string_to_databasejson(string, path):
    lst = []
    for n, p in enumerate(string.split('\n\n')):
        lst.append((
            p,
            {
                'id':n,
            }
        ))
    with open(path, 'w') as f:
        json.dump(lst, f, indent=2)

def textfile_to_database(path):
    with open(path, 'r') as f:
        string = f.read()
    lst = []
    origin = {
        'type': 'textfile',
        'path': path,
    }
    for n, p in enumerate(string.split('\n\n')):
        lst.append((
            p,
            {
                'origin': origin,
                'location': f'paragraph {n}'
            }
        ))
    return TestDatabase(lst)

def col(ft, s):
    """For printing text with colors.
    
    Uses ansi escape sequences. (ft is "first two", s is "string")"""
    # black-30, red-31, green-32, yellow-33, blue-34, magenta-35, cyan-36, white-37
    u = '\u001b'
    numbers = dict([(string,30+n) for n, string in enumerate(('bl','re','gr','ye','blu','ma','cy','wh'))])
    n = numbers[ft]
    return f'{u}[{n}m{s}{u}[0m'

go_up = lambda n: print(f'\u001b[{n}A')
go_down = lambda n: print(f'\u001b[{n}B')
clear_line = lambda: print('\u001b[2K', end='')

db = textfile_to_database('paulgraham.txt')

def is_int(s):
    try:
        int(s)
        return True
    except:
        return False

def show_results(results):
    for n, r in enumerate(results[:5]):
        string = r[0]
        print(  col('gr',f'{n}. ') + string.replace(q, col('cy', q))  )
        print(f'\t{r[1]}')
        print(col('gr', '--'*20))

while True:
    print(col('ma', '-'*20))

    i = input('> ')
    go_up(2)
    clear_line()
    print(f'> {col("cy", i)}')

    if is_int(i):
        chosen_string = results[int(i)][0]

        loc_string = results[int(i)][1]['location']
        if loc_string.startswith('paragraph '):
            loc = int(loc_string[len('paragraph '):])
        else:
            raise Exception
        context = db.get_context(loc)
        print(col('gr', chosen_string))
        print(context.replace(q, col('cy', q)))
    else:
        q = i
        results = db.search(q)
        show_results(results)
