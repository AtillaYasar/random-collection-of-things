import json, os

try:
    from colorama import init
    init()
    def col(ft, s):
        """For printing text with colors.
        
        Uses ansi escape sequences. (ft is "first two", s is "string")"""
        # black-30, red-31, green-32, yellow-33, blue-34, magenta-35, cyan-36, white-37
        u = '\u001b'
        numbers = dict([(string,30+n) for n, string in enumerate(('bl','re','gr','ye','blu','ma','cy','wh'))])
        n = numbers[ft]
        return f'{u}[{n}m{s}{u}[0m'
    colinstalled = True
except:
    colinstalled = False
    print('install colorama for colors')

def readfile(path):
    with open(path, 'r', encoding='utf-8') as f:
        if path.endswith('.json'):
            content = json.load(f)
        else:
            content = f.read()
    return content

def writefile(path, content):
    with open(path, 'w', encoding='utf-8') as f:
        if isinstance(content, (dict, list)):
            json.dump(content, f, indent=2)
        else:
            f.write(content)

class Clips:
    def __init__(self):
        mapperpath = 'cliptitle_to_ep.json'
        clipspath = 'clips.json'
        fullepspath = 'fulleps.json'

        mapper = readfile(mapperpath)
        clips = readfile(clipspath)
        fulleps = readfile(fullepspath)

        self.mapper = mapper
        self.clips = clips
        self.fulleps = fulleps
        
        # checking
        for c in self.clips:
            found = False
            title = c['title']
            ep_url = mapper[title]
            for ep in self.fulleps:
                if ep['link'] == ep_url:
                    found = True
                    break
            if not found:
                raise Exception(f'couldnt find full episode for {title}')
    
    def getep(self, cliptitle):
        ep_url = self.mapper[cliptitle]
        for ep in self.fulleps:
            if ep['link'] == ep_url:
                return ep
        raise Exception(f'couldnt find full episode for {cliptitle}')

    def cli(self):
        print("search for lex fridman clip titles, get the clip's link, episode title, episode link")
        while True:
            i = input('searchterm: ')
            i = i.lower()
            found = []
            for c in self.clips:
                if i in c['title'].lower():
                    title = c['title']
                    found.append(title)
            if len(found) == 0:
                print(f'no clips found with "{i}" in the title.')
            else:
                if colinstalled:
                    print('\n'.join([f'{col("ma", n+1)}. {title.lower().replace(i, col("cy",i))}' for n, title in enumerate(found)]))
                else:
                    print('\n'.join([f'{n+1}. {title}' for n, title in enumerate(found)]))
                print()
                print('write a number to get the clip link, episode title, episode link')
                i = input('choice: ')
                i = int(i)-1
                title = found[i]
                ep = self.getep(title)
                for c in self.clips:
                    if c['title'] == title:
                        cliplink = c['link']
                        break
                for string in [
                    f'clip link: {cliplink}',
                    f'episode title: {ep["title"]}',
                    f'episode link: {ep["link"]}',
                    '',
                ]:
                    print(string)

if __name__ == '__main__':
    # source code for creating this folder is a little messier, not sure if ill share.
    print('this database was created using this clips playlist "https://www.youtube.com/playlist?list=PLrAXtmErZgOeciFP3CBCIEElOJeitOr41",\nthis episodes playlist "https://www.youtube.com/playlist?list=PLrAXtmErZgOdP_8GztsuKi9nrraNbKKp4",\nand this library "https://pypi.org/project/youtube-search-python/"')
    print('-'*10)
    Clips().cli()
