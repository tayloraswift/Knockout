import bisect
from model.wonder import words, _breaking_chars
from model import meredith, olivia

from IO.kevin import serialize_modules
from elements.elements import Paragraph, OpenFontpost, CloseFontpost, Image
B_OPEN = {Paragraph} | serialize_modules
deletion = {str} | serialize_modules

def outside_tag(sequence):
    for i in reversed(range(len(sequence) - 1)):

        if (type(sequence[i]), sequence[i + 1]) == (Paragraph, '</p>'):
            del sequence[i:i + 2]

    return sequence

class FCursor(object):
    def __init__(self, ctx):
        self.TRACT = meredith.mipsy[ctx['t']]
        self.assign_text(self.TRACT)
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
        if self.FTX is self.TRACT:
            i = self.i
            j = self.j
        else:
            i = self.si
            j = i
        return {'t': meredith.mipsy.index(self.TRACT), 'i': i, 'j': j, 'p': self.PG}

    def assign_text(self, ftext):
        self.FTX = ftext
        self.text = ftext.text

    # TARGETING SYSTEM
    def target(self, xo, yo):
        # perform naïve targeting (current page, current tract)
        x, y = meredith.page.normalize_XY(xo, yo, self.PG)
        imperfect, ftext, i_new, si = self.TRACT.target(x, y, self.PG, self.si)

        if imperfect:
            # fallbacks: current page, other tracts
            for chained_tract in meredith.mipsy: 
                imperfect_t, ftext_t, i_t, si_t = chained_tract.target(x, y, self.PG, i=None)
                if not imperfect_t:
                    # hit!
                    if ftext_t is not self.FTX:
                        # switch of tract context
                        self.assign_text(ftext_t)
                    self.TRACT = chained_tract
                    self.i = i_t
                    self.j = i_t
                    self.si = si_t
                    return
                    
            # fallbacks: other page, current tract
            binned_page = meredith.page.XY_to_page(xo, yo)
            x, y = meredith.page.normalize_XY(xo, yo, binned_page)
            
            imperfect_p, ftext_p, i_p, si_p = self.TRACT.target(x, y, binned_page, i=None)
            if not imperfect_p:
                # hit!
                if ftext_p is not self.FTX:
                    # switch of tract context
                    self.assign_text(ftext_p)
                self.i = i_p
                self.j = i_p
                self.si = si_p
                self.PG = binned_page
                return
                
            # fallbacks: other page, other tracts
            for chained_tract in meredith.mipsy:
                imperfect_pt, ftext_pt, i_pt, si_pt = chained_tract.target(x, y, binned_page, i=None)
                if not imperfect_pt:
                    # hit!
                    if ftext_pt is not self.FTX:
                        # switch of tract context
                        self.assign_text(ftext_pt)
                    self.TRACT = chained_tract
                    self.i = i_pt
                    self.j = i_pt
                    self.si = si_pt
                    self.PG = binned_page
                    return

        # best guess
        if ftext is not self.FTX:
            # switch of tract context
            self.assign_text(ftext)
        self.i = i_new
        self.j = i_new
        self.si = si
        return

    def target_select(self, xo, yo):
        # perform naïve targeting (current page, current tract)
        x, y = meredith.page.normalize_XY(xo, yo, self.PG)
        imperfect, i_new = self.FTX.target_select(x, y, self.PG, self.j)
        
        if imperfect:
            # fallbacks: other page, current tract
            binned_page = meredith.page.XY_to_page(xo, yo)
            x, y = meredith.page.normalize_XY(xo, yo, binned_page)
            
            imperfect_p, i_p = self.FTX.target_select(x, y, binned_page, i=None)
            if not imperfect_p:
                # hit!
                self.j = i_p
                self.PG = binned_page
                return

        # simple cursor assignment
        self.j = i_new
        return
    
    #############

    def paint_current_selection(self):
        ftags = {OpenFontpost, CloseFontpost}
        signs = (self.j < self.i,
                (type(self.text[self.i - 1]) in ftags, type(self.text[self.i]) in ftags) , 
                (type(self.text[self.j - 1]) in ftags, type(self.text[self.j]) in ftags))
        return self.FTX.paint_select(self.i, self.j), signs
    
    def take_selection(self):
        self.i, self.j = sorted((self.i, self.j))
        return self.text[self.i:self.j]

    def _recalculate(self):
        if self.FTX is self.TRACT:
            self.si = self.i
        self.TRACT.partial_recalculate(self.si)

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
            k = self.i + next(i for i, e in enumerate(self.text[self.i + 1:]) if type(e) in deletion) + 1
        else:
            k = self.i - next(i for i, e in enumerate(reversed(self.text[:self.i])) if type(e) in deletion) - 1
        
        start, end = sorted((k , j))
        offset = start - end + self._burn(start, end)
        
        # fix spelling lines
        self.FTX.misspellings = [pair if pair[1] < start else (pair[0] + offset, pair[1] + offset, pair[2]) if pair[0] > end else (0, 0, None) for pair in self.FTX.misspellings]
        self._recalculate()

    def insert(self, segment):
        if self.take_selection():
            self._burn(self.i, self.j)
            d = True
        else:
            d = False

        if segment:
            if type(self.text[self.i]) in B_OPEN: # outside
                # crop off chars
                try:
                    l = next(i for i, e in enumerate(segment) if type(e) in B_OPEN)
                    r = len(segment) - next(i for i, e in enumerate(reversed(segment)) if type(e) in serialize_modules or e == '</p>')
                    if r > l:
                        segment = segment[l:r]
                    else:
                        segment = []
                except StopIteration:
                    segment = []
            else: # inside
                if type(segment[0]) in B_OPEN:
                    segment.insert(0, '</p>')
                if segment[-1] == '</p>' or type(segment[-1]) in serialize_modules:
                    P = next(c.P for c in self.text[self.i::-1] if type(c) is Paragraph)
                    segment.append(Paragraph(P))

        s = len(segment)
        if s or d:
            self.text[self.i:self.j] = segment
            self._recalculate()
            self.i += s
            self.j = self.i
            
            # fix spelling lines
            self.FTX.misspellings = [pair if pair[1] < self.i else (pair[0] + s, pair[1] + s, pair[2]) if pair[0] > self.i else (pair[0], pair[1] + s, pair[2]) for pair in self.FTX.misspellings]

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
        try:
            # select block of spaces
            if self.text[self.i] == ' ':
                I = next(i for i, c in enumerate(self.text[self.j::-1]) if c != ' ') - 1
                self.i -= I
                
                J = next(i for i, c in enumerate(self.text[self.j:]) if c != ' ')
                self.j += J
            
            # select block of words
            elif str(self.text[self.j]) not in _breaking_chars:
                I = next(i for i, c in enumerate(self.text[self.j::-1]) if str(c) in _breaking_chars) - 1
                self.i -= I
                
                J = next(i for i, c in enumerate(self.text[self.j:]) if str(c) in _breaking_chars)
                self.j += J
            
            # select block of punctuation
            else:
                I = next(i for i, c in enumerate(self.text[self.j::-1]) if str(c) not in _breaking_chars or c == ' ') - 1
                self.i -= I
                
                # there can be only breaking chars at the end (</p>)
                try:
                    J = next(i for i, c in enumerate(self.text[self.j:]) if str(c) not in _breaking_chars or c == ' ')
                    self.j += J
                except StopIteration:
                    self.j = len(self.text) - 1

        except ValueError:
            pass

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
                
                self.text.insert(P_1, CAP[0](tag))
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

            if sign:
                ftags = [(i + P_1, type(e)) for i, e in enumerate(paragraph) if type(e) in CAP and e.F is tag] + [(P_2, CAP[1])] + [(None, None)]
            else:
                ftags = [(i + P_1, type(e)) for i, e in enumerate(paragraph) if type(e) in CAP and e.F is tag] + [(None, None)]
            
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
                    instructions += [(pair[1], False), (I, True, CAP[1](tag) )]
                    if not sign:
                        drift_i += 1
                elif I <= pair[0] < J:
                    instructions += [(pair[0], False), (J, True, CAP[0](tag) )]
                    if not sign:
                        drift_j += -1
                elif pair[0] < I and pair[1] > J:
                    instructions += [(I, True, CAP[1](tag) ), (J, True, CAP[0](tag) )]
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
                if self.text[P_1] == CAP[0](tag):
                    del self.text[P_1]
                    DA -= 1
                    
                    drift_i -= 1
                    drift_j -= 1

                else:
                    self.text.insert(P_1, CAP[1](tag) )
                    DA += 1
                    
                    drift_j += 1

            
            if activity:
                self.i = I + drift_i
                self.j = J + drift_j
                
                self._recalculate()
                
                # redo spelling for this paragraph
                self.FTX.misspellings = [pair if pair[1] < P_1 else
                        (pair[0] + DA, pair[1] + DA, pair[2]) if pair[0] > P_2 else
                        (0, 0, 0) for pair in self.FTX.misspellings ]
                # paragraph has changed
                self.FTX.misspellings += words(self.text[P_1:P_2 + DA] + ['</p>'], startindex=P_1, spell=True)[1]
                
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
