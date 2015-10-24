import bisect
from freetype import ft_errors
from copy import deepcopy

from state import constants
from state import noticeboard

from fonts import fonts
from fonts import fonttable

from interface import kookies

from model import meredith


class _Font_file_Field(kookies.Blank_space):
    def __init__(self, x, y, width, p, f, name=None):
    
        kookies.Blank_space.__init__(self, x, y, width, fonttable.table.get_font(p, f)['path'], callback=self._push_fontname, name=name)

        self.p = p
        self.f = f

        if not fonttable.table.get_font(self.p, self.f)['path_valid']:
            self.broken = True
        else:
            self.broken = False

    def _push_fontname(self, path):

        fonttable.table.clear()
        
        fonts.f_set_attribute('path', self.p, self.f, (False, path))
        self.broken = not fonttable.table.get_font(self.p, self.f)['path_valid']
        
        meredith.mipsy.rerender()

class _Font_numeric_Field(kookies.Numeric_field):
    def __init__(self, x, y, width, p, f, attribute, name=None):
        kookies.Numeric_field.__init__(self, x, y, width, 
                str(fonttable.table.get_font(p, f)[attribute]), 
                callback=self._push_attribute, 
                name=name)
        
        self.p = p
        self.f = f
        self._attribute = attribute
        
    def _push_attribute(self, value):
        fonttable.table.clear()
        
        fonts.f_set_attribute(self._attribute, self.p, self.f, (False, self._to_number(value)))
        
        meredith.mipsy.rerender()
    
class _Paragraph_numeric_Field(kookies.Numeric_field):
    def __init__(self, x, y, width, p, attribute, name=None):
        kookies.Numeric_field.__init__(self, x, y, width, 
                str(fonttable.p_table.get_paragraph(p)[attribute]), 
                callback=self._push_attribute, 
                name=name)
        
        self.p = p
        self._attribute = attribute

    def _push_attribute(self, value):
        fonttable.p_table.clear()
        
        fonts.p_set_attribute(self._attribute, self.p, (False, self._to_number(value)))
        meredith.mipsy.rerender()

class _Paragraph_checkbox(kookies.Checkbox):
    def __init__(self, x, y, width, p, attribute, name=None):
        kookies.Checkbox.__init__(self, x, y, width,
                fonttable.p_table.get_paragraph(p)[attribute], 
                callback=self._push_attribute, 
                string=name)
        
        self.p = p
        self._attribute = attribute

    def _push_attribute(self, value):
        fonttable.p_table.clear()
        
        fonts.p_set_attribute(self._attribute, self.p, (False, value))
        meredith.mipsy.rerender()
        
        klossy.refresh()


class _Paragraph_style_menu(kookies.Object_menu):
    def __init__(self, x, y, width, p, name=None):
        kookies.Object_menu.__init__(self, x, y, width, p, callback=self._push_pname, addition_callback=self._add_paragraph_class, menu_callback=self._menu_select_class, menu_options=sorted(fonts.paragraph_classes.keys()), name=name)
        
        self.p = p

#        self.hover_in_borders = self.in_borders


    def _push_pname(self, name):
        fonttable.p_table.clear()
        
        fonts.rename_p(self.p, name)
        meredith.mipsy.rename_paragraph_class(self.p, name)
        self.p = name

        meredith.mipsy.rerender()

    def _menu_select_class(self, name):
        p = meredith.mipsy.glyph_at()[2]
        meredith.mipsy.change_paragraph_class(p[1], name)
        klossy.refresh()
        return False

    def _add_paragraph_class(self):
        fonttable.p_table.clear()
        
        p = meredith.mipsy.glyph_at()[2]
        if len(p[0]) > 3 and p[0][-4] == '.' and len([c for c in p[0][-3:] if c in '1234567890']) == 3:
            serialnumber = int(p[0][-3:])
            while True:
                serialnumber += 1
                name = p[0][:-3] + str(serialnumber).zfill(3)
                if name not in fonts.paragraph_classes:
                    break
        else:
            name = p[0] + '.001'
        fonts.add_paragraph_class(name, p[0])
        meredith.mipsy.change_paragraph_class(p[1], name)

        klossy.refresh()
        

