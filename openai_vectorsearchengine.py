import numpy as np
import requests, json, os, time, random
from secret_things import openai_key

def singlecall_vector_search(query, strings):
    # tip: you could scale up a bit by replacing embedding_api with something that can return already-stored embeddings

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
            print(vars(response))
            raise Exception
        else:
            print('success')
        data = response.json()['data']
        return [d['embedding'] for d in data]

    vectors = embedder_api([query, *strings])
    query_emb = vectors[0]
    strings_emb = vectors[1:]

    triplets = sorted(
        [(
            n,
            strings[n],
            np.dot(query_emb,strings_emb[n])
        ) for n in range(len(strings))],
        key=lambda triplet: triplet[2],
        reverse=True
    )
    return triplets

# next level is multiple calls
# then you have storage between each call, plus checking beforehand for existing data
# oh and i should split it into getting data and performing a search

# theres also rate limit management

def multicall_vector_search(query, strings):
    def embedder_api(strings):
        headers = {
            "Authorization": f"Bearer {openai_key}",
            "Content-Type": "application/json"
        }
        data = {
            "input": strings,
            "model": "text-embedding-ada-002"
        }

        if os.path.exists('last_call.txt'):
            with open('last_call.txt', 'r') as f:
                last_call = int(f.read())
            wait_time = 20 - (time.time() - last_call)
        else:
            wait_time = 0
        time.sleep(wait_time)
        response = requests.post("https://api.openai.com/v1/embeddings", headers=headers, json=data)
        with open('last_call.txt', 'w') as f:
            f.write(str(time.time()))

        if response.status_code != 200:
            print(vars(response))
            raise Exception
        else:
            print('success')
        data = response.json()['data']
        return [d['embedding'] for d in data]

    per_call = 50
    vectors = []
    for i in range(0, len(strings), per_call):
        vectors += embedder_api(strings[i:i+per_call])

    query_emb = vectors[0]
    strings_emb = vectors[1:]

    def do_search():
        triplets = sorted(
            [(
                n,
                strings[n],
                np.dot(query_emb,strings_emb[n])
            ) for n in range(len(strings))],
            key=lambda triplet: triplet[2],
            reverse=True
        )
        return triplets
    return do_search()





def multicall_with_storage(strings, child_foldername=str(time.time())):
    """
    helpers:
        storefunc -- string, embedding -> None  (stores the embedding)
        checkfunc -- string -> Bool  (checks if the string is already stored)
        embedder_api -- strings -> embeddings
    """

    # prepare for storage
    parent_folder = 'embeddings'
    child_folder = f'{parent_folder}/{child_foldername}'
    for f in [parent_folder, child_folder]:
        if not os.path.exists(f):
            os.mkdir(f)

    mapper_json_path = f'{child_folder}/mapper.json'
    if os.path.exists(mapper_json_path):
        with open(mapper_json_path, 'r') as f:
            mapper = json.load(f)
    else:
        mapper = {}
        with open(mapper_json_path, 'w') as f:
            json.dump(mapper, f, indent=2)

    def storefunc(string, emb):
        path = f'{child_folder}/{time.time()}.json'
        mapper[string] = {'path':path}
        with open(mapper_json_path, 'w') as f:
            json.dump(mapper, f, indent=2)

        data = emb

        with open(path, 'w') as f:
            json.dump(data, f, indent=2)

    def checkfunc(string):
        if string in mapper:
            return True
        else:
            return False

    def embedder_api(strings):
        print(json.dumps(strings, indent=2))
        headers = {
            "Authorization": f"Bearer {openai_key}",
            "Content-Type": "application/json"
        }
        data = {
            "input": strings,
            "model": "text-embedding-ada-002"
        }

        if os.path.exists('last_call.txt'):
            with open('last_call.txt', 'r') as f:
                last_call = f.read()
            try:
                float(last_call)
                last_call = float(last_call)
            except:
                last_call = 0

            wait_time = max([20, 20 - (time.time() - last_call)])
        else:
            wait_time = 0
        time.sleep(wait_time)
        response = requests.post("https://api.openai.com/v1/embeddings", headers=headers, json=data)
        with open('last_call.txt', 'w') as f:
            f.write(str(time.time()))

        if response.status_code != 200:
            print(vars(response))
            raise Exception
        else:
            print('api call success')
        data = response.json()['data']
        data = sorted(data, key=lambda d: int(d['index']))
        return [d['embedding'] for d in data]
    
    existing = []
    new = []
    for string in strings:
        if checkfunc(string) == False:
            new.append(string)
        else:
            existing.append(string)
    print('\n'.join([
        f'existing={len(existing)}',
        f'new={len(new)}',
    ]))

    per_call = 50
    for i in range(0, len(new), per_call):
        print(f'embedding {i}:{i+per_call}')

        strings_subset = new[i:i+per_call]
        embeddings_subset = embedder_api(strings_subset)

        for s, e in zip(strings_subset, embeddings_subset):
            storefunc(s, e)

    print(f'stored {len(new)} embeddings (out of {len(strings)} existing) in {os.path.abspath(child_folder)}')

# usage example of multicall_with_storage
if 0:
    name_of_some_book = 'harry potter and yo mama'
    with open(f'{name_of_some_book}_strings.json', 'r') as f:
        data = json.load(f)
    strings = [s for s in data if len(s) > 0]
    multicall_with_storage(strings, child_foldername=name_of_some_book)
