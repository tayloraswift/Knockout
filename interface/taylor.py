import bisect
from math import pi, sqrt

from copy import deepcopy

import os
import cairo

from state import noticeboard
from state import constants
from state.contexts import Text as CText

from fonts import styles

from model import meredith
from model import cursor
from model import wonder
from model.wonder import character
from model import un, do

from typing import typing

from interface import kookies
from interface import caramel
from interface import menu, ui
from interface.base import accent

accent_light = caramel.accent

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
                cr.set_source_rgb( * accent)

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
                    cr.set_source_rgb( * accent)

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
        self._hover_j = self._switcher.hover(x - self._dx, 0)
        if self._hover_j != self._hover_memory:
            noticeboard.redraw_becky.push_change()
            self._hover_memory = self._hover_j
    
    def clear_hover(self):
        self._hover_j = None
        self._hover_memory = None
        noticeboard.redraw_becky.push_change()


def PDF():
    name = os.path.splitext(constants.filename)[0]
    surface = cairo.PDFSurface(name + '.pdf', meredith.page.WIDTH, meredith.page.HEIGHT)
    cr = cairo.Context(surface)
    
    classes = becky.page_classes()
    max_page = max(classes.keys())
    for p in range(max_page + 1):
        becky.print_page(cr, p, classes)
        cr.show_page()

def _place_tags(tag):
    un.history.undo_save(3)
    if not cursor.fcursor.bridge(tag, sign=True):
        un.history.pop()

def _punch_tags(tag):
    un.history.undo_save(3)
    if not cursor.fcursor.bridge(tag, sign=False):
        un.history.pop()

def _add_channel():
    caramel.delight.TRACT.channels.add_channel()
    caramel.delight.TRACT.deep_recalculate()

class Document_toolbar(object):
    def __init__(self, save):
        self._save = save
        self.refresh_class()
    
    def refresh_class(self):
        
        self._items = []
        self._active_box_i = None
        self._hover_box_ij = (None, None)
        self._hover_memory = (None, None)
        
        y = 120
        self._items.append(kookies.Button(5, y, 90, 30, callback=self._save, string='Save'))
        y += 30
        self._items.append(kookies.Button(5, y, 90, 30, callback=PDF, string='PDF'))
        
        y += 40
        self._items.append(kookies.Button(5, y, 90, 30, callback=do.undo, string='Undo'))
        y += 30
        self._items.append(kookies.Button(5, y, 90, 30, callback=do.redo, string='Redo'))
        
        y += 40
        self._items.append(kookies.Button(5, y, 90, 30, callback=_add_channel, string='Add portal'))
        y += 30
        self._items.append(kookies.Button(5, y, 90, 30, callback=meredith.mipsy.add_tract, string='Add tract'))

        y += 50
        self._items.append(kookies.Button(5, y, 90, 30, callback=_place_tags, string='Emphasis', params=(typing.keyboard['Ctrl i'],) ))
        y += 30
        self._items.append(kookies.Button(5, y, 90, 30, callback=_punch_tags, string='x Emphasis', params=(typing.keyboard['Ctrl I'],) ))

        y += 40
        self._items.append(kookies.Button(5, y, 90, 30, callback=_place_tags, string='Strong', params=(typing.keyboard['Ctrl b'],) ))
        y += 30
        self._items.append(kookies.Button(5, y, 90, 30, callback=_punch_tags, string='x Strong', params=(typing.keyboard['Ctrl B'],) ))

        y += 50
        self._items.append(kookies.Checkbox(15, y, 80, callback=meredith.page.toggle_dual, value_acquire=lambda: meredith.page.dual, name='Dual'.upper()))
        
        y += 50
        self._items.append(kookies.Selection_menu(5, y, 90, 30, menu_callback=constants.HINTS.set_hint_style, options_acquire=constants.default_hints, value_acquire=constants.HINTS.get_hint_style, source=0))
        y += 30
        self._items.append(kookies.Selection_menu(5, y, 90, 30, menu_callback=constants.HINTS.set_antialias, options_acquire=constants.default_antialias, value_acquire=constants.HINTS.get_antialias, source=0))
        
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
                self._items[inspect_i].focus(x, y)
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
                self._hover_box_ij = (inspect_i, self._items[inspect_i].hover(x, y))

        except IndexError:
            # if last index
            pass

        if self._hover_memory != self._hover_box_ij:
            self._hover_memory = self._hover_box_ij
            noticeboard.redraw_becky.push_change()

    def clear_hover(self):
        self._hover_box_ij = (None, None)
        self._hover_memory = (None, None)
        noticeboard.redraw_becky.push_change()


