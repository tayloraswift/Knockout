import meredith

import text_t
from text_t import character
import cairo
import math
import ui


# creates some font options
nohints = cairo.FontOptions()
nohints.set_hint_style(cairo.HINT_STYLE_NONE)

def draw_text(cr):
    # prints text
    
    for tract in meredith.mere.tracts:
        classed_glyphs = tract.extract_glyphs(200, 100)

        cr.set_font_options(nohints)
        for name, glyphs in classed_glyphs.items():
            cr.set_source_rgb(0, 0, 0)
            try:
                cr.set_font_size(text_t.paragraphclasses[name[0]].fontclasses[name[1]].fontsize)
                cr.set_font_face(text_t.paragraphclasses[name[0]].fontclasses[name[1]].font)
            except KeyError:
                cr.set_source_rgb(1, 0.15, 0.2)
                cr.set_font_size(text_t.paragraphclasses[name[0]].fontclasses[()].fontsize)
                cr.set_font_face(text_t.paragraphclasses[name[0]].fontclasses[()].font)

            cr.show_glyphs(glyphs)
            
        del classed_glyphs
    

def draw_channels(cr, x, y, highlight=False, radius=0):

    for channel in meredith.mere.tracts[meredith.mere.t].channels.channels:
        
        entrance = ui.Broken_bar(round(channel.railings[0][0][0] + 200), 
                round(channel.railings[0][0][1] - 5 + 100),
                round(channel.railings[1][0][0] + 200),
                0.3, 0.3, 0.3, 0.5, highlight, radius)
        portal = ui.Broken_bar(round(channel.railings[0][-1][0] + 200), 
                round(channel.railings[1][-1][1] + 100),
                round(channel.railings[1][-1][0] + 200),
                1, 0, 0.1, 0.5, highlight, radius)
        entrance.draw(cr, x, y)
        portal.draw(cr, x, y)

def _get_fontsize(p, f):
    try:
        fontsize = text_t.paragraphclasses[p].fontclasses[f].fontsize
    except KeyError:
        fontsize = text_t.paragraphclasses[p].fontclasses[()].fontsize
    return fontsize
    
