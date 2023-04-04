import openai, json, os
from secrets import openai_key

def open_json(filename):
    with open(filename, 'r') as f:
        return json.load(f)

def make_json(data, filename):
    with open(filename, 'w') as f:
        json.dump(data, f, indent=2)

class Cache:
    def __init__(self, filename):
        self.filename = filename
        if not os.path.exists(self.filename):
            with open(self.filename, 'w') as f:
                json.dump([], f)
        self.cache = self.load_cache()

    def load_cache(self):
        cache = open_json(self.filename)
        return cache

    def save_cache(self):
        make_json(self.cache, self.filename)

    def get(self, inp):
        for item in self.cache:
            if item['input'] == inp:
                return item['output']
        return None

    def add(self, inp, outp):
        self.cache.append({'input':inp, 'output':outp})
        self.save_cache()

def get_transcript(path, response_format):
    assert response_format in ['srt', 'text', 'verbose_json', 'json', 'vtt']

    cached = cache.get(
        {
            'path': path,
            'response_format': response_format
        }
    )

    if cached != None:
        print('using cached transcript')
        transcript = cached
    else:
        print('using api for transcript')
        audio_file = open(path, "rb")
        transcript = openai.Audio.transcribe("whisper-1", audio_file, response_format=response_format)
        cache.add(
            {
                'path': path,
                'response_format': response_format
            },
            transcript
        )

    return transcript

# helper function for processing the transcript
# what the api output looks like:
# 00:00:00,000 --> 00:00:01,000
'''
1
00:00:00,000 --> 00:00:02,000
This video was sponsored by Upside.

2
00:00:04,480 --> 00:00:06,480
Are you sure we're going the right way?

3
00:00:06,480 --> 00:00:08,480
I think so, but...

etc
'''
def process_srt_string(srt):
    def to_seconds(time):
        h, m, pre_s = time.split(':')
        h = int(h)
        m = int(m)
        pre_s, ms = pre_s.split(',')
        while True:
            if len(pre_s) == 0:
                pre_s = '0'
                break
            if pre_s[0] == '0':
                pre_s = pre_s[1:]
            else:
                break
        s = int(pre_s)
        ms = int(ms)
        return h*3600 + m*60 + s + ms/1000

    info = []
    blocks = srt.split('\n\n')
    for b in blocks:
        lines = b.split('\n')
        if len(lines) != 3:
            continue
        idx = lines[0]
        time_range = lines[1]
        text = lines[2]
        start, end = time_range.split(' --> ')

        # convert to seconds
        start = to_seconds(start)
        end = to_seconds(end)

        info.append({
            'start': start,
            'end': end,
            'text': text,
        })
    return info

# for testing
if True:
    openai.api_key = openai_key
    cache = Cache('whisper_cache.json')

    path = 'whisper_test.mp4'
    transcript = get_transcript(path, 'srt')

    processed = process_srt_string(transcript)
    print(json.dumps(processed, indent=2))
    print(transcript)
