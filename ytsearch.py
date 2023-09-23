from youtubesearchpython import *
import json, random, os, sys, time
import webbrowser
from vidchat import chatgpt_youtube  # https://github.com/AtillaYasar/random-collection-of-things/blob/main/vidchat.py
from youtube_transcript_api import YouTubeTranscriptApi  # only used in get_transcript

def get_transcript(url):
    video_id = url.split('v=')[1]
    t = YouTubeTranscriptApi.get_transcript(video_id)

    class Transcript(list):
        def get_timerange(self, start, end):
            # grabs a subset of the transcript
            def t_to_s(t):
                # t is in the format of 'hh:mm:ss'
                h, m, s = t.split(':')
                return int(h) * 3600 + int(m) * 60 + int(s)
            in_seconds = ':' not in start
            if not in_seconds:
                start = t_to_s(start)
                end = t_to_s(end)

            subset = [i for i in self if i['start'] >= start and i['start'] <= end]
            lines = [i['text'] for i in subset]
            return '\n'.join(lines)

    return Transcript(t)

def vidinfo(url, get_comments=True):
    # from youtubesearchpython import Video, ResultMode
    # returns info about a video
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
        'channelid': video['channel']['id'],
    }

    if get_comments:
        comments = get_yt_comments(url, 1)
        comments = [c['text'] for c in comments[:10]]
        comments = '\n'.join(comments)
        to_return['comments'] = comments
    return to_return

def vid_to_channelid(url):
    return vidinfo(url)['channelid']

def yt_channelvids(channelid, maxvids=None):
    # from youtubesearchpython import Playlist
    # returns videos
    playlist = Playlist(playlist_from_channel_id(channelid))
    if maxvids == None:
        while playlist.hasMoreVideos:
            playlist.getNextVideos()
    else:
        while playlist.hasMoreVideos and len(playlist.videos) < maxvids:
            playlist.getNextVideos()
    
    nicer = []
    for item in playlist.videos:
        nicer.append({
            'title': item['title'],
            'link': item['link'].partition('&list=')[0],
            'duration': item['accessibility']['duration'],
            'views': 0,  # views not available in playlist
            'channelname': item['channel']['name'],
            'channelid': item['channel']['id'],
            'channellink': item['channel']['link'],
        })

    return nicer

def yt_suggestions(query):
    # from youtubesearchpython import Suggestions, ResultMode
    # returns search terms
    suggestions = Suggestions(language = 'en', region = 'US')
    return suggestions.get(query, mode = ResultMode.json)

def bla():
    #from youtubesearchpython import Hashtag

    hashtag = Hashtag('ncs', limit = 1)

    print(hashtag.result())

def yt_search(query, maxvids=100):
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

def get_yt_comments(id_or_url, maxcomments=None):
    # from youtubesearchpython import VideosSearch

    # returns comments from a video

    """
    id_or_url: youtube video id or url, but sometimes id doesnt work.
    max_call_count: if None, will repeat api calls until no more comments, each call retrieves 20 comments
    """

    try:
        comments = Comments(id_or_url)
    except:
        return []

    # repeat api calls until no more comments
    if maxcomments == None:
        while comments.hasMoreComments:
            comments.getNextComments()
    else:
        while len(comments.comments["result"]) < maxcomments and comments.hasMoreComments:
            comments.getNextComments()

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

    return nicer

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

def start_cli_old(url, top_n):
    playlist = get_yt_playlist(url)
    print(f'total links: {len(playlist)}')
    while True:
        # shuffle and display choices
        lines = []
        lines.append(col('ma', '-'*20))
        random.shuffle(playlist)
        for n, item in enumerate(playlist[:top_n]):
            title, link = item
            lines.append(', '.join([
                col('gr', f'({n+1})'),
                col('cy', title),
                link,
            ]))
        lines.append(col('ma', '-'*20))
        print('\n'.join(lines))

        while True:
            # get choice
            i = input('write a number to pick, or r to reshuffle, or chat to chat. ')
            if '.' in i:
                choice = ['', i]
                print('assuming url, opening in chrome')
            elif i == 'chat':
                # will use the previous choice
                chatgpt_youtube(link, docli=True)
                open_chrome_tab(link)
                # search_google(f'{title}')  not sure what google search to do.
                break
            else:
                if i == 'r':
                    break
                try:
                    choice = playlist[int(i)-1]
                except:
                    print('invalid input')
                    continue

            # open video and search lyrics
            title, link = choice
            search_google(f'{title} lyrics')
            open_chrome_tab(link)

def open_chrome_tab(url):
    #import webbrowser

    chrome_path = r"C:\Program Files\Google\Chrome\Application\chrome.exe"

    webbrowser.register('chrome', None, webbrowser.BackgroundBrowser(chrome_path))
    webbrowser.get('chrome').open_new_tab(url)

def search_google(search_term):
    search_term = search_term.replace(' ', '+')
    url = f'https://www.google.com/search?q={search_term}'
    open_chrome_tab(url)

def coloredlist(lst):
    cols = ['ye', 'cy']
    strings = []
    for n, item in enumerate(lst):
        strings.append(col(cols[n%2], item))
    return ', '.join(strings)

def start_cli(videos, n):
    def display_videos(top_n):
        lines = []
        lines.append(col('ma', '-'*20))
        for n, item in enumerate(videos[:top_n]):

            values = coloredlist([
                item['title'],
                item['channelname'],
                item['views'],
                item['duration'],
            ])

            lines.append(', '.join([
                col('gr', f'({n+1})'),
                values,
            ]))
        lines.append(col('ma', '-'*20))
        print('\n'.join(lines))

    print(f'total videos: {len(videos)}')
    commands = {
        'r': 'shuffle',
        'number': 'pick a video',
        'q': 'quit',
    }
    commandsstring = ', '.join([f'{col("gr", k)}: {v}' for k, v in commands.items()])
    while True:
        # shuffle and display choices
        display_videos(n)

        while True:
            # get choice
            print(commandsstring)
            i = input()

            if i == 'r':
                random.shuffle(videos)
                break
            elif i == 'q':
                return
            else:
                try:
                    choice = videos[int(i)-1]
                except:
                    print('invalid input')
                    continue

            title = choice['title']
            link = choice['link']
            #search_google(f'{title} lyrics')
            open_chrome_tab(link)
            chatgpt_youtube(link, docli=True)

def get_yt_playlist(url):
    # from youtubesearchpython import Playlist
    
    playlist = Playlist(url)

    while playlist.hasMoreVideos:
        playlist.getNextVideos()

    nicer = []
    for item in playlist.videos:
        nicer.append({
            'title': item['title'],
            'link': item['link'].partition('&list=')[0],
            'duration': item['accessibility']['duration'],
            'views': 0,  # views not available in playlist
            'channelname': item['channel']['name'],
            'channelid': item['channel']['id'],
            'channellink': item['channel']['link'],
        })
    return nicer

top_n = 20
args = sys.argv[1:]

searchtype = args[0]
if searchtype == 'playlist':
    url = args[1]
    videos = get_yt_playlist(url)
    start_cli(videos, top_n)
elif searchtype == 'channel':
    url = args[1]
    channelid = vid_to_channelid(url)
    videos = yt_channelvids(channelid)
    start_cli(videos, top_n)
elif searchtype == 'search':
    searchterm = ' '.join(args[1:])
    videos = yt_search(searchterm, 200)
    start_cli(videos, top_n)

