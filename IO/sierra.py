from state import noticeboard
from state.contexts import Interface_context

from IO import tree, un

default_peripheral_data = (('textcursor', '<textcursor plane="0" i="0" j="0"/>'), 
    ('framecursor', '<framecursor section="0" frame="0"/>'), 
    ('view'       , '<view h="0" k="0" hc="0" kc="0" zoom="11" mode="text"/>'))

def load(name):
    with open(name, 'r') as fi:
        doc = fi.read()
    print(name)
    KT = tree.Knockout(name)
    
    KT.deserialize_high('<texttags/><blocktags/>')
    KT.deserialize_high(doc, default_peripheral_data)
    KT.setup_editors()
    
    KT.BODY.layout_all()

    # start undo tracking
    from interface import karlie, taylor
    context = Interface_context(KT)
    
    noticeboard.refresh_properties_type.push_change(KT.VIEW.mode)
    becky   = taylor.Document_view  (KT, context)
    klossy  = karlie.Properties     (KT, context, partition=1)
    
    panes = Panes(KT, becky, klossy)
    
    un.history.reset(KT, context, panes)
    un.history.save()
    
    return panes


class Panes(object):
    def __init__(self, KT, item1, item2):
        self.KT     = KT
        self.panes  = item1, item2
        self._p     = 950
        
        self.A      = 0
        self.H      = 0
        self.active = item1
        self.hover  = item1
        
        self.h      = None
        self.k      = None

    def critical_width(self):
        return self.h - self._p
    
    def _item_size(self):
        self.panes[0].resize(self._p         , self.k)
        self.panes[1].resize(self.h - self._p, self.k)

    def pane(self, x):
        return -10 < x - self._p < 10

    def pane_resize(self, x):
        self._p = min(self.h - 175, max(175, int(x)))
        self._item_size()
        return self.h - self._p

    def resize(self, h, k):
        if self.h is not None:
            self._p += h - self.h
        self.h = h
        self.k = k
        self._item_size()
    
    def set_active_hover_region(self, x, y):
        r = x > self._p
        O = self.panes[r]
        if self.hover is not O:
            self.hover.hover(-1, -1)
            self.hover = O
        self.H = r
        return self.convert(x, y, r)

    def set_active_region(self, x, y):
        r = x > self._p
        O = self.panes[r]
        if self.active is not O:
            self.active.exit()
            self.active = O
        if self.hover is not O:
            self.hover.hover(-1, -1)
            self.hover = O
        self.A = r
        return self.convert(x, y, r)
    
    def convert(self, x, y, r):
        if r:
            return x - self._p, y
        else:
            return x, y
    
    def shortcuts(self):
        self.panes[0].shortcuts()
        self.panes[1].shortcuts()
