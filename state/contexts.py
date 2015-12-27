from model import meredith

class Text_context(object):
    def __init__(self):
        self.update()
    def update(self):
        self.tract = meredith.mipsy.tracts[0]
        self.paragraph =  self.tract.text[meredith.mipsy.paragraph_at()[1]]
    
    def update_p(self, p):
        self.paragraph = self.tract.text[p[1]]

Text = Text_context()
