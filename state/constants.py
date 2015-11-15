filename = ''

windowwidth = 1300
windowheight = 800

UI = [0, 1000]

class Window(object):
    def __init__(self, h, k):
        self.resize(h, k)
    
    def get_k(self):
        return self.k
    
    def get_h(self):
        return self.h
    
    def resize(self, h, k):
        self.h = h
        self.k = k

window = Window(1300, 800)
