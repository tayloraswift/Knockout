import bisect
from math import pi, sqrt
import os
import cairo

from itertools import chain

from fonts.interfacefonts import ISTYLES
from fonts import SPACENAMES

from meredith.datablocks import DOCUMENT

from edit import wonder
from edit import cursor, caramel

from IO import un

from keyboard import keyboard

from state import noticeboard, constants
from state.contexts import Text as CText
from state.constants import accent, accent_light

from meredith.smoothing import fontsettings
from meredith.meta import filedata

from interface import kookies, fields, ui
from interface.menu import menu

class Mode_switcher(object):
    def __init__(self, callback, default):
        self._hover_j = None
        signals = [('render', 'R'), ('text', 'T'), ('frames', 'F')]
        default = next(i for i, k in enumerate(signals) if k[0] == default)
        self._switcher = kookies.Tabs_round(0, -70, 40, 30, default=default, callback=callback, signals=signals, longstrings=['View render', 'Edit text', 'Edit frames'])

    def is_over(self, x, y):
        return self._switcher.is_over(x - self._dx, y - self._dy)

    def resize(self, k):
        # center
        self._dx = (constants.UI[1] - 100)/2 + 100 
        self._dy = k

    def render(self, cr, h, k):
        cr.save()
        cr.translate(self._dx , k)
        
        self._switcher.draw(cr, hover=(None, self._hover_j))
        
        cr.restore()
    
    def press(self, x):
        self._switcher.focus(x - self._dx, 0)
    
    def hover(self, x):
        j = self._switcher.hover(x - self._dx, 0)
        if j != self._hover_j:
            noticeboard.redraw_becky.push_change()
            self._hover_j = j
    
    def clear_hover(self):
        self._hover_j = None
        noticeboard.redraw_becky.push_change()

def PDF():
    name = os.path.splitext(filedata['filepath'])[0]
    surface = cairo.PDFSurface(name + '.pdf', DOCUMENT['width']*0.75, DOCUMENT['height']*0.75)
    cr = cairo.Context(surface)
    cr.scale(0.75, 0.75)
    pages = DOCUMENT.transfer()
    max_page = max(k for k in pages if k is not None)
    for p in range(max_page + 1):
        if p in pages:
            becky.print_page(cr, p, pages[p])
        cr.show_page()

def _place_tags(key):
    un.history.undo_save(3)
    if not cursor.fcursor.bridge(keyboard[key], sign=True):
        un.history.pop()

def _punch_tags(key):
    un.history.undo_save(3)
    if not cursor.fcursor.bridge(keyboard[key], sign=False):
        un.history.pop()

