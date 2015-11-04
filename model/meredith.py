from model import text_t as comp
from model import channels


class Meredith(object):
    def __init__(self):
        self.tracts = []
        
    def reinit(self, kitty):
        self.tracts = [comp.Text(k['text'], channels.Channels([channels.Channel(c[0], c[1]) for c in k['outline']]) ) for k in kitty if k['outline']]
        self.t = 0
        self.rerender()
            
    def rerender(self):
        for tr in self.tracts:
            tr.deep_recalculate()

    
    def target_channel(self, x, y, radius):
        # try local
        t = self.t
        c = self.tracts[t].channels.target_channel(x, y, radius)
        
        if c is None:
            print('None')
            for t, tract in enumerate(self.tracts):
                c = tract.channels.target_channel(x, y, radius)
                if c is not None:
                    return t, c

        return t, c
    
    def set_t(self, tindex):
        self.t = tindex
    
    def set_cursor_xy(self, x, y, c=None):
        self.tracts[self.t].cursor.set_cursor(
                self.tracts[self.t].target_glyph(x, y, c=c),
                self.tracts[self.t].text
                )
        # count words because why not
        self.tracts[self.t].count_words()
        
    def set_select_xy(self, x, y, c=None):
        self.tracts[self.t].select.set_cursor(
                self.tracts[self.t].target_glyph(x, y, c=c),
                self.tracts[self.t].text
                )
    def select_all(self):
        self.tracts[self.t].expand_cursors()
    
    def text(self):
        return self.tracts[self.t].text
    
    def selection(self):
        return self.tracts[self.t].cursor.cursor, self.tracts[self.t].select.cursor
    
    def at(self, relativeindex=0):
        return self.tracts[self.t].text[self.tracts[self.t].cursor.cursor + relativeindex]
    def at_select(self, relativeindex=0):
        return self.tracts[self.t].text[self.tracts[self.t].select.cursor + relativeindex]
    
    def glyph_at(self, relativeindex=0):
        return self.tracts[self.t].text_index_location(self.tracts[self.t].cursor.cursor + relativeindex)
            
    def cdelete(self, rel1, rel2):
        return self.tracts[self.t].delete(self.tracts[self.t].cursor.cursor + rel1, self.tracts[self.t].cursor.cursor + rel2)
    
    def active_cursor(self):
        return self.tracts[self.t].cursor.cursor
    def active_select(self):
        return self.tracts[self.t].select.cursor
            
    def match_cursors(self):
        self.tracts[self.t].match_cursors()
    
    def hop(self, dl):
        self.tracts[self.t].cursor.set_cursor(self.tracts[self.t].target_glyph(self.tracts[self.t].text_index_location(self.tracts[self.t].cursor.cursor)[0], 0, (self.tracts[self.t].index_to_line(self.tracts[self.t].cursor.cursor) + dl) % self.tracts[self.t].max_l() ), self.tracts[self.t].text)

    def words(self):
        return self.tracts[self.t].word_count()
        
    def add_channel(self):
        self.tracts[self.t].channels.add_channel()
    
    def add_tract(self):
        self.tracts.append( comp.Text('<p>{new}</p>', channels.Channels([self.tracts[-1].channels.generate_channel()]) ) )
        self.t = len(self.tracts) - 1
        self.rerender()
    
    def rename_paragraph_class(self, old, new):
        for tract in self.tracts:
            tract.text[:] = [['<p>', new] if e == ['<p>', old] else e for e in tract.text]

    def change_paragraph_class(self, i, po):
        self.tracts[self.t].text[i][1] = po
            
#    def modify_font(self, p, names):
#        fonts.paragraph_classes[p].fontclasses[names].update_path(path) 

mipsy = Meredith()
