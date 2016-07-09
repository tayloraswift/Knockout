#!/usr/bin/env python3.5

import sys

from os import environ
environ['LD_LIBRARY_PATH'] = '/usr/local/lib/girepository-1.0'
environ['GI_TYPELIB_PATH'] = '/usr/local/lib/girepository-1.0'

from IO import sierra

from interface.splash import Recent

_fail = '\033[91m'
_endc = '\033[0m'
_bold = '\033[1m'

def main(argv):
    recent = Recent('data/recent.txt')
    if len(argv) > 1:
        try:
            sierra.load(argv[1])
        
        except FileNotFoundError:
            print (_fail + _bold + 'ERROR:' + _endc + _fail + ' Document file \'' + filename + '\' does not exist!' + _endc)
            sierra.load('default.html')
        
        else:
            recent.add(argv[1])
            recent = None
    else:
        sierra.load('default.html')
    
    from app import Gtk, Display
    app = Display(recent)
    Gtk.main()
    
if __name__ == "__main__":
    main(sys.argv)
