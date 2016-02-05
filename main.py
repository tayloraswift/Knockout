import sys

from IO import sierra

_fail = '\033[91m'
_endc = '\033[0m'
_bold = '\033[1m'

def main(argv):
    try:
        filename = argv[1]
    except IndexError:
        print (_fail + _bold + 'ERROR:' + _endc + _fail + ' No document file specified!' + _endc)
        filename = 'default.txt'
    try:
        sierra.load(filename)

    except FileNotFoundError:
        print (_fail + _bold + 'ERROR:' + _endc + _fail + ' Document file \'' + filename + '\' does not exist!' + _endc)
        sierra.load('default.txt')
    
    import app
    app.main()
    
if __name__ == "__main__":
    main(sys.argv)
