"""
This is the factoriopath module. 

It looks for a .factorioPath in $HOME, but otherwise tries to figure out the best place for a factorio install.

"""
import os

def getFactorioPath():
    try:
        with open("%s/.factorioPath" % (os.path.expanduser("~")), "r") as data_file:
            path = data_file.readline().strip()
    except:
        print("%s/.factorioPath not found. Using default." % (expanduser("~")))
        if os.path.isdir("/opt/factorio"):
            path = "/opt/factorio"
        elif os.access("/opt", os.W_OK):
            path = "/opt/factorio"
        else:
            path = "%s/factorio" % (expanduser("~"))
    return path

if __name__ == "__main__":
    import doctest
    doctest.testmod()   