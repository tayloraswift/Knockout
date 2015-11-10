import bisect

from pyphen import pyphen
pyphen.language_fallback('en_US')

from fonts import fonttable

from model import kevin
from model import errors
from model.wordprocessor import words, _breaking_chars, character

hy = pyphen.Pyphen(lang='en_US')


def outside_tag(sequence):
    for i in reversed(range(len(sequence) - 1)):

        if (character(sequence[i]), sequence[i + 1]) == ('<p>', '</p>'):
            del sequence[i:i + 2]

    return sequence

def _fail_class(startindex, l, attempt):
    errors.styleerrors.add_style_error(attempt, l)
    return ('_interface', startindex), fonttable.p_table.get_paragraph('_interface')
        
class Textline(object):
    def __init__(self, text, anchor, stop, y, c, l, startindex, paragraph, fontclass, leading):
        self._p = paragraph
        self._f = fontclass

        try:
            self._fontclass = fonttable.table.get_font(paragraph[0], tuple(fontclass))
        except KeyError:
            self._fontclass = fonttable.table.get_font(paragraph[0], () )

        # takes 1,989 characters starting from startindex
        self._sorts = text[startindex:startindex + 1989]
        
        # character index to start with
        self.startindex = startindex
        self.leading = leading
        
        # x positions
        self.anchor = anchor
        self.stop = stop
        
        # line y position
        self.y = y
        self.c = c
        self.l = l
        
        # terminal hyphen
        self.hyphen = None

    def build_line(self, hyphenate):
        
        p, p_i = self._p
        
        # go by syllable until you reach the end
        index = self.startindex
        
        # lists that contain glyphs and specials
        self.glyphs = []
#        self.special = []
        
        # start on the anchor
        x = self.anchor
        n = 0

        for entity in self._sorts:
            glyph = character(entity)
            glyphanchor = x
            
            if glyph == '<p>':
                if n > 0:
                    break
                else:
                
                    # we don’t load the style because the outer function takes care of that
                    # retract x position
                    glyphanchor -= self._fontclass['fontsize']
                    glyphwidth = 0
                    x -= self._fontclass['tracking']

            elif glyph == '</p>':
                self.glyphs.append((self._fontclass['fontmetrics'].character_index(glyph), x, self.y, self._p, tuple(self._f)))
                # paragraph breaks are signaled by a negative index
                return (self.startindex + len(self.glyphs))*-1 - 1
                break

            elif glyph == '<f>':

                # look for negative classes
                if '~' + entity[1] in self._f:
                    self._f.remove('~' + entity[1])
                else:
                    self._f.append(entity[1])
                    self._f.sort()
                    
                try:
                    self._fontclass = fonttable.table.get_font(p, tuple(self._f))
                except KeyError:
                    # happens if requested style is not defined
                    errors.styleerrors.add_style_error(tuple(self._f), self.l)
                    try:
                        self._fontclass = fonttable.table.get_font(p, () )
                    except AttributeError:
                        self._fontclass = fonttable.table.get_font('_interface', () )
            elif glyph == '</f>':

                try:
                    self._f.remove(entity[1])
                    self._fontclass = fonttable.table.get_font(p, tuple(self._f))
                except (ValueError, KeyError):
                    # happens if the tag didn't exist
                    self._f.append('~' + entity[1])
                    self._f.sort()
                    errors.styleerrors.add_style_error(tuple(self._f), self.l)
                    try:
                        self._fontclass = fonttable.table.get_font(p, () )
                    except AttributeError:
                        self._fontclass = fonttable.table.get_font('_interface', () )

            glyphwidth = self._fontclass['fontmetrics'].advance_pixel_width(glyph)*self._fontclass['fontsize']
            self.glyphs.append((self._fontclass['fontmetrics'].character_index(glyph), glyphanchor, self.y, self._p, tuple(self._f), glyphanchor + glyphwidth))
            
            
            if glyph == '<br>':
                x -= self._fontclass['tracking']
                break
            
            x += glyphwidth + self._fontclass['tracking']
            n = len(self.glyphs)
            
            # work out line breaks
            if x > self.stop:
                if glyph == ' ':
                    pass
                
                elif ' ' in self._sorts[:n] or '-' in self._sorts[:n]:
                    i = next(i for i,v in zip(range(len(self._sorts[:n]) - 1, 0, -1), reversed(self._sorts[:n])) if v == ' ' or v == '-')
                    
                    ### AUTO HYPHENATION
                    if hyphenate:
                        try:
                            j = self._sorts[i + 1:].index(' ')
                        except ValueError:
                            j = self.startindex
                        
                        word = ''.join([c if type(c) is not list else ' ' for c in self._sorts[i + 1: i + 1 + j] ])
                        for pair in hy.iterate(word):
                            k = len(pair[0])
                            
