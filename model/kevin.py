import html, itertools

from pyparsing import Word, Suppress, CharsNotIn, nums, alphanums, dictOf

from model import table

from bulletholes.counter import TCounter as Counter
from fonts import styles

def _parse_tag(tag):
    int_value = Word(nums)
    str_value = Suppress("\"") + CharsNotIn("\"") + Suppress("\"")
    value = int_value | str_value
    identifier = Word(alphanums)
    result = dictOf(identifier + Suppress("="), value)

    return result.parseString(tag).asDict()

def serialize(text):
    b = text.copy()
    for e, entity in enumerate(b):
        if not isinstance(entity, str):
            if entity[0] == '<f>':
                if entity[1].name == 'emphasis':
                    b[e] = '<em>'
                elif entity[1].name == 'strong':
                    b[e] = '<strong>'
                else:
                    b[e] = '<f class="' + entity[1].name + '">'
            
            elif entity[0] == '</f>':
                if entity[1].name == 'emphasis':
                    b[e] = '</em>'
                elif entity[1].name == 'strong':
                    b[e] = '</strong>'
                else:
                    b[e] = '</f class="' + entity[1].name + '">'
            
            elif entity[0] == '<p>':
                if entity[1] != {styles.PTAGS['body']}:
                    b[e] = '<p class="' + '&'.join(itertools.chain.from_iterable((P.name for i in range(V)) for P, V in entity[1].items())) + '">'
                else:
                    b[e] = '<p>'

            elif entity[0] == '<image>':
                source, width = entity[1]
                b[e] = '<image src="' + source + '" width="' + str(width) + '">'
            
            elif entity[0] == '<td>':
                b[e] = '<td rowspan="' + str(entity[1]) + '" colspan="' + str(entity[2]) + '">'

            elif entity[0] == '<table>':
                b[e] = '<table>' + serialize(entity.flatten()) + '</table>'

        elif entity == '<':
            b[e] = '&lt;'
        elif entity == '>':
            b[e] = '&gt;'

#        elif entity == '</p>':
#            b[e] = '</p>\n'

    return ''.join(b)

def _parse_entities(b):
    gap_end = {'</table>', '</p>'}
    whitespace = {' ', '\n', '<br>', '\t'}
    b = b.copy()
    build = []
    while True:
        try:
            opentag = b.index('<')
            closetag = b.index('>') + 1
        except ValueError:
            break

        build += list(html.unescape(''.join(b[:opentag])))
        entity = ''.join(b[opentag:closetag])
        
        content = entity[1:-1].strip()
        first_space = content.find(' ')
        if first_space == -1:
            tag = content
            fields = {}
        else:
            tag = content[:first_space]
            R = content[first_space + 1:]
            fields = _parse_tag(R)
        
        if tag == 'p':
            # clear the gap
            try:
                gap_begin = next(len(build) - i for i, v in enumerate(reversed(build)) if type(v) is str and v in gap_end)
                if all(type(e) is str and e in whitespace for e in build[gap_begin:]):
                    del build[gap_begin:]
            except StopIteration:
                pass
            
            if 'class' in fields:
                ptags = Counter(styles.PTAGS[T.strip()] for T in fields['class'].split('&'))
            else:
                ptags = Counter({styles.PTAGS['body']: 1})
            build.append(['<p>', ptags])
            del b[:closetag]
        
        elif tag in {'f', '/f'}:
            ftag = styles.FTAGS[fields['class']]
            build.append(('<' + tag + '>', ftag))
            del b[:closetag]
        
        elif tag == 'image':
            build.append(('<image>', (fields['src'], int(fields['width']))))
            del b[:closetag]
        
        elif tag == 'table':
            del b[:closetag]
            # recursivity
            data, b = _parse_entities(b)
            build.append(table.Table(fields, data))
            
        elif tag == '/table':
            del b[:closetag]
            return build, b
        
        elif tag == 'td':
            if 'rowspan' in fields:
                rs = int(fields['rowspan'])
            else:
                rs = 1
            if 'colspan' in fields:
                cs = int(fields['colspan'])
            else:
                cs = 1
            build.append(('<td>', rs, cs))
            del b[:closetag]
        
        else:
            build.append(entity)
            del b[:closetag]
            
    build += list(html.unescape(''.join(b)))
    # clear the gap
    try:
        gap_begin = next(len(build) - i for i, v in enumerate(reversed(build)) if type(v) is str and v in gap_end)
        if all(type(e) is str and e in whitespace for e in build[gap_begin:]):
            del build[gap_begin:]
    except StopIteration:
        pass
    
    return build, []

def deserialize(string):
    string = string.replace('\u000A\u000A', '</p><p>')
    string = string.replace('\u000A', '<br>')
    string = string.replace('<em>', '<f class="emphasis">')
    string = string.replace('</em>', '</f class="emphasis">')
    string = string.replace('<strong>', '<f class="strong">')
    string = string.replace('</strong>', '</f class="strong">')

    return _parse_entities(list(string))[0]
