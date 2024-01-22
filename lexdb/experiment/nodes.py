from overall_imports import find_full_episode, get_transcript

class Node:
    def __init__(self, dictionary, get_special_values={}):
        self.dictionary = dictionary
        self.get_special_values = get_special_values
        for k,v in get_special_values.items():
            assert callable(v)  # function will be fed self.dictionary, to find the value
    
    def __setitem__(self, key, value):
        self.dictionary[key] = value

    def __getitem__(self, key):
        if key in self.dictionary:
            return self.dictionary[key]
        elif key in self.get_special_values:
            func = self.get_special_values[key]
            v = func(self.dictionary)
            self[key] = v
            return self[key]
        else:
            raise Exception(f'no getter for {key}')

class Clip(Node):
    def __init__(self, dictionary):
        get_special_values = {
            'transcript': lambda d:get_transcript(d['link']),
            'full episode': lambda d:find_full_episode(d),
        }
        super().__init__(dictionary, get_special_values)

class Full(Node):
    def __init__(self, dictionary):
        get_special_values = {
            'transcript': lambda d:get_transcript(d['link']),
        }
        super().__init__(dictionary, get_special_values)

def test():
    from overall_imports import readfile
    clip_info = readfile('clips.json')[0]
    c = Clip(clip_info)
    # second time will be fast
    print(len(Full(c['full episode'])['transcript']))
    print(len(Full(c['full episode'])['transcript']))

if __name__ == '__main__':
    test()
