from state import contexts
from model import meredith
from fonts import styles

class Text_ops(object):
    def __init__(self):
        self.context = contexts.Text
    
    def link_parastyle(self, P):
        self.context.paragraph[1] = P
    
    def p_set_attribute(self, value, A):
        setattr(self.context.paragraph[1], A, (False, value))
        styles.PARASTYLES.update_tables()
        meredith.mipsy.recalculate_all()

    def p_link_inheritance(self, P, A):
        PSTYLE = self.context.paragraph[1]
        if P is None:
            setattr(PSTYLE, A, (False, getattr(PSTYLE, 'u_' + A)))
        else:
            # save old value in case of a disaster
            V = getattr(PSTYLE, A)
            setattr(PSTYLE, A, (True, P))

            try:
                styles.PARASTYLES.update_tables()
            except RuntimeError:
                setattr(PSTYLE, A, V)
                print('REFERENCE LOOP DETECTED')
                styles.PARASTYLES.update_tables()
        
        meredith.mipsy.recalculate_all()

Text = Text_ops()
