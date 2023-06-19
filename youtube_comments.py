import json
from youtubesearchpython import *

def get_yt_comments(id_or_url, max_call_count=None):
    # from youtubesearchpython import *
    
    """
    id_or_url: youtube video id or url, but sometimes id doesnt work.
    max_call_count: if None, will repeat api calls until no more comments, each call retrieves 20 comments
    """

    comments = Comments(id_or_url)

    # repeat api calls until no more comments
    if max_call_count == None:
        while comments.hasMoreComments:
            comments.getNextComments()
    else:
        iterations = 0
        while comments.hasMoreComments and iterations <= max_call_count:
            comments.getNextComments()
            #count = len(comments.comments["result"])
            #print(f'Comments Retrieved: {count}')
            iterations += 1

    # now reshape the data for convenience

    # helper for sorting by likes
    def get_likes(item):
        text = item['votes']['simpleText']
        if text == None:
            return 0
        elif 'K' in text:
            return int(float(text.replace('K', '')) * 1000)
        else:
            return int(text)
    sorted_by_likes = sorted(
        comments.comments['result'],
        key=lambda x: get_likes(x),
        reverse=True
    )

    nicer = []
    for comment in sorted_by_likes:
        comment_id = comment['id']
        username = comment['author']['name']
        likes = comment['votes']['simpleText']
        text = comment['content']
        published = comment['published']
        
        nicer.append({
            'comment_id': comment_id,
            'username': username,
            'likes': likes,
            'text': text,
            'published': published,
        })
    
    return nicer

lst = get_yt_comments(
    "https://www.youtube.com/watch?v=9ZwG7QnkLZM&ab_channel=Nas-Topic",
    3,
)
print(json.dumps(lst[0:5], indent=4))