def draw_annotations(cr):
    
    
    specials = [i for i, entity in enumerate(meredith.mere.text()) if character(entity) in ['<p>', '</p>', '<br>', '<f>', '</f>']]
    
    cr.set_source_rgba(0, 0, 0, 0.4)
    for i in specials:
            
        if character(meredith.mere.text()[i]) == '<p>':
            x, y, p, f = meredith.mere.tracts[meredith.mere.t].text_index_location(i)
            x = round(x + 200)
            y = round(y + 100)
            fontsize = _get_fontsize(p, f)
            
            cr.move_to(x, y)
            cr.rel_line_to(0, round(-fontsize))
            cr.rel_line_to(-3, 0)
            cr.rel_line_to(-3, round(fontsize)/2)
            cr.line_to(x - 3, y)
            cr.close_path()
            cr.fill()
        elif character(meredith.mere.text()[i]) == '<br>':
            x, y, p, f = meredith.mere.tracts[meredith.mere.t].text_index_location(i + 1)
            fontsize = _get_fontsize(p, f)
            x = round(x + 200)
            y = round(y + 100)
            cr.rectangle(x - 6, y - round(fontsize), 3, round(fontsize))
            cr.rectangle(x - 10, y - 3, 4, 3)
            cr.fill()
        
        elif character(meredith.mere.text()[i]) == '<f>':
            x, y, p, f = meredith.mere.tracts[meredith.mere.t].text_index_location(i)
            fontsize = _get_fontsize(p, f)
            x = round(x + 200)
            y = round(y + 100)
            
            cr.move_to(x, y - fontsize)
            cr.rel_line_to(0, 6)
            cr.rel_line_to(-1, 0)
            cr.rel_line_to(-3, -6)
            cr.close_path()
            cr.fill()

        elif character(meredith.mere.text()[i]) == '</f>':
            x, y, p, f = meredith.mere.tracts[meredith.mere.t].text_index_location(i)
            fontsize = _get_fontsize(p, f)
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

    posts = sorted(list(meredith.mere.selection()))

    firstline = meredith.mere.tracts[meredith.mere.t].index_to_line(posts[0])
    lastline = meredith.mere.tracts[meredith.mere.t].index_to_line(posts[1])


    start = meredith.mere.tracts[meredith.mere.t].text_index_location(posts[0])[0]
    
    linenumber = firstline
    while True:
        if linenumber != firstline:
            start = meredith.mere.tracts[meredith.mere.t].glyphs[linenumber].anchor
        
        stop = meredith.mere.tracts[meredith.mere.t].glyphs[linenumber].stop

        if linenumber == lastline:
            stop = meredith.mere.tracts[meredith.mere.t].text_index_location(posts[1])[0]

        leading = meredith.mere.tracts[meredith.mere.t].glyphs[linenumber].leading
        
        cr.rectangle(round(200 + start), 
                round(100 + meredith.mere.tracts[meredith.mere.t].glyphs[linenumber].y - leading), 
                stop - start, 
                leading)
        linenumber += 1

        if linenumber > lastline:
            break
    cr.fill() 

    # print cursors
    cr.set_source_rgb(1, 0.2, 0.6)
    cx, cy, p, f = meredith.mere.tracts[meredith.mere.t].text_index_location(meredith.mere.active_cursor())

    cr.rectangle(round(200 + cx - 1), 
                round(100 + cy - text_t.paragraphclasses[p].leading), 
                2, 
                text_t.paragraphclasses[p].leading)
    # special cursor if adjacent to font tag
    if character(meredith.mere.at(0)) in ['<f>', '</f>']:
        cr.rectangle(round(200 + cx - 3), 
                round(100 + cy - text_t.paragraphclasses[p].leading), 
                4, 
                2)
        cr.rectangle(round(200 + cx - 3), 
                round(100 + cy), 
                4, 
                2)
    if character(meredith.mere.at(-1)) in ['<f>', '</f>']:
        cr.rectangle(round(200 + cx - 1), 
                round(100 + cy - text_t.paragraphclasses[p].leading), 
                4, 
                2)
        cr.rectangle(round(200 + cx - 1), 
                round(100 + cy), 
                4, 
                2)
    cr.fill()


    cx, cy, p, f = meredith.mere.tracts[meredith.mere.t].text_index_location(meredith.mere.active_select())

    cr.rectangle(round(200 + cx - 1), 
                round(100 + cy - text_t.paragraphclasses[p].leading), 
                2, 
                text_t.paragraphclasses[p].leading)
    # special cursor if adjacent to font tag
    if character(meredith.mere.at_select(0)) in ['<f>', '</f>']:
        cr.rectangle(round(200 + cx - 3), 
                round(100 + cy - text_t.paragraphclasses[p].leading), 
                4, 
                2)
        cr.rectangle(round(200 + cx - 3), 
                round(100 + cy), 
                4, 
                2)
    if character(meredith.mere.at_select(-1)) in ['<f>', '</f>']:
        cr.rectangle(round(200 + cx - 1), 
                round(100 + cy - text_t.paragraphclasses[p].leading), 
                4, 
                2)
        cr.rectangle(round(200 + cx - 1), 
                round(100 + cy), 
                4, 
                2)
    cr.fill()
    


def draw_railings(cr, x, y):
    for channel in meredith.mere.tracts[meredith.mere.t].channels.channels:
        for railing in channel.railings:
            ui.Interactive_Line([(p[0] + 200, p[1] + 100) for p in railing], 0, 0, 0, 0.3, 2, 3, 20).draw(cr, x, y)
            # draw selections
            for p in railing:
                if p[2]:
                    cr.arc(p[0] + 200, p[1] + 100, 5, 0, 2*math.pi)
                    cr.set_line_width(1)
                    cr.stroke()
