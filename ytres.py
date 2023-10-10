import requests, json, webbrowser, sys
import urllib.parse
from youtubesearchpython import VideosSearch
from abc import ABC, abstractmethod
from youtube_transcript_api import YouTubeTranscriptApi
from secrets import natdev_session

from secrets import spotify_client_id, spotify_client_secret
from colorama import init
init()

def nat_dev(model, prompt, print_func=lambda token:print(token, end='', flush=True), mock=False):

    # prepare request
    url = "https://nat.dev/api/inference/text"

    if model in ['llama', 'llama70b-v2-chat', 'llama70b-v2', 'llama70b']:
        name = 'replicate:llama70b-v2-chat'
        tag = 'replicate:llama70b-v2-chat'
        provider = 'replicate'
    else:
        name = model
        tag = f'openai:{model}'
        provider = 'openai'
    payload_dict = {
        "prompt": prompt,
        "models": [
            {
                "name": name,
                "tag": tag,
                "capabilities": ["chat"],
                "provider": provider,
                "parameters": {
                    "temperature": 0.5,
                    "maximumLength": 400,
                    "topP": 1,
                    "presencePenalty": 0,
                    "frequencyPenalty": 0,
                    "stopSequences": [],
                    "numberOfSamples": 1,
                },
                "enabled": True,
                "selected": True,
            }
        ],
        "stream": True,
    }
    if provider == 'replicate':
        payload_dict['models'][0]['parameters']['repetitionPenalty'] = 1
        del payload_dict['models'][0]['parameters']['presencePenalty']
        del payload_dict['models'][0]['parameters']['frequencyPenalty']

    payload = json.dumps(payload_dict)
    session = natdev_session
    headers = {
        "Content-Type": "text/plain;charset=UTF-8",
        "Accept": "*/*",
        "Referer": "https://nat.dev/",
        "Origin": "https://nat.dev",
        "Sec-Fetch-Dest": "empty",
        "Sec-Fetch-Mode": "cors",
        "Sec-Fetch-Site": "same-origin",
        "Cookie": f"__session={session}",
    }
    if mock:
        with open('mock.json', 'w') as f:
            f.write(json.dumps(payload_dict, indent=4))
            f.write('\n\n')
            f.write(payload_dict['prompt'])
        print_func('mock response')
        return 'mock response'

    response = requests.post(url, headers=headers, data=payload, stream=True)

    # collect tokens, use print_func
    all_tokens = []
    for line in response.iter_lines():
        if line == b'event:status':
            continue
        else:
            data = str(line, 'utf-8').partition('data:')[2]
            if data == '':
                continue
            token = json.loads(data)['token']
            if token == '[INITIALIZING]':
                continue
            if token == '[COMPLETED]':
                break
            else:
                print_func(token)
                all_tokens.append(token)
    return ''.join(all_tokens)

def col(ft, s):
    """For printing text with colors.
    
    Uses ansi escape sequences. (ft is "first two", s is "string")"""
    # black-30, red-31, green-32, yellow-33, blue-34, magenta-35, cyan-36, white-37
    u = '\u001b'
    numbers = dict([(string,30+n) for n, string in enumerate(('bl','re','gr','ye','blu','ma','cy','wh'))])
    n = numbers[ft]
    return f'{u}[{n}m{s}{u}[0m'

def bgcol(ft, s):
    u = '\u001b'
    numbers = dict([(string,40+n) for n, string in enumerate(('bl','re','gr','ye','blu','ma','cy','wh'))])
    n = numbers[ft]
    return f'{u}[{n}m{s}{u}[0m'

def yt_search(query, maxvids=5):
    # from youtubesearchpython import VideosSearch
    # returns videos

    search = VideosSearch(query, limit=20)

    # get all pages
    full = []
    full += search.result()['result']
    loopcount = 0
    while len(full) < maxvids:
        search.next()
        full += search.result()['result']

    items = []
    # get nicer representation
    for item in full:
        ID = item['id']
        title = item['title']
        published = item['publishedTime']
        thumbnails = item['thumbnails']
        link = item['link']
        views = item['viewCount']['short']
        duration = item['accessibility']['duration']

        channelname = item['channel']['name']
        channelid = item['channel']['id']
        channellink = item['channel']['link']

        items.append({
            'link': link,
            'thumbnails': thumbnails,
            'id': ID,
            'title': title,
            'views': views,
            'duration': duration,
            'published': published,
            'channelname': channelname,
            'channelid': channelid,
            'channellink': channellink,
        })
    
    return items

