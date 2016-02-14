import bisect
from itertools import chain

from model.olivia import Atomic_text, Block
from model.george import Swimming_pool
from interface.base import accent

def _print_td(td):
        A = td[1]
        if 'rowspan' not in A or A['rowspan'] == 1:
            if 'colspan' not in A or A['colspan'] == 1:
                return '<td>'
            else:
                return '<td colspan="' + A['colspan'] + '">'
        else:
            if 'colspan' not in A or A['colspan'] == 1:
                return '<td rowspan="' + A['rowspan'] + '">'
            else:
                return '<td rowspan="' + A['rowspan'] + '" colspan="' + A['colspan'] + '">'

class _Table_cell(Atomic_text):
    def __init__(self, text, rowspan, colspan):
        Atomic_text.__init__(self, text)
        self.rs = rowspan
        self.cs = colspan
    
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
    return max(cell._SLUGS[-1]['y'] for cell in cells)

def _build_matrix(data):
    MATRIX = Matrix()
    length = 0
    for i, row in enumerate(data):
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
    return MATRIX

class Table(object):
    def __init__(self, L):
        self._table = L
        self.data = [[_Table_cell(C, int(td[1].get('rowspan', 1)), int(td[1].get('colspan', 1))) for td, C in R] for tr, R in L[1]]
        self._FLOW = [cell for row in self.data for cell in row]
        self._MATRIX = _build_matrix(self.data)
    
    def represent(self, serialize, indent):
        lines = [[indent, '<table>']]
        for tr, R in self._table[1]:
            lines.append([indent + 1, '<tr>'])
            for td, C in R:
                lines.append([indent + 2, _print_td(td)])
                lines.extend(serialize(C, indent + 3))
                lines.append([indent + 2, '</td>'])
            lines.append([indent + 1, '</tr>'])
        lines.append([indent, '</table>'])
        return lines

    def fill(self, bounds, c, y):
        top = y
        row_y = []
        for r, row in enumerate(self.data):
            cellcount = len(self._MATRIX[r])
            for cell in row:
                # calculate percentages
                cellbounds = TCell_container(bounds, cell.col/cellcount, (cell.col + cell.cs)/cellcount)
                cell.cast(cellbounds, c, y)
            y = _row_height(self.data, r, y)
            row_y.append(y)
        
        return _MBlock(self._FLOW, self._MATRIX, bounds, top, y, row_y)

class _MBlock(Block):
    def __init__(self, FLOW, matrix, bounds, top, bottom, row_y):
        x1, x2 = bounds.bounds(top)
        Block.__init__(self, FLOW, top, bottom, x1, x2)
        
        self._matrix = matrix
        self._row_y = row_y
        self._bounds = bounds

    def _print_annot(self, cr, O):
        if O in self._FLOW:
            cr.set_source_rgb( * accent)
            cl = len(self._matrix[0])
            for r, y in enumerate(self._row_y[:-1]):
                x1, x2 = self._bounds.bounds(y)
                cw = (x2 - x1)/cl
                for c in range(1, cl):
                    cr.rectangle(int(x1 + cw*c), y - 3, 1, 7)
                    cr.rectangle(int(x1 + cw*c) - 3, y, 7, 1)
            cr.fill()

    def I(self, x, y):
        x1, x2 = self._bounds.bounds(y)
        r = bisect.bisect(self._row_y, y)
        c = int((x - x1) // ((x2 - x1) / len(self._matrix[r])))
        try:
            return self._matrix[r][c]
        except IndexError:
            print('Empty cell selected')
            return self['j']

    def deposit(self, repository):
        for A in self._FLOW:
            A.deposit(repository)
        repository['_paint_annot'].append(self._print_annot)
