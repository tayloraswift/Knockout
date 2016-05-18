from itertools import chain

from model.wonder import words
from elements import datablocks
# from elements.elements import Paragraph, OpenFontpost, CloseFontpost, Block_element
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
        self._set_plane(address(datablocks.DOCUMENT, plane_address), plane_address)
        self.i = i
        self.j = j
        self._doc = datablocks.DOCUMENT
        self._section = datablocks.DOCUMENT.content[plane_address[0]]
        
        self.PG = 0 # stopgap
    
    def _char(self, i, offset=0):
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
            signs = (str(self._char(i, -1)) in _zeros, str(self._char(i)) in _zeros) , (str(self._char(j, -1)) in _zeros, str(self._char(j)) in _zeros)
        else:
            signs = (False, False), (False, False)
        
        lit = self._blocks[i[0]: j[0] + double]
        bounds = [[None, None] for b in lit]
        if double:
            bounds[0][0] = i[1]
            bounds[-1][1] = j[1]
        
        return list(chain.from_iterable(block.highlight( * bound ) for bound, block in zip(bounds, lit))), signs

    # TARGETING SYSTEM
    def _to_c_global(self, x, y):
        S = self._section
        c, p = S['frames'].which(x, y, 20)
        if c is None:
            # try other sections
            for s, section in (ss for ss in enumerate(self._doc.content) if ss[0] is not S): 
                c, _p = section['frames'].which(x, y, 20)
                if c is not None:
                    self._section = section
                    self.plane_address[0] = s
                    self.PG = _p
                    x, y = self._doc.medium.normalize_XY(x, y, _p)
                    return x, section['frames'].y2u(y, c)
            
            c = self.PLANE.where(self.i)[1]['c']
        else:
            self.PG = p
        x, y = self._doc.medium.normalize_XY(x, y, self.PG)
        return x, self._section['frames'].y2u(y, c)

    def _to_c_local(self, x, y):
        c, p = self._section['frames'].which(x, y, 20)
        if c is None:
            c = self.PLANE.where(self.j)[1]['c']
        else:
            self.PG = p
        x, y = self._doc.medium.normalize_XY(x, y, self.PG)
        return x, self._section['frames'].y2u(y, c)
            
    def target(self, x, y):
        x, u = self._to_c_global(x, y)
        
        address, stack = zip( * self._section.which(x, u) )
        
        address_i, plane = next(enumerate(box for box in chain(reversed(stack), (self._section,)) if box is not None and type(box).plane))
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

    def run_stats(self, spell=False):
        word_total = 0
        for block in self._blocks:
            word_total += block.run_stats(spell)
        self.word_total = word_total

