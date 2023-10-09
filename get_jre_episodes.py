import requests, json, webbrowser
from secrets import spotify_client_id, spotify_client_secret

def open_chrome_tab(url):
    #import webbrowser

    chrome_path = r"C:\Program Files\Google\Chrome\Application\chrome.exe"
    webbrowser.register('chrome', None, webbrowser.BackgroundBrowser(chrome_path))
    webbrowser.get('chrome').open_new_tab(url)

def get_token():
    client_id = spotify_client_id
    client_secret = spotify_client_secret
    url = 'https://accounts.spotify.com/api/token'
    headers = {
        'Content-Type': 'application/x-www-form-urlencoded'
    }
    data = {
        'grant_type': 'client_credentials',
        'client_id': client_id,
        'client_secret': client_secret
    }

    response = requests.post(url, headers=headers, data=data)
    token = response.json()['access_token']
    return token

def get_jre_episodes():
    def parse_response(response):
        j = response.json()
        episodes = j['items']
        next_url = j['next']
        return episodes, next_url

    def parse_episode(e):
        d = {k:e[k] for k in ['description','duration_ms','external_urls','name','release_date','href']}
        d['thumbnail'] = e['images'][0]['url']
        d['id'] = e['external_urls']['spotify'].split('/')[-1]
        d['url'] = e['external_urls']['spotify']
        for k in ['external_urls']: # cleanup
            del d[k]
        return d

    class Episode:
        def __init__(self, e):
            self.d = parse_episode(e)
        def open(self):
            open_chrome_tab(self.d['url'])
        def __getitem__(self, k):
            return self.d[k]
        def __repr__(self):
            return json.dumps(self.d, indent=4)

    class Results:
        def __init__(self, response):
            episodes, next_url = parse_response(response)
            self.episodes = [Episode(e) for e in episodes]
            self.next_url = next_url
        def getmore(self):
            if self.next_url is None:
                print('No more episodes to get.')
                return False
            print(f'grabbing {self.next_url}')
            response = requests.get(self.next_url, headers=headers)
            episodes, next_url = parse_response(response)
            self.episodes += [Episode(e) for e in episodes]
            self.next_url = next_url
            return True
        def __getitem__(self, i):
            return self.episodes[i]
        def __len__(self):
            return len(self.episodes)

    headers = {
        'Authorization': 'Bearer ' + token
    }
    params = {
        'market': 'US',
        'limit': '50',
        'offset': '0'
    }
    ID = '4rOoJ6Egrf8K2IrywzwOMk'
    url = 'https://api.spotify.com/v1/shows/' + ID + '/episodes'
    response = requests.get(url, headers=headers, params=params)
    results = Results(response)
    return results

token = get_token()
r = get_jre_episodes()
while True:
    ret = r.getmore()
    if not ret:
        break

print(len(r))  # prints 2199, which is more than there are jre episodes, maybe because there are also fight companion episodes
