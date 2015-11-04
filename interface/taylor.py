import bisect
from math import pi

import sierra

from state import noticeboard
from state import constants

from fonts import fonttable

from model import meredith
from model.text_t import character

from typing import typing

from interface import kookies
from interface import olivia


# used in rendering with undefined classes
def get_fontsize(p, f):
    try:
        fontsize = fonttable.table.get_font(p, f)['fontsize']
    except KeyError:
        fontsize = fonttable.table.get_font(p, () )['fontsize']
    return fontsize

def paragraph_context_changed(previous=[None]):
    p = meredith.mipsy.glyph_at(0)[2]
    if p != previous[0]:
        previous[0] = p
        return True
    else:
        return False

class Tabs_round(kookies.Tabs):
    def __init__(self, x, y, width, height, default=0, callback=None, signals=None, strings=None, longstrings=None):
        kookies.Tabs.__init__(self, x, y, width, height, default=default, callback=callback, signals=signals, strings=strings)
        
        self._longstrings = longstrings
        self._add_static_text(self._x + self._width//2, self._y_bottom + 20, self._longstrings[default], align=0)
    
    def focus(self, x):
        self._active = self._target(x)
        self._callback(self._signals[self._active])
        
        del self._texts[-1]
        self._add_static_text(self._x + self._width//2, self._y_bottom + 20, self._longstrings[self._active], align=0)
        
    def draw(self, cr, hover=(None, None)):
        cr.set_font_size(self.font['fontsize'])
        cr.set_font_face(self.font['font'])
        
        for i, button in enumerate(self._x_left):

            if i == hover[1] or i == self._active:
                cr.set_source_rgba(1, 0.2, 0.6, 1)

            else:
                cr.set_source_rgb(0,0,0)

            radius = self._height/2
            x, y = button + int(round(self._button_width/2)), (self._y + self._y_bottom)//2
            cr.arc(x, y, radius, 0, 2*pi)
            cr.close_path()
            cr.fill()
                
            if i == self._active:
                cr.set_source_rgb(1,1,1)
            
            else:
                cr.set_source_rgb(1,1,1)
                
                radius = self._height/2 - 1.5
                x, y = button + int(round(self._button_width/2)), (self._y + self._y_bottom)//2
                cr.arc(x, y, radius, 0, 2*pi)
                cr.close_path()
                cr.fill()
                
                if i == hover[1]:
                    cr.set_source_rgba(1, 0.2, 0.6, 1)

                else:
                    cr.set_source_rgb(0,0,0)
            
            cr.show_glyphs(self._texts[i])

        cr.set_source_rgb(1,1,1)
        radius = 10
        width = self._texts[-1][-1][1] - self._texts[-1][0][1] + 20
        y1, y2, x1, x2 = self._y_bottom + 5, self._y_bottom + 25, self._x + (self._width - width)//2, self._x + (self._width + width)//2
        cr.arc(x1 + radius, y1 + radius, radius, 2*(pi/2), 3*(pi/2))
        cr.arc(x2 - radius, y1 + radius, radius, 3*(pi/2), 4*(pi/2))
        cr.arc(x2 - radius, y2 - radius, radius, 0*(pi/2), 1*(pi/2))
        cr.arc(x1 + radius, y2 - radius, radius, 1*(pi/2), 2*(pi/2))
        cr.close_path()

        cr.fill()
                
        cr.set_source_rgb(0,0,0)
        cr.show_glyphs(self._texts[-1])

class Mode_switcher(object):
    def __init__(self, callback):
        self._h = constants.windowwidth
        self._k = constants.windowheight
        self._hover_j = None
        self._hover_memory = None
        self._switcher = Tabs_round((self._h - constants.propertieswidth - 100)/2 + 100 - 40, self._k - 70, 80, 30, callback=callback, signals=['text', 'channels'], strings=['T', 'C'], longstrings=['Edit text', 'Edit channels'])

    def is_over(self, x, y):
        return self._switcher.is_over(x, y)

    def resize(self, h, k):
        # center
        dx = (h - self._h)/2
        self._h = h
        dy = k - self._k
        self._k = k
        self._switcher.translate(dx=dx, dy=dy)

    def render(self, cr):
        self._switcher.draw(cr, hover=(None, self._hover_j))
    
    def press(self, x):
        self._switcher.focus(x)
    
    def hover(self, x):
        self._hover_j = self._switcher.hover(x)
        if self._hover_j != self._hover_memory:
            noticeboard.refresh.push_change()
            self._hover_memory = self._hover_j
    
    def clear_hover(self):
        self._hover_j = None
        self._hover_memory = None
        noticeboard.refresh.push_change()


def PDF():
    import cairo
    surface = cairo.PDFSurface("PDF.pdf", 765, 990)
    cr = cairo.Context(surface)
    becky._draw_text(cr, refresh=True)
    cr.show_page()
    
    # put text back where it was before
    meredith.mipsy.rerender()
        
class Document_toolbar(object):
    def __init__(self):
        self.refresh_class()
    
    def refresh_class(self):
        
        self._items = []
        self._active_box_i = None
        self._hover_box_ij = (None, None)
        self._hover_memory = (None, None)
        
        y = 120
        self._items.append(kookies.Button(5, y, 90, 30, callback=sierra.save, string='Save'))
        y += 30
        self._items.append(kookies.Button(5, y, 90, 30, callback=PDF, string='PDF'))
        y += 30
        self._items.append(kookies.Button(5, y, 90, 30, callback=meredith.mipsy.add_channel, string='Add portal'))
        y += 30
        self._items.append(kookies.Button(5, y, 90, 30, callback=meredith.mipsy.add_tract, string='Add tract'))



    def render(self, cr):
        for i, entry in enumerate(self._items):
            if i == self._hover_box_ij[0]:
                entry.draw(cr, hover=self._hover_box_ij)
            else:
                entry.draw(cr)
    
    def press(self, x, y):
        b = None

        inspect_i = bisect.bisect([item.y for item in self._items], y)

        try:
            if self._items[inspect_i].is_over(x, y):
                self._items[inspect_i].focus(x)
                b = inspect_i

        except IndexError:
            pass
        # defocus the other box, if applicable
        if b is None or b != self._active_box_i:
            if self._active_box_i is not None:
                if self._items[self._active_box_i].defocus():
                    self.refresh_class()
                    
            self._active_box_i = b

    def release(self, x, y):
        inspect_i = bisect.bisect([item.y for item in self._items], y)

        bl = False
        try:
            if self._items[inspect_i].is_over(x, y) and inspect_i == self._active_box_i:
                bl = True
        except IndexError:
            pass
        
        if self._active_box_i is not None:
            self._items[self._active_box_i].release(action = bl)

        self._active_box_i = None

    def hover(self, x, y):
    
        self._hover_box_ij = (None, None)

        inspect_i = bisect.bisect([item.y for item in self._items], y)
        try:
            if self._items[inspect_i].is_over_hover(x, y):
                self._hover_box_ij = (inspect_i, self._items[inspect_i].hover(x))

        except IndexError:
            # if last index
            pass

        if self._hover_memory != self._hover_box_ij:
            self._hover_memory = self._hover_box_ij
            noticeboard.refresh.push_change()

    def clear_hover(self):
        self._hover_box_ij = (None, None)
        self._hover_memory = (None, None)
        noticeboard.refresh.push_change()

class Document_view(object):
    def __init__(self):
        self._mode = 'text'
        self._region_active, self._region_hover = 'view', 'view'
        self._toolbar = Document_toolbar()
        self._mode_switcher = Mode_switcher(self.change_mode)
        
        self._stake = None
        
        self._scroll_notches = [0.1, 0.13, 0.15, 0.2, 0.22, 0.3, 0.4, 0.5, 0.6, 0.8, 0.89, 1, 1.25, 1.5, 1.75, 1.989, 2, 2.5, 3, 4, 5, 6, 7, 8, 9, 10, 12, 15, 20, 30, 40]
        self._scroll_notch_i = 11
        
        # window widths (CURRENTLY UNUSED)
        self._hw = constants.windowwidth
        self._kw = constants.windowheight
        
        # transform parameters
        self._Hc = (self._hw - constants.propertieswidth - 100) / 2 + 100
        self._Kc = (self._kw) / 2
        
        self._H = 200
        self._K = 100

        self._A = self._scroll_notches[self._scroll_notch_i]
    
    # TRANSFORMATION FUNCTIONS
    def _Tx(self, x):
        return self._A*(x + self._H - self._Hc) + self._Hc

    def _Ty(self, y):
        return self._A*(y + self._K - self._Kc) + self._Kc
    
    def _T_1(self, x, y):
        x = (x - self._Hc) / self._A - self._H + self._Hc
        y = (y - self._Kc) / self._A - self._K + self._Kc
        return x, y
    
    ##############
    
    def _check_region_press(self, x, y):
        if x < 100:
            region = 'toolbar'
        elif self._mode_switcher.is_over(x, y):
            region = 'switcher'
        else:
            region = 'view'
        
        if self._region_active != region:
#            if self._region_active == 'switcher':
#                pass
            self._region_active = region
    
    def _check_region_hover(self, x, y):
        if x < 100:
            region = 'toolbar'
        elif self._mode_switcher.is_over(x, y):
            region = 'switcher'
        else:
            region = 'view'
        
        if self._region_hover != region:
            if self._region_hover == 'switcher':
                self._mode_switcher.clear_hover()
            if self._region_hover == 'toolbar':
                self._toolbar.clear_hover()
            self._region_hover = region

    def key_input(self, name, char):
        if self._mode == 'text':
            clipboard = typing.type_document(name, char)
            # check if paragraph context changed
            if paragraph_context_changed():
                noticeboard.refresh_properties_stack.push_change()
            
            return clipboard
            
        elif self._mode == 'channels':
            olivia.dibbles.key_input(name)
            
    def press(self, x, y, name):
        self._check_region_press(x, y)
        
        if self._region_active == 'view':
            # TEXT EDITING MODE
            if self._mode == 'text':
                try:
                    t, c = meredith.mipsy.target_channel( * self._T_1(x, y), radius=20)
                    meredith.mipsy.set_t(t)
                    meredith.mipsy.set_cursor_xy( * self._T_1(x, y) , c=c)
                    meredith.mipsy.match_cursors()
                    
                    # used to keep track of ui redraws
                    self._sel_cursor = meredith.mipsy.selection()[1]
                except IndexError:
                    # occurs if an empty channel is selected
                    pass
                # check if paragraph context changed
                if paragraph_context_changed():
                    noticeboard.refresh_properties_stack.push_change()
            
            # CHANNEL EDITING MODE
            elif self._mode == 'channels':
                olivia.dibbles.press( * self._T_1(x, y) , name=name)

        elif self._region_active == 'toolbar':
            self._toolbar.press(x, y)
        elif self._region_active == 'switcher':
            self._mode_switcher.press(x)

    def press_motion(self, x, y):
        if self._region_active == 'view':
            if self._mode == 'text':
                try:
                    meredith.mipsy.set_select_xy( * self._T_1(x, y) )
                    if meredith.mipsy.selection()[1] != self._sel_cursor:
                        self._sel_cursor = meredith.mipsy.selection()[1]
                        noticeboard.refresh.push_change()
                except IndexError:
                    # occurs if an empty channel is selected
                    pass

            elif self._mode == 'channels':
                olivia.dibbles.press_motion( * self._T_1(x, y) )
        elif self._region_active == 'toolbar':
            pass
        elif self._region_active == 'switcher':
            pass
    
    def press_mid(self, x, y):
        self._stake = (x, y, self._H, self._K)
    
    def drag(self, x, y):
        # release
        if x == -1:
            self._stake = None
            self._H = int(round(self._H))
            self._K = int(round(self._K))
            
            meredith.mipsy.rerender()
        # drag
        else:
            self._H = int(round( (x - self._stake[0]) / self._A + self._stake[2]))
            self._K = int(round( (y - self._stake[1]) / self._A + self._stake[3]))
            
            meredith.mipsy.rerender()

    def release(self, x, y):
        self._toolbar.release(x, y)

        if self._region_active == 'view':
            if self._mode == 'channels':
                olivia.dibbles.release()
        elif self._region_active == 'toolbar':
            pass
        elif self._region_active == 'switcher':
            pass

    def scroll(self, x, y, mod):
        if y < 0:
            y = abs(y)
            direction = 0
        else:
            direction = 1
        
        if mod == 'ctrl':
            # zoom
            if direction and self._scroll_notch_i > 0:
                self._scroll_notch_i -= 1
            elif self._scroll_notch_i < len(self._scroll_notches) - 1:
                self._scroll_notch_i += 1
            
            dhc = x - self._Hc
            self._Hc += dhc
            self._H -= int(dhc * (1 - self._A) / self._A)
            
            dkc = y - self._Kc
            self._Kc += dkc
            self._K -= int(dkc * (1 - self._A) / self._A)
            
            self._A = self._scroll_notches[self._scroll_notch_i]
        
        else:
            # scroll
            if direction:
                self._K -= int(100 / self._A)
            else:
                self._K += int(100 / self._A)
        
        meredith.mipsy.rerender()
        noticeboard.refresh.push_change()

    def hover(self, x, y):
        self._check_region_hover(x, y)
        
        if self._region_hover == 'view':
            if self._mode == 'text':
                pass

            elif self._mode == 'channels':
                olivia.dibbles.hover( * self._T_1(x, y) )
        elif self._region_hover == 'toolbar':
            self._toolbar.hover(x, y)
        elif self._region_hover == 'switcher':
            self._mode_switcher.hover(x)

    def resize(self, h, k):
        self._mode_switcher.resize(h, k)
        
        self._hw = h
        self._kw = k

    def change_mode(self, mode):
        self._mode = mode
    
    
    def _draw_text(self, cr, mx=0, my=0, cx=765/2, cy=990/2, A=1, refresh=False):
        # prints text

        for tract in meredith.mipsy.tracts:
            classed_glyphs = tract.extract_glyphs(mx, my, cx, cy, A, refresh)

            for name, glyphs in classed_glyphs.items():
                try:
                    cr.set_source_rgb(0, 0, 0)
                    font = fonttable.table.get_font( * name)
                except KeyError:
                    cr.set_source_rgb(1, 0.15, 0.2)
                    try:
                        font = fonttable.table.get_font(name[0], ())
                    except AttributeError:
                        font = fonttable.table.get_font('_interface', ())
                
                cr.set_font_size(font['fontsize'] * A)
                cr.set_font_face(font['font'])
                    
                cr.show_glyphs(glyphs)
                
            del classed_glyphs

    def _draw_annotations(self, cr):
        specials = (i for i, entity in enumerate(meredith.mipsy.text()) if type(entity) is list or entity == '<br>')

        for i in specials:
            if character(meredith.mipsy.text()[i]) == '<p>':
                x, y, p, f = meredith.mipsy.tracts[meredith.mipsy.t].text_index_location(i)
                # this works because paragraph always comes first
                if i == meredith.mipsy.glyph_at(0)[2][1]:
                    cr.set_source_rgba(1, 0.2, 0.6, 0.7)
                else:
                    cr.set_source_rgba(0, 0, 0, 0.4)
                x = round(self._Tx(x))
                y = round(self._Ty(y))
                fontsize = get_fontsize(p[0], f) * self._A
                
                cr.move_to(x, y)
                cr.rel_line_to(0, round(-fontsize))
                cr.rel_line_to(-3, 0)
                # sharp edge do not round
                cr.rel_line_to(-(fontsize/5), round(fontsize)/2)
                cr.line_to(x - 3, y)
                cr.close_path()
                cr.fill()
            elif character(meredith.mipsy.text()[i]) == '<br>':
                x, y, p, f = meredith.mipsy.tracts[meredith.mipsy.t].text_index_location(i + 1)
                fontsize = get_fontsize(p[0], f) * self._A
                x = round(self._Tx(x))
                y = round(self._Ty(y))
                cr.rectangle(x - 6, y - round(fontsize), 3, round(fontsize))
                cr.rectangle(x - 10, y - 3, 4, 3)
                cr.fill()
            
            elif character(meredith.mipsy.text()[i]) == '<f>':
                x, y, p, f = meredith.mipsy.tracts[meredith.mipsy.t].text_index_location(i)
                fontsize = get_fontsize(p[0], f) * self._A
                x = round(self._Tx(x))
                y = round(self._Ty(y))
                
                cr.move_to(x, y - fontsize)
                cr.rel_line_to(0, 6)
                cr.rel_line_to(-1, 0)
                cr.rel_line_to(-3, -6)
                cr.close_path()
                cr.fill()

            elif character(meredith.mipsy.text()[i]) == '</f>':
                x, y, p, f = meredith.mipsy.tracts[meredith.mipsy.t].text_index_location(i)
                fontsize = get_fontsize(p[0], f) * self._A
                x = round(self._Tx(x))
                y = round(self._Ty(y))
                
                cr.move_to(x, y - fontsize)
                cr.rel_line_to(0, 6)
                cr.rel_line_to(1, 0)
                cr.rel_line_to(3, -6)
                cr.close_path()
                cr.fill()

    def _draw_cursors(self, cr):
        # print highlights

        cr.set_source_rgba(0, 0, 0, 0.1)

        posts = sorted(list(meredith.mipsy.selection()))

        firstline = meredith.mipsy.tracts[meredith.mipsy.t].index_to_line(posts[0])
        lastline = meredith.mipsy.tracts[meredith.mipsy.t].index_to_line(posts[1])

        start = meredith.mipsy.tracts[meredith.mipsy.t].text_index_location(posts[0])[0]
        
        linenumber = firstline
        while True:
            # get line dimensions
            anchor, stop, leading, y = meredith.mipsy.tracts[meredith.mipsy.t].line_data(linenumber)
            if linenumber != firstline:
                start = anchor

            if linenumber == lastline:
                stop = meredith.mipsy.tracts[meredith.mipsy.t].text_index_location(posts[1])[0]
            
            cr.rectangle(round(self._Tx(start)), 
                    round(self._Ty(y - leading)), 
                    (stop - start) * self._A, 
                    leading * self._A)
            linenumber += 1

            if linenumber > lastline:
                break
        cr.fill() 

        # print cursors
        cr.set_source_rgb(1, 0.2, 0.6)
        cx, cy, p, f = meredith.mipsy.tracts[meredith.mipsy.t].text_index_location(meredith.mipsy.active_cursor())
        leading = fonttable.p_table.get_paragraph(p[0])['leading']

        ux = round(self._Tx(cx))
        uy = round(self._Ty(cy - leading))
        uh = round(leading * self._A)
        
        cr.rectangle(ux - 1, 
                    uy, 
                    2, 
                    uh)
        # special cursor if adjacent to font tag
        if character(meredith.mipsy.at(0)) in ['<f>', '</f>']:
            cr.rectangle(ux - 3, 
                    uy, 
                    4, 
                    2)
            cr.rectangle(ux - 3, 
                    uy + uh, 
                    4, 
                    2)
        if character(meredith.mipsy.at(-1)) in ['<f>', '</f>']:
            cr.rectangle(ux - 1, 
                    uy, 
                    4, 
                    2)
            cr.rectangle(ux - 1, 
                    uy + uh, 
                    4, 
                    2)
        cr.fill()


        cx, cy, p, f = meredith.mipsy.tracts[meredith.mipsy.t].text_index_location(meredith.mipsy.active_select())
        leading = fonttable.p_table.get_paragraph(p[0])['leading']
        
        ux = round(self._Tx(cx))
        uy = round(self._Ty(cy - leading))
        uh = round(leading * self._A)
        
        cr.rectangle(ux - 1, 
                    uy, 
                    2, 
                    uh)
        # special cursor if adjacent to font tag
        if character(meredith.mipsy.at_select(0)) in ['<f>', '</f>']:
            cr.rectangle(ux - 3, 
                    uy, 
                    4, 
                    2)
            cr.rectangle(ux - 3, 
                    uy + uh, 
                    4, 
                    2)
        if character(meredith.mipsy.at_select(-1)) in ['<f>', '</f>']:
            cr.rectangle(ux - 1, 
                    uy, 
                    4, 
                    2)
            cr.rectangle(ux - 1, 
                    uy + uh, 
                    4, 
                    2)
        cr.fill()
        

    def render(self, cr, h, k):
        #draw page border
        cr.set_source_rgba(0, 0, 0, 0.2)
        px = self._Tx(0)
        py = self._Ty(0)
        cr.rectangle(px, py, 765*self._A, 1)
        cr.rectangle(px, py, 1, 990*self._A)
        cr.rectangle(px + 765*self._A, py, 1, 990*self._A)
        cr.rectangle(px, py + 990*self._A, 765*self._A, 1)
        cr.fill()
        
        cr.rectangle(100, 0, 
                h - 100 - constants.propertieswidth, 
                k)
        cr.clip()
        self._draw_text(cr, self._H, self._K, self._Hc, self._Kc, self._A, False)
        cr.reset_clip()
        self._draw_annotations(cr)
        
        if self._mode == 'text':
            self._draw_cursors(cr)
            olivia.dibbles.render(cr, self._Tx, self._Ty)
        else:
            olivia.dibbles.render(cr, self._Tx, self._Ty, show_rails=True)
        
        self._mode_switcher.render(cr)
        
        # DRAW TOOLBAR BACKGROUND
        cr.rectangle(0, 0, 100, k)
        cr.set_source_rgb(1, 1, 1)
        cr.fill()
        self._toolbar.render(cr)
        
        cr.rectangle(100, 0, 2, k)
        cr.set_source_rgb(0.9, 0.9, 0.9)
        cr.fill()
        
        # draw stats
        cr.set_source_rgba(0, 0, 0, 0.8)
        font = fonttable.table.get_font('_interface', ('strong',))
        
        cr.set_font_size(font['fontsize'])
        cr.set_font_face(font['font'])
        
        cr.move_to(130, k - 20)
        cr.show_text('{0:g}'.format(self._A*100) + '%')
        
becky = Document_view()

