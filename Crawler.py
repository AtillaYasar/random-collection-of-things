# at a high level, crawls a nested structure of dictionaries and lists, and converts the whole thing to a list of dictionaries, while keeping track of its path through the structure, and returns a list of dictionaries.
# to use: create a crawler with the object you want to crawl, call crawler() (because it has the __call__ method, get result from Crawler.result
class Crawler:
    def __init__(self, obj):
        self.meta = {
            'name':'meta information about this list of dictionaries',
            'current path':[],
            'notes':'\n'.join([
                'source refers to either a list index, or a dictionary key',
                'group size refers to size of a list or dictionary that the name is a part of',
                'name refers to dictionary key, list index, or in case of other, str(other)'
            ])
        }
        self.obj = obj

    # the recursive function that does the work. crawls and records path, storing information to self.result
    
    # has different behavior for 3 categories of objects: `dict and list`:--> go inside, `all others`:--> dont go inside
    def crawl(self, obj, source):
        self.meta['current path'].append(source) # <-- record path upon entry

        def ifList(listArg):
            for n, item in enumerate(listArg):
                self.result.append({
                    'name':n,
                    'type':'list index',
                    'leads to':str(type(item)),
                    'source':source,
                    'group size':len(listArg),
                    'current path':self.meta['current path'] # <-- use path info
                    })
                
                self.crawl(item, n) # <-- does a recursion  (someone should invent the word "recurse" so that we can use it)

        def ifDict(dictArg):
            for k,v in dictArg.items():
                # store things
                self.result.append({
                    'name':k,
                    'type':'dictionary key',
                    'leads to':str(type(v)),
                    'source':source,
                    'group size':len(dictArg.keys()),
                    'current path':self.meta['current path'] # <-- use path info
                    })
                
                # recurse
                self.crawl(v, k)

        def ifElse(elseArg):
            self.result.append({
                'name':str(elseArg),
                'type':str(type(elseArg)),
                'leads to':None,
                'source':source,
                'current path':self.meta['current path'] # <-- use path info
                })
            # no recursion anymore, meaning it will "exit" the function, shortening the path and continuing in whatever structure it came from

        t = type(obj)
        if t == list:
            ifList(obj)
        elif t == dict:
            ifDict(obj)
        else:
            ifElse(obj)
        self.meta['current path'] = self.meta['current path'][:-1] # <-- shorten path upon exiting

    def __call__(self):
        self.result = []
        self.crawl(self.obj, '')
        return self.result

# example use below.
import json, copy
def open_json(filename):
    with open(filename, 'r', encoding="utf-8") as f:
        contents = json.load(f)
        f.close()
    return contents

def make_json(dic, filename):
    with open(filename, 'w', encoding="utf-8") as f:
        json.dump(dic, f, indent=4)
        f.close()

input_json = 'stampy.json'
c = Crawler(open_json(input_json))
result = c()
make_json(result, 'crawled.json')

