from model import olivia
from model import george
from model import penclick
from model.wonder import character

from state import noticeboard

class Meredith(object):
    def __init__(self, kitty, grid, contexts):
        self.tracts = [olivia.Text(k['text'], george.Washington([george.Swimming_pool( * c ) for c in k['outline']]), * k['cursors'] ) for k in kitty if k['outline']]

        self.page_context = contexts['p']
        self.hover_page_context = 0
        
        self._C = contexts['c']
        
        self.page_grid = grid

        self.recalculate_all()
    
    def C(self):
        return self._C
    
    def recalculate_all(self):
        for tract in self.tracts:
            tract.deep_recalculate()

    def positive_page_context(self, x, y):
        if not self.channel_select(x, y):
            old_pg = self.page_context
            self.page_context = penclick.page.XY_to_page(x, y)
            xp, yp = self.XY(x, y)
            if not self.channel_select(xp, yp):
                self.page_context = old_pg
                x, y = self.XY(x, y)
            else:
                x, y = xp, yp
        return x, y
                
    def set_page_context(self, x, y):
        self.page_context = penclick.page.XY_to_page(x, y)
        return self.XY(x, y)
            
    def set_hover_page_context(self, x, y):
        self.hover_page_context = penclick.page.XY_to_page(x, y)
        return self._XY_hover(x, y)
    
    def XY(self, x, y):
        return penclick.page.normalize_XY(x, y, self.page_context)
    def _XY_hover(self, x, y):
        return penclick.page.normalize_XY(x, y, self.hover_page_context)

    def channel_select(self, x, y, search_all=False):
        # try local
        c_local = self.tracts[0].channels.target_channel(x, y, self.page_context, 20)
        
        if c_local is not None and c_local != self._C:
            self._C = c_local
            return True
        
        elif search_all:
            for t, tract in enumerate(self.tracts):
                c = tract.channels.target_channel(x, y, self.page_context, 20)
                if c is not None:
                    self.tracts.insert(0, self.tracts.pop(t))
                    self._C = c
                    return True
        
        return False

    def channel_point_select(self, x, y):
        c, r, i = self.tracts[0].channels.target_point(x, y, self.page_context, 20)
        portal = None
        
        if c is not None:
            if r is None:
                portal = self.tracts[0].channels.channels[c].target_portal(x, y, radius=5)
            elif i is None:
                # insert point if one was not found
                i = self.tracts[0].channels.channels[c].insert_point(r, y)
            
            if c != self._C:
                self._C = c
                noticeboard.refresh_properties_stack.push_change()
        
        else:
            if self.channel_select(x, y, search_all=True):
                noticeboard.refresh_properties_stack.push_change()
                c = self._C
            else:
                c = None
        
        return c, r, i, portal

    def set_cursor(self, i):
        self.tracts[0].cursor.set_cursor(
                i,
                self.tracts[0].text
                )

    def lookup_xy(self, x, y):
        return self.tracts[0].target_glyph(x, y, c=self._C)
            
    def set_cursor_xy(self, x, y):
        self.tracts[0].cursor.set_cursor(
                self.lookup_xy(x, y),
                self.tracts[0].text
                )
        
    def set_select_xy(self, x, y):
        self.tracts[0].select.set_cursor(
                self.lookup_xy(x, y),
                self.tracts[0].text
                )


    def at_absolute(self, i):
        return character(self.tracts[0].text[i])
    
    def paragraph_at(self):
        return self.tracts[0].pp_at(self.tracts[0].cursor.cursor)
            
    def match_cursors(self):
        self.tracts[0].select.cursor = self.tracts[0].cursor.cursor
    
    def hop(self, dl):
        try:
            self.tracts[0].cursor.set_cursor(
                    self.tracts[0].target_glyph(
                            self.tracts[0].text_index_location(self.tracts[0].cursor.cursor)[0], 
                            0, 
                            self.tracts[0].index_to_line(self.tracts[0].cursor.cursor) + dl
                            ), 
                    self.tracts[0].text)
        except IndexError:
            pass
        
    def add_channel(self):
        self.tracts[0].channels.add_channel()
        self.recalculate_all()
    
    def add_tract(self):
        self.tracts.append( olivia.Text('<p>{new}</p>', george.Washington([self.tracts[-1].channels.generate_channel()]), 1, 1 ) )
        self.t = len(self.tracts) - 1
        self.recalculate_all()
    
    def rename_paragraph_class(self, old, new):
        for tract in self.tracts:
            tract.text[:] = [('<p>', new) if e == ('<p>', old) else e for e in tract.text]
    
    def change_channel_page(self, page, c):
        self.tracts[0].channels.channels[c].set_page(page)
        self.recalculate_all()
            
    def stats(self, spell=False):
        self.tracts[0].stats(spell)

mipsy = None
