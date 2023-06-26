from youtubesearchpython import Playlist, Video, ResultMode, VideosSearch, Comments
import json, os, threading, time, sys
from secret_things import openai_key
import openai

def make_json(dic, filename):
    with open(filename, 'w', encoding="utf-8") as f:
        json.dump(dic, f, indent=2)
        f.close()

def col(ft, s):
    """For printing text with colors.
    
    Uses ansi escape sequences. (ft is "first two", s is "string")"""
    # black-30, red-31, green-32, yellow-33, blue-34, magenta-35, cyan-36, white-37
    u = '\u001b'
    numbers = dict([(string,30+n) for n, string in enumerate(('bl','re','gr','ye','blu','ma','cy','wh'))])
    n = numbers[ft]
    return f'{u}[{n}m{s}{u}[0m'

def open_json(filename):
    with open(filename, 'r', encoding="utf-8") as f:
        contents = json.load(f)
        f.close()
    return contents

def get_yt_comments(id_or_url, max_call_count=None):
    # from youtubesearchpython import VideosSearch

    """
    id_or_url: youtube video id or url, but sometimes id doesnt work.
    max_call_count: if None, will repeat api calls until no more comments, each call retrieves 20 comments
    """

    print(f'getting comments from {id_or_url}...')
    inputargs = {'id_or_url':id_or_url, 'max_call_count':max_call_count}

    cached = cacher.get(inputargs)
    if cached == None:
        try:
            comments = Comments(id_or_url)
        except:
            cacher.add({'id_or_url':id_or_url, 'max_call_count':max_call_count}, [])
            return []

        # repeat api calls until no more comments
        if max_call_count == None:
            while comments.hasMoreComments:
                comments.getNextComments()
        else:
            iterations = 0
            while comments.hasMoreComments and iterations < max_call_count:
                comments.getNextComments()
                #count = len(comments.comments["result"])
                #print(f'Comments Retrieved: {count}')
                iterations += 1

        # now reshape the data for convenience

        # helper for sorting by likes
        def get_likes(item):
            text = item['votes']['simpleText']
            if text == None:
                return 0
            elif 'K' in text:
                return int(float(text.replace('K', '')) * 1000)
            elif 'M' in text:
                return int(float(text.replace('M', '')) * 1000000)
            else:
                return int(text)
        sorted_by_likes = sorted(
            comments.comments['result'],
            key=lambda x: get_likes(x),
            reverse=True
        )

        nicer = []
        for comment in sorted_by_likes:
            comment_id = comment['id']
            username = comment['author']['name']
            likes = comment['votes']['simpleText']
            text = comment['content']
            published = comment['published']

            nicer.append({
                'comment_id': comment_id,
                'username': username,
                'likes': likes,
                'text': text,
                'published': published,
            })

        cacher.add(inputargs, nicer)

        return nicer
    else:
        nicer = cached
        return nicer

def vidinfo(url):
    # from youtubesearchpython import Video, ResultMode
    video = Video.getInfo(url, mode = ResultMode.json)

    to_return = {
        'title': video['title'],
        'seconds': video['duration']['secondsText'],
        'views': video['viewCount']['text'],
        'description': video['description'],
        'upload_date': video['uploadDate'],
        'category': video['category'],
        'keywords': video['keywords'],
        'link': video['link'],
        'channelname': video['channel']['name'],
        'channellink': video['channel']['link'],
    }

    comments = get_yt_comments(url, 1)
    '''comments = [c['text'] for c in comments[:10]]
    comments = '\n'.join(comments)'''
    to_return['comments'] = comments
    return to_return

openai.api_key = openai_key
def use_chatgpt_stream(messages, printfunc):
    response = openai.ChatCompletion.create(
        model='gpt-3.5-turbo',
        messages=messages,
        temperature=0.5,
        stream=True
    )

    collection = []
    for chunk in response:
        delta = chunk['choices'][0]['delta']
        if delta == {}:
            break
        elif 'role' in delta:
            continue
        elif 'content' in delta:
            printfunc(delta['content'])
            collection.append(delta['content'])

    response = ''.join(collection)
    return response

def printfunc(s):
    sys.stdout.write(s)
    sys.stdout.flush()

def chatgpt_youtube(url, docli=True):
    # putting the above into a function.
    # requires: use_chatgpt_stream, vidinfo

    # helper functions
    def get_info(url):
        def stringify_comments(comments):
            lines = []
            for c in comments[:]:
                username = c['username']
                likes = c['likes']
                text = c['text']
                lines.append(f'"{username}": {text}')
            return '\n'.join(lines)
        info = vidinfo(url)
        if 'comments' in info:
            info['comments'] = stringify_comments(info['comments'])
        
        lines = []
        for key, value in info.items():
            lines.append(f'{key}: {value}')
        return '\n'.join(lines)

    def make_messages(info):
        return [
            {
                'role': 'user',
                'content': '\n'.join([
                    'hey. i have some info about a video, and i want you to tell me some more interesting things about it. like extra context or trivia or background info of anything related to the video',
                    'video info:',
                    info,
                    '',
                    'Some additional interesting things about this video:',
                ])
            }
        ]
    def chatgpt_caller(messages):
        def printfunc(s):
            sys.stdout.write(s)
            sys.stdout.flush()
        response = use_chatgpt_stream(messages, printfunc)
        return response
    def messagestostring(messages):
        seperator = col('gr', '\n---\n')
        return seperator.join([message['content'] for message in messages])

    info = get_info(url)
    messages = make_messages(info)
    convid = time.time()
    if docli:
        commands = {
            's': 'show the conversation so far',
            'q': 'quit the conversation',
        }
        print(json.dumps(commands, indent=4))
        while docli:
            response = chatgpt_caller(messages)
            messages.append({
                'role': 'user',
                'content': response
            })
            make_json(messages, f'{backup_folder}/{convid}.json')
            print('\n-----------------------------\nwrite a command or a prompt.')
            while True:
                i = input()
                if i == 'q':
                    docli = False
                    break
                elif i == 's':
                    print(messagestostring(messages))
                    continue
                else:
                    messages.append({
                        'role': 'user',
                        'content': i
                    })
                    break
    else:
        response = chatgpt_caller(messages)
        print(response)

class Cache:
    # intended for storing API calls and downloads that take a long time

    def __init__(self, filename):
        self.filename = filename
        if not os.path.exists(self.filename):
            with open(self.filename, 'w') as f:
                json.dump([], f)
        self.cache = self.load_cache()
        self.lock = threading.Lock()  # create a lock object

    def load_cache(self):
        cache = open_json(self.filename)
        items = []
        for item in cache:
            if item not in items:
                items.append(item)
        return items

    def save_cache(self):
        with self.lock:  # acquire the lock
            make_json(self.cache, self.filename)
            print(f'saved to {self.filename}')
        # release the lock

    def get(self, inp):
        #print(f'{col("cy", "trying to get inp=")}{inp}')
        for item in self.cache:
            if item['input'] == inp:
                #print(f'{col("cy", "found inp=")}{inp}')
                return item['output']
        #print(col('cy', 'not found'))
        return None

    def add(self, inp, outp):
        print(f'{col("cy", "adding inp=")}{inp}, {col("cy", "outp=")}{outp}')
        self.cache.append({'input':inp, 'output':outp})
        self.save_cache()

backup_folder = 'chatbackup'
if not os.path.exists(backup_folder):
    os.mkdir(backup_folder)
url = "https://www.youtube.com/watch?v=ArHg1d40Zt8&ab_channel=RetiredPlayersAssociation"
cacher = Cache('cache.json')
chatgpt_youtube(url)
