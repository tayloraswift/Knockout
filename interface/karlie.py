import bisect

from state import constants, contexts
from state import noticeboard

from fonts import styles

from interface import kookies, caramel, ui, ops

from model import meredith, penclick
from model import un

class _Font_file_Field(kookies.Blank_space):
    def __init__(self, x, y, width, after, name=None):
        kookies.Blank_space.__init__(self, x, y, width, callback = ops.Fontstyle.f_set_attribute, 
                value_acquire = self._value_acquire, 
                params=('path',), 
                before=un.history.save, 
                after=after, name=name)

    def _value_acquire(self, A):
        self.broken = not contexts.Fontstyle.fontstyle.u_path_valid
        return contexts.Fontstyle.fontstyle.u_path

def _create_f_field(TYPE, x, y, width, attribute, after, name='', **kwargs):
    return TYPE(x, y, width,
            callback= ops.Fontstyle.f_set_attribute, 
            value_acquire = lambda A: getattr(contexts.Fontstyle.fontstyle, 'u_' + A),
            params = (attribute,), 
            before=un.history.save,
            after=after,
            name=name, **kwargs)
            
def _create_p_field(TYPE, x, y, width, attribute, after, name='', **kwargs):
    return TYPE(x, y, width,
            callback = ops.Parastyle.p_set_attribute, 
            value_acquire= lambda A: getattr(contexts.Parastyle.parastyle, 'u_' + A),
            params = (attribute,), 
            before=un.history.save,
            after=after,
            name=name, **kwargs)

def _create_f_inherit(x, y, width, attribute, after, source=0):
    return kookies.Datablock_selection_menu(x, y, width=width, height=15, menu_callback = ops.Fontstyle.f_link_inheritance, 
            options_acquire = lambda: ((None, 'None'),) + tuple( (l, l.name) for l in sorted(styles.FONTSTYLES.values(), key=lambda k: k.name) ),
            value_acquire = lambda A: contexts.Fontstyle.fontstyle.read_inherit_name(A), 
            params = (attribute,),
            before = un.history.save, after=after,
            source=source)
            
def _create_p_inherit(x, y, width, attribute, after, source=0):
    return kookies.Datablock_selection_menu(x, y, width=width, height=15, menu_callback = ops.Parastyle.p_link_inheritance, 
            options_acquire = lambda: ((None, 'None'),) + tuple( (l, l.name) for l in sorted(styles.PARASTYLES.values(), key=lambda k: k.name) ),
            value_acquire = lambda A: contexts.Parastyle.parastyle.read_inherit_name(A), 
            params = (attribute,),
            before = un.history.save, after=after,
            source=source)

class _F_preview(kookies.Heading):
    def __init__(self, x, y, width, height, text, f):
        self._F = f
        self._text = text
        kookies.Heading.__init__(self, x, y, width, height, text, font=self._F, fontsize = 15)

    def _SYNCHRONIZE(self):
        del self._texts[0]
        self._add_static_text(self._x, self._y + 16, self._text, fontsize=15)

    def draw(self, cr, hover=(None, None)):
        cr.set_source_rgb(0,0,0)
        
        cr.set_font_size(15)
        cr.set_font_face(self.font.u_font)
        cr.show_glyphs(self._texts[0])


