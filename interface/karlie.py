import bisect
from freetype import ft_errors
from copy import deepcopy

from state import constants
from state import noticeboard

from fonts import fonts
from fonts import fonttable
from fonts import fontsetters as fs

from interface import kookies, caramel, ui

from model import meredith, penclick
from model import un


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
        
        fs.f_set_attribute('path', self.p, self.f, (False, path))
        self.broken = not fonttable.table.get_font(self.p, self.f)['path_valid']
        
        meredith.mipsy.recalculate_all()

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
        
        fs.f_set_attribute(self._attribute, self.p, self.f, (False, self._to_number(value)))
        
        meredith.mipsy.recalculate_all()
    
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
        
        fs.p_set_attribute(self._attribute, self.p, (False, self._to_number(value)))
        meredith.mipsy.recalculate_all()

class _Paragraph_checkbox(kookies.Checkbox):
    def __init__(self, x, y, width, p, attribute, name=None):
        self.p = p
        self._attribute = attribute
        
        kookies.Checkbox.__init__(self, x, y, width,
                callback=self._push_attribute,
                value_acquire=self._value_acquire,
                string=name)

    def _value_acquire(self):
        return fonttable.p_table.get_paragraph(self.p)[self._attribute]

    def _push_attribute(self, value):
        fonttable.p_table.clear()
        
        fs.p_set_attribute(self._attribute, self.p, (False, value))
        meredith.mipsy.recalculate_all()
        
#        klossy.refresh()

class _Paragraph_style_menu(kookies.Object_menu):
    def __init__(self, x, y, width, p, name=None, source=0):
        entries = sorted(fonts.paragraph_classes.keys())
        entries = list(zip(entries, [str(v) for v in entries]))
        kookies.Object_menu.__init__(self, x, y, width, p, callback=self._push_pname, addition_callback=self._add_paragraph_class, menu_callback=self._menu_select_class, menu_options=entries, name=name, source=source)
        
        self.p = p


    def _push_pname(self, name):
        fonttable.p_table.clear()
        
        fs.rename_p(self.p, name)
        meredith.mipsy.rename_paragraph_class(self.p, name)
        self.p = name

        meredith.mipsy.recalculate_all()

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
        fs.add_paragraph_class(name, p[0])
        meredith.mipsy.change_paragraph_class(p[1], name)

        klossy.refresh()
        

def _PF_options_acquire():
    combos = ['x']
    for key in sorted(fonts.paragraph_classes.keys()):
        if not fonts.paragraph_classes[key]['fontclasses'][0]:
            combos += [ (key, ff) for ff in fonts.paragraph_classes[key]['fontclasses'][1].keys() ]
    return list(zip(combos, [str(v) for v in combos]))
    
class _Inheritance_selection_menu(kookies.Selection_menu):
    def __init__(self, x, y, p, f, attribute, source=0):
        self._p = p
        self._f = f
        self._attribute = attribute

        kookies.Selection_menu.__init__(self, x, y, width=180, height=15, menu_callback=self._push_inherit, options_acquire=_PF_options_acquire, value_acquire=self._value_acquire, source=source)
    
    def _value_acquire(self):
        if self._attribute == '_all':
            current = fonts.paragraph_classes[self._p]['fontclasses'][1][self._f]
        else:
            current = fonts.f_read_attribute(self._attribute, self._p, self._f)
        
        if current[0]:
            return tuple(current[1])
        else:
            return 'x'
    
    def _push_inherit(self, value):
        fonttable.table.clear()
        if value == 'x':
            if self._attribute == '_all':
                fonts.paragraph_classes[self._p]['fontclasses'][1][self._f] = deepcopy(fonts.f_get_f(self._p, self._f))
            else:
                fs.f_set_attribute(self._attribute, self._p, self._f, (False, fonttable.table.get_font(self._p, self._f)[self._attribute]) )
        else:
            # save old value in case of a disaster
            if self._attribute == '_all':
                v = fonts.f_get_f(self._p, self._f)
            else:
                v = fonts.f_get_attribute(self._attribute, self._p, self._f)
            
            value = (True, value)
            fs.f_set_attribute(self._attribute, self._p, self._f, value)

            try:
                fonttable.table.get_font(self._p, self._f)
            except RuntimeError:
                fonttable.table.clear()
                fs.f_set_attribute(self._attribute, self._p, self._f, v)
                print('REFERENCE LOOP DETECTED')

        klossy.refresh()

def _P_options_acquire():
    PPP = ['x'] + list(fonts.paragraph_classes.keys())
    return list(zip(PPP, [str(v) for v in PPP]))
    
