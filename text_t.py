import bisect
import itertools
import operator

import freetype

import channels

import kevin
import errors

import pycairo_font

ordinalmap = {
        'other': -1,
        '<br>': -2,
        '<p>': -3,
        '</p>': -4,
        
        '<f>': -5,
        '</f>': -6
        }

# extended fontface class
class FFace(freetype.Face):
    
    def advance_width(self, character):
        avw = 1000
        if len(character) == 1:
            avw = self.get_advance(self.get_char_index(character), True)
        elif character == '<br>':
            avw = 0
        elif character == '<p>':
            avw = 0
        
        elif character in ['<f>', '</f>']:
            avw = 0
        
        return avw
        
class TypeClass(object):
    def __init__(self, fontpath, fontsize):
        self.path = fontpath
        self.fontface = FFace(fontpath)
        self.fontsize = fontsize
        
        self.font = pycairo_font.create_cairo_font_face_for_file(self.path)
    
    def character_index(self, c):
        try:
            return (self.fontface.get_char_index(c))
        except TypeError:
            return ordinalmap[c]
    
    def glyph_width(self, c):
        return self.fontface.advance_width(c)/self.fontface.units_per_EM*self.fontsize

class ParagraphClass(object):
    def __init__(self, fontclasses, lineheight, margin_bottom):
        self.fontclasses = fontclasses
        self.lineheight = lineheight
        self.margin_bottom = margin_bottom
        
        try:
            self.leading = lineheight * self.fontclasses[()].fontsize
        except KeyError:
            self.leading = lineheight * max([v.fontsize for v in self.fontclasses.values()])
            print('No "none" style found!')

fontclasses_a = {
        (): TypeClass("/home/kelvin/.fonts/Proforma-Book.otf", 15),
        ('caption',): TypeClass("/home/kelvin/.fonts/NeueFrutiger45.otf", 13),
        ('emphasis',): TypeClass("/home/kelvin/.fonts/Proforma-BookItalic.otf", 15),
        ('strong',): TypeClass("/home/kelvin/.fonts/Proforma-Bold.otf", 15),
        ('emphasis', 'strong',): TypeClass("/home/kelvin/.fonts/Proforma-BoldItalic.otf", 15)
}

fontclasses_b = {
        (): TypeClass("/home/kelvin/.fonts/NeueFrutiger45.otf", 18),
        ('caption',): TypeClass("/home/kelvin/.fonts/NeueFrutiger45.otf", 15),
        ('emphasis',): TypeClass("/home/kelvin/.fonts/NeueFrutiger45Italic.otf", 18),
        ('strong',): TypeClass("/home/kelvin/.fonts/NeueFrutiger65.otf", 18),
        ('emphasis', 'strong'): TypeClass("/home/kelvin/.fonts/NeueFrutiger65Italic.otf", 18)
}

paragraphclasses = {}

paragraphclasses['body'] = ParagraphClass(fontclasses_a, 1.3, 5)
paragraphclasses['h1'] = ParagraphClass(fontclasses_b, 1.5, 10)


def character(entity):
    if not isinstance(entity, str):
        entity = entity[0]
    return entity

#def get_character(text, index):
#    entity = character(text[index])
#    return entity

def outside_tag(sequence, tags=('<p>', '</p>')):
    for i in reversed(range(len(sequence))):
        try:
            if character(sequence[i]) == tags[0] and character(sequence[i + 1]) == tags[1]:
                del sequence[i:i + 2]
        except IndexError:
            pass
    return sequence

        
