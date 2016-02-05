from model import meredith
from style import styles

def p_set_attribute(value, A):
    styles.PARASTYLES.active.attributes[A] = value
    styles.PARASTYLES.update_p()
    meredith.mipsy.recalculate_all()

def f_set_attribute(value, A):
    styles.PARASTYLES.active.layerable.active.F.attributes[A] = value
    styles.PARASTYLES.update_f()
    meredith.mipsy.recalculate_all()

def link_fontstyle(fontstyle):
    styles.PARASTYLES.active.layerable.active.F = fontstyle

def link_pegs(pegs):
    styles.PARASTYLES.active.layerable.active.F.attributes['pegs'] = pegs

def g_set_active_x(x):
    G = styles.PARASTYLES.active.layerable.active.F.attributes['pegs']
    G.active[0] = x

def g_set_active_y(y):
    G = styles.PARASTYLES.active.layerable.active.F.attributes['pegs']
    G.active[1] = y

