import os, sys
import requests, json, time, base64

from secrets import elevenlabs_key
import pygame

import subprocess

from pydub import AudioSegment
import sys
import requests
from itertools import combinations

def col(ft, s):
    """For printing text with colors.
    
    Uses ansi escape sequences. (ft is "first two", s is "string")"""
    # black-30, red-31, green-32, yellow-33, blue-34, magenta-35, cyan-36, white-37
    u = '\u001b'
    numbers = dict([(string,30+n) for n, string in enumerate(('bl','re','gr','ye','blu','ma','cy','wh'))])
    n = numbers[ft]
    return f'{u}[{n}m{s}{u}[0m'

def generate_and_save(voice_id, string, output_path, stability, similarity):
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

def get_name_ID_mapping():
    """Returns a dictionary mapping voice names to voice ids."""

    # get and parse response
    headers = {
        "Content-Type": "application/json",
        'xi-api-key': elevenlabs_key,
        }
    url = 'https://api.elevenlabs.io/v1/voices'
    r = requests.request(url=url, method='get', headers=headers)
    c = r.content
    d = json.loads(c)

    # extract the names and ids
    mapping = {}
    for item in d['voices']:
        mapping[item['name']] = item['voice_id']
    mapping = dict(sorted(mapping.items(), key=lambda x: x[0]))
    return mapping

def create_voice(paths, name, description='', labels=''):
    url = 'https://api.elevenlabs.io/v1/voices/add'
    headers = {
        'accept': 'application/json',
        'xi-api-key': elevenlabs_key,
    }
    data = {
        'name': name,
        'description': description,
        'labels': labels,
    }
    files = []
    for path in paths:
        files.append(('files', (os.path.basename(path), open(path, 'rb'), 'audio/mpeg')))

    response = requests.post(url, headers=headers, data=data, files=files)
    print(f'create_voice, name={col("cy",name)}, status code = ', response.status_code)

    return response.json()['voice_id']

def delete_voice(ID):

    url = f'https://api.elevenlabs.io/v1/voices/{ID}'
    headers = {
        'accept': 'application/json',
        'xi-api-key': elevenlabs_key,
    }

    response = requests.delete(url, headers=headers)
    print(f'delete_voice {col("cy", ID)}, status code = ', response.status_code)

def permutation(lst):
 
    # If lst is empty then there are no permutations
    if len(lst) == 0:
        return []
 
    # If there is only one element in lst then, only
    # one permutation is possible
    if len(lst) == 1:
        return [lst]
 
    # Find the permutations for lst if there are
    # more than 1 characters
 
    l = [] # empty list that will store current permutation
 
    # Iterate the input(lst) and calculate the permutation
    for i in range(len(lst)):
       m = lst[i]
 
       # Extract lst[i] or m from the list.  remLst is
       # remaining list
       remLst = lst[:i] + lst[i+1:]
 
       # Generating all permutations where m is first
       # element
       for p in permutation(remLst):
           l.append([m] + p)
    return l
 
def all_combinations(data):
    combs = []
    count = 0
    for i in range(1, len(data)+1):
        for p in combinations(data, i):
            count += 1
            combs.append(p)
    return combs
tts_text = """
Hey there! I am some unnamed voice, saying some sample lines. Let me know if you like it okay?

I can whisper, like this: "I am standing... right... behind you.. don't turn around."

Or I can shout, like this: "HEY!!! I hate you and everything you ever did!!"

Or I can say something sweet, like, "I always thought you were a wonderful person. Wanna go out some time, and maybe, like, get ice cream together?"
"""[1:-1]
tts_text = 'Just a quick test. Hi there!'

# create folders for outputs
outputs_folder_base = 'outputs'
if not os.path.exists(outputs_folder_base):
    os.mkdir(outputs_folder_base)
testrun = str(time.time())
outputs_folder = f'{outputs_folder_base}/{testrun}'
if not os.path.exists(outputs_folder):
    os.mkdir(outputs_folder)

# gather sample sets
samples = [os.path.join('samples', f) for f in os.listdir('samples')]
combs = all_combinations(samples)

# generate speech
for c in combs:
    filenames = [os.path.basename(f).split('.')[0] for f in c]
    voice_name = '+'.join(filenames)
    voice_id = create_voice(c, voice_name)
    for stab in (0.1, 0.8):
        for sim in (0.1, 0.8):
            # create filename, which contains info about the samples and settings
            name_dict = {
                'samples': voice_name,
                'stability': stab,
                'similarity': sim,
            }
            filename = '&'.join([f'{k}={v}' for k,v in name_dict.items()])

            # finally, generate the speech
            generate_and_save(voice_id, tts_text, f'{outputs_folder}/{filename}.mp3', stab, sim)
    delete_voice(voice_id)

