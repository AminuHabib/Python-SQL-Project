#ModuleInstaller is the function that will load the packages needed for the program
import subprocess
import sys

#import Conda as the environment
def __isConda()-> bool:
    try:
        import conda
    except:
        is_conda = False
    else:
        is_conda = True

    return is_conda

#import Pip as the environment
def __isPip()-> bool:
    try:
        import pip
    except:
        is_pip = False
    else:
        is_pip = True

    return is_pip

def installModule(package):
    
    packageManager = "pip"

    if __isConda() == True:
        packageManager = "conda"
        subprocess.check_call([sys.executable, "-m", packageManager, "install", "-y", package])
    else:
        subprocess.check_call([sys.executable, "-m", packageManager, "install", package])


     
 
    