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

    def downloadAll(self,dirContents,fileNameList,fileNameListLocal):
        
        numberOfDownload = 0

        for n in range(len(fileNameList)):
            fileName = fileNameList[n]
            
            if not (fileName in fileNameListLocal):
                print("DownLoading...")
                sha = 0
                for i in range(len(dirContents)):
                    if dirContents[i].name == fileName:
                        sha = dirContents[i].sha

                blob    = repo.get_git_blob(sha)
                content = base64.b64decode(blob.content)

                with open(fileName, mode="wb") as f:
                    f.write(content)
                numberOfDownload = numberOfDownload + 1
                
        if numberOfDownload>0:
            return True
        else:
            return False
        
    @staticmethod
    def getFileNameListLocal(extList):
        import glob
        fileNameListLocal = []
        for i in range(len(extList)):
            files = glob.glob("./*"+extList[i])
            for ii in range(len(files)):
                fileNameListLocal.append(os.path.basename(files[ii]))
        return fileNameListLocal

token         = '[token]'
repository    = 'bluedack-space/AutoScience'
dirName       = '/Image'
extList       = ['.jpeg','.jpg']

gitHdl        = GitHubHandler ( token )
repo          = gitHdl.getRepository ( repository )

import time
while True:
    dirContents   = gitHdl.getDirectoryContents ( repo, dirName )
    fileNameList      = gitHdl.getFileNameList ( dirContents, extList )
    fileNameListLocal = gitHdl.getFileNameListLocal(extList)
    flagDownLoaded    = gitHdl.downloadAll ( dirContents, fileNameList, fileNameListLocal )
    
    if flagDownLoaded:
        print("New Downloaded file is found !!!!")
    
    print("Waiting for next checking....")
    time.sleep(10.0)