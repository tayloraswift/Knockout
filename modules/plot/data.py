from meredith.paragraph import Plane

class Data(Plane):
    def _key_icon(self, cr, k1, k2):
        cr.set_source_rgba( * self['color'] )
        cr.rectangle(self._right, k1, -4, k2 - k1)
        cr.fill()

    def key(self):
        if self['key']:
            return (Flowing_text(self.content), self._key_icon, self['color']),
        else:
            return ()
    
    def freeze(self, h):
        self._right = h
