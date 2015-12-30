from state import contexts
from model import meredith
from fonts import styles

class Tag_ops(object):
    def __init__(self):
        self.context = contexts.Tag
    
    def t_set_attribute(self, value, A):
        setattr(self.context.tag, A, value)
        styles.PARASTYLES.update_tables()
        meredith.mipsy.recalculate_all()
    
    def rename_active_subtag(self, name):
        T = self.context.tag
        T.elements[name] = T.elements.pop(T.active)
        T.active = name

class Text_ops(object):
    def __init__(self):
        self.context = contexts.Text
    
    def link_parastyle(self, P):
        self.context.paragraph[1] = P
        contexts.Text.update_force()

class Para_ops(object):
    def __init__(self):
        self.context = contexts.Parastyle
    
    def p_set_attribute(self, value, A):
        setattr(self.context.parastyle, A, (False, value))
        styles.PARASTYLES.update_tables()
        meredith.mipsy.recalculate_all()

    def p_link_inheritance(self, P, A):
        if P is None:
            setattr(self.context.parastyle, A, (False, getattr(self.context.parastyle, 'u_' + A)))
        else:
            # save old value in case of a disaster
            V = getattr(self.context.parastyle, A)
            setattr(self.context.parastyle, A, (True, P))

            try:
                styles.PARASTYLES.update_tables()
            except RuntimeError:
                setattr(self.context.parastyle, A, V)
                print('REFERENCE LOOP DETECTED')
                styles.PARASTYLES.update_tables()
        
        meredith.mipsy.recalculate_all()
    
    def link_keymap(self, M):
        self.context.parastyle.fontclasses = M
        contexts.Keymap.update(M)
        styles.PARASTYLES.update_tables()

class Keymap_ops(object):
    def __init__(self):
        self.context = contexts.Keymap

    def add_key(self):
        self.context.keymap.add_slot()
    
    def del_active_key(self):
        self.context.keymap.delete_slot()
    
    def remap_active(self, states):
        tags = tuple(sorted(T.name for state, T in zip(states, styles.TAGLIST.ordered) if state))
        M = self.context.keymap.elements
        if tags in self.context.keymap.elements:
            tags = ('_occupied', ) + tags

        M[tags] = M.pop(self.context.keymap.active)
        self.context.keymap.active = tags
        styles.PARASTYLES.update_tables()

    def link_fontstyle(self, F):
        self.context.keymap.elements[self.context.keymap.active] = F
        contexts.Fontstyle.update(F)
        styles.PARASTYLES.update_tables()

class Font_ops(object):
    def __init__(self):
        self.context = contexts.Fontstyle
    
    def f_set_attribute(self, value, A):
        setattr(self.context.fontstyle, A, (False, value))
        styles.FONTSTYLES.update_tables()
        meredith.mipsy.recalculate_all()

    def f_link_inheritance(self, F, A):
        if F is None:
            setattr(self.context.fontstyle, A, (False, getattr(self.context.fontstyle, 'u_' + A)))
        else:
            # save old value in case of a disaster
            V = getattr(self.context.fontstyle, A)
            setattr(self.context.fontstyle, A, (True, F))

            try:
                styles.FONTSTYLES.update_tables()
            except RuntimeError:
                setattr(self.context.fontstyle, A, V)
                print('REFERENCE LOOP DETECTED')
                styles.FONTSTYLES.update_tables()
        
        meredith.mipsy.recalculate_all()

    def link_pegs(self, G):
        self.context.fontstyle.pegs = G
        contexts.Pegs.update(G)
#        styles.PARASTYLES.update_tables()

class Pegs_ops(object):
    def __init__(self):
        self.context = contexts.Pegs
    
    def set_active_x(self, x):
        G = contexts.Pegs.pegs
        G.elements[G.active][0] = x

    def set_active_y(self, y):
        G = contexts.Pegs.pegs
        G.elements[G.active][1] = y

Text = Text_ops()
Parastyle = Para_ops()
Keymap = Keymap_ops()
Fontstyle = Font_ops()
Pegs = Pegs_ops()

Tag = Tag_ops()
