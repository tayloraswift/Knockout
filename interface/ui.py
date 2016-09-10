class Cell(object):
    def key_input(self, name, char):
        print(name)
    
    def hover(self, x, y=-1):
        pass
    
    def scroll(self, x, y=-1, char='', axis=False):
        pass
    
    def press(self, x, y=-1, char=''):
        pass
    
    def press_mid(self, x, y=-1):
        pass
    
    def press_right(self, x, y=-1):
        pass
    
    
    def dpress(self):
        pass
    
    
    def press_motion(self, x, y=-1):
        pass
    
    def drag(self, x, y=-1):
        pass
    
    
    def release(self, x, y=-1):
        pass
