import requests, json, webbrowser
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
    t = YouTubeTranscriptApi.get_transcript(video_id)

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

def get_token():
    client_id = spotify_client_id
    client_secret = spotify_client_secret
    url = 'https://accounts.spotify.com/api/token'
    headers = {
        'Content-Type': 'application/x-www-form-urlencoded'
    }
    data = {
        'grant_type': 'client_credentials',
        'client_id': client_id,
        'client_secret': client_secret
    }

    response = requests.post(url, headers=headers, data=data)
    token = response.json()['access_token']
    return token

def get_jre_episodes():
    def parse_response(response):
        j = response.json()
        episodes = j['items']
        next_url = j['next']
        return episodes, next_url

    def parse_episode(e):
        d = {k:e[k] for k in ['description','duration_ms','external_urls','name','release_date','href']}
        d['thumbnail'] = e['images'][0]['url']
        d['id'] = e['external_urls']['spotify'].split('/')[-1]
        d['url'] = e['external_urls']['spotify']
        for k in ['external_urls']: # cleanup
            del d[k]
        return d

    class Episode:
        def __init__(self, e):
            self.d = parse_episode(e)
        def open(self):
            open_chrome_tab(self.d['url'])
        def __getitem__(self, k):
            return self.d[k]
        def __repr__(self):
            return json.dumps(self.d, indent=4)

    class Results:
        def __init__(self, response):
            episodes, next_url = parse_response(response)
            self.episodes = [Episode(e) for e in episodes]
            self.next_url = next_url
        def getmore(self):
            if self.next_url is None:
                print('No more episodes to get.')
                return False
            print(f'grabbing {self.next_url}')
            response = requests.get(self.next_url, headers=headers)
            episodes, next_url = parse_response(response)
            self.episodes += [Episode(e) for e in episodes]
            self.next_url = next_url
            return True
        def __getitem__(self, i):
            return self.episodes[i]
        def __len__(self):
            return len(self.episodes)

    headers = {
        'Authorization': 'Bearer ' + token
    }
    params = {
        'market': 'US',
        'limit': '50',
        'offset': '0'
    }
    ID = '4rOoJ6Egrf8K2IrywzwOMk'
    url = 'https://api.spotify.com/v1/shows/' + ID + '/episodes'
    response = requests.get(url, headers=headers, params=params)
    results = Results(response)
    return results

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
    def __init__(self, options):
        assert all([isinstance(option, CliOption) for option in options])
        self.options = options
    def start(self):
        def show():
            for i, option in enumerate(self.options):
                print(f'{i}: {option}' + ' ' + '/'.join([k for k in option.additional_functions.keys()]))

        while True:
            show()
            i = input('>>> ')
            if i == 'q':
                break
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
        Cli([Video(r) for r in res]).start()

class EpOption(CliOption):
    def __init__(self, ep):
        assert isinstance(ep, Ep)
        self.ep = ep
        self.additional_functions = {
            'ytres': self.ep.ytresults,
            'yt': self.ep.openyt,
            'google': self.ep.opengoogle,
        }
    def on_select(self):
        self.ep.open()
    def __repr__(self):
        return ', '.join([
            col('cy', self.ep['name']),
            col('ye', self.ep['description']),
        ])
print('all_jre.json is a pre-createdfile.')
with open('all_jre.json', 'r') as f:
    j = json.load(f)

Cli([EpOption(Ep(e)) for e in j[:100]]).start()
