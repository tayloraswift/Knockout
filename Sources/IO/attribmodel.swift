protocol AssignableFormatDict: class
{
    func assign(gene:Gene, valstr:String, strdict:inout [String: String])
}

protocol StorableFormatDict: class
{
    associatedtype T
    static
    var absolute_defval:T { get }
    var dict:[String: T] { get set }
    static
    func interpret(_ str:String, gene:Gene) -> T?
}

extension StorableFormatDict where Self: AssignableFormatDict
{
    func assign(gene:Gene, valstr:String, strdict _:inout [String: String])
    {
        self.dict[gene.name] = Self.interpret(valstr, gene: gene) ?? Self.interpret(gene.defstr, gene: gene) ?? Self.absolute_defval
    }
}

protocol RepresentableFormatDict:StorableFormatDict
{
    static
    func repr(_ v:T, gene:Gene) -> String
}

extension RepresentableFormatDict where Self: AssignableFormatDict
{
    func assign(gene:Gene, valstr:String, strdict:inout [String: String])
    {
        let v:T = Self.interpret(valstr, gene: gene) ?? Self.interpret(gene.defstr, gene: gene) ?? Self.absolute_defval
        self.dict[gene.name] = v
        strdict[gene.name] = Self.repr(v, gene: gene)
    }
}

class PolarDict<T>
{
    //fileprivate
    var dict:[String: T] = [:]
    subscript(name:String) -> T?
    {
        get
        {
            return self.dict[name]
        }
    }
}

class SyncedDict<T: Equatable>:PolarDict<T>
{
    class
    func repr(_ v:T, gene:Gene) -> String
    {
        return String(describing: v)
    }
}

final
class BoolDict:SyncedDict<Bool>, RepresentableFormatDict, AssignableFormatDict
{
    static
    let absolute_defval:Bool = false
    class
    func interpret(_ str:String, gene:Gene) -> Bool?
    {
        if str == "true" || str == "True"
        {
            return true
        }
        else if str == "false" || str == "False"
        {
            return false
        }
        else if let n = IntDict.interpret(str, gene: gene)
        {
            return n != 0
        }
        else
        {
            return nil
        }
    }
}

final
class IntDict:SyncedDict<Int>, RepresentableFormatDict, AssignableFormatDict
{
    static
    let absolute_defval:Int = 0
    static
    func interpret(_ str:String, gene:Gene) -> Int?
    {
        return Int(str, radix:gene.formatinfo.radix) // add arithmetic functionality later
    }
}

final
class FloatDict:SyncedDict<Double>, RepresentableFormatDict, AssignableFormatDict
{
    static
    let absolute_defval:Double = 0
    class
    func interpret(_ str:String, gene:Gene) -> Double?
    {
        return Double(str) // add arithmetic functionality later
    }

    override class
    func repr(_ f:Double, gene:Gene) -> String
    {
        if f <= Double(Int.max) && abs(f.truncatingRemainder(dividingBy: 1)) < 0.00_000_1
        {

            return String(describing: Int(f))
        }
        else
        {
            return String(describing: f)
        }

    }
}

final
class BinomialDict:SyncedDict<Binomial>, RepresentableFormatDict, AssignableFormatDict
{
    static
    let absolute_defval:Binomial = Binomial(β_0: 0, β_1: 0)
    class
    func interpret(_ str:String, gene:Gene) -> Binomial?
    {
        return Binomial(str, gene: gene)
    }

    override class
    func repr(_ v:Binomial, gene:Gene) -> String
    {
        return v.repr(gene: gene)
    }
}

final
class StrDict:PolarDict<String>, StorableFormatDict, AssignableFormatDict
{
    static
    let absolute_defval:String = "" // this is never used but we need it for the protocol
    class
    func interpret(_ str:String, gene:Gene) -> String?
    {
        return str
    }
}
