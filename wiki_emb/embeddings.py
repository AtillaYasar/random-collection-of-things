import os, time, json, openai, math
import numpy as np
from secrets import openai_key

from overall_imports import text_append, text_create, text_read, make_json, open_json, col, check_return, show_layer, cols

openai.organization = "org-ExxER7UutRm3CU6M9FdszAoE"
openai.api_key = openai_key

class DataHandler:
    """Indexer maps a string to the path where the embedding of that string is stored."""

    def __init__(self, indexer_path):
        self.indexer_path = indexer_path
        self.embedding_folder = 'embeddings'
        if self.embedding_folder not in os.listdir():
            os.mkdir(self.embedding_folder)

        if os.path.isfile(indexer_path):
            pass
        else:
            make_json({}, indexer_path)
        self.indexer = open_json(self.indexer_path)

        # i want certainty about the structure.
        assert type(self.indexer) is dict
        for k,v in self.indexer.items():
            assert type(v) is dict
            for key in ['path', 'meta']:
                assert key in v
            assert type(v['path']) is str
            assert type(v['meta']) is list
    
    def _find_embedding(self, string):
        indexer = self.indexer
        if string in indexer:
            emb = open_json(indexer[string]['path'])
            return emb
        else:
            return None
    
    def _store_embedding(self, string, emb, meta):
        if string in self.indexer:
            print(f'string already exists.')
            print(f'first 10 chars:{string[0:10]}')
            return False
        path = f'{self.embedding_folder}/'+str(time.time())+'.json'
        make_json(emb, path)

        indexer = self.indexer
        indexer[string] = {
            'path':path,
            'meta':meta,
        }
        make_json(indexer, self.indexer_path)

    def get_embedding(self, string, meta=[]):
        """Will return the embedding of a string, either by grabbing it form the database, or using the api."""

        emb = self._find_embedding(string)
        if emb == None:
            emb = use_api(string)
            self._store_embedding(string, emb, meta)
            return emb
        else:
            return emb
    
    def embed_list(self, lst, meta_lst):
        for item, meta in zip(lst, meta_lst):
            assert type(meta) is list
            self.get_embedding(item, meta)
    
    def delete_embedding(self, string):
        if string in self.indexer:
            del self.indexer[string]
            return True
        else:
            return False

    def search(self, string, excluder=None):
        """If excluder(string, meta) returns True, the string is excluded"""

        def default_excluder(string, meta):
            if meta == []:
                return True
            if 'search query' in meta:
                return True
            else:
                return False
        if excluder == None:
            excluder = default_excluder
        assert callable(excluder)

        v1 = self.get_embedding(string, meta=['search query'])
        scores = {}
        for stored_string, d in self.indexer.items():
            if excluder(stored_string, d['meta']):
                continue
            v2 = open_json(d['path'])
            score = cosine_similarity(v1, v2)
            scores[stored_string] = {
                'score':score,
                'meta':d['meta'],
            }
        scores = dict(sorted(scores.items(), key=lambda tup:tup[1]['score'], reverse=True))
        return scores

    def show_scores(self, scores):
        print(col('cy', 'top 5'))
        for k in list(scores.keys())[:5]:
            score = scores[k]['score']
            meta = scores[k]['meta']
            string = k
            print(score)
            print(meta)
            print(string)
            print()
        print(col('cy', 'bottom 5'))
        for k in list(scores.keys())[-5:]:
            print(scores[k])
            print(k)
            print()

def use_api(string):
    print(col('cy','using api for ') + string)
    if type(string) is not str:
        exit('use_api can only take a string')
    response = openai.Embedding.create(input=string, model='text-embedding-ada-002')
    embedding = response['data'][0]['embedding']
    return embedding

def cosine_similarity(vec1, vec2):
    """Compare 2 vectors, return score."""

    if len(vec1) != len(vec2):
        raise ValueError("Vectors must have the same length")

    # Initialize variables to store the dot product and magnitudes
    dot_product = 0
    vec1_magnitude = 0
    vec2_magnitude = 0

    # Iterate over the elements of the vectors and update the variables
    for x, y in zip(vec1, vec2):
        dot_product += x * y
        vec1_magnitude += x**2
        vec2_magnitude += y**2

    score = dot_product / (math.sqrt(vec1_magnitude) * math.sqrt(vec2_magnitude))
    return score



















