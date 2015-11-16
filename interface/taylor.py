import bisect
from math import pi

from copy import deepcopy

import os
import cairo

import sierra

from state import noticeboard
from state import constants

from fonts import fonttable

from model import meredith
from model import wonder
from model import un, do

character = wonder.character

from typing import typing

from interface import kookies
from interface import olivia
from interface import menu, ui


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
    def __init__(self, x, y, width, height, default=0, callback=None, signals=(), longstrings=None):
        kookies.Tabs.__init__(self, x, y, width, height, default=default, callback=callback, signals=signals)
        
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
        self._hover_j = None
        self._hover_memory = None
        self._switcher = Tabs_round( -40, -70, 80, 30, callback=callback, signals=[('text', 'T'), ('channels', 'C')], longstrings=['Edit text', 'Edit channels'])

    def is_over(self, x, y):
        return self._switcher.is_over(x - self._dx, y - self._dy)

    def resize(self, h, k):
        # center
        self._dx = (constants.UI[1] - 100)/2 + 100 
        self._dy = k

    def render(self, cr, h, k):
        cr.save()
        cr.translate( self._dx , k)
        
        self._switcher.draw(cr, hover=(None, self._hover_j))
        
        cr.restore()
    
    def press(self, x):
        self._switcher.focus(x - self._dx)
    
    def hover(self, x):
        self._hover_j = self._switcher.hover(x - self._dx)
        if self._hover_j != self._hover_memory:
            noticeboard.refresh.push_change()
            self._hover_memory = self._hover_j
    
    def clear_hover(self):
        self._hover_j = None
        self._hover_memory = None
        noticeboard.refresh.push_change()


def PDF():
    name = os.path.splitext(constants.filename)[0]
    surface = cairo.PDFSurface(name + '.pdf', 765, 990)
    cr = cairo.Context(surface)
    
    classes = becky.page_classes()
    max_page = max(classes.keys())
    for p in range(max_page + 1):
        try:
            becky.print_page(cr, p, classes)
        except KeyError:
            pass
        cr.show_page()
    
    # put text back where it was before
    meredith.mipsy.rerender()

def place_tags(tag):
    un.history.undo_save(3)
    if meredith.mipsy.tracts[meredith.mipsy.t].bridge(tag, sign=True):
        meredith.mipsy.stats(spell=True)
    else:
        un.history.pop(3)

def punch_tags(tag):
    un.history.undo_save(3)
    if meredith.mipsy.tracts[meredith.mipsy.t].bridge(tag, sign=False):
        meredith.mipsy.stats(spell=True)
    else:
        un.history.pop(3)

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
        
        y += 40
        self._items.append(kookies.Button(5, y, 90, 30, callback=do.undo, string='Undo'))
        y += 30
        self._items.append(kookies.Button(5, y, 90, 30, callback=do.redo, string='Redo'))
        
        y += 40
        self._items.append(kookies.Button(5, y, 90, 30, callback=meredith.mipsy.add_channel, string='Add portal'))
        y += 30
        self._items.append(kookies.Button(5, y, 90, 30, callback=meredith.mipsy.add_tract, string='Add tract'))

        y += 50
        self._items.append(kookies.Button(5, y, 90, 30, callback=place_tags, string='Emphasis', params=('emphasis',) ))
        y += 30
        self._items.append(kookies.Button(5, y, 90, 30, callback=punch_tags, string='x Emphasis', params=('emphasis',) ))

        y += 40
        self._items.append(kookies.Button(5, y, 90, 30, callback=place_tags, string='Strong', params=('strong',) ))
        y += 30
        self._items.append(kookies.Button(5, y, 90, 30, callback=punch_tags, string='x Strong', params=('strong',) ))

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


def _replace_misspelled(word):
    if word[0] == '“':
        wonder.struck.add(word[1:-1])
    else:
        typing.type_document('Paste', list(word))
    meredith.mipsy.stats(spell=True)

