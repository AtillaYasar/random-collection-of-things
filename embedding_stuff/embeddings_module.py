import os, time, json, openai, math, time
import numpy as np
from secrets import openai_key

from overall_imports import text_append, text_create, text_read, make_json, open_json, col, check_return, show_layer, cols

openai.organization = "org-ExxER7UutRm3CU6M9FdszAoE"
openai.api_key = openai_key

def get_args_cli(*to_get):
    while True:
        part_splitter = '___'
        arg_splitter = ','
        print(to_get)
        print(f'part_splitter:{[part_splitter]}')
        print(f'arg_splitter:{[arg_splitter]}')

        i = input()

        extracts = {to_get[n]:part.partition('=')[2].split(arg_splitter) for n, part in enumerate(i.split(part_splitter))}
        for k in to_get:
            extracts[k] = extracts.get(k, [])

        print(f'extracts')
        print(json.dumps(extracts, indent=2))

        i = input('happy? (yes/no)\n')
        if i == 'yes':
            print(col('gr', 'cool.'))
            break
        elif i == 'no':
            print(col('gr', 'k lets try again'))
            continue
        else:
            print(col('re', 'breh.'))
    assert len(extracts) == len(to_get)
    return extracts

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

        self.emb_array = np.load('emb_array.npy')
        self.string_to_index = open_json('string_to_index.json')

        # i want certainty about the structure.
        assert type(self.indexer) is dict
        for k,v in self.indexer.items():
            assert type(v) is dict
            for key in ['path', 'meta']:
                assert key in v
            assert type(v['path']) is str
            assert type(v['meta']) is list
    
    def make_numpy_array(self):
        # make numpy array of embeddings
        t0 = time.time()
        embeddings_list = []
        string_to_index = {}
        for n, (string, info) in enumerate(self.indexer.items()):
            emb_path = info['path']
            emb = open_json(emb_path)
            embeddings_list.append(emb)
            string_to_index[string] = n
        self.emb_array = np.array(embeddings_list)
        self.string_to_index = string_to_index
        print(time.time()-t0, 'seconds to make an np array')
        np.save('emb_array.npy', self.emb_array)
        make_json(string_to_index, 'string_to_index.json')

    def _find_embedding(self, string):

        idx = self.string_to_index.get(string, None)
        if idx != None:
            emb = self.emb_array[idx]
            return 'success', emb
        else:
            indexer = self.indexer
            if string in indexer:
                emb = open_json(indexer[string]['path'])
                return 'success', emb
            else:
                return 'fail', None

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
    
        report, emb = self._find_embedding(string)
        if report == 'success':
            return emb            
        else:
            emb = use_api(string)
            if meta == ['search query']:
                pass
            else:
                self._store_embedding(string, emb, meta)
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

    def search(self, root_embedding, search_parameters):
        """
        root_embedding -- the embedding with which to compare the stuff in the database. (weird name, i know.)
        search_parameters -- stuff about how to shape the dataset during search
        """

        assert isinstance(root_embedding, (list, np.ndarray))
        assert type(search_parameters) is dict
        
        # fill in defaults.
        search_param_defaults = {
        'top_n':5,
        'hasno':['search query'],
        'has':[]
        }
        for k,v in search_param_defaults.items():
            if k not in search_parameters:
                search_parameters[k] = v
        print(search_parameters)
        top_n = int(search_parameters['top_n'])
        hasno = search_parameters['hasno']
        has = search_parameters['has']

        t0 = time.time()

        embeddings_iterable = self.emb_array

        strings_iterable = [string.encode('utf-8') for string in self.indexer.keys()]
        paths_iterable = [item['path'].encode('utf-8') for item in self.indexer.values()]
        metatags_iterable = [item['meta'] for item in self.indexer.values()]
        scores = np.dot(self.emb_array, root_embedding)

        my_types = [
            ('score', float),
            ('embedded text', f'S{max(map(len,strings_iterable))}'),
            ('path', f'S{max(map(len,paths_iterable))}'),
            ('meta tags', list),
        ]
        combined = list(zip(scores, strings_iterable, paths_iterable, metatags_iterable))
        combined_array = np.array(combined, dtype=my_types)

        # create boolean filter mask. (i think thats what its called)
        filtermask = []
        print(search_parameters)

        # for creating a filter mask.
        def checker(meta_tags, has, hasno):
            # deal breakers return False. if it survives, it returns True
            for existing_tag in meta_tags:
                if existing_tag in hasno:
                    return False
            for required in has:
                if required not in meta_tags:
                    return False
            return True

        assert len(metatags_iterable) == len(combined_array)
        for item in metatags_iterable:

            if checker(item, has, hasno):
                filtermask.append(True)
            else:
                filtermask.append(False)


        assert len(filtermask) == len(combined_array)
        # apply filter mask
        combined_array = combined_array[filtermask]

        # sort by score, get top_n
        transformed = np.sort(combined_array, order='score')
        transformed = reversed(transformed[-top_n:])

        # make result usable without needing to know the specifics of the code above.
        # and the for loop is not costly anymore, with a tiny array.
        result = []
        for item in transformed:
            result.append({
                'score':round(item[0], 3),
                'text':item[1].decode('utf-8'),
                'path':item[2].decode('utf-8'),
                'meta tags':item[3],
            })
        
        print(f'search took {time.time()-t0} seconds')

        print(col('re', '=============================='))

        return result

    def search_and_show(self, search_term, params):
        if type(search_term) is str:
            embedding_to_search = self.get_embedding(search_term, ['search query'])
        elif type(search_term) is list:
            all_embs = []
            for item in search_term:
                assert type(item is str)
                all_embs.append(
                    self.get_embedding(item, ['search query'])
                )
            summed = all_embs[0]
            for emb in all_embs[1:]:
                for idx, scalar in enumerate(emb):
                    summed[idx] += scalar
            for idx, scalar in enumerate(summed):
                summed[idx] /= len(all_embs)
            assert len(summed) == len(all_embs[0])
            embedding_to_search = summed
        else:
            raise TypeError

        # do search
        searchres = self.search(embedding_to_search, params)

        # show results nicely.
        for item in searchres:
            s = item['score']
            te = item['text']
            ta = item['meta tags']

            print(f'score ' + col('cy', s))
            print(te)
            print(' '*4 + '--- ' + ', '.join(ta) + ' ---')
            print()