#                            if k < 3 or len(pair[1]) < 3:
#                                continue
                            
                            try:
                                pf = (self.glyphs[i + k][3][0], self.glyphs[i + k][4])
                                try:
                                    fc = fonttable.table.get_font( * pf )
                                except KeyError:
                                    try:
                                        fc = fonttable.table.get_font(p, () )
                                    except AttributeError:
                                        fc = fonttable.table.get_font('_interface', () )
                                    
                                if self.glyphs[i + k][5] + fc['fontmetrics'].advance_pixel_width('-')*fc['fontsize'] < self.stop:
                                    i = i + k
                                    if self._sorts[i] != '-':
                                        self.hyphen = (fc['fontmetrics'].character_index('-'), ) + (self.glyphs[i][5], self.glyphs[i][2]) + pf
                                    break
                            except IndexError:
                                pass
                    ####################
                    
                    del self.glyphs[i + 1:]

                else:
                    del self.glyphs[-1]
                break
                
        # n changes
        return self.startindex + len(self.glyphs)
        


class Cursor(object):
    def __init__(self, text):
        self.cursor = 0
        self.skip(1, text)
    
    def skip(self, jump, text):
        self.cursor += jump
        # prevent overruns
        if self.cursor > len(text) - 1:
            self.cursor = len(text) - 1
        if character(text[self.cursor]) in ['<p>']:
            direction = 1
            if jump < 0:
                direction = -1
            while True:
                self.cursor += direction
                if character(text[self.cursor]) not in ['<p>']:
                    break

    def set_cursor(self, index, text):
        self.cursor = index
        self.skip(0, text)

class Text(object):
    def __init__(self, text, channels):
        self.text = kevin.deserialize(text)
        self.channels = channels
        
        self._glyphs = []
        
        self.sorted_glyphs = {}
        
        # create cursor objects
        self.cursor = Cursor(self.text)
        self.select = Cursor(self.text)
        
        # STATS
        self.word_count = '—'
        self.misspellings = []
        
    def _generate_lines(self, l, startindex):
        c = 0
        
        try:
            # ylevel is the y position of the first line to print
            # here we are removing the last existing line so we can redraw that one as well
            li = self._glyphs.pop(-1)
            y = li.y - li.leading
            c = li.c
            
        except IndexError:
            # which happens if nothing has yet been rendered
            p = (self.text[0][1], 0)
            f = []
            try:
                paragraphclass = fonttable.p_table.get_paragraph(p[0])
            except KeyError:
                # happens if requested style is not defined
                p, paragraphclass = _fail_class(startindex, l, (p[0],))
                
            
            y = self.channels.channels[c].railings[0][0][1]
        while True:
            # check for paragraph change
            try:
                if character(self.text[startindex]) != '<p>':
                    # extract last used style
                    f = list(self._glyphs[-1].glyphs[-1][4])
                    p = self._glyphs[-1].glyphs[-1][3]
                else:
                    f = []
                    p = (self.text[startindex][1], startindex)
                    
                try:
                    paragraphclass = fonttable.p_table.get_paragraph(p[0])
                except KeyError:
                    # happens if requested style is not defined
                    p, paragraphclass = _fail_class(startindex, l, (p[0],))

                    
            except IndexError:
                pass

            # move down
            y += paragraphclass['leading']
            
            # see if the lines have overrun the portals
            if y > self.channels.channels[c].railings[1][-1][1] and c < len(self.channels.channels) - 1:
                c += 1
                # shift to below entrance
                y = self.channels.channels[c].railings[0][0][1] + paragraphclass['leading']

            # generate line objects
            line = Textline(self.text, 
                    self.channels.channels[c].edge(0, y)[0], 
                    self.channels.channels[c].edge(1, y)[0], 
                    y, 
                    c,
                    l,
                    startindex,
                    p, 
                    f,
                    paragraphclass['leading']
                    )
            
            # get the index of the last glyph printed (while printing said line) so we know where to start next time
            startindex = line.build_line(paragraphclass['hyphenate'])
            # check for paragraph break (which returns a negative version of startindex)
            if startindex < 0:

                startindex = abs(startindex) - 1
                y += paragraphclass['margin_bottom']
                
                if startindex > len(self.text) - 1:
                    self._glyphs.append(line)
                    del line
                    # this is the end of the document
                    break
            else:
                pass
            l += 1

            self._glyphs.append(line)
            del line
