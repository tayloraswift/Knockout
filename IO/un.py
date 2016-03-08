from copy import deepcopy

from style import styles
from model import meredith
from IO import kevin
from edit import cursor

class UN(object):
    def __init__(self):
        self._history = []
        self._i = 0
        
        self._state = None
    
    def save(self):
        if len(self._history) > 989:
            del self._history[:89]
            self._i -= 89
        
        kitty = [(kevin.serialize(t.text), deepcopy(t.channels.channels), t.text.misspellings[:]) for t in meredith.mipsy]
        page_xy = (meredith.page.WIDTH, meredith.page.HEIGHT)
        
        textcontexts = cursor.fcursor.polaroid()
        channelcontexts = {
#                        't': meredith.mipsy.index(caramel.delight.R_FTX),
#                        'c': caramel.delight.C(), 
#                        'p': caramel.delight.PG
                        }
        if len(self._history) > self._i:
            del self._history[self._i:]
        
        # save styles
        PPP = styles.PARASTYLES.polaroid()
        FFF = {N: F.polaroid() for N, F in styles.FONTSTYLES.items()}

        PTT = [T.polaroid() for T in styles.PTAGS.values() if not T.is_group]
        FTT = [T.polaroid() for T in styles.FTAGS.values() if not T.is_group]

        self._history.append({'kitty': kitty, 'contexts': {'text': textcontexts, 'channels': channelcontexts}, 'styles': {'PARASTYLES': PPP, 'FONTSTYLES': FFF, 'PTAGLIST': PTT, 'FTAGLIST': FTT}, 'page': page_xy})
        self._i = len(self._history)

    def pop(self):
        del self._history[-1]
        self._i = len(self._history)
        
    def _restore(self, i):
        image = self._history[i]
        styles.faith(image['styles'])
        
        meredith.page.WIDTH, meredith.page.HEIGHT = image['page']

        for t in range(len(meredith.mipsy)):
            text, channels, msp = image['kitty'][t]
            meredith.mipsy[t].text[:] = kevin.deserialize(text)
            meredith.mipsy[t].text.misspellings = msp
            meredith.mipsy[t].channels.channels = channels
        
        cursor.fcursor.__init__(image['contexts']['text'])
    
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
