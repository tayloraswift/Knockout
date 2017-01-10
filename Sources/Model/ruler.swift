extension Array where Element: Comparable
{
    fileprivate
    mutating func insertion_sort_one_item(at i:Int) -> Int
    // it’s okay, i thought this was a weird thing to need too
    {
        let too_high:Bool // else it’s too low...can’t please everyone
        if i > 0
        {
            too_high = self[i - 1] > self[i]
        }
        else if self.count > 1
        {
            too_high = self[0] < self[1]
        }
        else
        {
            return i
        }

        var j = i
        if too_high
        {
            while j > 0 && self[j - 1] > self[j] // still too high
            {
                (self[j - 1], self[j]) = (self[j], self[j - 1])
                j -= 1
            }
        }
        else
        {
            let stay_away = self.count - 1
            while j < stay_away && self[j] > self[j + 1] // still too low
            {
                (self[j], self[j + 1]) = (self[j + 1], self[j])
                j += 1
            }
        }
        return j
    }
}

public final
class Ruler:ObjectReprElement
{
    private(set)
    var ruler:[Int]
    private(set)
    var selected:Int?
    // ^ for interface drawing
    private
    let increment:Int

    init(_ points:[Int] = [], increment:Int = 10)
    {
        self.ruler = points
        self.increment = increment
    }

    convenience
    init(_ str:String, gene:Gene)
    {
        self.init(str.characters.split_on_whitespace().flatMap{IntDict.interpret($0, gene: gene)})
    }

    func repr(gene _:Gene) -> String
    {
        return self.ruler.map(String.init).joined(separator: " ")
    }

    // covered: what do you think
    func deselect()
    {
        self.selected = nil
    }

    // covered: yes
    func press(u:Int)
    {
        let b = self.ruler.bisect(u, with: (<=))
        self.selected = self.find_elem(closest_to: u, bin: b)
        if self.selected == nil
        {
            self.ruler.insert(self.round(u), at: b)
            self.selected = b
        }
    }

    // covered: yes
    func motion_press(u:Int)
    {
        if let i = self.selected
        {
            self.ruler[i] = self.round(u)
        }
    }

    // covered: yes
    func release()
    {
        if let i = self.selected
        {
            self.selected = self.ruler.insertion_sort_one_item(at: i)
            // the old version was O(n), this implementation is O(n), but it feels like a uglier and more complicated O(n)
        }
    }

    // covered: no, because this is too simple and my mocking function is getting too complicated
    func delete()
    {
        if let i = self.selected
        {
            self.ruler.remove(at: i)
            self.selected = nil
        }
    }

    // covered: no, but shit would hit the fan if it didn’t work
    private
    func round(_ u:Int) -> Int // round to nearest increment, but you already knew that
    {
        let z = u + self.increment/2
        let r = (z % self.increment)
        return z - (r >= 0 ? r : r + self.increment)
        // me neither. http://stackoverflow.com/a/41180619/6451264
    }

    // covered: no, but motion_press(:) is and that’s close enough isn’t it
    private
    func find_elem(closest_to u:Int, bin:Int) -> Int?
    {
        if self.ruler.isEmpty
        {
            return nil
        }
        var i = bin
        let d2 = i < self.ruler.count ? self.ruler[i] - u : Int.max

        let d1 = i > 0 ? u - self.ruler[i - 1] : Int.max
        if d1 < d2
        {
            i -= 1
        }
        return 2*abs(u - self.ruler[i]) <= self.increment ? i : nil
    }
}
