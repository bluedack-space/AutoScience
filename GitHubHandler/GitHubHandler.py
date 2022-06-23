import base64
import os
from github import Github

class GitHubHandler():

    github = None

    def __init__(self,token):
        self.Github(token)

    def __del__(self):
        pass

    def Github(self,token):
        self.github = Github(token)
    
    def getRepository(self,repository):
        return self.github.get_repo(repository)

    def getDirectoryContents(self,repo,dirName):
        dirContents = repo.get_dir_contents(dirName)
        return dirContents
    
    def getFileNameList(self,dirContents,extList):
        fileNameList = []
        for i in range(len(dirContents)):
            fileNameExist = dirContents[i].name
            root, ext = os.path.splitext(fileNameExist)
            if ext in extList:
                print("########"+fileNameExist)
                fileNameList.append(fileNameExist)
        return fileNameList

    def downloadAll(self,dirContents,fileNameList):

        for n in range(len(fileNameList)):

            fileName = fileNameList[n]

            sha = 0
            for i in range(len(dirContents)):
                if dirContents[i].name == fileName:
                    sha = dirContents[i].sha

            blob    = repo.get_git_blob(sha)
            content = base64.b64decode(blob.content)

            with open(fileName, mode="wb") as f:
                f.write(content)

token      = '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'
repository = 'bluedack-space/AutoScience'
dirName    = '/Image'
extList    = ['.jpeg','.jpg']

gitHdl            = GitHubHandler ( token )
repo              = gitHdl.getRepository ( repository )
dirContents       = gitHdl.getDirectoryContents ( repo, dirName )
fileNameList      = gitHdl.getFileNameList ( dirContents, extList )
gitHdl.downloadAll ( dirContents, fileNameList )
