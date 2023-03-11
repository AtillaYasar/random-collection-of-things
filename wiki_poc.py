import wikipedia
import wikipediaapi, json

def get_wikiapi_object(title):
    obj = wikipediaapi.Wikipedia('en').page(title)
    return obj

def show_page(query):
    ind = ' '*4
    obj = get_wikiapi_object(query)
    print(col('ma', obj.title))
    print('------')
    last_n = None
    for s in obj.sections:
        #print(type(s))  # class WikipediaPageSection
        print(col('ye', s.title))
        subsections = s.sections
        if len(subsections) == 0:
            print(col('cy', f'{ind}- no subsections'))
            if last_n == None:
                pass
            else:
                print('\n'.join(f'{ind}{line}' for line in s.text[0:last_n].split('\n')))
        else:
            for sub in subsections:
                print(col('cy', f'{ind}-{sub.title}'))
                subsubsections = sub.sections
                if len(subsubsections) == 0:
                    print(col('gr', f'{ind*2}- no subsubsections'))
                    if last_n == None:
                        pass
                    else:
                        print('\n'.join(f'{ind*2}{line}' for line in sub.text[0:last_n].split('\n')))
                else:
                    for subsub in subsubsections:
                        print(col('gr', f'{ind*2}- subsub count:{len(subsub.sections)}'))

        print('---')

def show_specific(lst):
    assert type(lst) is list
    assert len(lst) > 0 and len(lst) < 4
    for item in lst:
        assert type(item) is str

    finding = None

    if len(lst) == 0:
        raise Exception
    
    page_name = lst[0]
    page_name = page_name.replace(' ', '_')
    obj = get_wikiapi_object(page_name)
    assert obj.exists()

    if len(lst) == 1:
        finding = obj.text
    elif len(lst) == 2:
        subt_name = lst[1]
        for s in obj.sections:
            if s.title == subt_name:
                finding = s.full_text()
    elif len(lst) == 3:
        subt_name = lst[1]
        sub_subt_name = lst[2]
        for s in obj.sections:
            if s.title == subt_name:
                for subsection in s.sections:
                    if subsection.title == sub_subt_name:
                        finding = subsection.full_text()
    else:
        print(col('re', 'wrong argument'))
    
    if finding == None:
        return None
    else:
        return finding

'''
class WikipediaPageSection

level
    Returns indentation level of the current section.
text
    ATTRIBUTE: text of the current section. not a function.
sections
    Returns subsections of the current section.
section_by_title
    Returns subsections of the current section with given title.
full_text
    Returns text of the current section as well as all its subsections.
        doesnt work for full page, have to use text instead.
'''

def col(ft, s):
    """For printing text with colors.
    
    Uses ansi escape sequences. (ft is "first two", s is "string")"""
    # black-30, red-31, green-32, yellow-33, blue-34, magenta-35, cyan-36, white-37
    u = '\u001b'
    numbers = dict([(string,30+n) for n, string in enumerate(('bl','re','gr','ye','blu','ma','cy','wh'))])
    n = numbers[ft]
    return f'{u}[{n}m{s}{u}[0m'

class WikiHandler:
    def __init__(self):
        self.commands = {
            'search':self.w_search,
            'summary':self.w_summary,
        }
    def w_search(self, arg):
        res = wikipedia.search(arg, suggestion=False)
        for title in res:
            print(f'title:{title}', wikipedia.page(title=title))
        return None
    def w_summary(self, arg):
        return wikipedia.summary(arg)

def search_something(initial_query):
    wiki_handler = WikiHandler()
    query = initial_query
    results = wikipedia.search(query, suggestion=False)  # returns a list of strings
    print(f'results:{results}')
    assert type(results) is list
    for r in results:
        assert type(r) is str

    ind = ' '*4
    print('----------')
    for r in results:
        print(col('ma', r))
        try:
            page_object = wikipedia.page(title=r, redirect=False, auto_suggest=False)
        except wikipedia.DisambiguationError:
            print(col('cy', f'{ind}got a DisambiguationError'))
        else:            
            print(col('cy', f'{ind}page_object.title:{page_object.title}'))

        print('---')
    print('----------')

tuples = (
    (
        'search',
        'to find a wiki page',
        [
            'search flowers for winter',
        ],
        search_something,
    ),
    (
        'hierarchy',
        "to show a page's hierarchy of sections and subsections",
        [
            'hierarchy Plumeria',
        ],
        show_page,
    ),
    (
        'content',
        'to show a specific part of the page, can have up to two subsection titles.',
        [
            'content Starship Troopers',
            'content Starship Troopers.Themes',
            'content Starship Troopers.Themes.Militarism',
        ],
        show_specific,
    ),
)
mapping = {t[0]:t[3] for t in tuples}
print(f'mapping:{mapping}')
ind = ' '*4
colors = ['ma', 'ye', 'ye']

def print_surrounded(string):
    edge = '-_'*30
    print(col('gr', edge))
    print(string)
    print(col('gr', edge))

while True:
    for cmd, description, examples, function in tuples:
        print('command: ' + col(colors[0], cmd))
        print(f'{ind}description: ' + col(colors[1], description))
        print(f'{ind}examples: ' + ' or '.join([col(colors[2], f'{ex}') for ex in examples]))
        print()
    print('...')
    i = input()

    cmd, _, rest = i.partition(' ')
    func = mapping.get(cmd, None)
    if func == None:
        print(col('re', f'the "{cmd}" command does not exist. try again.'))
        print()
    else:
        if func == search_something:
            edge = '-_'*30
            print(col('gr', edge))
            func(rest)
            print(col('gr', edge))
            print({
                'func':func,
                'rest':rest,
            })
        elif func == show_page:
            rest = rest.replace(' ', '_')

            edge = '-_'*30
            print(col('gr', edge))
            func(rest)
            print(col('gr', edge))
            
            print({
                'func':func,
                'rest':rest,
            })
        elif func == show_specific:
            terms = rest.split('.')
            
            edge = '-_'*30
            print(col('gr', edge))
            print(func(terms))
            print(col('gr', edge))

            print({
                'func':func,
                'terms':terms,
            })
        

