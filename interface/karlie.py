from bisect import bisect
from itertools import chain

from state import constants, noticeboard

from interface import kookies, fields, contents, ui, source

from fonts import common_features

from meredith.styles import Blockstyle

from IO import un

def _Z_state(N, A, layer):
    # test for definition
    if A in N.attrs:
        # test for stack membership
        if N in layer.members:
            # test for stack visibility
            if N is layer.Z[A]:
                return 3, '' # defined, in effect
            else:
                return 2, '' # defined, but overriden
        else:   
            return 1, '' # defined, but not applicable
    else:
        last = layer.Z[A]
        return - (last.isbase), last.attrs[A] # undefined, unapplicable

def _stack_row(i, row, y, gap, width, node, get_layer, refresh):
    width += 10
    divisions = [int(r[0] * width) for r in row]
    divisions = zip(divisions, chain(divisions[1:], (width,)), row)
    return _columns([TYPE(15 + a    , y + i*gap, b - a - 10, 
                            node    = node, 
                            A       = A, 
                            Z       = lambda N, A: _Z_state(N, A, get_layer()),
                            refresh = refresh,
                            name    = name) for a, b, (_, TYPE, A, name) in divisions])

def _stack_properties( * I ):
    * I , L = I
    return chain.from_iterable(_stack_row(i, row, * I ) for i, row in enumerate(L))

