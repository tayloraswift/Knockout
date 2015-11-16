class Cell(object):

    def key_input(self, name, char):
        print(name)
    
    def hover(self, x, y=-1):
        print((x, y))
    
    def scroll(self, x, y=-1, char=''):
        print((x, y, char))
    
    
    def press(self, x, y=-1, char=''):
        print((x, y))
    
    def press_mid(self, x, y=-1):
        print((x, y))
    
    def press_right(self, x, y=-1):
        print((x, y))
    
    
    def dpress(self):
        print('double click')
    
    
    def press_motion(self, x, y=-1):
        print((x, y))
    
    def drag(self, x, y=-1):
        print((x, y))
    
    
    def release(self, x, y=-1):
        print('release')
