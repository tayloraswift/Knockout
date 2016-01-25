import html, itertools

from pyparsing import Word, Suppress, CharsNotIn, nums, alphanums, dictOf

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

        elif entity == '<':
            b[e] = '&lt;'
        elif entity == '>':
            b[e] = '&gt;'

    return ''.join(b)

def deserialize(string):

    b = list(string)
    while True:
        try:
            opentag = b.index('<')
            closetag = b.index('>')

        except ValueError:
            break
        entity = ''.join(b[opentag + 1:closetag])
        
        if entity == 'p':
            entity = ['<p>', Counter({styles.PTAGS['body']: 1}) ]
        elif entity == '/p':
            entity = '</p>'
        elif entity == 'em':
            entity = ('<f>', styles.FTAGS['emphasis'])
        elif entity == '/em':
            entity = ('</f>', styles.FTAGS['emphasis'])
        elif entity == 'strong':
            entity = ('<f>', styles.FTAGS['strong'])
        elif entity == '/strong':
            entity = ('</f>', styles.FTAGS['strong'])

        else:
            first_space = entity.find(' ')
            if first_space == -1:
                tag = entity
            else:
                tag = entity[:first_space]
                R = entity[first_space + 1:]
                fields = _parse_tag(R)

            if tag == 'p':
                ptags = Counter(styles.PTAGS[T.strip()] for T in fields['class'].split('&'))
                entity = ['<p>', ptags]
            
            elif tag in {'f', '/f'}:
                ftag = styles.FTAGS[fields['class']]
                entity = ('<' + tag + '>', ftag)
            
            elif tag == 'image':
                entity = ('<image>', (fields['src'], int(fields['width'])))
            
            else:
                entity = '<' + tag + '>'
        
        del b[opentag:closetag + 1]
        b.insert(opentag, entity)

    d = []
    for k, g in [(k, list(g)) for k, g in itertools.groupby(b, key=lambda e: 1 if len(e) != 1 else 2 if e == '\u000A' else 0)]:
        if k == 0:
            d += list(html.unescape(''.join(g)))
        elif k == 1:
            d += g
        elif k == 2:
            d += ['</p>', ['<p>', Counter({styles.PTAGS['body']: 1})]]

    return d
