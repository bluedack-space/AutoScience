import sys

from PIL import Image, ExifTags
from pprint import pprint
import piexif

import traceback

import re

class ImageMetaDataHandler:
    img = None

    def __init__(self) -> None:
        pass

    def __del__(self) -> None:
        pass
    
    def openImage(self,fileNameImage=None):
        try:
            self.img = Image.open(fileNameImage)
        except:
            traceback.print_exc()
            
    def getEXIF(self):
        return self.img._getexif()

    def getEXIF_Values(self):
        return self.img._getexif().values()

    @staticmethod
    def getTagNameList():
        tags = ExifTags.TAGS
        return tags

    @staticmethod
    def displayTagNameList():
        tags = ImageMetaDataHandler.getTagNameList()
        pprint(tags)

    @staticmethod
    def setEXIF_Comment(fileNameImage=None,comment=None):
        exif_dict = piexif.load(fileNameImage)
        exif_dict['0th'][40092] = ImageMetaDataHandler.convertStringToEXIFBytes(comment)
        exif_bytes = piexif.dump(exif_dict)
        piexif.insert(exif_bytes, fileNameImage)

    @staticmethod
    def setEXIF_Tag(fileNameImage=None,tag=None):
        exif_dict = piexif.load(fileNameImage)
        exif_dict['0th'][40094] = ImageMetaDataHandler.convertStringToEXIFBytes(tag)
        exif_bytes = piexif.dump(exif_dict)
        piexif.insert(exif_bytes, fileNameImage)

    def getEXIF_Tag(self):
        exif_dict = self.getEXIF()
        
        tag = exif_dict[40094]
        print(tag)
        tag = tag.decode("utf-8").replace("\x00","")
        print(tag)
        #tag = re.sub(r"[\n\r]+","",u)

        return tag 
                
    @staticmethod
    def convertStringToEXIFBytes(string):
        stringArray = list(string)
        asciiArray = ()
        for letter in stringArray:
            asciiArray = asciiArray + (ord(letter), 0)
        asciiArray = asciiArray + (0, 0)
        return asciiArray

if __name__ == '__main__':

    filename = "IMG_1495.JPG"

    # [01] Insert comment and camera information 
    ImageMetaDataHandler.setEXIF_Comment(fileNameImage=filename,comment="Hello this is inserted comment !")
    ImageMetaDataHandler.setEXIF_Tag(fileNameImage=filename,tag="EL30;AZ45")

    # [02] Constructor and image file open
    imgMetaHdl = ImageMetaDataHandler()
    imgMetaHdl.openImage(fileNameImage=filename)

    buff = imgMetaHdl.getEXIF_Tag()
    print(buff)
    
    # [03] Get Exif data and display those
    #dict = imgMetaHdl.getEXIF()
    #print(dict)

    # [04] Check of the comment and camera information
    #for i in range(len(dict)):
    #    value = list(dict.values())[i]
    #    if type(value) is bytes:
    #        print(value.decode("utf-8"))