class FCursor(object):
    def __init__(self, ctx):
        self.R_FTX = meredith.mipsy[ctx['t']]
        self.assign_text(self.R_FTX)
        if max(ctx['i'], ctx['j']) < len(self.text):
            self.si = ctx['i']
            self.i = ctx['i']
            self.j = ctx['j']
        else:
            self.si = 0
            self.i = 0
            self.j = 0

        self.PG = ctx['p']

    def polaroid(self):
        if self.FTX is self.R_FTX:
            i = self.i
            j = self.j
        else:
            i = self.si
            j = i
        return {'t': meredith.mipsy.index(self.R_FTX), 'i': i, 'j': j, 'p': self.PG}

    def assign_text(self, ftext):
        self.FTX = ftext
        self.text = ftext.text


    def paint_current_selection(self):
        zeros = {'<fc/>', '<fo/>', '\t'}
        signs = (self.j < self.i,
                (str(self.text[self.i - 1]) in zeros, str(self.text[self.i]) in zeros) , 
                (str(self.text[self.j - 1]) in zeros, str(self.text[self.j]) in zeros))
        return self.FTX.paint_select(self.i, self.j), signs
    
    def take_selection(self):
        self.i, self.j = sorted((self.i, self.j))
        return self.text[self.i:self.j]

    def _recalculate(self):
        if self.FTX is self.R_FTX:
            self.si = self.i
        self.R_FTX.partial_layout(self.si)

    def _burn(self, i, j):
        # filter for paragraph elements
        ptags = [e for e in self.text[i:j] if e == '</p>' or type(e) is Paragraph]
        
        ash = []
        di = 0
        if ptags:
            left = ptags[0]
            if left == '</p>': 
                ash.append(left)
                
            right = ptags[-1]
            if type(right) is Paragraph:
                ash.append(right)
                di = 1
        if len(ash) == 2:
            ash = []
            di = 0
        
        self.i = i + di
        self.text[i:j] = ash
        self.j = self.i
        return len(ash)

    def delspace(self, direction=False): # only called when i = j
        j = self.j
        if direction:
            try:
                k = self.i + next(i for i, e in enumerate(self.text[self.i + 1:]) if type(e) is not Paragraph) + 1
            except StopIteration:
                k = len(self.text) - 1
        else:
            try:
                k = self.i - next(i for i, e in enumerate(reversed(self.text[:self.i])) if type(e) is not Paragraph) - 1
            except StopIteration:
                k = 1
        
        start, end = sorted((k , j))
        offset = start - end + self._burn(start, end)
        
        # fix spelling lines
        self.text.misspellings = [pair if pair[1] < start else (pair[0] + offset, pair[1] + offset, pair[2]) if pair[0] > end else (0, 0, None) for pair in self.text.misspellings]
        self._recalculate()

    def insert(self, segment):
        if self.take_selection():
            m = self.i - self.j
            m += self._burn(self.i, self.j)
            d = True
        else:
            d = False
            m = 0

        if segment:
            if not self.text or isinstance(self.text[self.i], (Paragraph, Block_element)): # outside
                # crop off chars
                try:
                    l = next(i for i, e in enumerate(segment) if isinstance(e, (Paragraph, Block_element)))
                    r = len(segment) - next(i for i, e in enumerate(reversed(segment)) if isinstance(e, (Paragraph, Block_element)) or e == '</p>')
                    if r > l:
                        segment = segment[l:r]
                    else:
                        segment = []
                except StopIteration:
                    segment = []
            else: # inside
                if isinstance(segment[0], (Paragraph, Block_element)):
                    segment.insert(0, '</p>')
                if segment[-1] == '</p>' or isinstance(segment[-1], Block_element):
                    P = next(c.P.copy() for c in self.text[self.i::-1] if type(c) is Paragraph)
                    segment.append(Paragraph(P))
        
        s = len(segment)
        m += s
        if s or d:
            self.text[self.i:self.j] = segment
            self._recalculate()
            self.i += s
            self.j = self.i
            
            # fix spelling lines
            self.text.misspellings = [pair if pair[1] < self.i else (pair[0] + m, pair[1] + m, pair[2]) if pair[0] > self.i else (pair[0], pair[1] + m, pair[2]) for pair in self.text.misspellings]

    def expand_cursors(self):
        # order
        self.i, self.j = sorted((self.i, self.j))
        
        if type(self.text[self.i - 1]) is Paragraph and self.text[self.j] == '</p>':
            self.i = 1
            self.j = len(self.text) - 1
        else:
            self.j += self.text[self.j:].index('</p>')
            self.i -= next(i for i, v in enumerate(self.text[self.i::-1]) if type(v) is Paragraph) - 1

    def expand_cursors_word(self):
        self.i, self.j = expand_cursors_word(self.text, self.i)

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

    def hop(self, direction): #implemented exclusively for arrow-up/down events
        self.i = self.FTX.line_jump(self.i, direction)

    def pp_at(self):
        return self.FTX.line_at(self.i)['PP']

    def styling_at(self):
        line = self.FTX.line_at(self.i)
        try:
            glyph = line['GLYPHS'][self.i - line['i']]
        except IndexError:
            glyph = line['GLYPHS'][-1]

        return line['PP'], glyph[3]

    def front_and_back(self):
        return self.FTX.line_indices(self.i)
