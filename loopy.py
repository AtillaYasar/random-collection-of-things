import os, subprocess, sys

args = sys.argv[1:]
while True:
    name = args[0]
    if name + '.py' not in os.listdir():
        print(f'{name} is not a program. write something like `loopy.py main`')
        exit()
    subprocess.run(["python", "-m", name])
