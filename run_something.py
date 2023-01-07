import os

while True:
    files = os.listdir()
    for i,f in enumerate(files):
        print(f'{i} {f}')
    print('type a number to run that file')
    i = input()
    try:
        files[int(i)]
    except:
        input('invalid input')
    else:
        file = files[int(i)]
        os.system(f'python {file}')
        input()
        
