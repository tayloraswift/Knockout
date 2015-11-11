from fonts.fonts import GET
from model import un

from copy import deepcopy

def f_set_attribute(attribute, p, f, value):
    un.history.undo_save(3)
    # assumes root p and f
    GET()[p]['fontclasses'][1][f][1][attribute] = value


def p_set_attribute(attribute, p, value):
    un.history.undo_save(3)
    GET()[p][attribute] = value

def add_paragraph_class(name, clone):
    paragraph_classes = GET()
    if name not in paragraph_classes:
        un.history.undo_save(3)
        paragraph_classes[name] = deepcopy(paragraph_classes[clone])

def rename_p(old, new):
    un.history.undo_save(3)
    paragraph_classes = GET()
    for k in paragraph_classes:
        # travel through fontclasses
        if not paragraph_classes[k]['fontclasses'][0]:
            for f in paragraph_classes[k]['fontclasses'][1]:
            
                paragraph_classes[k]['fontclasses'][1][f] = list(paragraph_classes[k]['fontclasses'][1][f])
                
                # inherit flag
                if paragraph_classes[k]['fontclasses'][1][f][0]:
                    
                    paragraph_classes[k]['fontclasses'][1][f][1] = list(paragraph_classes[k]['fontclasses'][1][f][1])
                    
                    if paragraph_classes[k]['fontclasses'][1][f][1] [0] == old:
                        paragraph_classes[k]['fontclasses'][1][f][1] [0] = new
                else:
                    paragraph_classes[k]['fontclasses'][1][f] = list(paragraph_classes[k]['fontclasses'][1][f])
                    
                    for a in paragraph_classes[k]['fontclasses'][1][f][1]:
                        paragraph_classes[k]['fontclasses'][1][f][1][a] = list(paragraph_classes[k]['fontclasses'][1][f][1][a])
                        # inherit flag
                        if paragraph_classes[k]['fontclasses'][1][f][1][a][0]:
                            
                            paragraph_classes[k]['fontclasses'][1][f][1][a][1] = list(paragraph_classes[k]['fontclasses'][1][f][1][a][1])

                            if paragraph_classes[k]['fontclasses'][1][f][1][a][1] [0] == old:
                                paragraph_classes[k]['fontclasses'][1][f][1][a][1] [0] = new

                    
            
        for l in paragraph_classes[k]:
            paragraph_classes[k][l] = list(paragraph_classes[k][l])
            # inherit flag
            if paragraph_classes[k][l][0]:
                if paragraph_classes[k][l][1] == old:
                    paragraph_classes[k][l][1] = new
        
        if k == old:
            paragraph_classes[new] = paragraph_classes[k]
            del paragraph_classes[old]