class _Inheritance_selection_menu(kookies.Selection_menu):
    def __init__(self, x, y, callback, p, f, attribute):
        self._p = p
        self._f = f
        self._attribute = attribute
        
        if self._attribute == '_all':
            current = fonts.paragraph_classes[self._p]['fontclasses'][1][self._f]
        else:
            current = fonts.f_read_attribute(self._attribute, self._p, self._f)
        if current[0]:
            default = current[1]
        else:
            default = 'x'
        
        combos = ['x']
        for key in sorted(fonts.paragraph_classes.keys()):
            if not fonts.paragraph_classes[key]['fontclasses'][0]:
                combos += [ (key, ff) for ff in fonts.paragraph_classes[key]['fontclasses'][1].keys() ]
        kookies.Selection_menu.__init__(self, x, y, width=50, height=15, callback=callback, menu_callback=self._push_inherit, menu_options=combos, default=default)
        
    def _push_inherit(self, value):
        fonttable.table.clear()
        if value == 'x':
            if self._attribute == '_all':
                fonts.paragraph_classes[self._p]['fontclasses'][1][self._f] = deepcopy(fonts.f_get_f(self._p, self._f))
            else:
                fonts.f_set_attribute(self._attribute, self._p, self._f, (False, fonttable.table.get_font(self._p, self._f)[self._attribute]) )
        else:
            if self._attribute == '_all':
                # save old value in case of a disaster
                v = fonts.f_get_f(self._p, self._f)
                value = (True, value)
                fonts.paragraph_classes[self._p]['fontclasses'][1][self._f] = value

                try:
                    fonttable.table.get_font(self._p, self._f)
                except RuntimeError:
                    fonttable.table.clear()
                    fonts.paragraph_classes[self._p]['fontclasses'][1][self._f] = v
                    print('REFERENCE LOOP DETECTED')
            else:
                # save old value in case of a disaster
                v = fonts.f_get_attribute(self._attribute, self._p, self._f)
                value = (True, value)
                fonts.f_set_attribute(self._attribute, self._p, self._f, value)

                try:
                    fonttable.table.get_font(self._p, self._f)
                except RuntimeError:
                    fonttable.table.clear()
                    fonts.f_set_attribute(self._attribute, self._p, self._f, v)
                    print('REFERENCE LOOP DETECTED')
        
        klossy.refresh()

class _Paragraph_inheritance_menu(kookies.Selection_menu):
    def __init__(self, x, y, callback, p, attribute):
        self._p = p
        self._attribute = attribute
        
        current = fonts.p_read_attribute(self._attribute, self._p)
        
        if current[0]:
            default = current[1]
        else:
            default = 'x'
        
        combos = ['x']
        combos += fonts.paragraph_classes.keys()
        kookies.Selection_menu.__init__(self, x, y, width=50, height=15, callback=callback, menu_callback=self._push_inherit, menu_options=combos, default=default)
        
    def _push_inherit(self, value):
        fonttable.p_table.clear()
        if value == 'x':
            fonts.p_set_attribute(self._attribute, self._p, (False, fonttable.p_table.get_paragraph(self._p)[self._attribute]) )
        else:
            # save old value in case of a disaster
            v = fonts.p_get_attribute(self._attribute, self._p)
            value = (True, value)
            fonts.p_set_attribute(self._attribute, self._p, value)

            try:
                fonttable.p_table.get_paragraph(self._p)
            except RuntimeError:
                fonttable.p_table.clear()
                fonts.p_set_attribute(self._attribute, self._p, v)
                print('REFERENCE LOOP DETECTED')
        
        klossy.refresh()
    

class _preview(kookies.Heading):
    def __init__(self, x, y, width, height, text, p, f):
        
        kookies.Heading.__init__(self, x, y, width, height, text, font=fonttable.table.get_font(p[0], f), fontsize = 15)
        
        self.p = p
        self.f = f

        
    def draw(self, cr, hover=(None, None)):
        cr.set_source_rgb(0,0,0)
        
        cr.set_font_size(15)
        cr.set_font_face(self.font['font'])
        cr.show_glyphs(self._texts[0])

