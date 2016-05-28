from bisect import bisect
from itertools import chain, accumulate, groupby

from olivia.frames import Subcell
from interface.base import accent
from meredith.box import Box
from meredith.paragraph import Plane, Blockelement

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
        self._planes = set(self._FLOW)
        
        # columns
        cl = len(self._MATRIX[0])
        distr = [0] + [d if d else 1 for d in self['distr']]
        distr.extend([1] * (cl - len(distr) + 1))
        total = sum(distr)
        self._MATRIX.partitions = tuple(accumulate(d/total for d in distr))
        
        # rules
        r = len(self._MATRIX)
        self._hrules = [i for i in self['hrules'] if 0 <= i <= r]
        self._vrules = [i for i in self['vrules'] if 0 <= i <= cl]

    def which(self, x, u, r):
        if (r > 1 or r < 0) and x > self.left_edge:
            x1, x2, *_ = self._frames.at(u)
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
        
        row_u = [frames.read_u()] * (len(self._MATRIX) + 1)
        part = self._MATRIX.partitions
        cellbottom = self['cellbottom']
        for r, overlay, row in ((c, P_table, b) if c else (c, head, b) for c, b in enumerate(self._CELLS)):
            frames.space(self['celltop'])
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
        
        
        # calculate grid
        grid = []
        pgrid = []
        cl = len(self._MATRIX[0])
        for u in row_u:
            x1, x2, y, pn = frames.at(u)
            width = x2 - x1
            grid.append([(int(round(x1 + width*factor)), y) for factor in part])
            pgrid.append(pn)
        self._grid = grid
        self._ortho = list(zip( * grid ))

        # calculate annot grid
        grouped_rows = ((page, list(g[1] for g in G)) for page, G in groupby(enumerate(grid), key=lambda R: pgrid[R[0]]))
        paint_annot_functions = [(page, (lambda * args: self._paint_annot( * args, rows), 0, 0)) for page, rows in grouped_rows]
        # calculate grid
        grouped_rules = ((page, list(G)) for page, G in groupby(self._hrules, key=lambda h: pgrid[h]))
        paint_functions = [(page, (lambda * args: self._paint_table_hrules( * args, rows), 0, 0)) for page, rows in grouped_rules]
        p0 = pgrid[0]
        if self._vrules and len(paint_annot_functions) == 1:
            paint_functions.append((p0, (self._paint_table_vrules, 0, 0)))
        
        return row_u[-1], [], self._FLOW, paint_functions, paint_annot_functions

    def _paint_annot(self, cr, O, rows):
        if O in self._planes:
            cr.set_source_rgb( * accent )
            for x, y in chain.from_iterable(rows):
                cr.rectangle(int(x), y - 3.25, 0.5, 7)
                cr.rectangle(int(x) - 3.25, y, 7, 0.5)
            cr.fill()

    def _paint_table_hrules(self, cr, hrules):
        e = (self['rulewidth'] % 2) / 2
        p = self['rulemargin']
        cr.set_line_width(self['rulewidth'])
        cr.set_source_rgb(0, 0, 0)
        for hrule in hrules:
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

    def _paint_table_vrules(self, cr):
        e = (self['rulewidth'] % 2) / 2
        p = self['rulemargin']
        cr.set_line_width(self['rulewidth'])
        cr.set_source_rgb(0, 0, 0)
        for vrule in self._vrules:
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

members = [Table, Table_tr, Table_td]