class _TWO_COLUMN(object):
    def __init__(self, left, right):
        lbb = left.bounding_box()
        rbb = right.bounding_box()
        self.partition = (lbb[1] + rbb[0]) // 2
        self.y = max((lbb[3], rbb[3]))
        
        self.draw = lambda cr: None
        self._SYNCHRONIZE = lambda: None

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

    def _stack_bisect(self, x, y):
        i = bisect.bisect(self._rows, y)
        try:
            item = self._items[i]
        except IndexError:
            i -= 1
            item = self._items[i]
        
        if isinstance(item, _TWO_COLUMN):
            if x < item.partition:
                i += 1
            else:
                i += 2
        return i

    def refresh(self):
        meredith.mipsy.recalculate_all() # must come before because it rewrites all the paragraph styles
        self._reconstruct()
    
    def synchronize(self):
        for item in self._items:
            item._SYNCHRONIZE()
        
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
                self._items[self._active_box_i].defocus()
                self._active_box_i = None
            else:
                return self._items[self._active_box_i].type_box(name, char)
    
    def press(self, x, y, char):

        b = None
        bb = self._stack_bisect(x, y)

        if self._items[bb].is_over(x, y):
            self._items[bb].focus(x, y)
            b = bb

        # defocus the other box, if applicable
        if b is None or b != self._active_box_i:
            if self._active_box_i is not None:
                self._items[self._active_box_i].defocus()
            self._active_box_i = b
            
    def press_motion(self, x, y):
        if self._active_box_i is not None and self._items[self._active_box_i].focus_drag(x):
            noticeboard.redraw_klossy.push_change()
    
    def hover(self, x, y, hovered=[None]):
    
        self._hover_box_ij = (None, None)
        
        bb = self._stack_bisect(x, y)

        if self._items[bb].is_over_hover(x, y):
            self._hover_box_ij = (bb, self._items[bb].hover(x, y))

        if hovered[0] != self._hover_box_ij:
            hovered[0] = self._hover_box_ij
            noticeboard.redraw_klossy.push_change()


