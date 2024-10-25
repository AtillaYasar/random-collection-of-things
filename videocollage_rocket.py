

"""
Code result, video collage: https://youtu.be/_fmpXQJsz48

BASIC LOGIC
- calculate position and and new size for each video so it fits into a background image
- for each frame:
    grab next frame from each video, resize, paste to correct location onto background image
        (if a video runs out of frames (if cap.read()[0]==False), stop asking for its frames and instead use a blank image in its place.)

CAVEATS / CAUTION
Some things are hardcoded/manual/wouldnt work with other videos, and/or are mega dumb/confusing:
    - `cap.set(cv2.CAP_PROP_POS_FRAMES, 550 if 'launch' in v['path'] else 1500 if '1' in v['path'] else 700 if '5' in v['path'] else fcount-2 )`
        + manually sets starting frames for some of the videos
    - fps happened to be around 30 fps for most of the videos, some 24, and fps of the first video is 30, so i just assume 30 fps for all videos.
        + (accounting for different fps is doable but seems like a drag and collage looks fine anyway.)
        + `endlength = 30*10` for example this assumes 30 fps, to get a 10 second ending blackness
    - paths: paths are rocket/<1-6>.mp4 and one rocket/launch.mp4
    - the part where i set x and y for each video individually, this is an ugly way of defining video sizes and positions. way better would be some tkinter interface to look at and play with the positionings, store them, then load them from this script.
    - `if not r or ('1' in v['path'] and count + startcount>1750):`
        +  i forgot what the 1750 is for lol
    - delete last line if you dont want to autoplay with mpv.

twitter vids are downloaded with this: https://ssstwitter.com/en
"""

import subprocess

import cv2
import numpy as np
import os, json

final = cv2.imread( 'rocket/blank.png' )  # is resized later
blank = cv2.imread('rocket/blank.png')
outpath = 'rocket/output.mp4'
bg_image = cv2.imread('rocket/blank.png')  # is resized later
startcount = 0  # at 0 unless testing code
endlength = 30*10
padx, pady = [ 100, 100 ]

vids = [ {'path':f'rocket/{i}.mp4'} for i in range(1,7) ]
vids.insert(0, { 'path':'rocket/launch.mp4' })

# ----------------------------------------------
vids = { i['path']:i for i in vids }

x = 300
y = 100
vids['rocket/launch.mp4'].update({ 'x':[0, 2], 'y':[0, 4] })
vids['rocket/6.mp4'].update({ 'x':[2, 3], 'y':[0, 4] })
vids['rocket/2.mp4'].update({ 'x':[0, 1], 'y':[4, 8] })
vids['rocket/3.mp4'].update({ 'x':[1, 2], 'y':[4, 8] })
vids['rocket/4.mp4'].update({ 'x':[2, 3], 'y':[4, 8] })
vids['rocket/1.mp4'].update({ 'x':[0, 1.5], 'y':[8, 12] })
vids['rocket/5.mp4'].update({ 'x':[1.5, 3], 'y':[8, 12] })

order = [
    'launch',
    '6',
    '2',
    '3',
    '4',
    '1',
    '5',
]
order = [ f'rocket/{i}.mp4' for i in order ]
vids = [ vids[k] for k in order ]

for v in vids:
    _x, _y = v['x'], v['y']
    _x = [ _x[0]*x, _x[1]*x ]
    _y = [ _y[0]*y, _y[1]*y ]
    _x = [ int(i) for i in _x ]
    _y = [ int(i) for i in _y ]
    v['x'] = _x
    v['y'] = _y
    w,h = [ v['x'][1]-v['x'][0] , v['y'][1]-v['y'][0] ]
    v['size'] = [ w, h ]
    print(v['path'], _x, _y, v['size'])
print(vids)
# ----------------------------------------------

for v in vids:
    cap = cv2.VideoCapture(v['path'])
    fcount = cap.get(cv2.CAP_PROP_FRAME_COUNT)
    cap.set(cv2.CAP_PROP_POS_FRAMES, 550 if 'launch' in v['path'] else 1500 if '1' in v['path'] else 700 if '5' in v['path'] else fcount-2 )
    ret, last = cap.read()
    cap.set(cv2.CAP_PROP_POS_FRAMES, startcount)

    last = blank

    w = cap.get(cv2.CAP_PROP_FRAME_WIDTH)
    h = cap.get(cv2.CAP_PROP_FRAME_HEIGHT)
    fps = cap.get(cv2.CAP_PROP_FPS)
    d = { 'cap':cap, 'done':0, 'fps':fps, 'last':last }
    v.update(d)
[ print({k:v for k,v in v.items() if k!='last'}) for v in vids ]

size = [ max(v['x'][1] for v in vids) + 2*padx, max(v['y'][1] for v in vids) + 2*pady ]
print(size)
if size[0]>2500 or size[1]>2500:  # big resolution crashes pc lol
    print(f'resolution too big: {size}, fix code')
    exit()
bg_image = cv2.resize(bg_image, size)
final = cv2.resize(final, size)

# writer object
outd = { 'path': outpath, 'size': size, 'fps': int( vids[0]['fps'] ) }
fourcc = cv2.VideoWriter_fourcc(*'h264')
writer = cv2.VideoWriter(outd['path'], fourcc, outd['fps'], outd['size'])

count = 0
ending_start = False
endcount = 0
# writer loop
while True:
    count += 1
    print(count)
    if count>200 and 0:
        break
    if all([v['done'] for v in vids]):
        if endcount > endlength:
            break
        else:
            ending_start = True
            endcount +=1

    frames = []
    for i, v in enumerate(vids):
        if v['done']:
            # f = blank
            f = vids[i]['last']
        else:
            r, f = v['cap'].read()
            if not r or ('1' in v['path'] and count + startcount>1750):
                v['done'] = True
                # f = blank
                f = vids[i]['last']
        frames.append(f)
    frame_bg = bg_image.copy()

    if not ending_start:
        for j, frame in enumerate(frames):
            vid = vids[j]
            frame = cv2.resize(frame, vid['size'] )
            row = int( vid['y'][0]/y )
            col = int( vid['x'][0]/x )
            row, col = 0, 0
            
            frame_bg[ vid['y'][0] + pady :vid['y'][1] + pady, vid['x'][0] + padx :vid['x'][1] + padx ] = frame

        writer.write(frame_bg)
    else:
        writer.write(final)

for v in vids:
    v['cap'].release()
writer.release()

subprocess.run( f'mpv {outpath} --loop' )
