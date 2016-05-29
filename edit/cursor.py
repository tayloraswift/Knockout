from itertools import chain

from meredith.datablocks import DOCUMENT
from meredith.elements import PosFontpost, NegFontpost

from IO.tree import serialize, deserialize

from edit.wonder import words
from edit.text import expand_cursors_word

def address(box, path):
    for i in path:
        box = box.content[i]
    return box

_zeros = {'<fc/>', '<fo/>', '\t'}

class PlaneCursor(object):
    def __init__(self, plane_address, i, j):
        try:
            self._set_plane(address(DOCUMENT, plane_address), plane_address)
        except IndexError:
            plane_address = [0]
            i = (0,)
            j = (0,)
            self._set_plane(address(DOCUMENT, plane_address), plane_address)
        self.i = i
        self.j = j
        self.section = DOCUMENT.content[plane_address[0]]
        
        self.PG = 0 # stopgap
    
    def _set_plane(self, PLANE, plane_address):
        if not type(PLANE).plane:
            raise IndexError('Selected box is not a plane')
        self.PLANE = PLANE
        self.plane_address = plane_address
        self._blocks = self.PLANE.content

    ## TARGETING SYSTEM ##
    
    def _to_c_global(self, x, y):
        S = self.section
        c, p = S['frames'].which(x, y, 20)
        if c is None:
            # try other sections
            for s, section in (ss for ss in enumerate(DOCUMENT.content) if ss[0] is not S): 
                c, _p = section['frames'].which(x, y, 20)
                if c is not None:
                    self.section = section
                    self.plane_address[0] = s
                    self.PG = _p
                    x, y = DOCUMENT.normalize_XY(x, y, _p)
                    return x, section['frames'].y2u(y, c)
            
            c = self.PLANE.where(self.i)[1]['c']
        else:
            self.PG = p
        x, y = DOCUMENT.normalize_XY(x, y, self.PG)
        return x, self.section['frames'].y2u(y, c)

    def _to_c_local(self, x, y):
        c, p = self.section['frames'].which(x, y, 20)
        if c is None:
            c = self.PLANE.where(self.j)[1]['c']
        else:
            self.PG = p
        x, y = DOCUMENT.normalize_XY(x, y, self.PG)
        return x, self.section['frames'].y2u(y, c)
    
    def _next_textfacing(self, j, direction):
        if direction:
            i, block = next((i, block) for i, block in enumerate(self._blocks[j:]) if type(block).textfacing)
            return j + i, 0
        else:
            i, block = next((i, block) for i, block in enumerate(self._blocks[j::-1]) if type(block).textfacing)
            j2 = len(block.content)
            return j - i, j2
    
    def target(self, x, y):
        x, u = self._to_c_global(x, y)
        
        address, stack = zip( * self.section.which(x, u) )
        address_i, plane = next((i, box) for i, box in enumerate(chain(reversed(stack), (self.section,))) if box is not None and type(box).plane)
        address_i = len(address) - address_i
        if plane is not self.PLANE:
            self._set_plane(plane, [self.plane_address[0]] + list(address[:address_i]))
        
        if stack[-1] is None:
            self.i = address[-2:]
        else:
            self.i = (address[-1],)
        self.j = self.i

    def target_select(self, x, y):
        self._target_shallow( * self._to_c_local(x, y) )
    
    def _target_shallow(self, x, u):
        j, *_ = zip( * self.PLANE.which(x, u, len(self.i)) )
        if len(j) < len(self.i):
            self.j = self._next_textfacing(j[0], j < self.i)
        else:
            self.j = j
    
    def hop(self, direction):
        if len(self.i) == 2:
            l, line, glyph = self._blocks[self.i[0]].where((self.i[1],))
            self._target_shallow(line['x'] + glyph[1], line['u'] + (direction - 0.5)*line['leading'])
            self.i = self.j
        else:
            self.i = self.increment_cursor((self.i[0] + direction,), 0, True)
            self.j = self.i
    
    def home_end(self, direction):
        if len(self.i) == 2:
            l, line, G = self._blocks[self.i[0]].where((self.i[1],))
            if direction:
                i = (self.i[0], line['j'] - 1)
            else:
                i = (self.i[0], line['i'])
            self.i = i
            self.j = i
        else:
            self.hop(2*direction - 1)
    ## TEXT OPERATIONS ##
    
    def _sort_cursors(self):
        if self.i > self.j:
            self.i, self.j = self.j, self.i
    
    def increment_cursor(self, a, da, clamp=False):
        a = list(a)
        if len(a) == 2:
            a[1] += da
            if a[1] < 0:
                if a[0] > 0:
                    a[0] -= 1
                    a[1] = len(self._blocks[a[0]].content)
                else:
                    a = [0, 0]

            elif a[1] > len(self._blocks[a[0]].content):
                if a[0] < len(self._blocks) - 1:
                    a[0] += 1
                    a[1] = 0
                else:
                    a = [len(self._blocks) - 1, len(self._blocks[a[0]].content)]
        else:
            a[0] = min(len(self._blocks) - clamp, max(0, a[0] + da))
        return tuple(a)
        
    def delete(self, da=0, db=0, nolayout=False):
        self._sort_cursors()
        
        a = self.increment_cursor(self.i, da, not nolayout)
        b = self.increment_cursor(self.j, db, not nolayout)
        
        if len(a) == 2:
            affected = self._blocks[a[0]:b[0] + 1]
            if len(affected) == 1:
                affected[0].delete(a[1], b[1])
            else:
                a_end = len(self._blocks[a[0]].content)
                affected[0].delete(a[1], a_end)
                affected[0].insert(a_end, affected[-1].content[b[1]:])
                self._blocks[a[0]:b[0] + 1] = affected[0:1]

        else:
            del self._blocks[a[0]:b[0]]

        self.i = a
        self.j = self.i
        
        if not nolayout:
            self._relayout()
    
    def insert_chars(self, text):
        if len(self.i) == 2:
            if self.i != self.j:
                self.delete(nolayout=True)
            self._blocks[self.i[0]].insert(self.i[1], text)
            self.i = (self.i[0], self.i[1] + len(text))
            self.j = self.i
            self._relayout()
    
    def insert(self, blocks):
        if self.i != self.j:
            self.delete(nolayout=True)

        if len(self.i) == 2:
            affected = [self._blocks[self.i[0]]]
            
            if not type(blocks[-1]).textfacing: # if the block does not have text in .content
                blocks += [affected[0].copy_empty()]
            
            if len(blocks) == 1 and type(blocks[0]).textfacing:
                self.insert_chars(blocks[0].content)
            else:
                after_cut = affected[0].content[self.i[1]:]
                a_end = self.i[1] + len(after_cut)
                affected[0].delete(self.i[1], a_end)
                
                # attach blocks
                affected[0].insert(self.i[1], blocks[0].content)
                affected.extend(blocks[1:])
                i_end = len(blocks[-1].content)
                affected[-1].insert(i_end, after_cut)
                
                self._blocks[self.i[0] : self.i[0] + 1] = affected
                
                self._relayout() # relayout before cursor movement
                
                self.i = (self.i[0] + len(affected) - 1, i_end)
                self.j = self.i
        else:
            self._blocks[self.i[0]:self.i[0]] = blocks
            self._relayout()
            self.i = (self.i[0] + len(blocks),)
            self.j = self.i
    
    def bridge(self, tag, sign):
        if self.i == self.j and len(self.i) == 2:
            if sign:
                self.insert_chars([PosFontpost({'class': tag})])
            else:
                self.insert_chars([NegFontpost({'class': tag})])
            return True
        else:
            signargs = PosFontpost({'class': tag}), NegFontpost({'class': tag}), sign
            self._sort_cursors()
            if len(self.i) == 2:
                affected = self._blocks[self.i[0]:self.j[0] + 1]
                if len(affected) == 1:
                    activity, I, J = affected[0].bridge(self.i[1], self.j[1], * signargs )
                else:
                    begin, *middle, end = affected
                    a1, I, _ = begin.bridge(self.i[1], len(begin.content), * signargs)
                    aM = any(block.bridge(0, len(block.content), * signargs)[0] for block in middle)
                    a2, _, J = end.bridge(0, self.j[1], * signargs)
                    activity = a1 or aM or a2
                if activity:
                    self.i = (self.i[0], I)
                    self.j = (self.j[0], J)

            else:
                middle = self._blocks[self.i[0]:self.j[0]]
                activity = any(block.bridge(0, len(block.content), * signargs)[0] for block in middle)

            if activity:
                self._relayout()   
                return True
            else:
                return False
    
    def _relayout(self):
        if self.PLANE is self.section:
            self.section.layout(b=self.i[0], cascade=True)
        else:
            self.section.layout(b=self.plane_address[1], cascade=True)
    
    def run_stats(self, spell=False):
        self.word_total = sum(block.run_stats(spell) for block in self._blocks)
    
    ## IN/OUT ##
    
    def copy_selection(self):
        P = tuple(self.plane_address)
        if self.i > self.j:
            A = P + self.j
            B = P + self.i
        else:
            A = P + self.i
            B = P + self.j

        if A[:-1] == B[:-1]:
            base = address(DOCUMENT, A[:-1]).content
            return serialize(base[A[-1]:B[-1]])
        elif A[:-2] == B[:-2]:
            base = address(DOCUMENT, A[:-2]).content
            return serialize(base[A[-2]:B[-2] + 1], trim=(A[-1], B[-1]))
    
    def paste(self, L):
        self.insert(deserialize(L, fragment=True))
    
    ## NON-SPATIAL SELECTION TOOLS ##
    
    def expand_cursors_word(self):
        if len(self.i) == 2:
            a, b = expand_cursors_word(self._blocks[self.i[0]].content, self.i[1])
            self.i = (self.i[0], a)
            self.j = (self.i[0], b)
        else:
            self.j = (self.i[0] + 1,)

    def expand_cursors(self):
        self._sort_cursors()
        
        if len(self.i) == 2:
            pb = len(self._blocks[self.j[0]].content)
            if self.i[1] == 0 and self.j[1] == pb:
                self.i = (0, 0)
                self.j = (len(self._blocks) - 1, len(self._blocks[-1].content))
            else:
                self.i = (self.i[0], 0)
                self.j = (self.j[0], pb)
        else:
            self.i = (0,)
            self.j = (len(self._blocks),)
    
    ## CONTEXT INDICATORS ##
    
    def char(self, i, offset=0):
        try:
            ii = i[1] + offset
            if ii < 0:
                return None
            else:
                return self._blocks[i[0]].content[ii]
        except IndexError:
            return None
    
    def at(self):
        try:
            return address(self.PLANE, self.i)
        except IndexError:
            return None
    
    def paint_current_selection(self):
        i, j = sorted((self.i, self.j))
        double = len(i) == 2
        if double:
            signs = (str(self.char(i, -1)) in _zeros, str(self.char(i)) in _zeros) , (str(self.char(j, -1)) in _zeros, str(self.char(j)) in _zeros)
        else:
            signs = (False, False), (False, False)
        lit = self._blocks[i[0]: j[0] + 1]
        bounds = [[-1, -2] for b in lit]
        if double:
            bounds[0][0] = i[1]
            bounds[-1][1] = j[1]
        else:
            bounds[-1][1] = -1
        return list(chain.from_iterable(block.highlight( * bound ) for bound, block in zip(bounds, lit))), signs
    
    def styling_at(self):
        try:
            l, line, glyph = self.PLANE.where(self.i)
            return line['BLOCK'], glyph[3]
        except IndexError:
            return self._blocks[-1], None
