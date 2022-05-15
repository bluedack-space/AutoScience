import sys
import toml

class TomlHandler:

    def __init__(self) -> None:
        pass

    def __del__(self) -> None:
        pass

    @staticmethod
    def displayContents(fileNameToml):
        with open(fileNameToml) as f:
            obj = toml.load(f)
            print(obj)
            data = toml.dumps(obj) 
            print(data)

    @staticmethod
    def getTomlObject(fileNameToml):
        try:
            with open(fileNameToml) as f:
                obj = toml.load(f)
                return obj
        except:
            return None

    @staticmethod
    def addNewItem(obj=None,key=None,value=None):
        obj[key] = value
    
    @staticmethod
    def save(obj=None,fileNameToml=None):
        with open(fileNameToml, 'w') as f:
            f.write(toml.dumps(obj))

if __name__ == '__main__':

    fileNameToml = sys.argv[1]

    #[01] Display All Contents of TOML
    TomlHandler.displayContents(fileNameToml=fileNameToml)

    #[02] Get Object of TOML
    obj = TomlHandler.getTomlObject(fileNameToml=fileNameToml)

    #[03] Add New Item to TOML Object
    TomlHandler.addNewItem(obj=obj,key='new',value='HOGE')

    #[04] Do something by using TOML
    if obj['app']=='AutoScience':
        print("This Toms data is for AutoScience")

    if obj['configuration']['type']=='log':
        print("This Toms data is for Log")
    
    print(obj)

    #[05] Save File
    TomlHandler.save(obj,fileNameToml="output.toml")
