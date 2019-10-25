from shutil import copyfile
from os import listdir
from os.path import isfile, join

onlyfiles = [f for f in listdir('./new/') if isfile(join('./new/', f))]
onlyfiles.sort()
print(onlyfiles)

i = 1
for infile in onlyfiles:
    if infile[len(infile)-3:len(infile)] == 'png':
        if i <= 9:
            suffix = f'00{i}'
        elif i <= 99:
            suffix = f'0{i}'
        else:
            suffix = f'{i}'

        copyfile('./new/'+infile, f'./files/image_{suffix}.png')
        i += 1

# ffmpeg -framerate 1/5 -pattern_type glob -i "./files/*.png" -vf "fps=25" out.mp4 -vf "pad=ceil(iw/2)*2:ceil(ih/2)*2"