class Properties_Panel(object):
    def __init__(self):
        self._h = constants.windowwidth
        self._k = constants.windowheight
        
        self._tabstrip = kookies.Tabs(self._h - constants.propertieswidth/2 - 50 , 50, 100, 30, callback=self._tab_switch, signals=['paragraph', 'font', '?'], strings=['P', 'F', '?'])
        self._tab = self._tabstrip.active_name()
        
        self.refresh_class(meredith.mipsy.glyph_at()[2])

    
    def refresh_class(self, p):
        
        self._items = [self._tabstrip]
        self._active_box_i = None
        self._hover_box_ij = (None, None)
        
        y = 145
        
        self._items.append(kookies.Heading(self._h - constants.propertieswidth + 15, 90, 250, 30, p[0], upper=True))

        if self._tab == 'font':
        
            for key, item in sorted(fonts.get_fontclasses(p[0]).items()):
                if key:
                    classname = 'Class: ' + ', '.join(key)
                else:
                    classname = 'Class: none'
                
                self._items.append(_preview(self._h - constants.propertieswidth + 16, y, 250, 0, classname, p, key ))
                
                if fonts.f_read_f(p[0], key)[0]:
                    self._items.append(_Inheritance_selection_menu(self._h - constants.propertieswidth + 200, y + 20, callback=None, p=p[0], f=key, attribute='_all'))
                    y += 50
                else:
                    self._items.append(_Inheritance_selection_menu(self._h - constants.propertieswidth + 200, y + 3, callback=None, p=p[0], f=key, attribute='_all'))
                    y += 30
                    
                    self._items.append(_Font_file_Field(self._h - constants.propertieswidth + 15, y, 250, p[0], key, name='FONT FILE' ))
                    y += 30
                    self._items.append(_Inheritance_selection_menu(self._h - constants.propertieswidth + 200, y, callback=None, p=p[0], f=key, attribute='path'))
                    y += 15
                    
                    self._items.append(_Font_numeric_Field(self._h - constants.propertieswidth + 15, y, 250, p[0], key, attribute='fontsize', name='FONT SIZE' ))
                    y += 30
                    self._items.append(_Inheritance_selection_menu(self._h - constants.propertieswidth + 200, y, callback=None, p=p[0], f=key, attribute='fontsize'))
                    y += 15
                    
                    self._items.append(_Font_numeric_Field(self._h - constants.propertieswidth + 15, y, 250, p[0], key, attribute='tracking', name='TRACKING' ))
                    y += 30
                    self._items.append(_Inheritance_selection_menu(self._h - constants.propertieswidth + 200, y, callback=None, p=p[0], f=key, attribute='tracking'))
                    y += 30
                        
        elif self._tab == 'paragraph':
            self._items.append(_Paragraph_style_menu(self._h - constants.propertieswidth + 15, y, 250, p[0], name='RENAME CLASS'))
            y += 45
            
            self._items.append(_Paragraph_numeric_Field(self._h - constants.propertieswidth + 15, y, 250, p[0], attribute='leading', name='LEADING' ))
            y += 30
            self._items.append(_Paragraph_inheritance_menu(self._h - constants.propertieswidth + 200, y, callback=None, p=p[0], attribute='leading'))
            y += 15
            
            self._items.append(_Paragraph_numeric_Field(self._h - constants.propertieswidth + 15, y, 250, p[0], attribute='margin_bottom', name='BOTTOM MARGIN' ))
            y += 30
            self._items.append(_Paragraph_inheritance_menu(self._h - constants.propertieswidth + 200, y, callback=None, p=p[0], attribute='margin_bottom'))
            y += 15

            self._items.append(_Paragraph_checkbox(self._h - constants.propertieswidth + 15, y + 15, 100, p[0], attribute='hyphenate', name='HYPHENATE' ))
            y += 30
            self._items.append(_Paragraph_inheritance_menu(self._h - constants.propertieswidth + 200, y, callback=None, p=p[0], attribute='hyphenate'))
            y += 15
            
        self._stack()

    def refresh(self):
        meredith.mipsy.rerender() # must come before because it rewrites all the paragraph styles
        self.refresh_class(meredith.mipsy.glyph_at()[2])

    def _tab_switch(self, name):
        self._tab = name
        self.refresh_class(meredith.mipsy.glyph_at()[2])
        print(self._tab)
        
    def resize(self, h, k):
        dx = h - self._h
        self._h = h

        for entry in self._items:
            entry.translate(dx=dx)
    
    def render(self, cr, h, k):
        # DRAW BACKGROUND
        cr.rectangle(h - constants.propertieswidth, 0, 
                300, 
                k)
        cr.set_source_rgb(1, 1, 1)
        cr.fill()
        
        # check if entries need restacking
        if noticeboard.refresh_properties_stack.should_refresh():
            self.refresh_class(meredith.mipsy.glyph_at()[2])
        
        for i, entry in enumerate(self._items):
            if i == self._hover_box_ij[0]:
                entry.draw(cr, hover=self._hover_box_ij)
            else:
                entry.draw(cr)
        
        # DRAW SEPARATOR
        cr.rectangle(h - constants.propertieswidth, 0, 
                2, 
                k)
        cr.set_source_rgb(0.9, 0.9, 0.9)
        cr.fill()
    
    def key_input(self, name, char):
        if self._active_box_i is not None:
            if name == 'Return':
                if self._items[self._active_box_i].defocus():
                    print('UPDATE PANEL')
                    self.refresh_class(meredith.mipsy.glyph_at()[2])
                
                self._active_box_i = None
            else:
                return self._items[self._active_box_i].type_box(name, char)
    
    def _stack(self):
        self._rows = [item.y for item in self._items]

    def _stack_bisect(self, y):
        return bisect.bisect(self._rows, y)
    
    def press(self, x, y):

        b = None

        bb = self._stack_bisect(y)

        try:
            if self._items[bb].is_over(x, y):
                self._items[bb].focus(x)
                b = bb

        except IndexError:
            pass
        # defocus the other box, if applicable
        if b is None or b != self._active_box_i:
            if self._active_box_i is not None:
                if self._items[self._active_box_i].defocus():

                    print('UPDATE PANEL')
                    self.refresh_class(meredith.mipsy.glyph_at()[2])
                    
            self._active_box_i = b

            
    def press_motion(self, x):
        if self._active_box_i is not None:
            self._items[self._active_box_i].focus_drag(x)
    
    def hover(self, x, y, hovered=[None]):
    
        self._hover_box_ij = (None, None)
        
        bb = self._stack_bisect(y)
        try:
            if self._items[bb].is_over_hover(x, y):
                self._hover_box_ij = (bb, self._items[bb].hover(x))

        except IndexError:
            # if last index
            pass

        if hovered[0] != self._hover_box_ij:
            hovered[0] = self._hover_box_ij
            noticeboard.refresh.push_change()

klossy = Properties_Panel()

