from youtubesearchpython import Playlist
import webbrowser
import random

def col(ft, s):
    """For printing text with colors.
    
    Uses ansi escape sequences. (ft is "first two", s is "string")"""
    # black-30, red-31, green-32, yellow-33, blue-34, magenta-35, cyan-36, white-37
    u = '\u001b'
    numbers = dict([(string,30+n) for n, string in enumerate(('bl','re','gr','ye','blu','ma','cy','wh'))])
    n = numbers[ft]
    return f'{u}[{n}m{s}{u}[0m'

def get_yt_playlist(url):
    # from youtubesearchpython import Playlist
    
    playlist = Playlist(url)

    while playlist.hasMoreVideos:
        playlist.getNextVideos()

    nicer = []
    for item in playlist.videos:
        title = item['title']
        link = item['link']
        listless = link.partition('&list=')[0]
        nicer.append((title, listless))
    return nicer

def open_chrome_tab(url):
    #import webbrowser

    chrome_path = r"C:\Program Files\Google\Chrome\Application\chrome.exe"

    webbrowser.register('chrome', None, webbrowser.BackgroundBrowser(chrome_path))
    webbrowser.get('chrome').open_new_tab(url)

def search_google(search_term):
    search_term = search_term.replace(' ', '+')
    url = f'https://www.google.com/search?q={search_term}'
    open_chrome_tab(url)

# can feed playlist url via sys.argv or input() if you want.

# get playlist
url = 'https://www.youtube.com/playlist?list=PLYpZzg5x9QczXFsI-0G5z6npJl9vqymHW'
top_n = 10
playlist = get_yt_playlist(url)

# start cli
while True:
    # shuffle and display choices
    random.shuffle(playlist)
    for n, item in enumerate(playlist[:top_n]):
        title, link = item
        print(', '.join([
            col('gr', f'({n+1})'),
            col('cy', title),
            link,
        ]))
    print('---')

    while True:
        # get choice
        i = input('write a number to pick, or r to reshuffle. ')
        if i == 'r':
            break
        try:
            choice = playlist[int(i)-1]
        except:
            print('invalid input')
            continue

        # open video and search lyrics
        title, link = choice
        open_chrome_tab(link)
        search_google(f'{title} lyrics')

