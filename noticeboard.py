
class Refresh_draw(object):
    def __init__(self):
        self.properties_refresh = True
    
    def push_change(self):
        self.properties_refresh = True
    
    def should_refresh(self):
        if self.properties_refresh:
            self.properties_refresh = False
            return True
        else:
            return False

refresh = Refresh_draw()