class Document_toolbar(object):
    def __init__(self, save):
        self._save = save
        self.refresh_class()
    
    def refresh_class(self):
        
        self._items = []
        self._active_box = None
        self._hover_box_ij = (None, None)
        self._hover_memory = (None, None)
        
        y = 120
        self._items.append(kookies.Button(5, y, 90, 30, callback=self._save, name='Save'))
        y += 30
        self._items.append(kookies.Button(5, y, 90, 30, callback=PDF, name='PDF'))
        
        y += 40
        self._items.append(kookies.Button(5, y, 90, 30, callback=un.history.back, name='Undo'))
        y += 30
        self._items.append(kookies.Button(5, y, 90, 30, callback=un.history.forward, name='Redo'))
        
        y += 40
        self._items.append(kookies.Button(5, y, 90, 30, callback=caramel.delight.add_frame, name='Add frame'))
        y += 30
        self._items.append(kookies.Button(5, y, 90, 30, callback=DOCUMENT.add_section, name='Add section'))
        
        y += 50
        self._items.append(kookies.Button(5, y, 90, 30, callback=lambda: _place_tags('Ctrl i'), name='Emphasis'))
        y += 30
        self._items.append(kookies.Button(5, y, 90, 30, callback=lambda: _punch_tags('Ctrl I'), name='x Emphasis'))

        y += 40
        self._items.append(kookies.Button(5, y, 90, 30, callback=lambda: _place_tags('Ctrl b'), name='Strong'))
        y += 30
        self._items.append(kookies.Button(5, y, 90, 30, callback=lambda: _punch_tags('Ctrl B'), name='x Strong'))

        y += 40
        self._items.append(fields.Checkbox(20, y, 70, node=DOCUMENT, A='dual', name='Dual'.upper(), no_z=True))
        y += 35
        self._items.append(fields.Checkbox(20, y, 70, node=DOCUMENT, A='even', name='Even'.upper(), no_z=True))
        
        y += 50
        
        self._items.append(fields.Selection_menu(5, y, 90, partition=0, 
                                                menu_options=[(0, 'Default'), (1, 'None'), (2, 'Slight'), (3, 'Medium'), (4, 'Strong')], 
                                                node=fontsettings, 
                                                A='hinting',
                                                name='HINTING', no_z=True))
        y += 45
        self._items.append(fields.Selection_menu(5, y, 90, partition=0, 
                                                menu_options=[(0, 'Default'), (1, 'None'), (2, 'Grayscale'), (3, 'Subpixel')], 
                                                node=fontsettings, 
                                                A='antialias',
                                                name='ANTIALIAS', no_z=True))
                
        self._rows = [item.y_bottom for item in self._items]
        
    def render(self, cr):
        for i, entry in enumerate(self._items):
            if i == self._hover_box_ij[0]:
                entry.draw(cr, hover=self._hover_box_ij)
            else:
                entry.draw(cr)
    
    def _stack_bisect(self, x, y):
        try:
            return self._items[bisect.bisect(self._rows, y)]
        except IndexError:
            return self._items[-1]
    
    def press(self, x, y):
        b = None
        
        box = self._stack_bisect(x, y)

        try:
            if box.is_over(x, y):
                box.focus(x, y)
                b = box

        except IndexError:
            pass
        # defocus the other box, if applicable
        if b is None or b is not self._active_box:
            if self._active_box is not None:
                
                if self._active_box.defocus():
                    self.refresh_class()
            
            self._active_box = b
    
    def release(self, x, y):
        box = self._stack_bisect(x, y)

        bl = False
        try:
            if box.is_over(x, y) and box is self._active_box:
                bl = True
        except IndexError:
            pass
        
        if self._active_box is not None:
            self._active_box.release(action = bl)

    def hover(self, x, y):
    
        self._hover_box_ij = (None, None)

        inspect_i = bisect.bisect(self._rows, y)
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


def _replace_misspelled(word, label):
    if label[0] == '“':
        wonder.struck.add(word)
        with open(wonder.additional_words_file, 'a') as A:
            A.write(word + '\n')
    else:
        keyboard.type_document('Paste', word)
    cursor.fcursor.run_stats(spell=True) #probably only needs to be run on paragraph

