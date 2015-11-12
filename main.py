import sys

import sierra

def main(argv):
    try:
        sierra.load(argv[1])

    except IndexError:
        print ('No document file specified!')
        sierra.load('default.txt')
    
    import rt
    rt.main()
    
if __name__ == "__main__":
    main(sys.argv)