class _MULTI_COLUMN(object):
    def __init__(self, * args):
        BB = [W.bounding_box() for W in args]
        self.partitions = [(BB[i][1] + BB[i + 1][0]) // 2 for i in range(len(BB) - 1)]
        self.y_bottom = max((B[3] for B in BB))
        
        self.draw = lambda cr: None
        self.read = lambda: None

def _columns(columns):
    columns = list(columns)
    return [_MULTI_COLUMN( * columns), * columns]

# do not instantiate directly, requires a _reconstruct
class _Properties_panel(ui.Cell):
    def __init__(self, KT, context, partition=1):
        self.KT         = KT
        self.context    = context
        
        self.width      = None
        self.height     = None
        self._partition = partition
        self._swap_reconstruct(KT.VIEW.mode)
        self._scroll_anchor = False

    def shortcuts(self):
        pass
    
    def resize(self, h, k):
        self.height = k
        if h != self.width:
            self.width = h
            self._KW = h - 50
            self._reconstruct()

    def _tab_switch(self, name):
        if self._tab != name:
            self._dy = 0
            self._tab = name
            self._reconstruct()
        
    def _stack(self, padding=0):
        self._rows = [item.y_bottom for item in self._items]
        try:
            self._total_height = self._items[-1].y_bottom + padding
        except IndexError:
            self._total_height = 100 + padding

    def _stack_bisect(self, x, y):
        i = bisect(self._rows, y)
        try:
            item = self._items[i]
        except IndexError:
            i -= 1
            try:
                item = self._items[i]
            except IndexError:
                return kookies.Null
        
        if isinstance(item, _MULTI_COLUMN):
            return self._items[i + bisect(item.partitions, x) + 1]
        else:
            return item

    def _y_incr(self):
        return self._items[-1].y_bottom

    def refresh(self):
        meredith.mipsy.recalculate_all() # must come before because it rewrites all the paragraph styles
        self._reconstruct()
    
    def _synchronize(self):
        self.context.update()
        for item in self._items:
            item.read()
        self._HI.read()
    
    def _style_synchronize(self):
        self.context.update_force()
        for item in self._items:
            item.read()
        self._HI.read()
        
    def render(self, cr):
        k = self.height
        width = self.width
        # DRAW BACKGROUND
        cr.rectangle(0, 0, width, k)
        cr.set_source_rgb(1, 1, 1)
        cr.fill()
        
        # check if entries need restacking
        ref, mode = noticeboard.refresh_properties_type.should_refresh()
        if ref:
            self._swap_reconstruct(mode)
            self._reconstruct()
        elif self._tab in self.context.changed:
            self._reconstruct()
            if self._tab == 'character':
                self._dy = 0
        
        hover_box = self._hover_box_ij[0]

        cr.save()
        cr.translate(0, self._dy)
        for entry in self._items:
            if entry is hover_box:
                entry.draw(cr, hover=self._hover_box_ij)
            else:
                entry.draw(cr)
        
        cr.restore()

        # tabstrip
        cr.rectangle(0, 0, width, 90)
        cr.set_source_rgb(1, 1, 1)
        cr.fill()

        cr.save()
        cr.translate(width // 2, 0)
        if hover_box is self._tabstrip:
            self._tabstrip.draw(cr, hover=self._hover_box_ij)
        else:
            self._tabstrip.draw(cr)
        cr.restore()
        self._HI.draw(cr)
        
        # scrollbar
        if self._total_height > k:
            scrollbarheight = k / self._total_height * (k - 100)
            top = -self._dy / self._total_height * (k - 100)
            cr.rectangle(width - 10, top + 90, 3, scrollbarheight)
            cr.set_source_rgba(0, 0, 0, 0.2 + 0.1*self._scroll_anchor)
            cr.fill()
        
        # DRAW SEPARATOR
        cr.rectangle(0, 0, 
                2, 
                k)
        cr.set_source_rgb(0.9, 0.9, 0.9)
        cr.fill()
    
    def key_input(self, name, char):
        box = self._active_box_i
        if box is not None:
            if type(box) is source.Rose_garden:
                cp = box.type_box(name, char)
                self._stack(20)
                return cp
            elif name == 'Return':
                box.defocus()
                self._active_box_i = None
            else:
                return box.type_box(name, char)
    
    def press(self, x, y, char):
        b = None
        if y < 90:
            box = self._tabstrip
            x -= self.width // 2
        elif x > self.width - 15:
            self._scroll_anchor = True
            return
        else:
            y -= self._dy
            box = self._stack_bisect(x, y)

        if box.is_over(x, y):
            box.focus(x, y)
            b = box

        # defocus the other box, if applicable
        if b is None or b is not self._active_box_i:
            self.exit()
            self._active_box_i = b

    def dpress(self):
        if self._active_box_i is not None:
            self._active_box_i.dpress()
    
    def press_motion(self, x, y):
        yn = y - self._dy
        if self._scroll_anchor:
            dy = -(y - 90 - self.height / self._total_height * (self.height - 100) * 0.5 ) * self._total_height / (self.height - 100)
            dy = min(0, max(-self._total_height + self.height, dy))
            if dy != self._dy:
                self._dy = dy
                noticeboard.redraw_klossy.push_change()
        elif self._active_box_i is not None and self._active_box_i.focus_drag(x, yn):
            noticeboard.redraw_klossy.push_change()
    
    def release(self, x, y):
        self._scroll_anchor = False
    
    def exit(self):
        if self._active_box_i is not None:
            self._active_box_i.defocus()
            self._active_box_i = None
    
    def hover(self, x, y, hovered=[None]):
        if y < 90:
            box = self._tabstrip
            x -= self.width // 2
            SA = False
        elif x > self.width - 15:
            SA = -1
            box = kookies.Null
        else:
            y -= self._dy
            box = self._stack_bisect(x, y)
            SA = False
            
        if box.is_over_hover(x, y):
            self._hover_box_ij = (box, box.hover(x, y))
        else:
            self._hover_box_ij = (None, None)

        if hovered[0] != self._hover_box_ij:
            hovered[0] = self._hover_box_ij
            noticeboard.redraw_klossy.push_change()
            self._scroll_anchor = SA
        elif self._scroll_anchor != SA:
            self._scroll_anchor = SA
            noticeboard.redraw_klossy.push_change()

    def scroll(self, x, y, char):
        if y > 0:
            if self._dy >= -self._total_height + self.height:
                self._dy -= 22
                noticeboard.redraw_klossy.push_change()
        elif self._dy <= -22:
            self._dy += 22
            noticeboard.redraw_klossy.push_change()

    def _reconstruct(self):
        self.context.done(self._tab)
        self._heading = lambda: ''
        self._items = []
        self._active_box_i = None
        self._hover_box_ij = (None, None)
        
        self._panel(y=110, KW=self._KW)
        self._stack(20)
        self._HI = kookies.Heading(15, 60, self._KW, 30, self._heading, font=('title',), fontsize=18, upper=True)

def _print_counter(node):
    items = [k['name'] if v == 1 else k['name'] + ' (' + str(v) + ')' for k, v in node['class'].items() if v]
    if items:
        return ', '.join(items)
    else:
        return '{none}'

def _print_tcounter(node):
    return _print_counter(node), str(node['textstyle'])

def _print_bcounter(node):
    if type(node) is Blockstyle:
        return _print_counter(node), '▯' * len(node.content)
    else:
        return 'ELEMENT',

_BLOCK_PROPERTIES =[[(0, fields.Blank_space , 'leading'         , 'LEADING'      )],
                    [(0, fields.Blank_space , 'language'        , 'LANGUAGE'     )],
                    [(0, fields.Blank_space , 'align'           , 'ALIGN'        ), (0.6, fields.Blank_space, 'align_to'        , 'ALIGN ON'      )],
                    [(0, fields.Blank_space , 'indent'          , 'INDENT'       ), (0.6, fields.Blank_space, 'indent_range'    , 'FOR LINES'     )],
                    [(0, fields.Blank_space , 'margin_left'     , 'SPACE LEFT'   ), (0.5, fields.Blank_space, 'margin_right'    , 'SPACE RIGHT'   )],
                    [(0, fields.Blank_space , 'margin_top'      , 'SPACE BEFORE' ), (0.5, fields.Blank_space, 'margin_bottom'   , 'SPACE AFTER'   )],
                    [(0, fields.Checkbox    , 'hyphenate'       , 'HYPHENATE'    )],
                    [(0, fields.Checkbox    , 'keep_together'   , 'KEEP TOGETHER'), (0.5, fields.Checkbox   , 'keep_with_next'  , 'KEEP WITH NEXT')],
                    [(0, fields.Blank_space , 'incr_place_value', 'INCREMENT'    ), (0.4, fields.Blank_space, 'incr_assign'     , 'BY'            )],
                    [(0, fields.Blank_space , 'show_count'      , 'COUNTER TEXT' ), (0.7, fields.Blank_space, 'counter_space'   , 'SPACE'         )],
                    ]

_TEXT_PROPERTIES = [[(0, fields.Blank_space , 'path'        , 'FONT FILE'       )],
                    [(0, fields.Blank_space , 'path_emoji'  , 'EMOJI FONT FILE' )],
                    [(0, fields.Blank_space , 'fontsize'    , 'FONT SIZE'       )],
                    [(0, fields.Blank_space , 'tracking'    , 'TRACKING'        )],
                    [(0, fields.Blank_space , 'shift'       , 'VERTICAL SHIFT'  )],
                    [(0, fields.Checkbox    , 'capitals'    , 'CAPITALS'        )],
                    [(0, fields.Blank_space , 'color'       , 'COLOR'           )]
                    ]

class Properties(_Properties_panel):
    def _text_panel(self, y, KW):
        if self._tab == 'font':
            if self.context.kbs is not None:
                self._heading = lambda: ', '.join(T['name'] for T in self.context.kbs['class'])
                
                self._items.append(contents.Ordered(15, y, KW,
                            node = self.context.kbs, 
                            context = self.context,
                            slot = 'kbm',
                            display = _print_tcounter))
                y = self._y_incr() + 20
                
                if self.context.kbm is not None:
                    self._items.append(fields.Counter_editor(15, y, KW, (125, 28),
                                superset = self.KT.TTAGS.content, 
                                node = self.context.kbm, 
                                A = 'class',
                                refresh = self._style_synchronize))
                    y = self._y_incr() + 20
                    
                    self._items.append(fields.Object_menu(15, y, KW,
                                supernode = self.KT.TSTYLES, 
                                partition = self._partition, 
                                node = self.context.kbm, 
                                A = 'textstyle', 
                                refresh = self._style_synchronize,
                                name = 'FONTSTYLE'))

                    TS = self.context.kbm['textstyle']
                    if TS is not None:
                        y += 55
                        props_args = 45, KW, TS, lambda: self.context.ts, self.context.update_context
                        self._items.extend(_stack_properties(y, * props_args , _TEXT_PROPERTIES))
                        y += 45*len(_TEXT_PROPERTIES) + 10
                        
                        it_common_features = iter(common_features)
                        _OT_TEXT_PROPERTIES = [[(f / len(FF), fields.Small_int, F, F.upper()) for f, F in enumerate(FF)] 
                                                for FF in zip( * (it_common_features,) * max(KW // 145, 1) )]
                        self._items.extend(_stack_properties(y, * props_args , _OT_TEXT_PROPERTIES))
        
        elif self._tab == 'paragraph':
            self._heading = lambda: ', '.join(T['name'] if V == 1 else T['name'] + ' (' + str(V) + ')' for T, V in self.context.bk['class'].items() if V)
            
            self._items.append(fields.Counter_editor(15, y, KW, (125, 28),
                        superset = self.KT.BTAGS.content,
                        node = self.context.bk,
                        A = 'class',
                        refresh = self._style_synchronize))
            y = self._y_incr() + 20
            
            self._items.append(contents.Para_control_panel(15, y, KW, 
                    node = self.KT.BSTYLES, 
                    context = self.context, 
                    slot = 'kbs', 
                    display = _print_bcounter))
            y = self._y_incr() + 20
            
            if self.context.kbs is not None:
                self._items.append(fields.Counter_editor(15, y, KW, (125, 28),
                            superset = self.KT.BTAGS.content,
                            node = self.context.kbs,
                            A = 'class',
                            refresh = self._style_synchronize))
                y = self._y_incr() + 20
                
                self._items.extend(_stack_properties(y, 45, KW, self.context.kbs, lambda: self.context.bs, self.context.update_context, _BLOCK_PROPERTIES))
                y += 45*len(_BLOCK_PROPERTIES)
                
        
        elif self._tab == 'tags':
            self._heading = lambda: 'Document tags'
            
            self._items.append(contents.Ordered(15, y, KW - 50,
                        node = self.KT.BTAGS, 
                        context = self.context, 
                        slot = 'kbt', 
                        display = lambda l: l['name']))
            
            y = self._y_incr() + 20
            
            if self.context.kbt is not None:
                self._items.append(fields.Blank_space(15, y, KW, 
                        node = self.context.kbt,
                        A = 'name', 
                        refresh=self._synchronize, 
                        name='TAG NAME', no_z=True))
            y += 80

            self._items.append(contents.Ordered(15, y, KW - 50,
                        node = self.KT.TTAGS, 
                        context = self.context, 
                        slot = 'ktt', 
                        display = lambda l: l['name']))
            
            y = self._y_incr() + 20
            
            if self.context.ktt is not None:
                self._items.append(fields.Blank_space(15, y, KW, 
                        node = self.context.ktt,
                        A = 'name', 
                        refresh=self._synchronize, 
                        name='TAG NAME', no_z=True))
            
        elif self._tab == 'page':
            self._heading = lambda: 'Document pages'
            
            self._items.append(fields.Blank_space(15, y, KW, 
                        node = self.KT.BODY,
                        A = 'width',
                        name = 'WIDTH' ))
            
            y += 45
            self._items.append(fields.Blank_space(15, y, KW,
                        node = self.KT.BODY,
                        A = 'height',
                        name = 'HEIGHT' ))
            y += 45
            
            self._items.append(fields.Blank_space(15, y, KW, 
                        node=self.KT.filedata, 
                        A='filepath', 
                        name='SAVE AS'))
            y += 30
        
        elif self._tab == 'character':
            self._heading = lambda: 'Element source'
            
            self._items.append(source.Rose_garden(10, y, width=KW + 10, 
                    context = self.context,
                    save = un.history.save))
            y = self._y_incr() + 20
        return y

    def _frames_panel(self, y, KW):
        if self._tab == 'frames':
            c = self.context.c
            self._heading = lambda: 'Frame ' + str(c)
            if c is not None:
                self._items.append(fields.Blank_space(15, y, KW, 
                        node = self.KT.SCURSOR.section['frames'][c],
                        A = 'page', 
                        name = 'PAGE',
                        override_in = lambda N, A: N.page))
                y += 30

        if self._tab == 'section':
            section = self.context.sc
            self._heading = lambda: 'Section ' + str(section)
            if section is not None:
                self._items.append(fields.Blank_space(15, y, KW, 
                        node = self.KT.SCURSOR.section,
                        A = 'repeat', 
                        name = 'REPEAT'))
                y += 30
        
        return y
        
    def _swap_reconstruct(self, to):
        if to == 'text':
            tabs = (('page', 'M'), ('tags', 'T'), ('paragraph', 'P'), ('font', 'F'), ('character', 'C'))
            default = 2
            self._panel = self._text_panel

        elif to == 'frames':
            tabs = (('section', 'S'), ('frames', 'F'),)
            default = 1
            self._panel = self._frames_panel
        
        else:
            tabs = (('render', 'R'),)
            default = 0
            self._panel = lambda y, KW: 13
        
        self._tabstrip = kookies.Tabs(0, 20, 32, 30, default=default, callback=self._tab_switch, signals=tabs)
        self._tab = tabs[default][0]
        self._dy = 0