class Document_view(ui.Cell):
    def __init__(self, save, state={'mode': 'text', 'Hc': 0, 'Kc': 0, 'H': 0, 'K': 0, 'Zoom': 11}):
        self._mode = state['mode']
        self._region_active, self._region_hover = 'view', 'view'
        self._toolbar = Document_toolbar(save)
        self._mode_switcher = Mode_switcher(self.change_mode, default= self._mode)
        self.planecursor = cursor.fcursor
        
        self._stake = None
        
        self._scroll_notches = [0.1, 0.13, 0.15, 0.2, 0.22, 0.3, 0.4, 0.5, 0.6, 0.8, 0.89, 1, 1.25, 1.5, 1.75, 1.989, 2, 2.5, 3, 4, 5, 6, 7, 8, 9, 10, 12, 15, 20, 30]
        self._scroll_notch_i = state['Zoom']
        
        # transform parameters
        self._Hc = state['Hc']
        self._Kc = state['Kc']
        
        self._H = state['H']
        self._K = state['K']

        self._A = self._scroll_notches[self._scroll_notch_i]
        
        self._font = ISTYLES[('strong',)]

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
        return int(self._A * (DOCUMENT.map_X(x, pp) + self._H - self._Hc) + self._Hc)

    def _Y_to_screen(self, y, pp):
        return int(self._A * (DOCUMENT.map_Y(y, pp) + self._K - self._Kc) + self._Kc)
    
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
            clipboard = keyboard.type_document(name, char)
            # check if paragraph and font context changed
            CText.update()
            return clipboard
            
        elif self._mode == 'frames':
            caramel.delight.key_input(name)
            CText.update_frames()
            
    def press(self, x, y, name):
        self._check_region_press(x, y)
        
        if self._region_active == 'view':

            x, y = self._T_1(x, y)

            # TEXT EDITING MODE
            if self._mode == 'text':

                un.history.undo_save(0)
                self.planecursor.target(x, y)
                
                # used to keep track of ui redraws
                self._sel_cursor = self.planecursor.j
                
                # check if paragraph context changed
                CText.update()
                
                # count words
                self.planecursor.run_stats()
            
            # frame EDITING MODE
            elif self._mode == 'frames':
                caramel.delight.press(x, y, name=name)
                CText.update_frames()

        elif self._region_active == 'toolbar':
            self._toolbar.press(x, y)
        elif self._region_active == 'switcher':
            self._mode_switcher.press(x)

    def dpress(self):
        if self._region_active == 'view':
            # TEXT EDITING MODE
            if self._mode == 'text':
                self.planecursor.expand_cursors_word()
            elif self._mode == 'frames':
                caramel.delight.dpress()
    
    def press_right(self, x, y):
        self._check_region_press(x, y)
        
        if self._region_active == 'view':

            xo, yo = self._T_1(x, y)
            
            # TEXT EDITING MODE
            if self._mode == 'text':
                try:
                    self.planecursor.target(xo, yo)
                    if len(self.planecursor.i) != 2:
                        return
                    ib, it = self.planecursor.i
                    
                    ms = self.planecursor.PLANE.content[ib].content.misspellings
                    pair_i = bisect.bisect([pair[0] for pair in ms], it) - 1

                    if ms[pair_i][0] <= it <= ms[pair_i][1]:
                        self.planecursor.i = (ib, ms[pair_i][0])
                        self.planecursor.j = (self.planecursor.j[0], ms[pair_i][1])
                        
                        # used to keep track of ui redraws
                        self._sel_cursor = self.planecursor.j
                        suggestions = [ms[pair_i][2]] + [w.decode("utf-8") for w in wonder.struck.suggest(ms[pair_i][2].encode('latin-1', 'ignore'))]
                        labels = suggestions[:]
                        labels[0] = '“' + labels[0] + '”'
                        menu.create(x, y, 200, list(zip(suggestions, labels)), _replace_misspelled)

                except IndexError:
                    # occurs if an empty frame is selected
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

            if self._mode == 'text':
                self.planecursor.target_select(x, y)
                if self.planecursor.j != self._sel_cursor:
                    self._sel_cursor = self.planecursor.j
                    noticeboard.redraw_becky.push_change()

            elif self._mode == 'frames':
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
            if self._mode == 'frames':
                caramel.delight.release()
        elif self._region_active == 'toolbar':
            pass
        elif self._region_active == 'switcher':
            pass

    def scroll(self, x, y, mod):
        x = int(x)
        y = int(y)
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

            elif self._mode == 'frames':
                caramel.delight.hover( * self._T_1(x, y) )
                
        elif self._region_hover == 'toolbar':
            self._toolbar.hover(x, y)
        elif self._region_hover == 'switcher':
            self._mode_switcher.hover(x)

    def resize(self, k):
        self._mode_switcher.resize(k)

    def change_mode(self, mode):
        self._mode = mode
        CText.update()
        noticeboard.refresh_properties_type.push_change(mode)
    
    def _print_sorted(self, cr, classed_glyphs):
        for font, glyphs in (L for name, L in classed_glyphs.items() if type(name) is int):
            cr.set_source_rgba( * font['color'])
            cr.set_font_size(font['fontsize'])
            cr.set_font_face(font['font'])
            cr.show_glyphs(glyphs)
    
    def print_page(self, cr, p, page):
        m = self._mode
        self._mode = 'render'
        for operation, x, y, z in chain(page['_images'], page['_paint']):
            cr.save()
            cr.translate(x, y)
            operation(cr, 0)
            cr.restore()
        self._print_sorted(cr, page)
        self._mode = m
            
    def _draw_by_page(self, cr, mx_cx, my_cy, cx, cy, A=1):
        medium  = DOCUMENT
        PHEIGHT = medium['height']
        PWIDTH  = medium['width']
        
        max_page      = 0
        sorted_glyphs = DOCUMENT.transfer()
        section       = self.planecursor.plane_address[0]
        if self._mode == 'render':
            zoom = 0
        else:
            zoom = self._A
        for page, P in (PP for PP in sorted_glyphs.items() if PP[0] is not None):
            max_page = max(max_page, page)
            
            # Transform goes
            # x' = A (x + m - c) + c
            # x' = Ax + (Am - Ac + c)
            
            # Scale first (on bottom) is significantly faster in cairo
            cr.save()
            cr.translate(A*medium.map_X(mx_cx, page) + cx, A*medium.map_Y(my_cy, page) + cy)
            cr.scale(A, A)
            
            for operation, x, y, z in chain(P['_images'], P['_paint']):
                cr.save()
                cr.translate(x, y)
                operation(cr, zoom)
                cr.restore()
            self._print_sorted(cr, P)

            # only annotate active tract
            if self._mode == 'text':
                annot, paint_annot = sorted_glyphs.annot[section].get(page, ((), ()))
                O = self.planecursor.PLANE
                for operation, x, y in paint_annot:
                    cr.save()
                    cr.translate(x, y)
                    operation(cr, O)
                    cr.restore()
                cr.restore()
                cr.set_font_face(self._font['font'])
                self._draw_annotations(cr, annot, page)
            
            else:
                cr.restore()
        
        if self._mode == 'text':
            self._draw_spelling(cr, self.planecursor.section.highlight_spelling())
            selections, signs = self.planecursor.paint_current_selection()
            if selections:
                self._draw_selection_highlight(cr, selections, signs)
            
            page_highlight = self.planecursor.PG
        
        elif self._mode == 'frames':
            page_highlight = caramel.delight.PG
        
        else:
            page_highlight = None

        for pp in range(max_page + 1):
            
            #draw page border
            if pp == page_highlight:
                cr.set_source_rgba( * accent_light )
            else:
                cr.set_source_rgba(0, 0, 0, 0.2)

            px1 = self._X_to_screen(0, pp)
            py1 = self._Y_to_screen(0, pp)
            
            px2 = px1 + int(round(PWIDTH*self._A))
            py2 = py1 + int(round(PHEIGHT*self._A))
            
            prg = int(round(10*sqrt(self._A)))
            
            cr.rectangle(px1, py1, px2 - px1, 1         )
            cr.rectangle(px1, py1, 1        , py2 - py1 )
            cr.rectangle(px1, py2, px2 - px1, 1         )
            cr.rectangle(px2, py1, 1        , py2 - py1 )
            
            cr.rectangle(px1 - prg  , py1       , -prg,   1 )
            cr.rectangle(px1        , py1 - prg ,   1 , -prg)
            
            cr.rectangle(px2 + prg  , py1       ,  prg,   1 )
            cr.rectangle(px2        , py1 - prg ,   1 , -prg)
            
            cr.rectangle(px1 - prg  , py2       , -prg,   1 )
            cr.rectangle(px1        , py2 + prg ,   1 ,  prg)
            
            cr.rectangle(px2 + prg  , py2       ,  prg,   1 )
            cr.rectangle(px2        , py2 + prg ,   1 ,  prg)
            
            cr.fill()
            
            if self._mode == 'frames':
                caramel.delight.render_grid(cr, px1, py1, PWIDTH, PHEIGHT, self._A)

    def _draw_annotations(self, cr, annot, page):
        afs = int(6 * sqrt(self._A))
        uscore = 1 + (self._A > 0.5)
        cr.set_font_size(afs)
        SN = SPACENAMES
        
        activeblock = self.planecursor.PLANE.content[self.planecursor.i[0]]
        for a, x, y, BLOCK, F in annot:
            
            x = self._X_to_screen(x, page)
            y = self._Y_to_screen(y, page)
            
            fontsize = F['fontsize'] * self._A
            
            if BLOCK is activeblock:
                cr.set_source_rgba( * BLOCK.color )
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

            #        '<br>'
            elif a == -9:
                cr.rectangle(x + 2, y - fontsize, 2, fontsize)
                cr.rectangle(x + 2, y - 2, fontsize - 4, 2)
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
            
            elif -41 <= a <= -30: # nbsp
                cr.rectangle(x, y, F['__spacemetrics__'][a] * self._A, uscore)
                cr.rel_move_to(0, afs * 1.25)
                cr.show_text(SN[a])
                cr.fill()
            
            elif a == -8:
                cr.rectangle(x - 4, y + 4, 8, 2)
                cr.rectangle(x - 1, y + 5, 2, 5)
                cr.fill()
            
            elif a == -23:
                cr.rectangle(x, y - fontsize, fontsize, fontsize)
                cr.fill()

    def _draw_spelling(self, cr, underscores):
        cr.set_source_rgba(1, 0.15, 0.2, 0.8)
        for y, x1, x2, page in underscores:
            if page is not None:
                cr.rectangle(self._X_to_screen(x1, page), 
                        self._Y_to_screen(y + 2, page), 
                        int((x2 - x1) * self._A), 1)
        cr.fill()
        
    def _draw_selection_highlight(self, cr, selections, signs):
        cr.push_group()
        cr.set_source_rgba(0, 0, 0, 0.1)
        for y, x1, x2, leading, page in selections:
            if page is not None:
                cr.rectangle(self._X_to_screen(x1, page), 
                        self._Y_to_screen(y - leading, page), 
                        int((x2 - x1) * self._A), 
                        int(leading * self._A))
        cr.fill()
        
        self._draw_cursor(cr, signs[0], selections[0], False)
        self._draw_cursor(cr, signs[1], selections[-1], True)

        cr.pop_group_to_source()
        cr.paint_with_alpha(0.8)
    
    def _draw_cursor(self, cr, sign, selection, side):
        y1, x1, x2, leading, page = selection
        if page is None:
            return
        height = int(leading * self._A)
        x = self._X_to_screen(selection[1 + side], page)
        y = self._Y_to_screen(y1, page)
        
        cr.set_source_rgb(1, 0, 0.5)

        ux = x
        uy = y - height
        uh = height
        
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
        self._draw_by_page(cr, self._H - self._Hc, self._K - self._Kc, self._Hc, self._Kc, self._A)
        cr.set_font_face(self._font['font'])
        # frames
        if self._mode == 'text':
            caramel.delight.render(cr, self._X_to_screen, self._Y_to_screen, frames=self.planecursor.section['frames'])
        elif self._mode == 'frames':
            caramel.delight.render(cr, self._X_to_screen, self._Y_to_screen, A=self._A)
        
        if self._mode != 'render':
            # DRAW TOOLBAR BACKGROUND
            cr.rectangle(0, 0, 100, k)
            cr.set_source_rgb(1, 1, 1)
            cr.fill()
            self._toolbar.render(cr)
            
            cr.rectangle(100, 0, 2, k)
            cr.set_source_rgb(0.9, 0.9, 0.9)
            cr.fill()
        
        self._mode_switcher.render(cr, h, k)
        
        # draw stats
        cr.set_source_rgba(0, 0, 0, 0.8)
        cr.set_font_size(self._font['fontsize'])
        
        cr.move_to(130, k - 20)
        cr.show_text('{0:g}'.format(self._A*100) + '%')
        
        cr.move_to(constants.UI[1] - 150, k - 20)
        cr.show_text(str(self.planecursor.word_total) + ' words · page ' + str(self.planecursor.PG))
        
        cr.reset_clip()
