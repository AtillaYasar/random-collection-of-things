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
    assert response_format in ['srt', 'text']

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

openai.api_key = openai_key

cache = Cache('whisper_cache.json')

path = 'whisper_test.mp4'
transcript = get_transcript(path, 'srt')
# print(transcript)