def _replace_misspelled(word):
    if word[0] == '“':
        wonder.struck.add(word[1:-1])
    else:
        typing.keyboard.type_document('Paste', list(word))
    cursor.fcursor._ftx.stats(spell=True)

class Document_view(ui.Cell):
    def __init__(self, save, state={'mode': 'text', 'Hc': 0, 'Kc': 0, 'H': 0, 'K': 0, 'Zoom': 11}):
        self._mode = state['mode']
        self._region_active, self._region_hover = 'view', 'view'
        self._toolbar = Document_toolbar(save)
        self._mode_switcher = Mode_switcher(self.change_mode)
        self.keyboard = typing.keyboard
        self.fcursor = cursor.fcursor
        
        self._stake = None
        
        self._scroll_notches = [0.1, 0.13, 0.15, 0.2, 0.22, 0.3, 0.4, 0.5, 0.6, 0.8, 0.89, 1, 1.25, 1.5, 1.75, 1.989, 2, 2.5, 3, 4, 5, 6, 7, 8, 9, 10, 12, 15, 20, 30, 40]
        self._scroll_notch_i = state['Zoom']
        
        # transform parameters
        self._Hc = state['Hc']
        self._Kc = state['Kc']
        
        self._H = state['H']
        self._K = state['K']

        self._A = self._scroll_notches[self._scroll_notch_i]
        
        self.fcursor._ftx.stats(spell=True)
    
    def read_display_state(self):
        return {
            'mode': self._mode,
            'Hc': self._Hc,
            'Kc': self._Kc,
            'H': self._H,
            'K': self._K,
            'Zoom': self._scroll_notch_i
            }
    
    # TRANSFORMATION FUNCTIONS
    def _X_to_screen(self, x, pp):
        return int(self._A * (meredith.page.map_X(x, pp) + self._H - self._Hc) + self._Hc)

    def _Y_to_screen(self, y, pp):
        return int(self._A * (meredith.page.map_Y(y, pp) + self._K - self._Kc) + self._Kc)
    
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
            clipboard = self.keyboard.type_document(name, char)
            # check if paragraph and font context changed
            CText.update()
            
            return clipboard
            
        elif self._mode == 'channels':
            caramel.delight.key_input(name)
            
    def press(self, x, y, name):
        self._check_region_press(x, y)
        
        if self._region_active == 'view':

            x, y = self._T_1(x, y)

            # TEXT EDITING MODE
            if self._mode == 'text':
                try:
#                    x, y = meredith.mipsy.set_page_context(x, y)
                    
                    un.history.undo_save(0)
                    self.fcursor.target(x, y)
                    
                    # used to keep track of ui redraws
                    self._sel_cursor = self.fcursor.j
                    
                except ValueError:
                    # occurs if an empty channel is selected
                    print('empty channel selected')
                # check if paragraph context changed
                CText.update()
                
                # count words
                self.fcursor._ftx.stats()
            
            # CHANNEL EDITING MODE
            elif self._mode == 'channels':
                caramel.delight.press(x, y, name=name)

        elif self._region_active == 'toolbar':
            self._toolbar.press(x, y)
        elif self._region_active == 'switcher':
            self._mode_switcher.press(x)

    def dpress(self):
        if self._region_active == 'view':
            # TEXT EDITING MODE
            if self._mode == 'text':
                self.fcursor.expand_cursors_word()
    
    def press_right(self, x, y):
        if self._region_active == 'view':

            xo, yo = self._T_1(x, y)
            
            # TEXT EDITING MODE
            if self._mode == 'text':
                try:
                    self.fcursor.target(xo, yo)
                    i = self.fcursor.i
                    
                    ms = self.fcursor.TRACT.misspellings
                    pair_i = bisect.bisect([pair[0] for pair in ms], i) - 1

                    if ms[pair_i][0] <= i <= ms[pair_i][1]:

                        if i == ms[pair_i][1]:
                            self.fcursor.i -= 1
                        
                        # used to keep track of ui redraws
                        self._sel_cursor = self.fcursor.j
                        self.fcursor.expand_cursors_word()
                        suggestions = ['“' + ms[pair_i][2] + '”'] + [w.decode("utf-8") for w in wonder.struck.suggest(ms[pair_i][2])]
                        suggestions = list(zip(suggestions, [str(v) for v in suggestions]))
                        menu.menu.create(x, y, 200, suggestions, _replace_misspelled, () )

                except IndexError:
                    # occurs if an empty channel is selected
                    pass
                # check if paragraph context changed
                CText.update()
    
    def press_motion(self, x, y):
        if self._region_active == 'view':

            if y <= 5:
                self._K += int(10 / sqrt(self._A))
                noticeboard.redraw_becky.push_change()
            elif y >= constants.window.get_k() - 5:
                self._K -= int(10 / sqrt(self._A))
                noticeboard.redraw_becky.push_change()

            x, y = self._T_1(x, y)
