#!/usr/bin/env python3.5

import sys

from os import environ
environ['LD_LIBRARY_PATH'] = '/usr/local/lib/girepository-1.0'
environ['GI_TYPELIB_PATH'] = '/usr/local/lib/girepository-1.0'

from interface.splash import Recent

_fail = '\033[91m'
_endc = '\033[0m'
_bold = '\033[1m'

def main(argv):
    recent = Recent('data/recent.txt')
    
    from app import Gtk, Display
    app = Display()
    
    splash = True
    if len(argv) > 1:
        try:
            app.reload(argv[1])
        
        except FileNotFoundError:
            print (_fail + _bold + 'ERROR:' + _endc + _fail + ' Document file \'' + argv[1] + '\' does not exist!' + _endc)
            app.reload('default.html')
        
        else:
            recent.add(argv[1])
            splash = False
    else:
        app.reload('default.html')
    
    if splash:
        app.make_splash(recent)
    app.show_all()
    Gtk.main()
    
if __name__ == "__main__":
    main(sys.argv)
