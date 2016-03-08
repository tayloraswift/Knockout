from collections import Counter

# modified & stripped down counter object for tags

class TCounter(Counter):
    def __le__(self, other):
        for elem, count in self.items():
            ocount = other[elem]
            if not count or not ((count > 0 and ocount >= count) or (count < 0 and ocount <= count)):
                return False
        return True
    
    def __add__(self, other):
        result = self.__class__()
        for elem, count in self.items():
            result[elem] = count + other[elem]
        for elem, count in other.items():
            if elem not in self:
                result[elem] = count
        return result

    def __isub__(self, other):
        for elem, count in other.items():
            self[elem] -= count
        return self
