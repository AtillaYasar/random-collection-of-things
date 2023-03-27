from pytube import YouTube, Playlist
from overall_imports import*
import json, os, sys

# making something beautiful into something ugly, for the sake of convenience..
class PytubeHandler:
    """Reducing the pytube api down to a couple simple things I want to do with it."""

    def __init__(self):
        self.downloadables = []

    def get_stuff_from_link(self, link:str, to_get:[
        'title', 'description', 'channel url', 'length', 'downloadables',
    ]):
        """
        Will return a dictionary containing info about the linked Youtube video.

        Steps:
        - define contents of result  (with to_get)
        - get things from Youtube object
        - get things from Streams and StreamsQuery objects
        - use to_get to pick from the gathered info
        """

        # define what the result contains
        result = {}
        # to_get = ['title', 'description', 'channel url', 'length', 'downloadables']

        # things from the YouTube object
        yt = YouTube(link)  # pytube.YouTube object        
        title = yt.title
        channel_url = yt.channel_url
        description = yt.description
        length = yt.length  # in seconds
        thumbnail_url = yt.thumbnail_url
        vid_info = yt.vid_info

        # things from the Streams and StreamsQuery objects
        sq = yt.streams  # StreamsQuery object
        sq_f = sq.filter(progressive=True)  # filter for progressive. will limit to 720p, and make sjws happy
        from_stream = []
        for item in sq_f:
            from_stream.append({
                'stream object': item,
                'title': item.title,
                'resolution': item.resolution,
            })

        # use to_get to .... get things.
        available_things = {
            'title': title,
            'channel url': channel_url,
            'description': description,
            'length': length,
            'thumbnail url': thumbnail_url,
            'vid info': vid_info,
            'downloadables': from_stream,
        }
        for k,v in available_things.items():
            if k in to_get:  # filter using to_get
                result[k] = v
        return result
    
    def download_720p(self, link:str, folderpath=None):
        """Easy version of the full downloading capabilities."""

        success = False
        downloadables = self.get_stuff_from_link(link, ['title', 'downloadables'])['downloadables']
        for item in downloadables:
            if item['resolution'] == '720p':
                print(f'start downloading {item["title"]}')
                if folderpath == None:
                    item['stream object'].download()
                else:
                    item['stream object'].download(output_path = folderpath)
                success = True
                break

        if success:
            print(f'download of {item["title"]} finished')
        else:
            print(f'could not get 720p for {item["title"]}')

def download_playlist(handler_object, link):
    """Uses PytubeHandler.download_720p. Makes a folder for the download."""

    assert type(handler_object) == PytubeHandler
    
    pl_object = Playlist(link)
    pl_title = pl_object.title
    video_links = list(pl_object)

    # make folder
    ## tfw too low iq for recursion
    p0 = 'downloads'
    p1 = 'playlists'
    p2 = "".join(x for x in pl_title if x.isalnum())  # make string usable in path
    if p0 not in os.listdir():
        os.mkdir(p0)
    if p1 not in os.listdir(p0):
        os.mkdir(f'{p0}/{p1}')
    if p2 not in os.listdir(f'{p0}/{p1}'):
        os.mkdir(f'{p0}/{p1}/{p2}')
    folder = '/'.join([p0,p1,p2])
    
    def check_existence(string):
        return False

    for link in video_links:
        if check_existence(link):
            print(f'skipping {link}, already exists')
        else:
            handler_object.download_720p(link, folderpath=folder)
    
    print('completed all downloads.')

myra_list = 'https://www.youtube.com/playlist?list=PLU_8MEhMgb7RHhLujJ8YdZZs3rNv6Xp6p'
ph = PytubeHandler()
download_playlist(ph, myra_list)


