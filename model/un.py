from copy import deepcopy

from fonts import styles

from model.meredith import mipsy
from state.ctext import Tract
from model import penclick, kevin, cursor


class UN(object):
    def __init__(self):
        self._history = []
        self._i = 0
        
        self._state = None
    
    def save(self):
        if len(self._history) > 989:
            del self._history[:89]
            self._i -= 89
        
        kitty = [{'text': kevin.serialize(t.text), 'spelling': t.misspellings[:], 'outline': deepcopy(t.channels.channels)} for t in mipsy.tracts]
        page_xy = (penclick.page.WIDTH, penclick.page.HEIGHT)
        contexts = {'t': mipsy.tracts.index(Tract.tract),
                'i': cursor.fcursor.i,
                'j': cursor.fcursor.j}
        if len(self._history) > self._i:
            del self._history[self._i:]
        
        # save styles
        PPP = styles.PARASTYLES.polaroid()
        FFF = {N: F.polaroid() for N, F in styles.FONTSTYLES.items()}
        
        GGG = {N: G.polaroid() for N, G in styles.PEGS.items()}
        PTT = [T.polaroid() for T in styles.PTAGS.values() if not T.is_group]
        FTT = [T.polaroid() for T in styles.FTAGS.values() if not T.is_group]

        self._history.append({'kitty': kitty, 'contexts': contexts, 'styles': {'PARASTYLES': PPP, 'FONTSTYLES': FFF, 'PTAGLIST': PTT, 'FTAGLIST': FTT, 'PEGS': GGG}, 'page': page_xy})
        self._i = len(self._history)

    def pop(self):
        del self._history[-1]
        self._i = len(self._history)
        
    def _restore(self, i):
        image = self._history[i]
        styles.faith(image['styles'])
        
        penclick.page.WIDTH, penclick.page.HEIGHT = image['page']

        Tract.tract = mipsy.tracts[image['contexts']['t']]
        for t in range(len(mipsy.tracts)):
            mipsy.tracts[t].text = kevin.deserialize(image['kitty'][t]['text'])
            mipsy.tracts[t].misspellings = image['kitty'][t]['spelling']
            mipsy.tracts[t].channels.channels = image['kitty'][t]['outline']
        
        cursor.fcursor.__init__(Tract.tract, image['contexts']['i'], image['contexts']['j'])
    
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
