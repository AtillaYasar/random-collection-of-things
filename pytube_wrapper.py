from pytube import YouTube

# making something beautiful into something ugly, for the sake of convenience..
class PytubeHandler:
    """Reducing the pytube api down to a couple simple things I want to do with it."""

    def __init__(self):
        self.downloadables = []

    def get_stuff_from_link(self, link):
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
        to_get = ['title', 'description', 'channel url', 'length', 'downloadables']

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
                'title': item.title,
                'resolution': item.resolution,
            })
            self.downloadables.append({
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
