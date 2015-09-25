import meredith
import olivia
import fonts
from text_t import character
import cairo
import math
import ui


# creates some font options
nohints = cairo.FontOptions()
nohints.set_hint_style(cairo.HINT_STYLE_NONE)

def draw_text(cr):
    # prints text
    
    for tract in meredith.mipsy.tracts:
        classed_glyphs = tract.extract_glyphs(200, 100)

        cr.set_font_options(nohints)
        for name, glyphs in classed_glyphs.items():
            cr.set_source_rgb(0, 0, 0)
            try:
                cr.set_font_size(fonts.paragraph_classes[name[0]].fontclasses[name[1]].fontsize)
                cr.set_font_face(fonts.paragraph_classes[name[0]].fontclasses[name[1]].font)
            except KeyError:
                cr.set_source_rgb(1, 0.15, 0.2)
                cr.set_font_size(fonts.paragraph_classes[name[0]].fontclasses[()].fontsize)
                cr.set_font_face(fonts.paragraph_classes[name[0]].fontclasses[()].font)

            cr.show_glyphs(glyphs)
            
        del classed_glyphs

def _get_fontsize(p, f):
    try:
        fontsize = fonts.paragraph_classes[p].fontclasses[f].fontsize
    except KeyError:
        fontsize = fonts.paragraph_classes[p].fontclasses[()].fontsize
    return fontsize
    
def draw_annotations(cr):
    
    
    specials = [i for i, entity in enumerate(meredith.mipsy.text()) if character(entity) in ['<p>', '</p>', '<br>', '<f>', '</f>']]
    
    cr.set_source_rgba(0, 0, 0, 0.4)
    for i in specials:
            
        if character(meredith.mipsy.text()[i]) == '<p>':
            x, y, p, f = meredith.mipsy.tracts[meredith.mipsy.t].text_index_location(i)
            if i == meredith.mipsy.glyph_at(0)[2][1]:
                cr.set_source_rgba(1, 0.2, 0.6, 0.7)
            else:
                cr.set_source_rgba(0, 0, 0, 0.4)
            x = round(x + 200)
            y = round(y + 100)
            fontsize = _get_fontsize(p[0], f)
            
            cr.move_to(x, y)
            cr.rel_line_to(0, round(-fontsize))
            cr.rel_line_to(-3, 0)
            cr.rel_line_to(-3, round(fontsize)/2)
            cr.line_to(x - 3, y)
            cr.close_path()
            cr.fill()
        elif character(meredith.mipsy.text()[i]) == '<br>':
            x, y, p, f = meredith.mipsy.tracts[meredith.mipsy.t].text_index_location(i + 1)
            fontsize = _get_fontsize(p[0], f)
            x = round(x + 200)
            y = round(y + 100)
            cr.rectangle(x - 6, y - round(fontsize), 3, round(fontsize))
            cr.rectangle(x - 10, y - 3, 4, 3)
            cr.fill()
        
        elif character(meredith.mipsy.text()[i]) == '<f>':
            x, y, p, f = meredith.mipsy.tracts[meredith.mipsy.t].text_index_location(i)
            fontsize = _get_fontsize(p[0], f)
            x = round(x + 200)
            y = round(y + 100)
            
            cr.move_to(x, y - fontsize)
            cr.rel_line_to(0, 6)
            cr.rel_line_to(-1, 0)
            cr.rel_line_to(-3, -6)
            cr.close_path()
            cr.fill()

        elif character(meredith.mipsy.text()[i]) == '</f>':
            x, y, p, f = meredith.mipsy.tracts[meredith.mipsy.t].text_index_location(i)
            fontsize = _get_fontsize(p[0], f)
            x = round(x + 200)
            y = round(y + 100)
            
            cr.move_to(x, y - fontsize)
            cr.rel_line_to(0, 6)
            cr.rel_line_to(1, 0)
            cr.rel_line_to(3, -6)
            cr.close_path()
            cr.fill()
            

def draw_cursors(cr):
    # print highlights

    cr.set_source_rgba(0, 0, 0, 0.1)

    posts = sorted(list(meredith.mipsy.selection()))

    firstline = meredith.mipsy.tracts[meredith.mipsy.t].index_to_line(posts[0])
    lastline = meredith.mipsy.tracts[meredith.mipsy.t].index_to_line(posts[1])


    start = meredith.mipsy.tracts[meredith.mipsy.t].text_index_location(posts[0])[0]
    
    linenumber = firstline
    while True:
        if linenumber != firstline:
            start = meredith.mipsy.tracts[meredith.mipsy.t].glyphs[linenumber].anchor
        
        stop = meredith.mipsy.tracts[meredith.mipsy.t].glyphs[linenumber].stop

        if linenumber == lastline:
            stop = meredith.mipsy.tracts[meredith.mipsy.t].text_index_location(posts[1])[0]

        leading = meredith.mipsy.tracts[meredith.mipsy.t].glyphs[linenumber].leading
        
        cr.rectangle(round(200 + start), 
                round(100 + meredith.mipsy.tracts[meredith.mipsy.t].glyphs[linenumber].y - leading), 
                stop - start, 
                leading)
        linenumber += 1

        if linenumber > lastline:
            break
    cr.fill() 

    # print cursors
    cr.set_source_rgb(1, 0.2, 0.6)
    cx, cy, p, f = meredith.mipsy.tracts[meredith.mipsy.t].text_index_location(meredith.mipsy.active_cursor())

    cr.rectangle(round(200 + cx - 1), 
                round(100 + cy - fonts.paragraph_classes[p[0]].leading), 
                2, 
                fonts.paragraph_classes[p[0]].leading)
    # special cursor if adjacent to font tag
    if character(meredith.mipsy.at(0)) in ['<f>', '</f>']:
        cr.rectangle(round(200 + cx - 3), 
                round(100 + cy - fonts.paragraph_classes[p[0]].leading), 
                4, 
                2)
        cr.rectangle(round(200 + cx - 3), 
                round(100 + cy), 
                4, 
                2)
    if character(meredith.mipsy.at(-1)) in ['<f>', '</f>']:
        cr.rectangle(round(200 + cx - 1), 
                round(100 + cy - fonts.paragraph_classes[p[0]].leading), 
                4, 
                2)
        cr.rectangle(round(200 + cx - 1), 
                round(100 + cy), 
                4, 
                2)
    cr.fill()


    cx, cy, p, f = meredith.mipsy.tracts[meredith.mipsy.t].text_index_location(meredith.mipsy.active_select())

    cr.rectangle(round(200 + cx - 1), 
                round(100 + cy - fonts.paragraph_classes[p[0]].leading), 
                2, 
                fonts.paragraph_classes[p[0]].leading)
    # special cursor if adjacent to font tag
    if character(meredith.mipsy.at_select(0)) in ['<f>', '</f>']:
        cr.rectangle(round(200 + cx - 3), 
                round(100 + cy - fonts.paragraph_classes[p[0]].leading), 
                4, 
                2)
        cr.rectangle(round(200 + cx - 3), 
                round(100 + cy), 
                4, 
                2)
    if character(meredith.mipsy.at_select(-1)) in ['<f>', '</f>']:
        cr.rectangle(round(200 + cx - 1), 
                round(100 + cy - fonts.paragraph_classes[p[0]].leading), 
                4, 
                2)
        cr.rectangle(round(200 + cx - 1), 
                round(100 + cy), 
                4, 
                2)
    cr.fill()
    
def draw_channel_controls(cr, show_rails=False):
    olivia.dibbles.render(cr, show_rails)

