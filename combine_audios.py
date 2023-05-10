import os, time
from pydub import AudioSegment

folder = "to_paste"
if not os.path.exists(folder):
    os.makedirs(folder)
results_folder = "results"
if not os.path.exists(results_folder):
    os.makedirs(results_folder)
input(f'put audio files in the "{folder}" folder and hit enter when ready, combined audio will be in the "{results_folder}" folder')

files = sorted([f for f in os.listdir(folder) if f.endswith('.mp3')])
for f in files:
    print(f)
i = input('hit enter if youre happy with the ordering.')

combined = AudioSegment.empty()
for f in files:
    combined += AudioSegment.from_mp3(folder + '/' + f)
outpath = results_folder + '/combined' + str(time.time()).split('.')[0] + '.mp3'
combined.export(outpath, format="mp3")
print(f'saved to {outpath}')
