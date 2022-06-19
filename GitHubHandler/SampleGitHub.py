import base64
import os
from github import Github

token      = '[Setting]>[Developer Setting]'
repository = 'bluedack-space/AutoScience'
dirName    = '/Image'
fileName   = 'C5587634-532B-405C-8BA5-7C955357571C.jpeg'

g            = Github(token)
repo         = g.get_repo(repository)
dir_contents = repo.get_dir_contents(dirName)

fileNameListImage = []
for i in range(len(dir_contents)):
    fileNameExist = dir_contents[i].name
    root, ext = os.path.splitext(fileNameExist)
    print(ext)
    if ext == '.jpeg' or ext == '.jpg':
        fileNameListImage.append(fileNameExist)

for n in range(len(fileNameListImage)):
    fileName = fileNameListImage[n]

    sha = 0
    for i in range(len(dir_contents)):
        if dir_contents[i].name == fileName:
            sha = dir_contents[i].sha

    blob    = repo.get_git_blob(sha)
    content = base64.b64decode(blob.content)

    with open(fileName, mode="wb") as f:
        f.write(content)
