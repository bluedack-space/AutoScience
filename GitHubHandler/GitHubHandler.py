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
        return ffileNameListLocal
        
    @staticmethod
    def uploadFile(repo,fileNameList=None,dirPath=None,branch="main"):
        all_files = []
        contents  = repo.get_contents("")
        while contents:
            file_content = contents.pop(0)
            if file_content.type == "dir":
                contents.extend(repo.get_contents(file_content.path))
            else:
                file = file_content
                all_files.append(str(file).replace('ContentFile(path="','').replace('")',''))
    
        for i in range(len(fileNameList)):
            fileName = fileNameList[i]
        
            with open(fileName, 'r') as file:
                content = file.read()

            git_prefix = dirPath
            git_file   = git_prefix + fileName

            if git_file in all_files:
                contents = repo.get_contents(git_file)
                repo.update_file(contents.path, "committing files", content, contents.sha, branch="main")
                print(git_file + ' UPDATED')
            else:
                repo.create_file(git_file, "committing files", content, branch="main")
                print(git_file + ' CREATED')

#------------------------------------------------------------------------------------------------
token         = '[token]'
repository    = 'bluedack-space/AutoScience'
dirName       = '/Image'
extList       = ['.jpeg','.jpg']

gitHdl        = GitHubHandler ( token )
repo          = gitHdl.getRepository ( repository )

#[Upload files]
GitHubHandler.uploadFile(repo,fileNameList=["file1.txt","file2.txt"],dirPath="./Image/",branch="main")

#[Download files]
import time
while True:
    dirContents       = gitHdl.getDirectoryContents ( repo, dirName )
    fileNameList      = gitHdl.getFileNameList ( dirContents, extList )
    fileNameListLocal = gitHdl.getFileNameListLocal(extList)
    flagDownLoaded    = gitHdl.downloadAll ( dirContents, fileNameList, fileNameListLocal )
    
    if flagDownLoaded:
        print("New Downloaded file is found !!!!")
    
    print("Waiting for next checking....")
    time.sleep(10.0)