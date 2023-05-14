import requests, os, json, time, sys, subprocess
from secret_things import elevenlabs_key
from pydub import AudioSegment
import pygame

def col(ft, s):
    """For printing text with colors.
    
    Uses ansi escape sequences. (ft is "first two", s is "string")"""
    # black-30, red-31, green-32, yellow-33, blue-34, magenta-35, cyan-36, white-37
    u = '\u001b'
    numbers = dict([(string,30+n) for n, string in enumerate(('bl','re','gr','ye','blu','ma','cy','wh'))])
    n = numbers[ft]
    return f'{u}[{n}m{s}{u}[0m'

def make_json(dic, filename):
    with open(filename, 'w', encoding="utf-8") as f:
        json.dump(dic, f, indent=2)
        f.close()

def open_json(filename):
    with open(filename, 'r', encoding="utf-8") as f:
        contents = json.load(f)
        f.close()
    return contents

class Cacher:
    # intended for storing API calls and downloads that take a long time

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
        print(f'saved to {self.filename}')

    def get(self, inp):
        for item in self.cache:
            if item['input'] == inp:
                return item['output']
        return None

    def add(self, inp, outp):
        self.cache.append({'input':inp, 'output':outp})
        self.save_cache()

    def edit(self, inp, outp):
        "returns True if edited, False if not"

        for n, item in enumerate(self.cache):
            if item['input'] == inp:
                self.cache[n]['output'] = outp
                self.save_cache()
                return True
        return False

    def investigate(self, terms):
        "returns a list of items that contain the terms"

        allowed_keys = ['simple_match', 'multi_match', 'by_funcion']
        if not all([key in allowed_keys for key in terms.keys()]):
            print(f'invalid key, allowed keys are {allowed_keys}')
            return None

        results = []
        simple_match = terms.get('simple_match', None)
        multi_match = terms.get('multi_match', None)
        by_funcion = terms.get('by_funcion', None)
        for item in self.cache:
            if simple_match != None:
                if simple_match in str(item):
                    results.append(item)
                    continue
            if multi_match != None:
                if all([term in str(item) for term in multi_match]):
                    results.append(item)
                    continue
            if by_funcion != None:
                if by_funcion(item):
                    results.append(item)
                    continue
        
        return results

    def delete(self, inp):
        "returns True if deleted, False if not"

        for n, item in enumerate(self.cache):
            if item['input'] == inp:
                del self.cache[n]
                self.save_cache()
                return True
        return False

def create_voice(paths, name):
    url = 'https://api.elevenlabs.io/v1/voices/add'
    headers = {
        'accept': 'application/json',
        'xi-api-key': elevenlabs_key,
    }
    data = {
        'name': name,
        'description': '',
        'labels': ''
    }
    files = []
    for path in paths:
        files.append(('files', (os.path.basename(path), open(path, 'rb'), 'audio/mpeg')))

    response = requests.post(url, headers=headers, data=data, files=files)
    print(f'create_voice {col("cy",name)}, status code = ', response.status_code)
    return response.json()['voice_id']

def delete_voice(ID):
    import requests

    url = f'https://api.elevenlabs.io/v1/voices/{ID}'
    headers = {
        'accept': 'application/json',
        'xi-api-key': elevenlabs_key,
    }

    response = requests.delete(url, headers=headers)
    print(f'delete_voice {col("cy", ID)}, status code = ', response.status_code)

def generate_and_save(voice_id, string, output_path, stability=0.15, similarity=0.75):
    """Uses the elevenlabs tts api to convert a string to an audio file. Returns the path to the audio file."""

    # payload and headers for api request
    data = {
      "text": string,
      "voice_settings": {
        "stability": stability,
        "similarity_boost": similarity,
      }
    }
    headers = {
        "Content-Type": "application/json",
        'xi-api-key': elevenlabs_key,
        }
    # call api
    url = f'https://api.elevenlabs.io/v1/text-to-speech/{voice_id}'
    r = requests.request(url=url, data=json.dumps(data), method='post', headers=headers)
    # handle response
    if r.status_code == 200:
        with open(output_path, mode='bx') as f:
            f.write(r.content)
        return output_path
    else:
        print(vars(r))
        raise Exception('elevenlabs tts failed')

def crop(path, start_ms, end_ms, outpath):
    track = AudioSegment.from_file(path, format=path.split('.')[-1])
    track[start_ms:end_ms].export(outpath, format='mp3')
    return outpath

class Downloader:
    def __init__(self):
        pass

    def download_audio(self, folder, link):
        # yt-dlp -x "https://www.youtube.com/watch?v=XK8kZGGx_NM&ab_channel=Nas-Topic" -o "test.%(ext)s" -f mp4
        ID = link.partition('?v=')[2].partition('&')[0]
        subprocess.run(['yt-dlp', '-x', link, '-o', f'{folder}/{ID}.%(ext)s', '-f', 'm4a'])
        return f'{folder}/{ID}.m4a'

class AudioHandler:
    # requires cacher and downloader

    def __init__(self, folderpath):
        if folderpath not in os.listdir():
            os.mkdir(folderpath)
        
        self.tts_folder = 'tts_outputs'
        if self.tts_folder not in os.listdir():
            os.mkdir(self.tts_folder)
        self.folderpath = folderpath
        self.downloader = Downloader()
        self.cacher = Cacher(f'{folderpath}/youtube_cloning.json')

        pygame.init()

    def get_audio(self, link):
        # find cached audio, or download
        path = self.cacher.get(link)
        if path == None:
            print(f'will download {link}')
            path = self.downloader.download_audio(self.folderpath, link)
            self.cacher.add(link, path)
        else:
            print(f'found cached audio for {link}')
        return path

    def crop(self, link, start_ms, end_ms):
        # crop audio
        path = self.get_audio(link)
        ID = link.partition('?v=')[2].partition('&')[0]
        outpath = f'{self.folderpath}/{ID}_{start_ms}_{end_ms}.mp3'
        if os.path.exists(outpath) == True:
            print(f'found cached file at {outpath}')
        else:
            print(f'will crop and save to {outpath}')
            outpath = crop(path, start_ms, end_ms, outpath)
        return outpath

    def clone(self, sample_path, text):
        ID = create_voice([sample_path], time.time())
        speech_path = generate_and_save(
            ID,
            text,
            f'{self.tts_folder}/{time.time()}.mp3',
            stability=0.3,
            similarity=0.5,
        )
        pygame.mixer.music.load(speech_path)
        pygame.mixer.music.play()
        i = input('press enter to stop')
        delete_voice(ID)

if 'say_this.txt' not in os.listdir():
    with open('say_this.txt', 'w') as f:
        f.write("Hey ya'll I'm Grimes! I think it's kinda cool to merge with artificial intelligence.")

# test
folderpath = 'youtube_cloning'
audio_handler = AudioHandler(folderpath)
args = sys.argv
if len(args) != 4:
    print('invalid number of arguments')
    print('do this: python youtube_cloning.py "<link>" <start_ms> <end_ms>')
    print('example:')
    print('youtube_cloning.py "https://www.youtube.com/watch?v=_rH0pKr4o74&ab_channel=LexClips" 61500 120000')
    print('that will create a sample from 1:15 to 2:00, take text from say_this.txt and say it with grimes\' cloned voice')
else:
    link = args[1]
    start_ms = int(args[2])
    end_ms = int(args[3])
    audio_handler.get_audio(link)
    with open('say_this.txt', 'r') as f:
        text = f.read()
    sample_path = audio_handler.crop(link, start_ms, end_ms)
    audio_handler.clone(sample_path, text)