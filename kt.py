#!/usr/bin/env python3.5

import sys

from os import environ
environ['LD_LIBRARY_PATH'] = 'libraries/HB/lib/girepository-1.0'
environ['GI_TYPELIB_PATH'] = 'libraries/HB/lib/girepository-1.0'

from IO import sierra

_fail = '\033[91m'
_endc = '\033[0m'
_bold = '\033[1m'

def main(argv):
    try:
        filename = argv[1]
    except IndexError:
        print (_fail + _bold + 'ERROR:' + _endc + _fail + ' No document file specified!' + _endc)
        filename = 'default.html'
    try:
        sierra.load(filename)

    except FileNotFoundError:
        print (_fail + _bold + 'ERROR:' + _endc + _fail + ' Document file \'' + filename + '\' does not exist!' + _endc)
        sierra.load('default.html')
    
    import app
    app.main()
    
if __name__ == "__main__":
    main(sys.argv)
