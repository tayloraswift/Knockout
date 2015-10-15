import bisect

class Channel(object):
    def __init__(self, left, right):
        # create two railings, the borders
        self.railings = [left, right]
    
    def _is_outside(self, y):
        location = True
        if ( self.railings[0][0][1] <= y <= self.railings[1][-1][1] ):
            location = False
        return location
                    
    def edge(self, r, y):
        i = bisect.bisect([point[1] for point in self.railings[r]], y)
        # if y if below the last point
        try:
            xbelow = self.railings[r][i][0]
        except IndexError:
            return self.railings[r][-1]
        xabove = self.railings[r][i - 1][0]
        factor = (y - self.railings[r][i - 1][1])/(self.railings[r][i][1] - self.railings[r][i - 1][1])
        # returns an x coordinate, and the index of the point
        return (xbelow - xabove)*factor + xabove , i
    
    def insert_point(self, r, y):
        y = 10*round(y/10)
        # make sure to only insert points between the portals
        if not self._is_outside(y):
            x, i = self.edge(r, y)
            x = 10*round(x/10)
            self.railings[r].insert(i, [x, y, True])
            return i
        else:
            return None
    
    def _is_corner(self, r, i):
        if i == 0 or i == -1 or i == len(self.railings[r]) - 1:
            return True
        else:
            return False
    
    def move_point_to(self, r, i, x, y):
        x, y = 10*round(x/10), 10*round(y/10)
        # prevent points from falling on top of one another
        if [x, y] not in [p[:2] for p in self.railings[r]]:
            self.railings[r][i] = [x, y, True]
            # if top or bottom, translate the other point too
            if abs(self._is_corner(r, i)):
                # first or last point
                if i > 0:
                    i = -1
                self.railings[not r][i][1] = y

    def move_point_unconstrained(self, r, i, x, y):
        x, y = 10*round(x/10), 10*round(y/10)
        self.railings[r][i] = [x, y, True]

    def fix(self, r):
        # removes points that are outside the portals
        self.railings[r][:] = [point for point in self.railings[r] if not self._is_outside(point[1])]
        # sort list
        self.railings[r].sort(key = lambda k: k[1])
    
    def target_portal(self, x, y, radius=0):
        portal = None
        if self.railings[0][0][1] - radius - 5 <= y <= self.railings[0][0][1] + radius:
            if self.railings[0][0][0] < x < self.railings[1][0][0]:
                portal = ('entrance', x, y, self.railings[0][0][0], self.railings[0][0][1], self.railings[1][0][0])

        elif self.railings[0][-1][1] - radius <= y <= self.railings[0][-1][1] + radius + 5:
            if self.railings[0][-1][0] < x < self.railings[1][-1][0]:
                portal = ('portal', x, y, self.railings[0][-1][0], self.railings[0][-1][1], self.railings[1][-1][0])
        return portal
    
    
class Channels(object):
    def __init__(self, ic):
        self.channels = ic
 #####################   
    def target_channel(self, x, y, radius):
        for c, channel in enumerate(self.channels):
            if y >= channel.railings[0][0][1] - radius and y <= channel.railings[1][-1][1] + radius:
                if x >= channel.edge(0, y)[0] - radius and x <= channel.edge(1, y)[0] + radius:
                    return c
        return None
#######################
    def target_point(self, x, y, radius):
        cc, rr, ii = None, None, None
        for c in range(len(self.channels)):
            for r in range(len(self.channels[c].railings)):
                for i, point in enumerate(self.channels[c].railings[r]):
                    if abs(x - point[0]) + abs(y - point[1]) < radius:

                        return c, r, i
                # if that fails, take a railing, if possible
                if not self.channels[c]._is_outside(y) and abs(x - self.channels[c].edge(r, y)[0]) <= radius:
                    cc, rr, ii = c, r, None
        return cc, rr, ii
        
    def clear_selection(self):
        for c in range(len(self.channels)):
            for r in range(len(self.channels[c].railings)):
                for point in self.channels[c].railings[r]:
                    point[2] = False
    def delete_selection(self):
        for c in range(len(self.channels)):
            for r, railing in enumerate(self.channels[c].railings):
                railing[:] = [point for i, point in enumerate(railing) if not point[2] or self.channels[c]._is_corner(r, i)]


    def generate_channel(self):
        x1, y1, x2 = self.channels[-1].railings[0][-1][0], self.channels[-1].railings[0][-1][1] + 40, self.channels[-1].railings[1][-1][0]
        return Channel( [[x1, y1, False], [x1, y1 + 40, False]], [[x2, y1, False], [x2, y1 + 40, False]] )
    
    def add_channel(self):
        self.channels.append(self.generate_channel())