class Textline(object):
    def __init__(self, text, anchor, stop, y, c, l, startindex, paragraphclass, fontclass, leading):
        self._paragraphclass_name = paragraphclass
        self._fontclass_names = fontclass
        try:
            self._fontclass = paragraphclasses[paragraphclass].fontclasses[tuple(fontclass)]
        except KeyError:
            self._fontclass = paragraphclasses[paragraphclass].fontclasses[()]

        # takes 1,989 characters starting from startindex
        self.sorts = text[startindex:startindex + 1989]
        
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

        # go by syllable until you reach the end
        index = self.startindex
        
        # lists that contain glyphs and specials
        self.glyphs = []
        self.special = []
        
        # start on the anchor
        x = self.anchor
        n = 0

        for entity in self.sorts:
            glyph = character(entity)
            glyphanchor = x
            
            if glyph == '<p>':
                if n > 0:
                    break
                else:
                
                    # load style from tag
#                    self.fontclass = fontclasses[entity[1]]
                    # retract x position
                    glyphanchor -= self._fontclass.fontsize
                    glyphwidth = 0
                    # add to special marks
                    self.special.append(('<p>', glyphanchor, self.y))

            elif glyph == '</p>':
                self.glyphs.append((self._fontclass.character_index(glyph), x, self.y, self._paragraphclass_name, tuple(self._fontclass_names)))
                # paragraph breaks are signaled by a negative index
                return (self.startindex + len(self.glyphs))*-1 - 1
                break

            elif glyph == '<f>':
                
                # look for negative classes
                if '~' + entity[1] in self._fontclass_names:
                    self._fontclass_names.remove('~' + entity[1])
                else:
                    self._fontclass_names.append(entity[1])
                    self._fontclass_names.sort()
                    
                try:
                    self._fontclass = paragraphclasses[self._paragraphclass_name].fontclasses[tuple(self._fontclass_names)]
                except KeyError:
                    # happens if requested style is not defined
                    errors.styleerrors.add_style_error(tuple(self._fontclass_names), self.l)
                    self._fontclass = paragraphclasses[self._paragraphclass_name].fontclasses[()]
            elif glyph == '</f>':
                try:
                    self._fontclass_names.remove(entity[1])
                    self._fontclass = paragraphclasses[self._paragraphclass_name].fontclasses[tuple(self._fontclass_names)]
                except (ValueError, KeyError):
                    # happens if the tag didn't exist
                    self._fontclass_names.append('~' + entity[1])
                    self._fontclass_names.sort()
                    errors.styleerrors.add_style_error(tuple(self._fontclass_names), self.l)
                    self._fontclass = paragraphclasses[self._paragraphclass_name].fontclasses[()]

#            print((self.paragraphclass_name, self.fontclass_names))
            glyphwidth = self._fontclass.glyph_width(glyph)
            self.glyphs.append((self._fontclass.character_index(glyph), glyphanchor, self.y, self._paragraphclass_name, tuple(self._fontclass_names)))
            
            
            if glyph == '<br>':
                break
            
            x += glyphwidth
            n = len(self.glyphs)
            
            # work out line breaks
            if x > self.stop:
                if glyph == ' ':
                    pass
                
                elif ' ' in self.sorts[:n]:
                    i = n - 2
                    while True:
                        if self.sorts[i] == ' ':
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
        
        self.glyphs = []
        
        # create cursor objects
        self.cursor = Cursor(self.text)
        self.select = Cursor(self.text)

        
    def _generate_lines(self, i, startindex):
        c = 0
        
        try:
            # ylevel is the y position of the first line to print
            # here we are removing the last existing line so we can redraw that one as well
            li = self.glyphs.pop(-1)
            y, c= li.y, li.c
            
        except IndexError:
            # which happens if nothing has yet been rendered

            p = self.text[0][1]
            f = []
            paragraphclass = paragraphclasses[p]
            y = self.channels.channels[c].railings[0][0][1] + paragraphclass.leading
        while True:
            # see if the lines have overrun the portals
            if y > self.channels.channels[c].railings[1][-1][1] and c < len(self.channels.channels) - 1:
                c += 1
                # shift to below entrance
                y = self.channels.channels[c].railings[0][0][1] + paragraphclass.leading
            
            try:
                if character(self.text[startindex]) != '<p>':
                    # extract last used style
                    f = list(self.glyphs[-1].glyphs[-1][4])
                    p = self.glyphs[-1].glyphs[-1][3]
                else:
                    f = []
                    p = self.text[startindex][1]
                paragraphclass = paragraphclasses[p]
            except IndexError:
                pass

            # generate line objects
            line = Textline(self.text, 
                    self.channels.channels[c].edge(0, y)[0], 
                    self.channels.channels[c].edge(1, y)[0], 
                    y, 
                    c,
                    i,
                    startindex,
                    p, 
                    f,
                    paragraphclass.leading
                    )
            
            # get the index of the last glyph printed (while printing said line) so we know where to start next time
            startindex = line.build_line()
            # check for paragraph break (which returns a negative version of startindex)
            if startindex < 0:

                startindex = abs(startindex) - 1
                y += paragraphclass.leading + paragraphclass.margin_bottom
                
                if startindex > len(self.text) - 1:
                    self.glyphs.append(line)
                    del line
                    break
            else:
                y += paragraphclass.leading
            i += 1
