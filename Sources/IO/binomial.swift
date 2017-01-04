import Taylor

struct Binomial: Equatable
{
    private static
    let minus = Set<UnicodeScalar>("--–".unicodeScalars),
        signs = Binomial.minus.union("+".unicodeScalars),
        numbers = Set<UnicodeScalar>("1234567890.".unicodeScalars),
        allowed_gray = Binomial.signs ∪ Binomial.numbers
    let β_1:Double, β_0:Double

    private
    enum MathStates
    {
        case sign, scalar, dead
    }

    init(β_0:Double, β_1:Double)
    {
        self.β_0 = β_0
        self.β_1 = β_1
    }

    init(_ str:String, gene:Gene)
    {
        let symbol:UnicodeScalar = Binomial.pick_symbol(out_of: str, prefer: gene.formatinfo.symbol)
        let allowed_chars = Binomial.allowed_gray ∪ Set([symbol])
        let expression = str.unicodeScalars.filter{ allowed_chars.contains($0) }
        var β_1:Double = 0
        var β_0:Double = 0

        var state:MathStates = .sign
        var i:Int = 0, j:Int = 0
        var period_spotted:Int = 0

        var scalar:Double = 1
        func get_abs_val() -> Double
        {
            var float_str = ""
            expression[Range(i...j)].forEach{ float_str.append(Character($0)) }
            return FloatDict.interpret(float_str, gene: gene) ?? 1
        }

        for (k, c) in expression.enumerated()
        {
            if c ∈ Binomial.signs
            {
                if state != MathStates.sign
                {
                    if state == MathStates.scalar
                    {
                        β_0 += scalar * get_abs_val()
                    }
                    state = MathStates.sign
                    scalar = 1
                    period_spotted = 0
                }

                if c != UnicodeScalar("+")
                {
                    scalar = -scalar
                }
            }
            else if c == symbol
            {
                if state != MathStates.dead
                {
                    β_1 += scalar * get_abs_val()
                    state = MathStates.dead
                }
            }
            else
            {
                if state == MathStates.sign
                {
                    i = k
                    state = MathStates.scalar
                }
                if c == UnicodeScalar(".")
                {
                    period_spotted += 1
                }
                if period_spotted < 2 && state == MathStates.scalar
                {
                    j = k
                }

            }

        }
        if state == MathStates.scalar
        {
            β_0 += scalar * get_abs_val()
        }

        self.init(β_0: β_0, β_1: β_1)
    }

    func repr(gene:Gene) -> String
    {
        let str:String
        if self.β_1 != 0
        {
            let coefficient:String = abs(self.β_1) == 1 ? "" : FloatDict.repr(self.β_1, gene: gene)
            if self.β_0 != 0
            {
                let sign:String = self.β_1 < 0 ? " - " : " + "
                str = FloatDict.repr(self.β_0, gene: gene) + sign + coefficient + "K"
            }
            else
            {
                str = self.β_1 < 0 ? "-" + coefficient + "K" : coefficient + "K"
            }
        }
        else
        {
            str = FloatDict.repr(self.β_0, gene: gene)
        }
        return str
    }

    static private
    func pick_symbol(out_of str:String, prefer:UnicodeScalar) -> UnicodeScalar
    {
        var symbol:UnicodeScalar = prefer
        var symbol_count:[UnicodeScalar: Int] = [:]
        var max_count:Int = 0
        for c in str.unicodeScalars.filter({ UnicodeScalar("A")...UnicodeScalar("Z") ~= $0 || UnicodeScalar("a")...UnicodeScalar("z") ~= $0 })
        {
            if c == prefer
            {
                symbol = c
                break
            }
            else
            {
                let n = ( symbol_count[c] ?? 0 ) + 1
                symbol_count[c] = n
                if n > max_count
                {
                    max_count = n
                    symbol = c
                }
            }
        }
        return symbol
    }

    static
    func == (lhs:Binomial, rhs:Binomial) -> Bool
    {
        return lhs.β_0 == rhs.β_0 && lhs.β_1 == rhs.β_1
    }
}
