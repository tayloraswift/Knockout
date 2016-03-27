from model import meredith
from style import styles

def p_set_attribute(A, value):
    styles.PARASTYLES.active.assign(A, value)
    styles.PARASTYLES.update_p()
    meredith.mipsy.recalculate_all()

def f_set_attribute(A, value):
    styles.PARASTYLES.active.content.active.F.assign(A, value)
    styles.PARASTYLES.update_f()
    meredith.mipsy.recalculate_all()

def link_fontstyle(fontstyle):
    styles.PARASTYLES.active.content.active.F = fontstyle

