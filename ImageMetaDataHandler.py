import sys

from PIL import Image, ExifTags
from pprint import pprint
import piexif

class ImageMetaDataHandler:
    img = None

    def __init__(self) -> None:
        pass

    def __del__(self) -> None:
        pass
    
    def openImage(self,fileNameImage=None):
        self.img = Image.open(filename)

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

    @staticmethod
    def convertStringToEXIFBytes(string):
        stringArray = list(string)
        asciiArray = ()
        for letter in stringArray:
            asciiArray = asciiArray + (ord(letter), 0)
        asciiArray = asciiArray + (0, 0)
        return asciiArray

if __name__ == '__main__':

    filename = sys.argv[1]

    # [01] Insert comment and camera information 
    ImageMetaDataHandler.setEXIF_Comment(fileNameImage=filename,comment="Hello this is inserted comment !")
    ImageMetaDataHandler.setEXIF_Tag(fileNameImage=filename,tag="EL30;AZ45")

    # [02] Constructor and image file open
    imgMetaHdl = ImageMetaDataHandler()
    imgMetaHdl.openImage(fileNameImage=filename)

    # [03] Get Exif data and display those
    dict = imgMetaHdl.getEXIF()
    print(dict)

    # [04] Check of the comment and camera information
    for i in range(len(dict)):
        value = list(dict.values())[i]
        if type(value) is bytes:
            print(value.decode("utf-8"))