class Properties(_Properties_panel):
    def __init__(self, tabs = (), default=0, partition=1 ):
        self._reconstruct = self._reconstruct_text_properties
        
        _Properties_panel.__init__(self, tabs = tabs, default=default, partition=partition) 

    def _reconstruct_text_properties(self):
        # ALWAYS REQUIRES CALL TO _stack()
        print('reconstruct')

        p = contexts.Text.paragraph
        
        self._items = [self._tabstrip]
        self._active_box_i = None
        self._hover_box_ij = (None, None)
        
        y = 145
        
        self._items.append(kookies.Heading( 15, 90, 250, 30, p[1].name, upper=True))
               
        if self._tab == 'font':

            self._items.append(kookies.Object_menu(15, y, 250, 
                        value_acquire = lambda: contexts.Keymap.keymap, 
                        value_push = ops.Parastyle.link_keymap, 
                        library = styles.MAPS, 
                        before=un.history.save, after = self.refresh, name='RENAME KEYMAP', source=self._partition))
            y += 45
            
            self._items.append(kookies.Unorderable(15, y, 250, 250,
                        datablock = contexts.Keymap.keymap, 
                        protect = set(((),)),
                        display = lambda l: ', '.join(l) if l else '{none}',
                        before=un.history.save, after= lambda: (contexts.Fontstyle.update(), self.refresh())))
            
            y += 250
            self._items.append(kookies.Binary_table(15, y, 250, 100, (80, 26), 
                        callback= ops.Keymap.remap_active,
                        states_acquire = lambda: [ (T.name in set(contexts.Keymap.keymap.active), T.name ) for T in styles.TAGLIST.ordered ], 
                        before = un.history.save, after = self.refresh))
            
            y += 100
            
            key = contexts.Fontstyle.fontstyle
            if key is None:
                self._items.append(kookies.New_object_menu(15, y, 250,
                            value_push = ops.Keymap.link_fontstyle, 
                            library = styles.FONTSTYLES, 
                            before = un.history.save, after = self.refresh, name='FONTSTYLE', source=self._partition))

            else:
                self._items.append(kookies.Object_menu(15, y, 250,
                            value_acquire = lambda: contexts.Fontstyle.fontstyle, 
                            value_push = ops.Keymap.link_fontstyle, 
                            library = styles.FONTSTYLES, 
                            before = un.history.save, after = self.refresh, name='FONTSTYLE', source=self._partition))

                y += 55

                self._items.append(_F_preview( 16, y, 250, 0, 'Preview  ( ' + key.name + ' )', key ))
                y += 30
                
                self._items.append(_Font_file_Field( 15, y, 250, after=self.synchronize, name='FONT FILE' ))
                y += 30
                self._items.append(_create_f_inherit( 15, y, width=250, attribute='path', after=self.synchronize, source=self._partition))
                y += 15
                
                self._items.append(_create_f_field(kookies.Numeric_field, 15, y, 250, 'fontsize', after=self.synchronize, name='FONT SIZE') )

                y += 30
                self._items.append(_create_f_inherit( 15, y, width=250, attribute='fontsize', after=self.synchronize, source=self._partition))
                y += 15
                
                self._items.append(_create_f_field(kookies.Numeric_field, 15, y, 250, 'tracking', after=self.synchronize, name='TRACKING') )
                y += 30
                self._items.append(_create_f_inherit( 15, y, width=250, attribute='tracking', after=self.synchronize, source=self._partition))
                y += 30
                """
                g = fonts.TEXTURES[key]['pegs']
                self._items.append(kookies.Unordered( 15, y, 250, 100,
                        dict_acquire=lambda: fonts.PEGS[g],
                        new = lambda L: ('{new}', [0.13, 0.22]),
                        display = lambda l: str(l),
                        before=un.history.save, after=self._TURNOVER_WITH_REFRESH_F, after_delete=self._TURNOVER_WITH_REFRESH_F))
                y += 100
                if '_ACTIVE' in fonts.PEGS[g]:
                    self._items.append(kookies.Selection_menu(15, y, width=250, height=15, menu_callback = plane.pegs_push_tag, 
                                options_acquire=lambda: (('{new}', 'None'),) + tuple((k, k) for k in plane.tags_and_subtags(p[0])), 
                                value_acquire = lambda G: fonts.PEGS[G]['_ACTIVE'], 
                                params = (g,),
                                before = un.history.save, after=self._TURNOVER_WITH_REFRESH_F,
                                source=self._partition))
                    y += 45
                    """
        elif self._tab == 'paragraph':

            self._items.append(kookies.Object_menu( 15, y, 250, 
                        value_acquire=lambda: p[1], 
                        value_push=ops.Text.link_parastyle, 
                        library=styles.PARASTYLES, 
                        params = (), before=un.history.save, after=self.refresh, name='RENAME CLASS', source=self._partition))
            y += 45
            
            self._items.append(_create_p_field(kookies.Numeric_field, 15, y, 250, 'leading', after=self.synchronize, name='LEADING') )
            y += 30
            
            self._items.append(_create_p_inherit(15, y, width=250, attribute='leading', after=self.synchronize, source=self._partition))
            
            y += 15
            _tc_ = [_create_p_field(kookies.Binomial_field, 15, y, 175, 'indent', after=self.synchronize, name='INDENT', letter='K'), 
                    _create_p_field(kookies.Enumerate_field, 200, y, 65, 'indent_range', after=self.synchronize, name='FOR LINES') ]
            self._items.append( _TWO_COLUMN( * _tc_))
            self._items += _tc_
            
            y += 45
            _tc_ = [_create_p_inherit(15, y, width=175, attribute='indent', after=self.synchronize, source=self._partition), 
                    _create_p_inherit(200, y, width=65, attribute='indent_range', after=self.synchronize, source=self._partition) ]
            self._items.append( _TWO_COLUMN( * _tc_))
            self._items += _tc_
            
            y += 15
            _tc_ = [_create_p_field(kookies.Numeric_field, 15, y, 120, 'margin_left', after=self.synchronize, name='LEFT MARGIN'),
                    _create_p_field(kookies.Numeric_field, 145, y, 120, 'margin_right', after=self.synchronize, name='RIGHT MARGIN')]
            self._items.append( _TWO_COLUMN( * _tc_))
            self._items += _tc_
            y += 45
            _tc_ = [_create_p_inherit( 15, y, width=120, attribute='margin_left', after=self.synchronize, source=self._partition), 
                    _create_p_inherit( 145, y, width=120, attribute='margin_right', after=self.synchronize, source=self._partition) ]
            self._items.append( _TWO_COLUMN( * _tc_))
            self._items += _tc_
            
            y += 15
            _tc_ = [_create_p_field(kookies.Numeric_field, 15, y, 120, 'margin_top', after=self.synchronize, name='TOP MARGIN'),
                    _create_p_field(kookies.Numeric_field, 145, y, 120, 'margin_bottom', after=self.synchronize, name='BOTTOM MARGIN')]
            self._items.append( _TWO_COLUMN( * _tc_))
            self._items += _tc_

            y += 45
            _tc_ = [_create_p_inherit( 15, y, width=120, attribute='margin_top', after=self.synchronize, source=self._partition), 
                    _create_p_inherit( 145, y, width=120, attribute='margin_bottom', after=self.synchronize, source=self._partition) ]
            self._items.append( _TWO_COLUMN( * _tc_))
            self._items += _tc_
            
            y += 15
            self._items.append(_create_p_field(kookies.Checkbox, 15, y + 15, 100, 'hyphenate', after=self.synchronize, name='HYPHENATE') )
            y += 30
            self._items.append(_create_p_inherit(15, y, width=250, attribute='hyphenate', after=self.refresh, source=self._partition))
            """
            y += 30
            self._items.append(kookies.Orderable( 15, y, 200, 180,
                        list_acquire=lambda: fonts.TAGS[fonts.paragraph_classes[p[0]]['tags']], 
                        new = lambda L: {'subtags': {}, 'collapse': False ,'exclusive': False, 'name': '{new}'},
                        display = lambda l: l['name'],
                        before=un.history.save, after=self.refresh ))
            y += 180
            self._items.append(kookies.Blank_space(15, y, width=250, 
                    callback=fonts.q_set, 
                    value_acquire=fonts.q_read, 
                    params = ('name', p[0]), before=un.history.save, after=self.synchronize, name='TAG NAME'))

            y += 45
            self._items.append(kookies.Checkbox( 15, y + 15, 100, callback=fonts.q_set, 
                            value_acquire = fonts.q_read, params = ('exclusive', p[0]),
                            before = un.history.save,
                            after = self._TURNOVER_WITH_RERENDER_P,
                            name = 'EXCLUSIVE') )
            y += 45

            self._items.append(kookies.Unordered( 15, y, 250, 100,
                        dict_acquire=lambda: fonts.q_read('subtags', p[0]) ,
                        new = lambda L: ('{new}', None),
                        display = lambda l: l,
                        before=un.history.save, after=self._TURNOVER_WITH_REFRESH_F, after_delete=self._TURNOVER_WITH_REFRESH_F))

            y += 100
            if fonts.q_read('subtags', p[0]):
                self._items.append(kookies.Blank_space(15, y, width=250, 
                        callback=plane.tags_push_subtag_name, 
                        value_acquire= lambda P: fonts.q_read('subtags', P)['_ACTIVE'], 
                        params = (p[0],), before=un.history.save, after=self.synchronize, name='SUBTAG NAME'))

                y += 45
                self._items.append(kookies.Checkbox( 15, y + 15, 100, callback=fonts.q_set, 
                                value_acquire = fonts.q_read, params = ('collapse', p[0]),
                                before = un.history.save,
                                after = self._TURNOVER_WITH_RERENDER_P,
                                name = 'COLLAPSE') )
            """
        elif self._tab == 'page':
            self._items.append(kookies.Integer_field( 15, y, 250, 
                        callback = penclick.page.set_width,
                        value_acquire = lambda: penclick.page.WIDTH,
                        name = 'WIDTH' ))
            
            y += 45
            self._items.append(kookies.Integer_field( 15, y, 250,
                        callback = penclick.page.set_height,
                        value_acquire = lambda: penclick.page.HEIGHT,
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
                        callback = meredith.mipsy.change_channel_page, 
                        params = (c,),
                        value_acquire = lambda C: str(meredith.mipsy.tracts[0].channels.channels[C].page),
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


klossy = Properties(tabs = (('page', 'M'), ('paragraph', 'P'), ('font', 'F'), ('', '?')), default=1, partition=1 )