class Document_view(ui.Cell):
    def __init__(self):
        self._mode = 'text'
        self._region_active, self._region_hover = 'view', 'view'
        self._toolbar = Document_toolbar()
        self._mode_switcher = Mode_switcher(self.change_mode)
        
        self._stake = None
        
        self._scroll_notches = [0.1, 0.13, 0.15, 0.2, 0.22, 0.3, 0.4, 0.5, 0.6, 0.8, 0.89, 1, 1.25, 1.5, 1.75, 1.989, 2, 2.5, 3, 4, 5, 6, 7, 8, 9, 10, 12, 15, 20, 30, 40]
        self._scroll_notch_i = 11
        
        # transform parameters
        self._Hc = (constants.UI[1] - 100) / 2 + 100
        self._Kc = (constants.window.get_k()) / 2
        
        self._H = 200
        self._K = 100

        self._A = self._scroll_notches[self._scroll_notch_i]
        
        self.idle()
    
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
            # what page
            xo, yo = self._T_1(x, y)
            page = int(yo//1100)
            yo -= page*1100

            # TEXT EDITING MODE
            if self._mode == 'text':
                try:
                    un.history.undo_save(0)
                    
                    t, c = meredith.mipsy.target_channel( xo, yo, page, radius=20)
                    if c is not None:
                        meredith.mipsy.set_t(t)
                        meredith.mipsy.set_cursor_xy(xo, yo, c)
                        meredith.mipsy.match_cursors()
                        
                        # used to keep track of ui redraws
                        self._sel_cursor = meredith.mipsy.selection()[1]
                except IndexError:
                    # occurs if an empty channel is selected
                    pass
                # check if paragraph context changed
                if paragraph_context_changed():
                    noticeboard.refresh_properties_stack.push_change()
                
                # count words
                meredith.mipsy.stats()
            
            # CHANNEL EDITING MODE
            elif self._mode == 'channels':
                olivia.dibbles.press( xo, yo, page, name=name)

        elif self._region_active == 'toolbar':
            self._toolbar.press(x, y)
        elif self._region_active == 'switcher':
            self._mode_switcher.press(x)

    def dpress(self):
        if self._region_active == 'view':
            # TEXT EDITING MODE
            if self._mode == 'text':
                meredith.mipsy.select_word()
    
    def press_right(self, x, y):
        if self._region_active == 'view':
            # what page
            xo, yo = self._T_1(x, y)
            page = int(yo//1100)
            yo -= page*1100
            
            # TEXT EDITING MODE
            if self._mode == 'text':
                try:
                    t, c = meredith.mipsy.target_channel(xo, yo, page, radius=20)
                    i = meredith.mipsy.lookup_xy(t, c, xo, yo )
                    
                    ms = meredith.mipsy.tracts[meredith.mipsy.t].misspellings
                    pair_i = bisect.bisect([pair[0] for pair in ms], i) - 1

                    if ms[pair_i][0] <= i <= ms[pair_i][1]:

                        if i == ms[pair_i][1]:
                            i -= 1
                        meredith.mipsy.set_t(t)
                        meredith.mipsy.set_cursor(t, i)
                        meredith.mipsy.match_cursors()
                        
                        # used to keep track of ui redraws
                        self._sel_cursor = meredith.mipsy.selection()[1]
                        meredith.mipsy.select_word()
                        menu.menu.create(x, y, 200, ['“' + ms[pair_i][2] + '”'] + wonder.struck.suggest(ms[pair_i][2]), _replace_misspelled, () )

                except IndexError:
                    # occurs if an empty channel is selected
                    pass
                # check if paragraph context changed
                if paragraph_context_changed():
                    noticeboard.refresh_properties_stack.push_change()

        
    def press_motion(self, x, y):
        if self._region_active == 'view':
            # what page
            xo, yo = self._T_1(x, y)
            page = int(yo//1100)
            yo -= page*1100
            
            if self._mode == 'text':
                c = meredith.mipsy.tracts[meredith.mipsy.t].channels.target_channel(xo, yo, page, 20)
                try:
                    meredith.mipsy.set_select_xy( xo, yo, c=c )
                    if meredith.mipsy.selection()[1] != self._sel_cursor:
                        self._sel_cursor = meredith.mipsy.selection()[1]
                        noticeboard.refresh.push_change()
                except IndexError:
                    # occurs if an empty channel is selected
                    pass

            elif self._mode == 'channels':
                olivia.dibbles.press_motion(xo, yo)
        elif self._region_active == 'toolbar':
            pass
        elif self._region_active == 'switcher':
            pass
    
    def press_mid(self, x, y):
        self._stake = (x, y, self._H, self._K)
    
    def drag(self, x, y, reference=[0, 0]):
        # release
        if x == -1:
            self._stake = None
            self._H = int(round(self._H))
            self._K = int(round(self._K))
            
            meredith.mipsy.rerender()
            noticeboard.refresh.push_change()
        # drag
        else:
            
            self._H = int(round( (x - self._stake[0]) / self._A + self._stake[2]))
            self._K = int(round( (y - self._stake[1]) / self._A + self._stake[3]))
            
            # heaven knows why this expression works, but hey it works
            dx = (self._H - self._stake[2]) * self._A
            dy = (self._K - self._stake[3]) * self._A
            
            if [dx, dy] != reference:
                reference[:] = [dx, dy]
                noticeboard.refresh.push_change()

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
            if direction:
                if self._scroll_notch_i > 0:
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
                self._K -= int(50 / self._A)
            else:
                self._K += int(50 / self._A)
        
        meredith.mipsy.rerender()
        noticeboard.refresh.push_change()

    def hover(self, x, y):
        self._check_region_hover(x, y)
        
        if self._region_hover == 'view':
            if self._mode == 'text':
                pass

            elif self._mode == 'channels':
                # what page
                xo, yo = self._T_1(x, y)
                page = int(yo//1100)
                yo -= page*1100
                
                olivia.dibbles.hover( xo, yo, page )
                
        elif self._region_hover == 'toolbar':
            self._toolbar.hover(x, y)
        elif self._region_hover == 'switcher':
            self._mode_switcher.hover(x)

    def idle(self):
        meredith.mipsy.stats(spell=True)

    def resize(self, h, k):
        self._mode_switcher.resize(h, k)

    def change_mode(self, mode):
        self._mode = mode
        noticeboard.refresh_properties_stack.push_change()
        noticeboard.refresh_properties_type.push_change(mode)
    
    def _print_sorted(self, cr, classed_glyphs):
        for name, glyphs in classed_glyphs.items():
            try:
                cr.set_source_rgb(0, 0, 0)
                font = fonttable.table.get_font( * name)
            except TypeError:
                # happens on '_annot'
                continue
            except KeyError:
                cr.set_source_rgb(1, 0.15, 0.2)
                try:
                    font = fonttable.table.get_font(name[0], ())
                except AttributeError:
                    font = fonttable.table.get_font('_interface', ())
            
            cr.set_font_size(font['fontsize'])
            cr.set_font_face(font['font'])
                
            cr.show_glyphs(glyphs)
    
    def page_classes(self):
        classed_pages = {}

        jumbled_pages = [tract.extract_glyphs() for tract in meredith.mipsy.tracts]

        for dictionary in jumbled_pages:
            for page, sorted_glyphs in dictionary.items():
                if page in classed_pages:
                    for style, glyphs in sorted_glyphs.items():
                        classed_pages[page].setdefault(style, []).extend(glyphs)
                else:
                    classed_pages[page] = deepcopy(sorted_glyphs)
        
        return classed_pages
    
    def print_page(self, cr, p, classed_pages):
        self._print_sorted(cr, classed_pages[p])
            
    def _draw_by_page(self, cr, mx_cx=-765/2, my_cy=-990/2, cx=765/2, cy=990/2, A=1, refresh=False):
        max_page = 0

        for t, tract in enumerate(meredith.mipsy.tracts):
            # highlights
            if t == meredith.mipsy.t and self._mode == 'text':
                i, j = sorted(list(meredith.mipsy.selection()))

                l1 = meredith.mipsy.tracts[meredith.mipsy.t].index_to_line(i)
                l2 = meredith.mipsy.tracts[meredith.mipsy.t].index_to_line(j)

                start = meredith.mipsy.tracts[meredith.mipsy.t].text_index_location(i)[0]
                stop = meredith.mipsy.tracts[meredith.mipsy.t].text_index_location(j)[0]
            
                # spelling
                annoying_red_lines = []
                for pair in tract.misspellings:

                    u, v = pair[:2]

                    u_l = meredith.mipsy.tracts[meredith.mipsy.t].index_to_line(u)
                    v_l = meredith.mipsy.tracts[meredith.mipsy.t].index_to_line(v)

                    u_x = meredith.mipsy.tracts[meredith.mipsy.t].text_index_location(u)[0]
                    v_x = meredith.mipsy.tracts[meredith.mipsy.t].text_index_location(v)[0]
                    
                    annoying_red_lines.append((u_x, v_x, u_l, v_l, u, v))
        
            for page, sorted_glyphs in tract.extract_glyphs(refresh).items():
                if page > max_page:
                    max_page = page

                # Transform goes
                # x' = A (x + m - c) + c
                # x' = Ax + (Am - Ac + c)
                
                # Scale first (on bottom) is significantly faster in cairo
                cr.save()
                cr.translate(A*mx_cx + cx, A*(my_cy + page * 1100) + cy)
                cr.scale(A, A)

                self._print_sorted(cr, sorted_glyphs)
                
                # only annotate active tract
                if t == meredith.mipsy.t and self._mode == 'text':
                    print(sorted_glyphs['_intervals'])
                    self._draw_annotations(cr, sorted_glyphs['_annot'])
                    
                    self._highlight(cr, sorted_glyphs['_intervals'], self._selection_highlight, 0.75, start, stop, l1, l2, i, j)
                
                    for red_line in annoying_red_lines:
                        self._highlight(cr, sorted_glyphs['_intervals'], self._spelling_highlight, 1, * red_line)
                
                cr.restore()

        
        for pp in range(max_page + 1):
            #draw page border
            cr.set_source_rgba(0, 0, 0, 0.2)
            px = int(round(self._Tx(0)))
            py = int(round(self._Ty(pp * 1100)))
            cr.rectangle(px, py, int(round(765*self._A)), 1)
            cr.rectangle(px, py, 1, int(round(990*self._A)))
            cr.rectangle(px + int(round(765*self._A)), py, 1, int(round(990*self._A)))
            cr.rectangle(px, py + int(round(990*self._A)), int(round(765*self._A)), 1)
            cr.fill()

    def _GRID(self, cr, x, y):
        x, y = cr.user_to_device(x, y)
        return cr.device_to_user(int(x), int(y))

    def _draw_annotations(self, cr, annot):

        # constant numbers
        _1_ = 1/self._A
        _3_ = 3/self._A
        _4_ = 4/self._A
        _6_ = 6/self._A
        _10_ = 10/self._A

        for a in annot:
        
            x, y, p, f = a[1:5]
            
            x, y = self._GRID(cr, x, y)
            
            fontsize = round(get_fontsize(p[0], f) * self._A) / self._A

            if p[1] == meredith.mipsy.glyph_at(0)[2][1]:
                cr.set_source_rgba(1, 0.2, 0.6, 0.7)
            else:
                cr.set_source_rgba(0, 0, 0, 0.4)
            
            #         '<p>'
            if a[0] == -3:
                
                cr.move_to(x, y)
                cr.rel_line_to(0, -fontsize)
                cr.rel_line_to(-_3_, 0)
                # sharp edge do not round
                cr.rel_line_to(-fontsize/5, fontsize/2)
                cr.line_to(x - _3_, y)
                cr.close_path()
                cr.fill()

            #        '<br>' +1
            if a[0] == -2:
                
                fontsize = round(get_fontsize(p[0], f) * self._A) / self._A
                
                cr.rectangle(x - _6_, y - round(fontsize), _3_, round(fontsize))
                cr.rectangle(x - _10_, y - _3_, _4_, _3_)
                cr.fill()

            #           '<f>'
            elif a[0] == -5:
                cr.move_to(x, y - fontsize)
                cr.rel_line_to(0, _6_)
                cr.rel_line_to(-_1_, 0)
                cr.rel_line_to(-_3_, -_6_)
                cr.close_path()
                cr.fill()
            
            #          '</f>'
            elif a[0] == -6:
                cr.move_to(x, y - fontsize)
                cr.rel_line_to(0, _6_)
                cr.rel_line_to(_1_, 0)
                cr.rel_line_to(_3_, -_6_)
                cr.close_path()
                cr.fill()

    def _spelling_highlight(self, cr, x1, x2, y, height, I=None, J=None):
        # constant numbers
        _1_ = 1/self._A
        
        cr.set_source_rgba(1, 0.15, 0.2, 0.8)
        
        cr.rectangle(x1, y + int(2 * self._A) / self._A, x2 - x1, _1_)
        cr.fill()
        
    def _selection_highlight(self, cr, x1, x2, y, height, I=None, J=None):
        cr.set_source_rgba(0, 0, 0, 0.1)
        
        cr.rectangle(x1, y - height, x2 - x1, height)
        cr.fill()
        # print cursor
        if I is not None:
            self._draw_cursor(cr, I)
        if J is not None:
            self._draw_cursor(cr, J)


    def _highlight(self, cr, intervals, highlighting_engine, alpha, start_x, stop_x, l1, l2, I, J):
        if alpha != 1:
            cr.push_group()
        
        # find overlaps
        operant = []
        for interval in intervals:
            if l1 < interval[1] and l2 >= interval[0]:
                rng = sorted((max(l1, interval[0]), min(l2, interval[1] - 1)))
                operant += range(rng[0], rng[1] + 1)
        
        cr.set_source_rgba(0, 0, 0, 0.1)

        for l in operant:
            # get line dimensions
            start, stop, leading, y = meredith.mipsy.tracts[meredith.mipsy.t].line_data(l)
            start = self._GRID(cr, start, 0)[0]
            stop, y = self._GRID(cr, stop, y)
            leading = int(leading * self._A) / self._A
            
            if l == l1 == l2:
                highlighting_engine(cr, start_x, stop_x, y, leading, I, J)

            elif l == l1:
                highlighting_engine(cr, start_x, stop, y, leading, I, None)

            elif l == l2:
                highlighting_engine(cr, start, stop_x, y, leading, None, J)

            else:
                highlighting_engine(cr, start, stop, y, leading, None, None)
        
        if alpha != 1:
            cr.pop_group_to_source()
            cr.paint_with_alpha(alpha)
    
    def _draw_cursor(self, cr, i):
        # constant numbers
        _1_ = 1/self._A
        _2_ = 2/self._A
        _3_ = 3/self._A
        _4_ = 4/self._A
        
        cr.set_source_rgb(1, 0, 0.5)
        cx, cy, p, f = meredith.mipsy.tracts[meredith.mipsy.t].text_index_location(i)
        
        cx, cy = self._GRID(cr, cx, cy)
        leading = int(fonttable.p_table.get_paragraph(p[0])['leading'] * self._A) / self._A

        ux = cx
        uy = cy - leading
        uh = leading
        
        cr.rectangle(ux - _1_, 
                    uy, 
                    _2_, 
                    uh)
        # special cursor if adjacent to font tag
        if character(meredith.mipsy.at_absolute(i)) in ('<f>', '</f>'):
            cr.rectangle(ux - _3_, 
                    uy, 
                    _4_, 
                    _2_)
            cr.rectangle(ux - _3_, 
                    uy + uh, 
                    _4_, 
                    _2_)
        if character(meredith.mipsy.at_absolute(i - 1)) in ('<f>', '</f>'):
            cr.rectangle(ux - _1_, 
                    uy, 
                    _4_, 
                    _2_)
            cr.rectangle(ux - _1_, 
                    uy + uh, 
                    _4_, 
                    _2_)
        cr.fill()


    def render(self, cr, h, k):
        cr.rectangle(0, 0, 
                constants.UI[1], 
                k)
        cr.clip()
        
        # text
        self._draw_by_page(cr, self._H - self._Hc, self._K - self._Kc, self._Hc, self._Kc, self._A, False)
        
        # channels
        if self._mode == 'text':
            olivia.dibbles.render(cr, self._Tx, self._Ty, pageheight=1100)
        else:
            olivia.dibbles.render(cr, self._Tx, self._Ty, pageheight=1100, show_rails=True)
        
        self._mode_switcher.render(cr, h, k)
        
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

        if noticeboard.composition_sequence:
            cr.move_to(130, 40)
            cr.show_text(' '.join(noticeboard.composition_sequence))
        
        cr.move_to(130, k - 20)
        cr.show_text('{0:g}'.format(self._A*100) + '%')
        
        cr.move_to(constants.UI[1] - 100, k - 20)
        cr.show_text(str(meredith.mipsy.tracts[meredith.mipsy.t].word_count) + ' words')
        
        cr.reset_clip()

becky = Document_view()

