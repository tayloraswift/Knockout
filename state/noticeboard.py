# for typing state
composition_sequence = []

# for refreshing the ui
class Refresh_draw(object):
    def __init__(self):
        self._properties_refresh = True
    
    def push_change(self):
        self._properties_refresh = True
    
    def should_refresh(self):
        if self._properties_refresh:
            self._properties_refresh = False
            return True
        else:
            return False

class Refresh_with_param(object):
    def __init__(self):
        self._properties_refresh = True
        self._parameter = None
    
    def push_change(self, param):
        self._properties_refresh = True
        self._parameter = param
    
    def should_refresh(self):
        if self._properties_refresh:
            self._properties_refresh = False
            return True, self._parameter
        else:
            return False, False

class Selection_menus(object):
    def __init__(self):
        self._menus = {}
    
    def add_menu(self, ID):
        self._menus[ID] = False
    
    def push_refresh(self, ID):
        self._menus[ID] = True
    
    def should_refresh(self, ID):
        if self._menus[ID]:
            self._menus[ID] = False
            return True
        else:
            return False

refresh = Refresh_draw()
refresh_properties_stack = Refresh_draw()
refresh_properties_type = Refresh_with_param()

menus = Selection_menus()