def get_transcript(url):
    video_id = url.split('v=')[1]
    t = YouTubeTranscriptApi.get_transcript(video_id, languages=['en'])

    class Transcript(list):
        def __init__(self, t):
            super().__init__(t)
            self.duration = t[-1]['start'] + t[-1]['duration']

        def get_timerange(self, start, end):
            # grabs a subset of the transcript, can pass seconds or 'hh:mm:ss' strings
            def t_to_s(t):
                h, m, s = t.split(':')
                return int(h) * 3600 + int(m) * 60 + int(s)
            in_seconds = type(start) in (int, float)
            if not in_seconds:
                start = t_to_s(start)
                end = t_to_s(end)
            subset = [i for i in self if i['start'] >= start and i['start'] <= end]
            lines = [i['text'] for i in subset]
            return '\n'.join(lines)

        def get_full_text(self):
            return '\n'.join([i['text'] for i in self])

    return Transcript(t)

def open_chrome_tab(url):
    #import webbrowser

    chrome_path = r"C:\Program Files\Google\Chrome\Application\chrome.exe"
    webbrowser.register('chrome', None, webbrowser.BackgroundBrowser(chrome_path))
    webbrowser.get('chrome').open_new_tab(url)

def search_google(search_term):
    search_term = urllib.parse.quote(search_term)
    url = f'https://www.google.com/search?q={search_term}'
    open_chrome_tab(url)

def search_youtube(search_term):
    search_term = urllib.parse.quote(search_term)
    url = f'https://www.youtube.com/results?search_query={search_term}'
    open_chrome_tab(url)

"""
token = get_token()
r = get_jre_episodes()
while True:
    ret = r.getmore()
    if not ret:
        break

print(len(r))  # prints 2199, which is more than there are jre episodes, maybe because there are also fight companion episodes
"""

class CliOption(ABC):
    @abstractmethod
    def on_select(self):
        pass
    @abstractmethod
    def __repr__(self):
        pass

class Video(CliOption):
    def __init__(self, d):
        self.d = d
        self.additional_functions = {
            'summary': self.get_summary,
        }
    def on_select(self):
        open_chrome_tab(self.d['link'])
    def get_summary(self):
        t = get_transcript(self.d['link']).get_full_text()
        prompt = '\n'.join([
            'I will give you a transcript of a youtube video, and I want you to tell me everything that is being talked about.',
            '---',
            t,
            '---',
        ])
        def print_func(token):
            if token.startswith(' '):
                to_print = col('cy', token[:3]) + token[3:]
            else:
                to_print = token
            print(to_print, end='', flush=True)
        summary = nat_dev('gpt-3.5-turbo-instruct', prompt, print_func)
        print()

    def __repr__(self):
        return ', '.join([
            col('ma', self.d['title']),
            col('ye', self.d['views']),
            col('gr', self.d['duration']),
        ])

class Cli:
    def __init__(self, options, pagesize=10, pagenum=0, title=None):
        assert all([isinstance(option, CliOption) for option in options])
        self.options = options
        self.pagenum = pagenum
        self.pagesize = pagesize
        if title == None:
            self.title = f'untitled, {len(self.options)} options'
        else:
            self.title = title
    def start(self):
        def show():
            lines = []
            middlelines = []
            for i, option in enumerate(self.options[self.pagenum*self.pagesize:(self.pagenum+1)*self.pagesize]):
                middlelines.append(f'{i+self.pagenum*self.pagesize}: {option}' + ' ' + '/'.join([k for k in option.additional_functions.keys()]))

            edge = col('wh', bgcol('blu', '~'*20+self.title+'~'*20))
            lines.append(edge)
            lines += middlelines
            lines.append(edge)
            print('\n'.join(lines))

        while True:
            show()
            i = input('>>> ')
            if i == 'q':
                break
            elif i == 'p':
                self.pagenum -= 1
                continue
            elif i == 'n':
                self.pagenum += 1
                continue
            args = i.split(' ')
            try:
                self.options[int(args[0])]
            except:
                print('invalid input')
                continue
            else:
                if len(args) == 1:
                    self.options[int(i)].on_select()
                elif len(args) == 2:
                    self.options[int(args[0])].additional_functions[args[1]]()

class Ep:
    def __init__(self, d):
        self.d = d
    def open(self):
        open_chrome_tab(self['url'])
    def __getitem__(self, k):
        return self.d[k]
    def __repr__(self):
        return json.dumps(self.d, indent=4)
    def openyt(self):
        search_youtube(self['name'])
    def opengoogle(self):
        search_google(self['name'])
    def ytresults(self):
        res = yt_search(self['name'], 5)
        Cli(
            [Video(r) for r in res],
            pagesize=10,
            title=self['name']
        ).start()

def ytresults(query):
    res = yt_search(query, 5)
    Cli(
        [Video(r) for r in res],
        pagesize=10,
        title=query
    ).start()

query = ' '.join(sys.argv[1:])
ytresults(query)
