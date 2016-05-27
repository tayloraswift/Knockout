from bisect import bisect
from itertools import chain, accumulate

from olivia.frames import Subcell
from interface.base import accent
from meredith.box import Box
from meredith.paragraph import Plane, Blockelement
from state.exceptions import LineOverflow

class Matrix(list):
    def __str__(self):
        M = []
        for row in self:
            R = ''
            for cell in row:
                if cell is None:
                    C = '|    None    |'
                else:
                    value = ''.join(c for c in cell.text if len(c) == 1)
                    C = '|' + value + '            |'[len(value):]
                R += C
            M.append(R)
        return '\n'.join(M)

def _build_matrix(data):
    MATRIX = Matrix()
    length = 0
    for i, row in enumerate(data):
        # append rows to matrix if needed
        height = max(r['rowspan'] for r in row)
        if i + height > len(MATRIX):
            MATRIX += [[None] for k in range(i + height - len(MATRIX))]

        # extend matrix to fit the width
        length = max(length, sum(r['colspan'] for r in row) + sum(k is not None for k in MATRIX[i]))
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
                for rs in range(cell['rowspan']):
                    for cs in range(cell['colspan']):
                        MATRIX[i + rs][s + cs] = cell
    return MATRIX

class Table_td(Plane):
    name = 'td'
    DNA = [('rowspan', 'int', 1), ('colspan', 'int', 1)]

    def nail(self, i, j):
        self.col = j
        self.row = i

class Table_tr(Box):
    name = 'tr'

class Table(Blockelement):
    name = 'table'

    DNA = [('class', 'blocktc', 'body'), ('distr', 'float tuple', ''), ('celltop', 'float', 0), ('cellbottom', 'float', 0), ('hrules', 'int set', set()), ('vrules', 'int set', set()), ('rulemargin', 'int', 0), ('rulewidth', 'float', 1),
            ('cl_table', 'blocktc', 'tablecell'), ('cl_thead', 'blocktc', 'emphasis'), ('cl_tleft', 'blocktc', 'emphasis')]

    def _load(self):
        self._CELLS = [tr.content for tr in self.content]
        self._MATRIX = _build_matrix(self._CELLS)
        self._FLOW = list(chain.from_iterable(self._CELLS))
        
        # columns
        cl = len(self._MATRIX[0])
        distr = [0] + [d if d else 1 for d in self['distr']]
        distr.extend([1] * (cl - len(distr) + 1))
        total = sum(distr)
        self._MATRIX.partitions = tuple(accumulate(d/total for d in distr))
        
        # rules
        r = len(self._MATRIX)
        self._table = {'rulemargin': self['rulemargin'], 'rulewidth': self['rulewidth'], 
                'hrules': [i for i in self['hrules'] if 0 <= i <= r], 
                'vrules': [i for i in self['vrules'] if 0 <= i <= cl]}

    def which(self, x, u, r):
        if (r > 1 or r < 0) and x > self.left_edge:
            x1, x2 = self._frames.at(u)
            R = bisect(self._row_u, u) - 1
            C = max(0, bisect(self._MATRIX.partitions, (x - x1) / (x2 - x1)) - 1)
            try:
                cell = self._MATRIX[R][C]
            except (IndexError, ValueError):
                return ()
            for m, tr in enumerate(self.content):
                for n, td in enumerate(tr.content):
                    if td is cell:
                        return ((m, tr), (n, td), * cell.which(x, u, r - 2))
        return ()


    
    def _layout_block(self, frames, BSTYLE, cascade, overlay):
        self._frames = frames
        
        P_table = self['cl_table']
        head = P_table + self['cl_thead']
        left = P_table + self['cl_tleft']
        
        row_u = [0] * (len(self._MATRIX) + 1)
        part = self._MATRIX.partitions
        cellbottom = self['cellbottom']
        for r, overlay, row in ((c, P_table, b) if c else (c, head, b) for c, b in enumerate(self._CELLS)):
            y = row_u[r] + self['celltop']
            for i, cell in enumerate(row):
                if not i:
                    ol = overlay + left
                else:
                    ol = overlay
                
                frames.save_u()
                cell.layout(Subcell(frames, part[cell.col], part[cell.col + cell['colspan']]), 
                            u = frames.read_u(), overlay = ol)
                bottom = frames.read_u() + cellbottom
                frames.restore_u()
                
                ki = r + cell['rowspan']
                if bottom > row_u[ki]:
                    row_u[ki] = bottom
            frames.start(row_u[r + 1])
        
        self._row_u = row_u
        """
        table = {'_row_y': row_y, '_bounds': bounds.bounds}
        table.update(self._table)
        # calculate grid
        grid = []
        cl = len(self._MATRIX[0])
        part = self._MATRIX.partitions
        for y in row_y:
            x1, x2 = bounds.bounds(y)
            width = x2 - x1
            grid.append([(x1 + width*factor, y) for factor in part])
        
        if grid[-1][-1][1] > y2:
            raise LineOverflow
        """
        return row_u[-1]

    def run_stats(self, spell):
        return sum(block.run_stats(spell) for block in chain.from_iterable(cell.content for cell in self._FLOW))

    def highlight_spelling(self):
        return chain.from_iterable(cell.highlight_spelling() for cell in self._FLOW)
    
    def transfer(self, S):
        for cell in self._FLOW:
            cell.transfer(S)
        