#            print (line.glyphs)
            self.glyphs.append(line)
            del line
#            if startindex >= len(self.text):
#                break

    def _recalculate(self):
        # avoid recalculating lines that weren't affected
        try:
            affected = self.index_to_line( min(self.select.cursor, self.cursor.cursor) ) - 1
            if affected < 0:
                affected = 0
            startindex = self.glyphs[affected].startindex
            self.glyphs = self.glyphs[:affected + 1]
            #        i = affected
            self._generate_lines(affected, startindex)
        except AttributeError:
            self.deep_recalculate()
        
        # tally errors
        errors.styleerrors.update(affected)
            

    def deep_recalculate(self):
        self.glyphs = []
        self._generate_lines(0, 0)
        
        # tally errors
        errors.styleerrors.update(0)
        
    def target_line(self, x, y, c=None):
        # find which channel is clicked on
        if c is None:
            c = self.channels.target_channel(x, y, 20)
        # get all y values
        yy = [textline for textline in self.glyphs if textline.c == c]
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
            print(l)
        # find first glyph to the right of click spot
        glyphindex = bisect.bisect([glyph[1] for glyph in self.glyphs[l].glyphs], x )
        # determine x position of glyph before it
        glyphx = self.glyphs[l].glyphs[glyphindex - 1][1]
        # if click is closer to it, shift glyph index left one
        try:
            if abs(x - glyphx) < abs(x - self.glyphs[l].glyphs[glyphindex][1]):
                glyphindex += -1
        except IndexError:
            if l + 1 == len(self.glyphs):
                glyphindex = len(self.glyphs[l].glyphs)

            else:
                glyphindex = len(self.glyphs[l].glyphs) - 1

#        if glyphindex == len(self.glyphs)
            
        return glyphindex + self.glyphs[l].startindex

    # get line number given character index
    def index_to_line(self, index):
        return bisect.bisect([line.startindex for line in self.glyphs], index ) - 1

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
        lineindex = self.index_to_line(index)
        try:
            glyph = self.glyphs[lineindex].glyphs[index - self.glyphs[lineindex].startindex]
        except IndexError:
            glyph = self.glyphs[lineindex].glyphs[-1]
            print ('ahead')
            ahead = True

        y = glyph[2]
        x = glyph[1]
        p = glyph[3]
        f = glyph[4]

#        if ahead:
#            x += self.Face.advance_width(character(self.text[index]))/1000*self.fontsize
        return (x, y, p, f)


    def extract_glyphs(self, xx, yy):
        classed_glyphs = {}
        for line in self.glyphs:

            for glyph in line.glyphs:
                p, f = glyph[3], glyph[4]
                if (p, f) not in classed_glyphs:
                    classed_glyphs[(p, f)] = []
                classed_glyphs[(p, f)].append((glyph[0], glyph[1] + xx, glyph[2] + yy))

        return classed_glyphs
        