#            xp, yp = meredith.mipsy.XY(x, y)

            if self._mode == 'text':
                self.fcursor.target_select(x, y)
                if self.fcursor.j != self._sel_cursor:
                    self._sel_cursor = self.fcursor.j
                    noticeboard.redraw_becky.push_change()

            elif self._mode == 'channels':
                caramel.delight.press_motion(x, y)
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
            
            noticeboard.redraw_becky.push_change()
        # drag
        else:
            
            self._H = int(round( (x - self._stake[0]) / self._A + self._stake[2]))
            self._K = int(round( (y - self._stake[1]) / self._A + self._stake[3]))
            
            # heaven knows why this expression works, but hey it works
            dx = (self._H - self._stake[2]) * self._A
            dy = (self._K - self._stake[3]) * self._A
            
            if [dx, dy] != reference:
                reference[:] = [dx, dy]
                noticeboard.redraw_becky.push_change()

    def release(self, x, y):
        self._toolbar.release(x, y)

        if self._region_active == 'view':
            if self._mode == 'channels':
                caramel.delight.release()
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
                self._K -= int(50 / sqrt(self._A))
            else:
                self._K += int(50 / sqrt(self._A))
        
        noticeboard.redraw_becky.push_change()

    def hover(self, x, y):
        self._check_region_hover(x, y)
        
        if self._region_hover == 'view':
            if self._mode == 'text':
                pass

            elif self._mode == 'channels':
                caramel.delight.hover( * self._T_1(x, y) )
                
        elif self._region_hover == 'toolbar':
            self._toolbar.hover(x, y)
        elif self._region_hover == 'switcher':
            self._mode_switcher.hover(x)

    def resize(self, h, k):
        self._mode_switcher.resize(h, k)

    def change_mode(self, mode):
        self._mode = mode
        CText.update()
        noticeboard.refresh_properties_stack.push_change()
        noticeboard.refresh_properties_type.push_change(mode)
    
    def _print_sorted(self, cr, classed_glyphs):
        for font, glyphs in (L for name, L in classed_glyphs.items() if isinstance(name, int)):
            cr.set_source_rgba( * font['color'])
            cr.set_font_size(font['fontsize'])
            cr.set_font_face(font['font'])
            cr.show_glyphs(glyphs)
    
    def page_classes(self):
        classed_pages = {}

        jumbled_pages = [tract.extract_glyphs() for tract in meredith.mipsy.tracts]

        for dictionary in jumbled_pages:
            for page, sorted_glyphs in dictionary.items():
                if page in classed_pages:
                    for name, font, glyphs in ((key, * L) for key, L in sorted_glyphs.items() if L and (isinstance(key, int) or key == '_images')):
                        classed_pages[page].setdefault(name, (font, []))[1].extend(glyphs)
                else:
                    classed_pages[page] = {name: L for name, L in sorted_glyphs.items() if isinstance(name, int) or name == '_images'}
        
        return classed_pages
    
    def print_page(self, cr, p, classed_pages):
        if p in classed_pages:
            self._draw_images(cr, classed_pages[p]['_images'])
            self._print_sorted(cr, classed_pages[p])
            
    def _draw_by_page(self, cr, mx_cx, my_cy, cx, cy, A=1, refresh=False):
        PHEIGHT = meredith.page.HEIGHT
        PWIDTH = meredith.page.WIDTH
        
        max_page = 0
        for tract in meredith.mipsy.tracts:            
            for page, sorted_glyphs in tract.extract_glyphs(refresh).items():
                max_page = max(max_page, page)

                # Transform goes
                # x' = A (x + m - c) + c
                # x' = Ax + (Am - Ac + c)
                
                # Scale first (on bottom) is significantly faster in cairo
                cr.save()
                cr.translate(A*meredith.page.map_X(mx_cx, page) + cx, A*meredith.page.map_Y(my_cy, page) + cy)
                cr.scale(A, A)

                self._draw_images(cr, sorted_glyphs['_images'])
                self._print_sorted(cr, sorted_glyphs)

                cr.restore()
                
                # only annotate active tract
                if tract is self.fcursor.TRACT and self._mode == 'text':
                    self._draw_annotations(cr, sorted_glyphs['_annot'], page)
                    self._draw_spelling(cr, tract.paint_misspellings())
        
        if self._mode == 'text':
            meredith.mipsy.page_context, selections, signs = self.fcursor.paint_current_selection()
            self._draw_selection_highlight(cr, selections, signs)

        for pp in range(max_page + 1):
            
            #draw page border
            if pp == meredith.mipsy.page_context:
                cr.set_source_rgba( * accent_light, 0.7)
            else:
                cr.set_source_rgba(0, 0, 0, 0.2)

            px = self._X_to_screen(0, pp)
            py = self._Y_to_screen(0, pp)
            
            cr.rectangle(px, py, int(round(PWIDTH*self._A)), 1)
            
            cr.rectangle(px - int(round(20*self._A)), py, int(round(10*self._A)), 1)
            cr.rectangle(px + int(round((PWIDTH + 10)*self._A)), py, int(round(10*self._A)), 1)
            
            
            cr.rectangle(px, py, 1, int(round(PHEIGHT*self._A)))
            
            cr.rectangle(px, py - int(round(20*self._A)), 1, int(round(10*self._A)))
            cr.rectangle(px, py + int(round((PHEIGHT + 10)*self._A)), 1, int(round(10*self._A)))
            
            cr.rectangle(px + int(round(PWIDTH*self._A)), py, 1, int(round(PHEIGHT*self._A)) + 1)
            
            cr.rectangle(px + int(round(PWIDTH*self._A)), py - int(round(20*self._A)), 1, int(round(10*self._A)))
            cr.rectangle(px + int(round(PWIDTH*self._A)), py + int(round((PHEIGHT + 10)*self._A)), 1, int(round(10*self._A)))
            
            
            cr.rectangle(px, py + int(round(PHEIGHT*self._A)), int(round(PWIDTH*self._A)) + 1, 1)
            
            cr.rectangle(px - int(round(20*self._A)), py + int(round(PHEIGHT*self._A)), int(round(10*self._A)), 1)
            cr.rectangle(px + int(round((PWIDTH + 10)*self._A)), py + int(round(PHEIGHT*self._A)), int(round(10*self._A)), 1)
            
            cr.fill()
            
            if self._mode == 'channels':
                caramel.delight.render_grid(cr, px, py, PWIDTH, PHEIGHT, self._A)

    def _draw_images(self, cr, images):
        for IMAGE, x, y in images:
            image_surface = cairo.ImageSurface.create_from_png(IMAGE[0])
            
            H = image_surface.get_width()
            factor = IMAGE[1]/H
            
            cr.save()
            cr.translate(x, y)
            cr.scale(factor, factor)
            
            cr.set_source_surface(image_surface, 0, 0)
            cr.paint()
            
            cr.restore()

    def _draw_annotations(self, cr, annot, page):

        for a, x, y, PP, F in annot:
            
            x = self._X_to_screen(x, page)
            y = self._Y_to_screen(y, page)
            
            fontsize = F['fontsize'] * self._A

            if PP is self.fcursor.pp_at():
                cr.set_source_rgba( * accent_light, 0.7)
            else:
                cr.set_source_rgba(0, 0, 0, 0.4)
            
            #         '<p>'
            if a == -2:
                
                cr.move_to(x, y)
                cr.rel_line_to(0, -fontsize)
                cr.rel_line_to(-3, 0)
                # sharp edge do not round
                cr.rel_line_to(-fontsize/5, fontsize/2)
                cr.line_to(x - 3, y)
                cr.close_path()
                cr.fill()

            #        '<br>' +1
            elif a == -6:
                
                cr.rectangle(x - 6, y - fontsize, 3, fontsize)
                cr.rectangle(x - 10, y - 3, 4, 3)
                cr.fill()

            #           '<f>'
            elif a == -4:
                cr.move_to(x, y - fontsize)
                cr.rel_line_to(0, 6)
                cr.rel_line_to(-1, 0)
                cr.rel_line_to(-3, -6)
                cr.close_path()
                cr.fill()
            
            #          '</f>'
            elif a == -5:
                cr.move_to(x, y - fontsize)
                cr.rel_line_to(0, 6)
                cr.rel_line_to(1, 0)
                cr.rel_line_to(3, -6)
                cr.close_path()
                cr.fill()

    def _draw_spelling(self, cr, underscores):
        cr.set_source_rgba(1, 0.15, 0.2, 0.8)
        for y, x1, x2, page in underscores:
            cr.rectangle(self._X_to_screen(x1, page), 
                    self._Y_to_screen(y + 2, page), 
                    int((x2 - x1) * self._A), 1)
        cr.fill()
        
    def _draw_selection_highlight(self, cr, selections, signs):
        cr.push_group()
        cr.set_source_rgba(0, 0, 0, 0.1)
        for y, x1, x2, leading, page in selections:
            cr.rectangle(self._X_to_screen(x1, page), 
                    self._Y_to_screen(y - leading, page), 
                    int((x2 - x1) * self._A), 
                    int(leading * self._A))
        cr.fill()
        # print cursor
        reverse, isign, jsign = signs
        if reverse:
            isign, jsign = jsign, isign
        
        # first
        y1, x11, x21, leading1, page1 = selections[0]
        y2, x12, x22, leading2, page2 = selections[-1]
        self._draw_cursor(cr, isign, self._X_to_screen(x11, page1), self._Y_to_screen(y1, page1), int(leading1 * self._A))
        self._draw_cursor(cr, jsign, self._X_to_screen(x22, page2), self._Y_to_screen(y2, page2), int(leading2 * self._A))

        cr.pop_group_to_source()
        cr.paint_with_alpha(0.8)
    
    def _draw_cursor(self, cr, sign, x, y, leading):
        
        cr.set_source_rgb(1, 0, 0.5)

        ux = x
        uy = y - leading
        uh = leading
        
        cr.rectangle(ux - 1, 
                    uy, 
                    2, 
                    uh)
        # special cursor if adjacent to font tag
        if sign[0]:
            cr.rectangle(ux - 1, 
                    uy, 
                    4, 
                    2)
            cr.rectangle(ux - 1, 
                    uy + uh - 2, 
                    4, 
                    2)
        if sign[1]:
            cr.rectangle(ux - 3, 
                    uy, 
                    4, 
                    2)
            cr.rectangle(ux - 3, 
                    uy + uh - 2, 
                    4, 
                    2)
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
            caramel.delight.render(cr, self._X_to_screen, self._Y_to_screen)
        else:
            caramel.delight.render(cr, self._X_to_screen, self._Y_to_screen, show_rails=True)
        
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
        font = styles.ISTYLES[('strong',)]
        
        cr.set_font_size(font['fontsize'])
        cr.set_font_face(font['font'])

        if noticeboard.composition_sequence:
            cr.move_to(130, 40)
            cr.show_text(' '.join(noticeboard.composition_sequence))
        
        cr.move_to(130, k - 20)
        cr.show_text('{0:g}'.format(self._A*100) + '%')
        
        cr.move_to(constants.UI[1] - 150, k - 20)
        cr.show_text(str(self.fcursor._ftx.word_count) + ' words · page ' + str(self.fcursor.PG))
        
        cr.reset_clip()
