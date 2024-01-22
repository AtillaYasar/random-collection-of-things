import json, os, time

from youtube_transcript_api import YouTubeTranscriptApi

def writefile(path, content):
    with open(path, 'w', encoding='utf-8') as f:
        if isinstance(content, (dict, list)):
            json.dump(content, f, indent=2)
        else:
            f.write(content)

def readfile(path):
    with open(path, 'r', encoding='utf-8') as f:
        if path.endswith('.json'):
            content = json.load(f)
        else:
            content = f.read()
    return content

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
                parts = t.split(':')
                seconds = 0
                i = 0
                while len(parts) > 0:
                    last = parts.pop(-1)
                    seconds += int(last)*60**i
                    i += 1
                return seconds

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

mapper = readfile('cliptitle_to_ep.json')
fulleps = readfile('fulleps.json')
def find_full_episode(data):
    url = mapper[data['title']]
    for ep in fulleps:
        if ep['link'] == url:
            return ep
    raise Exception(f'couldnt find full episode for {data["title"]}')