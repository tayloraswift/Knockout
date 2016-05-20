from itertools import chain

from model.wonder import words

from elements.datablocks import DOCUMENT

from edit.text import expand_cursors_word

def address(box, path):
    for i in path:
        box = box.content[i]
    if not type(box).plane:
        raise IndexError('Selected box is not a plane')
    return box

_zeros = {'<fc/>', '<fo/>', '\t'}

class PlaneCursor(object):
    def __init__(self, plane_address, i, j):
        self._set_plane(address(DOCUMENT, plane_address), plane_address)
        self.i = i
        self.j = j
        self.section = DOCUMENT.content[plane_address[0]]
        
        self.PG = 0 # stopgap
    
    def char(self, i, offset=0):
        try:
            return self._blocks[i[0]].content[max(0, i[1] + offset)]
        except IndexError:
            return None
    
    def _set_plane(self, PLANE, plane_address):
        self.PLANE = PLANE
        self.plane_address = plane_address
        self._blocks = self.PLANE.content
    
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

    # TARGETING SYSTEM
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
            
    def target(self, x, y):
        x, u = self._to_c_global(x, y)
        
        address, stack = zip( * self.section.which(x, u) )
        address_i, plane = next(enumerate(box for box in chain(reversed(stack), (self.section,)) if box is not None and type(box).plane))
        if plane is not self.PLANE:
            self._set_plane(plane, [self.plane_address[0]] + list(address[:address_i]))
        
        if stack[-1] is None:
            self.i = address[-2:]
        else:
            self.i = (address[-1],)
        self.j = self.i

    def target_select(self, x, y):
        x, u = self._to_c_local(x, y)
        self.j, *_ = zip( * self.PLANE.which(x, u, len(self.i)) )
    
    #############
    def _sort_cursors(self):
        if self.i > self.j:
            self.i, self.j = self.j, self.i
    
    def delete(self, da=0, db=0, nolayout=False):
        self._sort_cursors()
        
        a = list(self.i)
        b = list(self.j)
        a[-1] += da
        b[-1] += db
        
        if len(a) == 2:
            if a[1] < 0 < a[0]:
                a[0] -= 1
                a[1] = len(self._blocks[a[0]].content)

        if len(b) == 2:
            if b[1] > len(self._blocks[b[0]].content) and b[0] < len(self._blocks) - 1:
                b[0] += 1
                b[1] = 0
    
        if len(a) == 2:
            affected = self._blocks[a[0]:b[0] + 1]
            if len(affected) == 1:
                affected[0].delete(a[1], b[1])
            else:
                a_end = len(self._blocks[a[0]].content)
                affected[0].delete(a[1], a_end)
                affected[0].insert(affected[-1].content[b[1]:], a_end)
                self._blocks[a[0]:b[0] + 1] = affected[0:1]

        else:
            del self._blocks[a[0]:b[0]]

        self.i = tuple(a)
        self.j = self.i
        
        if not nolayout:
            self._relayout()
    
    def insert_chars(self, text):
        if len(self.i) == 2:
            if self.i != self.j:
                self.delete(nolayout=True)
            self._blocks[self.i[0]].insert(text, self.i[1])
            self.i = (self.i[0], self.i[1] + len(text))
            self.j = self.i
            self._relayout()
    
    def insert(self, blocks):
        if self.i != self.j:
            self.delete(nolayout=True)
        
        if len(blocks) > 1:
            affected = [self._blocks[self.i[0]]]
            outer_end = affected[0].content[self.i[1]:]
            a_end = self.i[1] + len(outer_end)
            affected[0].delete(self.i[1], a_end)
            
            # attach blocks
            affected[0].insert(blocks[0].content, self.i[1])
            affected.extend(blocks[1:])
            i_end = len(blocks[-1].content)
            affected[-1].insert(outer_end, 0)
            
            self._blocks[self.i[0] : self.i[0] + 1] = affected
            
            self._relayout() # relayout before cursor movement
            
            self.i = (self.i[0] + len(affected) - 1, i_end)
            self.j = self.i
        elif len(self.i) != 2:
            self._blocks[self.i[0]:self.i[0]] = blocks
            
            self._relayout()
            
            self.i = (self.i[0] + len(blocks),)
            self.j = self.i
        else:
            self.insert_chars(blocks[0].content)
    
    def _relayout(self):
        if self.PLANE is self.section:
            self.section.layout(self.i[0], True)
        else:
            self.section.layout(self.plane_address[1], True)
    
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
    ##
    
    def styling_at(self):
        l, line, glyph = self.PLANE.where(self.i)
        return line['BLOCK'], glyph[3]

    def run_stats(self, spell=False):
        word_total = 0
        for block in self._blocks:
            word_total += block.run_stats(spell)
        self.word_total = word_total
    """
    def bridge(self, tag, sign):
        S = self.take_selection() # also sorts cursors
        if S and '</p>' not in S:
            
            DA = 0
            
            I = self.i
            J = self.j

            P_1 = I - next(i for i, c in enumerate(self.text[I - 1::-1]) if type(c) is Paragraph)
            P_2 = J + self.text[J:].index('</p>') + 1

            if sign:
                CAP = (CloseFontpost, OpenFontpost)
                
                self.text.insert(P_1, CAP[0]({'class': tag}))
                DA += 1
                
                P_2 += 1
                I += 1
                J += 1
            else:
                CAP = (OpenFontpost, CloseFontpost)
            
            paragraph = self.text[P_1:P_2]
            
            # if selection falls on top of range
            if type(self.text[I - 1]) is CAP[0]:
                I -= next(i for i, c in enumerate(self.text[I - 2::-1]) if type(c) is not CAP[0]) + 1

            if type(self.text[J]) is CAP[1]:
                J += next(i for i, c in enumerate(self.text[J + 1:]) if type(c) is not CAP[1]) + 1

            ftag = OpenFontpost({'class': tag})['class']
            if sign:
                ftags = [(i + P_1, type(e)) for i, e in enumerate(paragraph) if type(e) in CAP and e.F is ftag] + [(P_2, CAP[1])] + [(None, None)]
            else:
                ftags = [(i + P_1, type(e)) for i, e in enumerate(paragraph) if type(e) in CAP and e.F is ftag] + [(None, None)]
            
            pairs = []
            for i in reversed(range(len(ftags) - 2)):
                if (ftags[i][1], ftags[i + 1][1]) == CAP:
                    pairs.append((ftags[i][0], ftags[i + 1][0]))
                    del ftags[i:i + 2]
            
            # ERROR CHECKING
            if ftags != [(None, None)]:
                print ('INVALID TAG SEQUENCE, REMNANTS: ' + str(ftags))
            
            instructions = []
            drift_i = 0
            drift_j = 0

            for pair in pairs:
                if pair[1] <= I or pair[0] >= J:
                    pass
                elif pair[0] >= I and pair[1] <= J:
                    instructions += [(pair[0], False), (pair[1], False)]
                    DA -= 2
                    
                    drift_j += -2
                elif I < pair[1] <= J:
                    instructions += [(pair[1], False), (I, True, CAP[1]({'class': tag}) )]
                    if not sign:
                        drift_i += 1
                elif I <= pair[0] < J:
                    instructions += [(pair[0], False), (J, True, CAP[0]({'class': tag}) )]
                    if not sign:
                        drift_j += -1
                elif pair[0] < I and pair[1] > J:
                    instructions += [(I, True, CAP[1]({'class': tag}) ), (J, True, CAP[0]({'class': tag}) )]
                    DA += 2
                    
                    if sign:
                        drift_j += 2
                    else:
                        drift_i += 1
                        drift_j += 1

            if instructions:
                activity = True
                
                instructions.sort(reverse=True)
                for instruction in instructions:
                    if instruction[1]:
                        self.text.insert(instruction[0], instruction[2])
                    else:
                        del self.text[instruction[0]]
            else:
                activity = False
            
            if sign:
                if self.text[P_1] == CAP[0]({'class': tag}):
                    del self.text[P_1]
                    DA -= 1
                    
                    drift_i -= 1
                    drift_j -= 1

                else:
                    self.text.insert(P_1, CAP[1]({'class': tag}) )
                    DA += 1
                    
                    drift_j += 1

            
            if activity:
                self.i = I + drift_i
                self.j = J + drift_j
                
                self._recalculate()
                
                # redo spelling for this paragraph
                self.text.misspellings = [pair if pair[1] < P_1 else
                        (pair[0] + DA, pair[1] + DA, pair[2]) if pair[0] > P_2 else
                        (0, 0, 0) for pair in self.text.misspellings ]
                # paragraph has changed
                self.text.misspellings.extend(words(self.text[P_1:P_2 + DA] + ['</p>'], startindex=P_1, spell=True)[1])
                
                return True
            else:
                return False
    """