members = [Table, Table_tr, Table_td]

"""
class _MBlock(Block):
    def __init__(self, FLOW, grid, table, regions, PP):
        self._table = table
        Block.__init__(self, FLOW, grid[0][0][1], grid[-1][-1][1], grid[0][0][0], grid[-1][-1][0], PP)
        
        self._grid = grid
        self._ortho = list(zip( * grid ))
        self._regions = regions

    def _print_annot(self, cr, O):
        if O in self._FLOW:
            cr.set_source_rgb( * accent)
            for x, y in chain.from_iterable(self._grid):
                cr.rectangle(int(x), y - 3.25, 0.5, 7)
                cr.rectangle(int(x) - 3.25, y, 7, 0.5)
            self._handle(cr)
            cr.fill()

    def _print_table(self, cr):
        rulewidth = self._table['rulewidth']
        e = (rulewidth % 2) / 2
        p = self._table['rulemargin']
        cr.set_line_width(rulewidth)
        cr.set_source_rgb(0, 0, 0)
        for hrule in self._table['hrules']:
            if p:
                for a, b in zip(self._grid[hrule], self._grid[hrule][1:]):
                    cr.move_to(a[0] + p, a[1] + e)
                    cr.line_to(b[0] - p, b[1] + e)
                    cr.stroke()
            else:
                a = self._grid[hrule][0]
                b = self._grid[hrule][-1]
                cr.move_to(a[0], a[1] + e)
                cr.line_to(b[0], b[1] + e)
                cr.stroke()

        for vrule in self._table['vrules']:
            if p:
                for a, b in zip(self._ortho[vrule], self._ortho[vrule][1:]):
                    cr.move_to(a[0] + e, a[1] + p)
                    cr.line_to(b[0] + e, b[1] - p)
                    cr.stroke()
            else:
                a = self._ortho[vrule][0]
                b = self._ortho[vrule][-1]
                cr.move_to(a[0] + e, a[1])
                cr.line_to(b[0] + e, b[1])
                cr.stroke()

    def target(self, x, y):
        if x <= self['right']:
            return self._regions(x, y, self._table['_bounds'], self._table['_row_y'])
        return None

    def deposit(self, repository):
        repository['_paint'].append((self._print_table, 0, 0))
        repository['_paint_annot'].append((self._print_annot, 0, 0))
        for A in self._FLOW:
            A.deposit(repository)
"""
