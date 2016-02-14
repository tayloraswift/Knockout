import bisect
from model.wonder import words, _breaking_chars
from model import meredith, olivia

from elements.elements import Paragraph, OpenFontpost, CloseFontpost, Image

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
        self.index_to_line = ftext.index_to_line
        self.text_index_x = ftext.text_index_x

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
                    self.i = self.skip(i_t)
                    self.j = self.i
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
                self.i = self.skip(i_p)
                self.j = self.i
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
                    self.i = self.skip(i_pt)
                    self.j = self.i
                    self.si = si_pt
                    self.PG = binned_page
                    return

        # best guess
        if ftext is not self.FTX:
            # switch of tract context
            self.assign_text(ftext)
        self.i = self.skip(i_new)
        self.j = self.i
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
                self.j = self.skip(i_p)
                self.PG = binned_page
                return

        # simple cursor assignment
        self.j = self.skip(i_new)
        return
    
    #############

    def skip(self, i, jump=0):
        i += jump
        # prevent overruns
        i = min(len(self.text) - 1, max(1, i))
        if type(self.text[i]) is Paragraph:
            direction = 1
            if jump < 0:
                direction = -1
            while True:
                i += direction
                if type(self.text[i]) is not Paragraph:
                    break
        return i

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
        self.TRACT._dbuff( self.si )

    def delete(self, start=None, end=None, da=0, db=0):
        self.i, self.j = sorted((self.i, self.j))

        if start is None:
            start = self.i + da
            
        if end is None:
            end = self.j + db

        if [str(e) for e in self.text[start:end]] == ['</p>', '<p>']:
            del self.text[start:end]
            
            offset = start - end
        
        else:
            # delete every PAIRED paragraph block
            ptags = [ e for e in self.text[start:end] if e == '</p>' or type(e) is Paragraph ]
            del self.text[start:end]

            outside = outside_tag(ptags)
            
            if outside:
                if (outside[0], type(outside[1])) == ('</p>', Paragraph):
                    style = next(c.P for c in self.text[start::-1] if type(c) is Paragraph)
                    if style == outside[1].P:
                        del outside[0:2]
                        
                self.text[start:start] = outside

            offset = start - end + len(outside)
        
        # fix spelling lines
        self.FTX.misspellings = [pair if pair[1] < start else (pair[0] + offset, pair[1] + offset, pair[2]) if pair[0] > end else (0, 0, None) for pair in self.FTX.misspellings]

        self._recalculate()
        self.i = self.skip(self.i + da)
        self.j = self.i

    def insert(self, segment):
        if self.take_selection():
            self.delete(self.i, self.j)
        
        s = len(segment)
        self.text[self.i:self.j] = segment
        self._recalculate()
        self.i = self.skip(self.i + s)
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
        self.i = self.skip(self.FTX.line_jump(self.i, direction))

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
        return self.FTX.line_indices(self.index_to_line(self.i))
