import bisect
from itertools import chain

from model.cat import typeset_liquid
from model.olivia import Atomic_text
from model.george import Swimming_pool
from bulletholes.counter import TCounter as Counter

from elements.elements import Paragraph, OpenFontpost, CloseFontpost, Image

class CellPost(object):
    def __init__(self, rowspan, colspan):
        self.rowspan = rowspan
        self.colspan = colspan
    def __str__(self):
        return '<td>'

    def __repr__(self):
        if self.rowspan == 1:
            if self.colspan == 1:
                return '<td>'
            else:
                return '<td colspan="' + str(self.colspan) + '">'
        else:
            if self.colspan == 1:
                return '<td rowspan="' + str(self.rowspan) + '">'
            else:
                return '<td rowspan="' + str(self.rowspan) + '" colspan="' + str(self.colspan) + '">'

    def __len__(self):
        return 4

def _bin(data, odelimit, cdelimit):
    for i, v in ((i, v) for i, v in enumerate(data) if str(v) == odelimit):
        try:
            j = data[i:].index(cdelimit) + i
        except ValueError:
            print('unclosed bin')
            continue
        
        bindata = data[i + 1:j]
        if odelimit not in bindata:
            yield [v] + bindata + [cdelimit]
        else:
            print('superfluous bin tag')
            continue

class _Table_cell(Atomic_text):
    def __init__(self, text):
        Atomic_text.__init__(self, text[1:-1])
        self.rs = text[0].rowspan
        self.cs = text[0].colspan
    
    def nail(self, i, j):
        self.col = j
        self.row = i


class TCell_container(Swimming_pool):
    def __init__(self, SP, i, j):
        Swimming_pool.__init__(self, SP.railings, SP.page)
        self.i = i
        self.j = j
    
    def bounds(self, y):
        x1 = self.edge(0, y)[0]
        advance = self.edge(1, y)[0] - x1
        return x1 + advance*self.i, x1 + advance*self.j

class Matrix(list):
    def __str__(self):
        M = []
        for row in self:
            R = ''
            for cell in row:
                if cell is None:
                    C = '|    None    |'
                else:
                    value = ''.join(c for c in cell.text if isinstance(c, str))
                    C = '|' + value + '            |'[len(value):]
                R += C
            M.append(R)
        return '\n'.join(M)

def _row_height(data, r, y):
    cells = (cell for cell in chain.from_iterable(row for row in data) if cell.row + cell.rs - 1 == r)
    return max(cell._SLUGS[-1]['y'] + cell._SLUGS[-1]['leading'] for cell in cells)

class Table(object):
    def __init__(self, fields, data):
        self.fields = fields
        # process table structure
        # build rows
        self.data = [list(_Table_cell(C) for C in _bin(R, '<td>', '</td>')) for R in _bin(data, '<tr>', '</tr>')]
        self._build_matrix()

    def flatten(self):
        L = []
        for row in self.data:
            L.append('<tr>')
            for cell in row:
                L.extend([CellPost(cell.rs, cell.cs)] + cell.text + ['</td>'])
            L.append('</tr>')
            
        return L

    def _build_matrix(self):
        MATRIX = Matrix()
        length = 0
        for i, row in enumerate(self.data):
            # append rows to matrix if needed
            height = max(r.rs for r in row)
            if i + height > len(MATRIX):
                MATRIX += [[None] for k in range(i + height - len(MATRIX))]

            # extend matrix to fit the width
            length = max(length, sum(r.cs for r in row) + sum(k is not None for k in MATRIX[i]))
            empty = [None] * length
            if length > len(MATRIX[-1]):
                MATRIX[:] = [R + empty[:max(0, length - len(R))] for R in MATRIX]
            
            # drop in cells
            _cellnumber_ = 0
            for s, slot in enumerate(MATRIX[i]):
                # check if cell is occupied
                if slot is None:
                    try:
                        cell = row[_cellnumber_]
                        _cellnumber_ += 1
                    except IndexError:
                        break
                    cell.nail(i, s)
                    for rs in range(cell.rs):
                        for cs in range(cell.cs):
                            MATRIX[i + rs][s + cs] = cell
            
        print(MATRIX)
        self._MATRIX = MATRIX

    def fill(self, bounds, c, y):
        return Atomic_table(self._MATRIX, self.data, bounds, c, y)

class Atomic_table(dict):
    def __init__(self, matrix, data, bounds, c, y):
        self._matrix = matrix
        self._cells = [cell for row in data for cell in row]
        top = y
        row_y = []
        for r, row in enumerate(data):
            cellcount = len(self._matrix[r])
            for cell in row:
                # calculate percentages
                cellbounds = TCell_container(bounds, cell.col/cellcount, (cell.col + cell.cs)/cellcount)
                cell._SLUGS[:] = typeset_liquid(cellbounds, cell.text, {'j': 0, 'l': -1, 'P_BREAK': True}, 0, y, c, False)
                cell._precompute_search()
            y = _row_height(data, r, y)
            row_y.append(y)
        
        x1, x2 = bounds.bounds(top)
        self['x'] = x1
        self['width'] = x2 - x1
        self['y'] = y
        self['leading'] = y - top
        self['GLYPHS'] = [(-2, 0, y, None, None, x2 - x1)]
        self['P_BREAK'] = True
        self['PP'] = Paragraph(Counter())
        
        self['_row_y'] = row_y
        self['_bounds'] = bounds
        self['_cellcount'] = cellcount
    
    def I(self, x, y):
        x1, x2 = self['_bounds'].bounds(y)
        r = bisect.bisect(self['_row_y'], y)
        c = int((x - x1) // ((x2 - x1) / self['_cellcount']))
        try:
            return self._matrix[r][c]
        except IndexError:
            print('Empty cell selected')
            return self['j']

    def collect_text(self):
        return list(chain.from_iterable(cell.collect_text() for cell in self._cells))
    
    def deposit(self, repository):
        for cell in self._cells:
            cell.deposit(repository)