class _Paragraph_inheritance_menu(kookies.Selection_menu):
    def __init__(self, x, y, p, attribute, source=0):
        self._p = p
        self._attribute = attribute
        
        kookies.Selection_menu.__init__(self, x, y, width=180, height=15, menu_callback=self._push_inherit, options_acquire=_P_options_acquire, value_acquire=self._value_acquire, source=source)

    def _value_acquire(self):
        current = fonts.p_read_attribute(self._attribute, self._p)
        if current[0]:
            return current[1]
        else:
            return 'x'
    
    def _push_inherit(self, value):
        fonttable.p_table.clear()
        if value == 'x':
            fs.p_set_attribute(self._attribute, self._p, (False, fonttable.p_table.get_paragraph(self._p)[self._attribute]) )
        else:
            # save old value in case of a disaster
            v = fonts.p_get_attribute(self._attribute, self._p)
            value = (True, value)
            fs.p_set_attribute(self._attribute, self._p, value)

            try:
                fonttable.p_table.get_paragraph(self._p)
            except RuntimeError:
                fonttable.p_table.clear()
                fs.p_set_attribute(self._attribute, self._p, v)
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

# do not instantiate directly, requires a _reconstruct
class _Properties_panel(ui.Cell):
    def __init__(self, tabs = (), default=0, partition=1 ):
        
        self._partition = partition

        width = 140
        self._tabstrip = kookies.Tabs( (constants.window.get_h() - constants.UI[partition] - width)//2 , 50, width, 30, default=default, callback=self._tab_switch, signals=tabs)
        self._tab = tabs[default][0]
        
        self._reconstruct()

    def _tab_switch(self, name):
        if self._tab != name:
            self._tab = name
            self._reconstruct()
        
    def _stack(self):
        self._rows = [item.y for item in self._items]

    def _stack_bisect(self, y):
        return bisect.bisect(self._rows, y)

    def refresh(self):
        meredith.mipsy.recalculate_all() # must come before because it rewrites all the paragraph styles
        self._reconstruct()
    
    def render(self, cr, h, k):
        
        # DRAW BACKGROUND
        cr.rectangle(0, 0, 
                h - constants.UI[self._partition], 
                k)
        cr.set_source_rgb(1, 1, 1)
        cr.fill()
        
        # check if entries need restacking
        if noticeboard.refresh_properties_stack.should_refresh():
            mode = noticeboard.refresh_properties_type.should_refresh()
            if mode[0]:
                self._swap_reconstruct(mode[1])
            else:
                self._reconstruct()
        
        for i, entry in enumerate(self._items):
            if i == self._hover_box_ij[0]:
                entry.draw(cr, hover=self._hover_box_ij)
            else:
                entry.draw(cr)
        
        # DRAW SEPARATOR
        cr.rectangle(0, 0, 
                2, 
                k)
        cr.set_source_rgb(0.9, 0.9, 0.9)
        cr.fill()
    
    def key_input(self, name, char):
        if self._active_box_i is not None:
            if name == 'Return':
                if self._items[self._active_box_i].defocus():
                    print('UPDATE PANEL')
                    self._reconstruct()
                
                self._active_box_i = None
            else:
                return self._items[self._active_box_i].type_box(name, char)
    
    def press(self, x, y, char):

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
                    self._reconstruct()
                    
            self._active_box_i = b

            
    def press_motion(self, x, y):
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

class Properties(_Properties_panel):
    def __init__(self, tabs = (), default=0, partition=1 ):
        self._reconstruct = self._reconstruct_text_properties
        
        _Properties_panel.__init__(self, tabs = tabs, default=default, partition=partition) 

    def _reconstruct_text_properties(self):
        # ALWAYS REQUIRES CALL TO _stack()
        p = meredith.mipsy.glyph_at()[2]
        
        self._items = [self._tabstrip]
        self._active_box_i = None
        self._hover_box_ij = (None, None)
        
        y = 145
        
        self._items.append(kookies.Heading( 15, 90, 250, 30, p[0], upper=True))
        
        if self._tab == 'font':
        
            for key, item in sorted(fonts.get_fontclasses(p[0]).items()):
                if key:
                    classname = 'Class: ' + ', '.join(key)
                else:
                    classname = 'Class: none'
                
                self._items.append(_preview( 16, y, 250, 0, classname, p, key ))
                
                if fonts.f_read_f(p[0], key)[0]:
                    self._items.append(_Inheritance_selection_menu( 70, y + 20, p=p[0], f=key, attribute='_all', source=self._partition))
                    y += 50
                else:
                    self._items.append(_Inheritance_selection_menu( 70, y + 3, p=p[0], f=key, attribute='_all', source=self._partition))
                    y += 30
                    
                    self._items.append(_Font_file_Field( 15, y, 250, p[0], key, name='FONT FILE' ))
                    y += 30
                    self._items.append(_Inheritance_selection_menu( 70, y, p=p[0], f=key, attribute='path', source=self._partition))
                    y += 15
                    
                    self._items.append(_Font_numeric_Field( 15, y, 250, p[0], key, attribute='fontsize', name='FONT SIZE' ))
                    y += 30
                    self._items.append(_Inheritance_selection_menu( 70, y, p=p[0], f=key, attribute='fontsize', source=self._partition))
                    y += 15
                    
                    self._items.append(_Font_numeric_Field( 15, y, 250, p[0], key, attribute='tracking', name='TRACKING' ))
                    y += 30
                    self._items.append(_Inheritance_selection_menu( 70, y, p=p[0], f=key, attribute='tracking', source=self._partition))
                    y += 30
                        
        elif self._tab == 'paragraph':
            self._items.append(_Paragraph_style_menu( 15, y, 250, p[0], name='RENAME CLASS', source=self._partition))
            y += 45
            
            self._items.append(_Paragraph_numeric_Field( 15, y, 250, p[0], attribute='leading', name='LEADING' ))
            y += 30
            self._items.append(_Paragraph_inheritance_menu( 70, y, p=p[0], attribute='leading', source=self._partition))
            y += 15
            
            self._items.append(_Paragraph_numeric_Field( 15, y, 250, p[0], attribute='margin_bottom', name='BOTTOM MARGIN' ))
            y += 30
            self._items.append(_Paragraph_inheritance_menu( 70, y, p=p[0], attribute='margin_bottom', source=self._partition))
            y += 15

            self._items.append(_Paragraph_checkbox( 15, y + 15, 100, p[0], attribute='hyphenate', name='HYPHENATE' ))
            y += 30
            self._items.append(_Paragraph_inheritance_menu( 70, y, p=p[0], attribute='hyphenate', source=self._partition))
            y += 15

        elif self._tab == 'page':
            self._items.append(kookies.Integer_field( 15, y, 250, 
                        str(penclick.page.WIDTH), 
                        callback = penclick.page.set_width,
                        name = 'WIDTH' ))
            
            y += 45
            self._items.append(kookies.Integer_field( 15, y, 250, 
                        str(penclick.page.HEIGHT), 
                        callback = penclick.page.set_height,
                        name = 'HEIGHT' ))

        self._stack()

    def _reconstruct_channel_properties(self):
        # ALWAYS REQUIRES CALL TO _stack()
        c = meredith.mipsy.C()
        
        self._items = [self._tabstrip]
        self._active_box_i = None
        self._hover_box_ij = (None, None)
        
        y = 145
        
        self._items.append(kookies.Heading( 15, 90, 250, 30, 'Channel ' + str(c), upper=True))
        
        if self._tab == 'channels':
            if c is not None:
                self._items.append(kookies.Integer_field( 15, y, 250, 
                        str(meredith.mipsy.tracts[0].channels.channels[c].page), 
                        callback = meredith.mipsy.change_channel_page, 
                        params = (c,),
                        name = 'PAGE' ))
                y += 30
            
        self._stack()
        
    def _swap_reconstruct(self, to):
        width = 140

        if to == 'text':
            tabs = (('page', 'M'), ('paragraph', 'P'), ('font', 'F'), ('', '?'))
            default = 1
            self._tabstrip = kookies.Tabs( (constants.window.get_h() - constants.UI[self._partition] - width)//2 , 50, width, 30, default=default, callback=self._tab_switch, signals=tabs)
            self._tab = tabs[default][0]
            self._reconstruct = self._reconstruct_text_properties

        elif to == 'channels':
            tabs = (('channels', 'C'), ('', '?'))
            default = 0
            self._tabstrip = kookies.Tabs( (constants.window.get_h() - constants.UI[self._partition] - width)//2 , 50, width, 30, default=default, callback=self._tab_switch, signals=tabs)
            self._tab = tabs[default][0]
            self._reconstruct = self._reconstruct_channel_properties
        
        self._reconstruct()


klossy = Properties(tabs = (('page', 'M'), ('paragraph', 'P'), ('font', 'F'), ('', '?')), partition=1 )

