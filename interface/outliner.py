import bisect

from style.styles import ISTYLES
from interface.base import Base_kookie, accent, xhover

def _print_counter(counter):
    items = [k.name if v == 1 else k.name + ' (' + str(v) + ')' for k, v in counter.tags.items() if v]
    if items:
        return ', '.join(items)
    else:
        return '{none}'

class Node(object):
    def __init__(self, O, display, link=None, collapsed=False):
        self.O = O
        self.text = display
        self.link = link
        self.collapsed = collapsed
        self.children = []

class Outliner(Base_kookie):
    def __init__(self, x, y, width, height, model, element):
        Base_kookie.__init__(self, x, y, width, height, font=('strong',))
        self._model = model
        self._element = element
        
        # set hover function equal to press function
        self.is_over_hover = self.is_over
        self._SYNCHRONIZE()

    def _SYNCHRONIZE(self):
        TREE = Node(self._model, 'Document')
        for PSTYLE in self._model:
            pnode = Node(PSTYLE, _print_counter(PSTYLE))
            for slot in PSTYLE.layerable:
                snode = Node(slot, _print_counter(slot))
                fnode = Node(slot.F, slot.F.name)
                if 'pegs' in slot.F.attributes:
                    fnode.children.append(Node(slot.F.attributes['pegs'], slot.F.attributes['pegs'].name))
                snode.children.append(fnode)
                pnode.children.append(snode)
            TREE.children.append(pnode)
        self._TREE = TREE
        print(len(self._model), len(TREE.children))
        
    def focus(self, x, y):
        pass

    def hover(self, x, y):
        return 1

    def draw(self, cr, hover=(None, None)):
        cr.set_source_rgb(0.25, 0.25, 0.25)
        x = self._x
        y = self._y
        P = self._element.P
        
        x += 20
        self.draw_node(cr, self._TREE, y, 0)
#            if PSTYLE.tags <= P:
#                cr.set_source_rgb(0.25, 0.25, 0.25)
#            else:
#                cr.set_source_rgb(0.7, 0.7, 0.7)


    def draw_node(self, cr, node, y, indent):
        y += 26
        x = self._x + indent
        cr.rectangle(x, y, 20, 1)
        cr.move_to(x + 30, y + 5)
        cr.show_text(node.text)
        cr.fill()
        for child in node.children:
            y = self.draw_node(cr, child, y, indent + 20)
        return y
