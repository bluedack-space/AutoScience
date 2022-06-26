import base64
import os
from github import Github

import traceback

from enum import Enum

class FileType(Enum):
    BINARY = 1
    ASCII  = 2

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
        
        
        fileNameListDL = []
        
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
                
                fileNameListDL.append(fileName)
                                
        if len(fileNameListDL)>0:
            return True, fileNameListDL
        else:
            return False, None
        
    @staticmethod
    def getFileNameListLocal(extList):
        import glob
        fileNameListLocal = []
        for i in range(len(extList)):
            files = glob.glob("./*"+extList[i])
            for ii in range(len(files)):
                fileNameListLocal.append(os.path.basename(files[ii]))
        return fileNameListLocal

    @staticmethod
    def getFileType(fileName=None):
        root, ext = os.path.splitext(fileName)
        if ext==".jpeg" or ext==".jpg" or ext==".bmp" or ext==".png":
            return FileType.BINARY
        elif ext==".stl":
            return FileType.BINARY
        else:
            return FileType.ASCII
        
    @staticmethod
    def uploadFile(repo,fileNameList=None,dirPath=None,branch="main"):
        
        try:
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
                
                print("UL:"+str(fileName))
                                
                if GitHubHandler.getFileType(fileName=fileName)==FileType.BINARY:
                    fopenType = 'rb'               
                else:
                    fopenType = 'r'               
                    
                with open(fileName, fopenType) as file:
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
                    
        except:
            print("Error")
            print(traceback.format_exc())
        

import cv2

#------------------------------------------------------------------------------------------------
token         = '[token]'
repository    = 'bluedack-space/AutoScience'
dirName       = '/Image'
extList       = ['.jpeg','.jpg']

gitHdl        = GitHubHandler ( token )
repo          = gitHdl.getRepository ( repository )

#[Download files]
import time
while True:
    dirContents       = gitHdl.getDirectoryContents ( repo, dirName )
    fileNameList      = gitHdl.getFileNameList ( dirContents, extList )
    fileNameListLocal = gitHdl.getFileNameListLocal(extList)
    flagDownLoaded, fileNameListDL    = gitHdl.downloadAll ( dirContents, fileNameList, fileNameListLocal )
    
    if fileNameListDL!=None:
        fileNameListUL = []
        for ii in range(len(fileNameListDL)):
            fileName = fileNameListDL[ii]
            
            img         = cv2.imread(fileName)
            img_gray    = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
            
            root, ext = os.path.splitext(fileName)
            fileNameOut = root+"-asd"+ext
            
            cv2.imwrite(fileNameOut, img_gray)
            
            fileNameListUL.append(fileNameOut) 

        #[Upload files]
        print("!!!!"+str(fileNameListUL))
        GitHubHandler.uploadFile(repo,fileNameList=fileNameListUL,dirPath="./Image/",branch="main")

    if flagDownLoaded:
        print("New Downloaded file is found !!!!")
    
    print("Waiting for next checking....")
    time.sleep(10.0)
