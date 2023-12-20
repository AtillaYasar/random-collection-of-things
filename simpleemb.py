import requests, json, threading, time, os
import numpy as np

from colorama import init
init()

from secret_things import openai_key

def col(ft, s):
    """For printing text with colors.
    
    Uses ansi escape sequences. (ft is "first two", s is "string")"""
    # black-30, red-31, green-32, yellow-33, blue-34, magenta-35, cyan-36, white-37
    u = '\u001b'
    numbers = dict([(string,30+n) for n, string in enumerate(('bl','re','gr','ye','blu','ma','cy','wh'))])
    n = numbers[ft]
    return f'{u}[{n}m{s}{u}[0m'

def readfile(path):
    with open(path, 'r', encoding='utf-8') as f:
        if path.endswith('.json'):
            content = json.load(f)
        else:
            content = f.read()
    return content

def writefile(path, content):
    with open(path, 'w', encoding='utf-8') as f:
        if isinstance(content, (dict, list)):
            json.dump(content, f, indent=2)
        else:
            f.write(content)

def embedder_api(strings):
    headers = {
        "Authorization": f"Bearer {openai_key}",
        "Content-Type": "application/json"
    }
    data = {
        "input": strings,
        "model": "text-embedding-ada-002"
    }
    response = requests.post("https://api.openai.com/v1/embeddings", headers=headers, json=data)

    if response.status_code != 200:
        print(col('re', strings))
        print(vars(response))
        raise Exception
    else:
        print(f'successfully embedded {len(strings)} strings')
    data = response.json()['data']
    return [d['embedding'] for d in data]

class StaticDb:       
    def __init__(self, foldername):
        self.foldername = foldername
        self.nppath = f'{self.foldername}/array.npy'
        self.stringspath = f'{self.foldername}/idx_to_string.json'

    def create(self, strings):
        if not os.path.exists(self.foldername):
            os.mkdir(self.foldername)

        array = []
        
        to_embed = strings
        per_call = 50
        for i in range(0, len(to_embed), per_call):
            vectors = embedder_api(to_embed[i:i+per_call])
            array += vectors

        np.save(self.nppath, array)
        writefile(self.stringspath, strings)
    
    def load(self):
        self.array = np.load(self.nppath)
        self.strings = readfile(self.stringspath)
    
    def search(self, query, maxres):
        query_emb = embedder_api([query])[0]
        #t0 = time.time()
        assert len(query_emb) == 1536

        scores = np.dot(self.array, np.array(query_emb))
        dtype = [
            ('score', float),
            ('text', 'O'),
        ]
        values = []
        for score, string in zip(scores, self.strings):
            # Store the string as bytes, not as a Unicode string.
            values.append((score, string.encode('utf-8')))

        special_array = np.array(values, dtype=dtype)
        sorted_by_dot = np.sort(special_array, order='score')
        #print(time.time()-t0)
        topn = list(reversed(sorted_by_dot))[:maxres]
        res = [tup[1].decode('utf-8') for tup in topn]
        return res