#            if startindex >= len(self.text):
#                break


    def _recalculate(self):
        # clear sorts
        self.sorted_glyphs = {}
        # avoid recalculating lines that weren't affected
        try:
            affected = self.index_to_line( min(self.select.cursor, self.cursor.cursor) ) - 1
            if affected < 0:
                affected = 0
            startindex = self._glyphs[affected].startindex
            self._glyphs = self._glyphs[:affected + 1]
            #        i = affected
            self._generate_lines(affected, startindex)
        except AttributeError:
            self.deep_recalculate()
        
        # tally errors
        errors.styleerrors.update(affected)

    def deep_recalculate(self):
        # clear sorts
        self._glyphs = []
        self.sorted_glyphs = {}
        
        self._generate_lines(0, 0)
        
        # tally errors
        errors.styleerrors.update(0)


    def target_line(self, x, y, c=None):
        # find which channel is clicked on
        if c is None:
            c = self.channels.target_channel(x, y, 20)
        # get all y values
        yy = [textline for textline in self._glyphs if textline.c == c]
        # find the clicked line
        lineindex = None
        if y >= yy[-1].y:
            lineindex = len(yy) - 1
        else:
            lineindex = bisect.bisect([textline.y for textline in yy], y )

        return yy[lineindex].l
    
    def target_glyph(self, x, y, l=None, c=None):
        if c is None:
            c = self.channels.target_channel(x, y, 20)
        if l is None:
            l = self.target_line(x, y, c)

        # find first glyph to the right of click spot
        try:
            glyphindex = bisect.bisect([glyph[1] for glyph in self._glyphs[l].glyphs], x )
        except IndexError:
            # if l is greater than the length of the document
            l = l % len(self._glyphs)
            glyphindex = bisect.bisect([glyph[1] for glyph in self._glyphs[l].glyphs], x )
        
        # determine x position of glyph before it
        glyphx = self._glyphs[l].glyphs[glyphindex - 1][1]
        # if click is closer to it, shift glyph index left one
        try:
            if abs(x - glyphx) < abs(x - self._glyphs[l].glyphs[glyphindex][1]):
                glyphindex += -1
        except IndexError:
            glyphindex = len(self._glyphs[l].glyphs) - 1
            
        return glyphindex + self._glyphs[l].startindex

    # get line number given character index
    def index_to_line(self, index):
        return bisect.bisect([line.startindex for line in self._glyphs], index ) - 1

    def take_selection(self):
        if self.cursor.cursor == self.select.cursor:
            return False
        else:
            self._sort_cursors()

            return self.text[self.cursor.cursor:self.select.cursor]

    def delete(self, start=None, end=None, da=0, db=0):

        self._sort_cursors()

        if start is None:
            start = self.cursor.cursor + da
            
        if end is None:
            end = self.select.cursor + db


        if [character(e) for e in self.text[start:end]] == ['</p>', '<p>']:
            del self.text[start:end]
            
            offset = start - end
        
        else:
            # delete every PAIRED paragraph block
            ptags = [ e for e in self.text[start:end] if character(e) in ['<p>', '</p>'] ]
            del self.text[start:end]

            outside = outside_tag(ptags)
            if outside:
                if (outside[0], character(outside[1])) == ('</p>', '<p>'):
                    style = next(c[1] for c in self.text[start::-1] if character(c) == '<p>')
                    if style == outside[1][1]:
                        del outside[0:2]
                        
                self.text[start:start] = outside

            offset = start - end + len(outside)
        
        # fix spelling lines
        self.misspellings = [pair if pair[1] < start else (pair[0] + offset, pair[1] + offset) if pair[0] > end else (0, 0) for pair in self.misspellings]

        self._recalculate()
        self.cursor.set_cursor(start, self.text)
        self.select.cursor = self.cursor.cursor

    def insert(self, segment):
        if self.take_selection():
            self.delete(self.cursor.cursor, self.select.cursor)
        
        s = len(segment)
        self.text[self.cursor.cursor:self.cursor.cursor] = segment
        self._recalculate()
        self.cursor.skip(s, self.text)
        self.select.cursor = self.cursor.cursor
        
        # fix spelling lines
        self.misspellings = [pair if pair[1] < self.cursor.cursor else (pair[0] + s, pair[1] + s) if pair[0] > self.cursor.cursor else (pair[0], pair[1] + s) for pair in self.misspellings]
    
    def encapsulate(self, tag):
        if '</p>' not in self.take_selection():
            I = self.cursor.cursor
            J = self.select.cursor
            # if selection falls on top of range
            if character(self.text[I - 1]) == '<f>':
                I -= next(i for i, c in enumerate(self.text[I - 2::-1]) if character(c) != '<f>') + 1

            if character(self.text[J]) == '</f>':
                J += next(i for i, c in enumerate(self.text[J + 1:]) if character(c) != '</f>') + 1
          
            P_1 = I - next(i for i, c in enumerate(self.text[I - 1::-1]) if character(c) == '<p>')
            P_2 = J + self.text[J + 1:].index('</p>') + 1
            paragraph = self.text[P_1:P_2]

            ftags = [(i + P_1, e[0]) for i, e in enumerate(paragraph) if e == ['<f>', tag] or e == ['</f>', tag]] + [(None, None)]
            
            print(ftags)
            pairs = []
            for i in reversed(range(len(ftags) - 2)):
                if (ftags[i][1], ftags[i + 1][1]) == ('<f>', '</f>'):
                    pairs.append((ftags[i][0], ftags[i + 1][0]))
                    del ftags[i:i + 2]
            print(ftags)
            print(pairs)
            
            instructions = [(I, True, ['<f>', tag]), (J, True, ['</f>', tag])]
            UN = []
            drift_i = 0
            drift_j = 2
            triangle_a = 2
            for pair in pairs:
                # mind the exclusive comparisons
                if pair[1] < I or pair[0] > J:
                    pass
                elif pair[0] >= I and pair[1] <= J:
                    instructions += [(pair[0], False), (pair[1], False)]
                    drift_j += -2
                    triangle_a = 0
                elif I < pair[1] <= J:
                    # delete overlap
                    instructions.append((pair[1], False))
                    UN.append((I, False))
                    drift_j += -2
                    triangle_a = 0
                elif I <= pair[0] < J:
                    instructions.append((pair[0], False))
                    UN.append((J, False))
                    drift_j += -2
                    triangle_a = 0
                elif pair[0] < I and pair[1] > J:
                    UN += [(I, False), (J, False)]
                    drift_j += -2
                    triangle_a = 0
            
            instructions += list(set(UN))
            instructions.sort(reverse=True)
            print(instructions)
            
            for instruction in instructions:
                if instruction[1]:
                    self.text.insert(instruction[0], instruction[2])
                else:
                    del self.text[instruction[0]]
            
            self.cursor.cursor = I + drift_i
            self.select.cursor = J + drift_j

            self.misspellings = [ tuple(k + triangle_a if k >= J else k + triangle_a//1 if k >= I else k for k in pair[:2]) + pair[2:] for pair in self.misspellings]
            
            self._recalculate()

    def decapsulate(self, tag):
        if '</p>' not in self.take_selection():
            I = self.cursor.cursor
            J = self.select.cursor
            # if selection falls on top of range
            if character(self.text[I - 1]) == '<f>':
                I -= next(i for i, c in enumerate(self.text[I - 2::-1]) if character(c) != '<f>') + 1

            if character(self.text[J]) == '</f>':
                J += next(i for i, c in enumerate(self.text[J + 1:]) if character(c) != '</f>') + 1


            P_1 = I - next(i for i, c in enumerate(self.text[I - 1::-1]) if character(c) == '<p>')
            P_2 = J + self.text[J + 1:].index('</p>') + 1
            paragraph = self.text[P_1:P_2]

            ftags = [(i + P_1, e[0]) for i, e in enumerate(paragraph) if e == ['<f>', tag] or e == ['</f>', tag]] + [(None, None)]
            
            print(ftags)
            pairs = []
            for i in reversed(range(len(ftags) - 2)):
                if (ftags[i][1], ftags[i + 1][1]) == ('<f>', '</f>'):
                    pairs.append((ftags[i][0], ftags[i + 1][0]))
                    del ftags[i:i + 2]
            print(ftags)
            print(pairs)
            
            instructions = []
            drift_i = 0
            drift_j = 0
            triangle_a = 0
            for pair in pairs:
                if pair[1] <= I or pair[0] >= J:
                    pass
                elif pair[0] >= I and pair[1] <= J:
                    instructions += [(pair[0], False), (pair[1], False)]
                    drift_j += -2
                    triangle_a = -2
                elif I < pair[1] <= J:
                    instructions += [(pair[1], False), (I, True, ['</f>', tag])]
                    drift_i += 1
                elif I <= pair[0] < J:
                    instructions += [(pair[0], False), (J, True, ['<f>', tag])]
                    drift_j += -1
                elif pair[0] < I and pair[1] > J:
                    instructions += [(I, True, ['</f>', tag]), (J, True, ['<f>', tag])]
                    drift_i += 1
                    drift_j += 1
                    triangle_a = 2
            instructions.sort(reverse=True)
            print(instructions)
            
            for instruction in instructions:
                if instruction[1]:
                    self.text.insert(instruction[0], instruction[2])
                else:
                    del self.text[instruction[0]]

            self.cursor.cursor = I + drift_i
            self.select.cursor = J + drift_j

            self.misspellings = [ tuple(k + triangle_a if k >= J else k + triangle_a//1 if k >= I else k for k in pair[:2]) + pair[2:] for pair in self.misspellings]
            
            self._recalculate()
                
    def _sort_cursors(self):
        if self.cursor.cursor > self.select.cursor:
            self.cursor.cursor, self.select.cursor = self.select.cursor, self.cursor.cursor
    
    def expand_cursors(self):
        # order
        self._sort_cursors()
        
        if character(self.text[self.cursor.cursor - 1]) == '<p>' and character(self.text[self.select.cursor]) == '</p>':
            self.cursor.cursor = 1
            self.select.cursor = len(self.text) - 1
        else:
            self.select.cursor += self.text[self.select.cursor:].index('</p>')
            self.cursor.cursor = self.text_index_location(self.cursor.cursor)[2][1] + 1
    
    def expand_cursors_word(self):

        try:
            # select block of spaces
            if self.text[self.select.cursor] == ' ':
                I = next(i for i, c in enumerate(self.text[self.select.cursor::-1]) if c != ' ') - 1
                self.cursor.cursor -= I
                
                J = next(i for i, c in enumerate(self.text[self.select.cursor:]) if c != ' ')
                self.select.cursor += J
            
            # select block of words
            elif character(self.text[self.select.cursor]) not in _breaking_chars:
                I = next(i for i, c in enumerate(self.text[self.select.cursor::-1]) if character(c) in _breaking_chars) - 1
                self.cursor.cursor -= I
                
                J = next(i for i, c in enumerate(self.text[self.select.cursor:]) if character(c) in _breaking_chars)
                self.select.cursor += J
            
            # select block of punctuation
            else:
                I = next(i for i, c in enumerate(self.text[self.select.cursor::-1]) if character(c) not in _breaking_chars or c == ' ') - 1
                self.cursor.cursor -= I
                
                # there can be only breaking chars at the end (</p>)
                try:
                    J = next(i for i, c in enumerate(self.text[self.select.cursor:]) if character(c) not in _breaking_chars or c == ' ')
                    self.select.cursor += J
                except StopIteration:
                    self.select.cursor = len(self.text) - 1

        except ValueError:
            pass


    ### FUNCTIONS USEFUL FOR DRAWING AND INTERFACE
    
    def line_indices(self, l):
        return self._glyphs[l].startindex, self._glyphs[l].startindex + len(self._glyphs[l].glyphs)

    # get location of specific glyph
    def text_index_location(self, index, ahead=False):
        l = self.index_to_line(index)
        try:
            glyph = self._glyphs[l].glyphs[index - self._glyphs[l].startindex]
        except IndexError:
            glyph = self._glyphs[l].glyphs[-1]
            print ('ahead')
            ahead = True

        y = glyph[2]
        x = glyph[1]
        p = glyph[3]
        f = glyph[4]

#        if ahead:
#            x += self.Face.advance_width(character(self.text[index]))/1000*self.fontsize
        return (x, y, p, f)

    def stats(self, spell):
        if spell:
            self.word_count, self.misspellings = words(self.text, spell=True)
        else:
            self.word_count = words(self.text)

    def line_data(self, l):
        anchor = self._glyphs[l].anchor
        stop = self._glyphs[l].stop
        leading = self._glyphs[l].leading
        y = self._glyphs[l].y
        return anchor, stop, leading, y

    def transform_glyphs(self, dx, dy):

        for style, glyphs in self.sorted_glyphs.items():
            self._transformed_glyphs[style] = [ (glyph[0], glyph[1] + dx, glyph[2] + dy) for glyph in glyphs]

    def extract_glyphs(self, mx_cx, my_cy, cx, cy, A, refresh=False):
        
        if refresh:
            self.sorted_glyphs = {}
            self._transformed_glyphs = {}

        if not self.sorted_glyphs:
            
            for line in self._glyphs:
                p_name = line.glyphs[0][3][0]
                hyphen = line.hyphen
                for glyph in line.glyphs:
                    f = glyph[4]
                    k = (glyph[0], A*(glyph[1] + mx_cx) + cx, A*(glyph[2] + my_cy) + cy)
                    try:
                        self.sorted_glyphs[(p_name, f)].append(k)
                    except KeyError:
                        self.sorted_glyphs[(p_name, f)] = []
                        self.sorted_glyphs[(p_name, f)].append(k)
                if hyphen is not None:
                    try:
                        self.sorted_glyphs[hyphen[3:5]].append((hyphen[0], A*(hyphen[1] + mx_cx) + cx, A*(hyphen[2] + my_cy) + cy))
                    except KeyError:
                        self.sorted_glyphs[hyphen[3:5]] = []
                        self.sorted_glyphs[hyphen[3:5]].append((hyphen[0], A*(hyphen[1] + mx_cx) + cx, A*(hyphen[2] + my_cy) + cy))
            self._transformed_glyphs = self.sorted_glyphs.copy()
        return self._transformed_glyphs
