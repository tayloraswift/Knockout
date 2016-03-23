from IO import un
from model import meredith
from style import styles
from state import contexts
from elements.node import Node
    
def redo():
    if un.history.forward():
        styles.PARASTYLES.update_p()
        
        Node.MSL.turnover()
        
        meredith.mipsy.recalculate_all()
        contexts.Text.update_force()

def undo():
    if un.history.back():
        styles.PARASTYLES.update_p()

        Node.MSL.turnover()
        
        meredith.mipsy.recalculate_all()
        contexts.Text.update_force()
