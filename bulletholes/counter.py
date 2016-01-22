from collections import Counter

# modified counter object for tags

class TCounter(Counter):
    def __le__(self, other):
        for elem, count in self.items():
            newcount = count - other[elem]
            if (newcount > 0 and count > 0) or (newcount < 0 and count < 0):
                return False
        return True
