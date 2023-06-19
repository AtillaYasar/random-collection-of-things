import json
from youtubesearchpython import *

# wrapper around https://github.com/alexmercerind/youtube-search-python
# thanks to mister "alexmercerind" for building the wrapper. go sponsor him!

def get_yt_comments(id_or_url, max_call_count=None):
    # from youtubesearchpython import *

    """
    id_or_url: youtube video id or url, but sometimes id doesnt work.
    max_call_count: if None, will repeat api calls until no more comments, each call retrieves 20 comments
    """

    comments = Comments(id_or_url)

    # repeat api calls until no more comments
    if max_call_count == None:
        while comments.hasMoreComments:
            comments.getNextComments()
    else:
        iterations = 0
        while comments.hasMoreComments and iterations <= max_call_count:
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

def get_yt_playlist(url):
    # from youtubesearchpython import *

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

url = 'https://www.youtube.com/playlist?list=PLRBp0Fe2GpgmsW46rJyudVFlY6IYjFBIK'

"""
# retrieving videos from a channel
from youtubesearchpython import *

channel_id = "UC_aEa8K-EOJ3D6gOs7HcyNg"
playlist = Playlist(playlist_from_channel_id(channel_id))

print(f'Videos Retrieved: {len(playlist.videos)}')

while playlist.hasMoreVideos:
    print('Getting more videos...')
    playlist.getNextVideos()
    print(f'Videos Retrieved: {len(playlist.videos)}')

print('Found all the videos.')"""

def get_yt_channelvids(channel_id):
    # from youtubesearchpython import *

    playlist = Playlist(playlist_from_channel_id(channel_id))

    while playlist.hasMoreVideos:
        playlist.getNextVideos()

    nicer = []
    for item in playlist.videos:
        title = item['title']
        link = item['link']
        listless = link.partition('&list=')[0]
        nicer.append((title, listless))
    return nicer

#print(json.dumps(get_yt_channelvids('UC_aEa8K-EOJ3D6gOs7HcyNg'), indent=4))

def get_yt_search(query):
    # from youtubesearchpython import VideosSearch

    # to get more pages: `search.next()` to essentially expand `search.search()['result']`

    search = VideosSearch(query)
    items = []
    for item in search.result()['result']:
        ID = item['id']
        title = item['title']
        views = item['viewCount']['short']
        duration = item['duration']
        published = item['publishedTime']

        channelname = item['channel']['name']
        channelid = item['channel']['id']
        channellink = item['channel']['link']

        items.append({
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

# example usecase. get top 5 comments of 10 results of a query.
# note: throws some errors, doesnt fully work.
query = 'canada goose'
results = get_yt_search(query)
for result in results[:10]:
    print(result['title'])
    comments = get_yt_comments(result['id'], max_call_count=1)
    for comment in comments[:5]:
        print(f'\tlikes: {comment["likes"]}, username: {comment["username"]}')
        print(f'\t{comment["text"]}')
        print('---')
    print()

