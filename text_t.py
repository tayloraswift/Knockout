import bisect

import channels

import kevin
import errors

import fonts
import fonttable


def the_box_submitted(ip):
    print('the textbox submitted' + ip)

def character(entity):
    if type(entity) is list:
        entity = entity[0]
    return entity


def outside_tag(sequence, tags=('<p>', '</p>')):
    for i in reversed(range(len(sequence))):
        try:
            if character(sequence[i]) == tags[0] and character(sequence[i + 1]) == tags[1]:
                del sequence[i:i + 2]
        except IndexError:
            pass
    return sequence

def _fail_class(startindex, l, attempt):
    errors.styleerrors.add_style_error(attempt, l)
    return ('_interface', startindex), fonts.paragraph_classes['_interface']

        
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

    def build_line(self):
        
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
            self.glyphs.append((self._fontclass['fontmetrics'].character_index(glyph), glyphanchor, self.y, self._p, tuple(self._f)))
            
            
            if glyph == '<br>':
                x -= self._fontclass['tracking']
                break
            
            x += glyphwidth + self._fontclass['tracking']
            n = len(self.glyphs)
            
            # work out line breaks
            if x > self.stop:
                if glyph == ' ':
                    pass
                
                elif ' ' in self._sorts[:n]:
                    i = n - 2
                    while True:
                        if self._sorts[i] == ' ':
                            del self.glyphs[i + 1:]
                            break
                        i -= 1
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
    def __init__(self, text):
        self.text = kevin.deserialize(text)
        
        c1 = channels.Channel([[0, 0, False], [0, 800, False]], [[300, 0, False], [300, 800, False]])
        c2 = channels.Channel([[350, 0, False], [350, 800, False]], [[650, 0, False], [650, 800, False]])
        c3 = channels.Channel([[700, 0, False], [700, 800, False]], [[1000, 0, False], [1000, 800, False]])
        self.channels = channels.Channels([c1, c2, c3])
        
        self._glyphs = []
        
        self.sorted_glyphs = {}
        
        # create cursor objects
        self.cursor = Cursor(self.text)
        self.select = Cursor(self.text)

        
    def _generate_lines(self, l, startindex):
        c = 0
        
        try:
            # ylevel is the y position of the first line to print
            # here we are removing the last existing line so we can redraw that one as well
            li = self._glyphs.pop(-1)
            y, c= li.y, li.c
            
        except IndexError:
            # which happens if nothing has yet been rendered
            p = (self.text[0][1], 0)
            f = []
            try:
                paragraphclass = fonts.paragraph_classes[p[0]]
            except KeyError:
                # happens if requested style is not defined
                p, paragraphclass = _fail_class(startindex, l, (p[0],))
                
            
            y = self.channels.channels[c].railings[0][0][1] + fonts.get_leading(p[0])
        while True:
            # see if the lines have overrun the portals
            if y > self.channels.channels[c].railings[1][-1][1] and c < len(self.channels.channels) - 1:
                c += 1
                # shift to below entrance
                y = self.channels.channels[c].railings[0][0][1] + fonts.get_leading(p[0])
            
            try:
                if character(self.text[startindex]) != '<p>':
                    # extract last used style
                    f = list(self._glyphs[-1].glyphs[-1][4])
                    p = self._glyphs[-1].glyphs[-1][3]
                else:
                    f = []
                    p = (self.text[startindex][1], startindex)
                    
                try:
                    paragraphclass = fonts.paragraph_classes[p[0]]
                except KeyError:
                    # happens if requested style is not defined
                    p, paragraphclass = _fail_class(startindex, l, (p[0],))

                    
            except IndexError:
                pass

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
                    fonts.get_leading(p[0])
                    )
            
            # get the index of the last glyph printed (while printing said line) so we know where to start next time
            startindex = line.build_line()
            # check for paragraph break (which returns a negative version of startindex)
            if startindex < 0:

                startindex = abs(startindex) - 1
                y += fonts.get_leading(p[0]) + fonts.get_margin_bottom(p[0])
                
                if startindex > len(self.text) - 1:
                    self._glyphs.append(line)
                    del line
                    # this is the end of the document
                    break
            else:
                y += fonts.get_leading(p[0])
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
        glyphindex = bisect.bisect([glyph[1] for glyph in self._glyphs[l].glyphs], x )
        # determine x position of glyph before it
        glyphx = self._glyphs[l].glyphs[glyphindex - 1][1]
        # if click is closer to it, shift glyph index left one
        try:
            if abs(x - glyphx) < abs(x - self._glyphs[l].glyphs[glyphindex][1]):
                glyphindex += -1
        except IndexError:
            if l + 1 == len(self._glyphs):
                glyphindex = len(self._glyphs[l].glyphs)

            else:
                glyphindex = len(self._glyphs[l].glyphs) - 1

            
        return glyphindex + self._glyphs[l].startindex

    # get line number given character index
    def index_to_line(self, index):
        return bisect.bisect([line.startindex for line in self._glyphs], index ) - 1

    def take_selection(self):
        if self.cursor.cursor == self.select.cursor:
            return False
        else:
            posts = sorted([self.cursor.cursor, self.select.cursor])

            return self.text[posts[0]:posts[1]]

    def delete(self, start=None, end=None):
    
        # idiotproofing
        if start is None:
            start = self.cursor.cursor - 1
        elif end is None:
            end = start + 1
            
        if end is None:
            end = self.cursor.cursor
        elif start is None:
            start = end - 1

        if start > end:
            start, end = end, start


        if [character(e) for e in self.text[start:end]] == ['</p>', '<p>']:
            del self.text[start:end]
        
        else:
            # delete every PAIRED paragraph block
            ptags = [ e for e in self.text[start:end] if character(e) in ['<p>', '</p>'] ]
            del self.text[start:end]

            outside = outside_tag(ptags)
            if outside:
                self.text[start:start] = outside
    #            if character(outside) == '<p>':
    #                start += 1

        self._recalculate()
        self.cursor.set_cursor(start, self.text)
        self.select.cursor = self.cursor.cursor


    def insert(self, segment):
        if self.take_selection():
            self.delete(self.cursor.cursor, self.select.cursor)
            self.cursor.set_cursor( min(self.select.cursor, self.cursor.cursor) , self.text)
            
        self.text[self.cursor.cursor:self.cursor.cursor] = segment
        self._recalculate()
        self.cursor.skip(len(segment), self.text)
        self.select.cursor = self.cursor.cursor
    
    def match_cursors(self):
        self.select.cursor = self.cursor.cursor

    ### FUNCTIONS USEFUL FOR DRAWING AND INTERFACE
            
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

    def line_data(self, l):
        anchor = self._glyphs[l].anchor
        stop = self._glyphs[l].stop
        leading = self._glyphs[l].leading
        y = self._glyphs[l].y
        return anchor, stop, leading, y

    def extract_glyphs(self, xx, yy):
        if not self.sorted_glyphs:
            for line in self._glyphs:
                p_name = line.glyphs[0][3][0]
                for glyph in line.glyphs:
                    f = glyph[4]
                    try:
                        self.sorted_glyphs[(p_name, f)].append((glyph[0], glyph[1] + xx, glyph[2] + yy))
                    except KeyError:
                        self.sorted_glyphs[(p_name, f)] = []
                        self.sorted_glyphs[(p_name, f)].append((glyph[0], glyph[1] + xx, glyph[2] + yy))
        return self.sorted_glyphs
        
