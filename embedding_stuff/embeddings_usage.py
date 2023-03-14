import os

import embeddings_module
from overall_imports import text_read

def main():
    dh = embeddings_module.DataHandler('embedding_indexer.json')
    #dh.make_numpy_array()
    while True:
        print('press enter to do a search and compare.')
        search_terms_filename = 'search term.txt'
        print(f'filename = {search_terms_filename}')
        i = input()

        search_params = {
            'has':['lorebook'],
            'hasno':['search query'],
            'top_n':10,
        }

        paths = [f'multi terms/{name}' for name in os.listdir('multi terms')]

        use_multi = False
        if use_multi:
            search_term = [text_read(path) for path in paths]
        else:
            search_term = text_read(search_terms_filename)
        dh.search_and_show(search_term, search_params)

if __name__ == '__main__':
    main()