def get_matching(og, matches):
    def col(ft, s):
        """For printing text with colors.
        
        Uses ansi escape sequences. (ft is "first two", s is "string")"""
        # black-30, red-31, green-32, yellow-33, blue-34, magenta-35, cyan-36, white-37
        u = '\u001b'
        numbers = dict([(string,30+n) for n, string in enumerate(('bl','re','gr','ye','blu','ma','cy','wh'))])
        n = numbers[ft]
        return f'{u}[{n}m{s}{u}[0m'
    # asserts
    assert type(og) is str
    assert type(matches) is list
    for item in matches:
        assert type(item) is str

    og_words = og.split(' ')
    colors = ['cy', 'gr', 'ye', 'ma', 'blu', 're']
    color_mapping = {word:colors[i%len(colors)] for i, word in enumerate(og_words)}
    new_matches = []
    for match in matches:
        old_wordset = match.split(' ')
        new_wordset = []
        for word in old_wordset:
            if word in og_words:
                new_wordset.append(col(color_mapping[word], word))
            else:
                new_wordset.append(word)
        new_matches.append(' '.join(new_wordset))

    new_og = []
    for w in og_words:
        color = color_mapping.get(w, 'wh')
        new_og.append(col(color, w))
    new_og = ' '.join(new_og)

    return new_og, new_matches


def use_api(string):
    print(col('cy','using api for ') + string)
    if type(string) is not str:
        exit('use_api can only take a string')
    response = openai.Embedding.create(input=string, model='text-embedding-ada-002')
    embedding = response['data'][0]['embedding']
    return embedding












