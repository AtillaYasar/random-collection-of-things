from pytube import YouTube, Playlist
from overall_imports import*
import json, os, sys

class DatabaseHandler:
    def __init__(self):
        pass

# making something beautiful into something ugly, for the sake of convenience..
class PytubeHandler:
    """Reducing the pytube api down to a couple simple things I want to do with it."""

    def __init__(self):
        self.downloadables = []

    def get_stuff_from_link(self, link:str, to_get:[
        'title', 'description', 'channel url', 'length', 'downloadables', 'only_progressive'
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
        if 'only_progressive' in to_get:
            only_progressive = True
            to_get.remove('only_progressive')
        else:
            only_progressive = False
        sq_f = sq.filter(progressive=only_progressive)  # filter for progressive. will limit to 720p, and make sjws happy
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
    
    def _download_720p(self, stream_object, folderpath:str):
        """Helper for download_720p."""
        stream_object.download(output_path = folderpath)
    
    def download_720p(self, link:str, folderpath=None):
        """Easy version of the full downloading capabilities."""

        success = False
        downloadables = self.get_stuff_from_link(link, ['title', 'downloadables', 'only_progressive'])['downloadables']
        for item in downloadables:
            if item['resolution'] == '720p':
                print(f'start downloading {item["title"]}')
                if folderpath == None:
                    folderpath = os.getcwd()
                    self._download_720p(item['stream object'], folderpath)
                else:
                    self._download_720p(item['stream object'], folderpath)
                success = True
                break

        if success:
            print(f'download of {item["title"]} finished')
        else:
            print(f'could not get 720p for {item["title"]}')
    
    def _download_audio(self, stream_object, folderpath:str):
        """Helper for download_audio."""
        stream_object.download(output_path = folderpath)

    def download_audio(self, link:str, folderpath=None):
        """Just send a link and get the audio."""

        # just checking how this stuff works..

        downloadables = self.get_stuff_from_link(link, ['title', 'downloadables'])['downloadables']
        relevant_stream_objects = []
        for item in downloadables:
            title = item['title']
            mime_type = item['stream object'].mime_type
            quality = item['stream object'].abr
            if mime_type == 'audio/mp4' and quality != None:
                relevant_stream_objects.append({
                    'object': item['stream object'],
                    'quality': quality.split('kbps')[0],
                    'title': title,
                })
        
        relevant_stream_objects.sort(key=lambda x: int(x['quality']), reverse=True)
        print('available qualities:')
        for item in relevant_stream_objects:
            print(item['quality'])
            print(item['title'])
            print()
        
        highest_q = relevant_stream_objects[0]['object']
        if folderpath == None:
            folderpath = os.getcwd()
            self._download_audio(highest_q, folderpath)
        else:
            self._download_audio(highest_q, folderpath)

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

# for testing
## note: above class worked for playlists, before i changed it, havent tested after change.
## after the change, both audio and video work for the linked video.
if True:
    zachstar_vid = 'https://www.youtube.com/watch?v=uiCpTC0VMV0&'
    ph = PytubeHandler()
    ph.download_audio(zachstar_vid)
    ph.download_720p(zachstar_vid)



