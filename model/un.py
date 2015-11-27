from copy import deepcopy

from fonts.fonts import GET, REPLACE

from model.meredith import mipsy
from model import penclick


class UN(object):
    def __init__(self):
        self._history = []
        self._i = 0
        
        self._state = 0
    
    def save(self):
        if len(self._history) > 989:
            del self._history[:89]
            self._i -= 89
        
        kitty = [{'text': tuple(t.text), 'spelling': t.misspellings[:], 'outline': deepcopy(t.channels.channels), 'cursors': (t.cursor.cursor, t.select.cursor)} for t in mipsy.tracts]
        page_xy = (penclick.page.WIDTH, penclick.page.HEIGHT)
        if len(self._history) > self._i:
            del self._history[self._i:]
        self._history.append({'kitty': kitty, 'styles': deepcopy(GET()), 'page': page_xy})
        self._i = len(self._history)
    
    def pop(self):
        del self._history[-1]
        self._i = len(self._history)
        
    def _restore(self, i):
        REPLACE(self._history[i]['styles'])
        penclick.page.WIDTH, penclick.page.HEIGHT = self._history[i]['page']

        for t in range(len(mipsy.tracts)):
            mipsy.tracts[t].text = list(self._history[i]['kitty'][t]['text'])
            mipsy.tracts[t].misspellings = self._history[i]['kitty'][t]['spelling']
            mipsy.tracts[t].cursor.cursor = self._history[i]['kitty'][t]['cursors'][0]
            mipsy.tracts[t].select.cursor = self._history[i]['kitty'][t]['cursors'][1]
            mipsy.tracts[t].channels.channels = self._history[i]['kitty'][t]['outline']
    
    def back(self):
        if self._i > 0:
            if self._i == len(self._history):
                self.save()
                self._i -= 1
            
            self._i -= 1
            self._restore(self._i)
            
            return True
        else:
            print('No steps to undo')
            self._state = -89
            return False
    
    def forward(self):
        try:
            self._restore(self._i + 1)
            self._i += 1
            
            return True
        except IndexError:
            print('No steps to redo')
            self._state = -89
            return False

    # prevents excessive savings
    def undo_save(self, state):
        if state != self._state or state == 3:
            if self._state != 0:
                self.save()
            self._state = state
            
history = UN() 
