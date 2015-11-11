import sys

import sierra

if __name__ == "__main__":
    try:
        sierra.load(sys.argv[1])

    except IndexError:
        print ('No document file specified!')
        sierra.load('default.txt')
    
    import rt
    rt.main()
